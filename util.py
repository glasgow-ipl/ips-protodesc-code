#!/usr/bin/python3

import argparse
import pathlib
import json
import requests
import re
import functools
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from ietfdata import datatracker, rfcindex

# supported document extensions
valid_extns = [".xml", ".txt"]


@dataclass
class RootWorkingDir: 
    """=================================================================================================================================
    Root directory under which all input files will be stored.  
    Specified on the command-line using using -d option 
    ... defaults to current-working-dir>/ietf_data_cache 
      
    File structure is as follows : 
    root --- 
     |-- .sync  - file holding last polled time for rfcs and drafts. 
     |-- draft/draft-<draft-name>/<rev>/<input-draft-file>.<extn>
     |-- rfc/<rfcname>/<input-rfc-file>.<extn>
     |-- output  - holds the results of parser generator
           |-- draft/draft-<draft-name>/<rev>/<output-draft-file>.<extn>
           |-- rfc/<rfcname>/<output-rfc-file>.<extn>
    """
    root    : pathlib.Path
    doctypes: List[str] = field(default_factory=lambda: ["rfc", "draft"])

    def __post_init__(self) -> None:
        self.root = self.root.resolve()

        if not self.root.exists():
            raise AssertionError(f"Error writing to directory {self.root}")

        assert self.root.exists(), f"Root dir <{self.root}> does not exist."
        assert self.root.is_dir(), f"<{self.root} is not a directory"
        # TODO : Also add check to see if directory is writable
        self.sync = self.root / ".sync"
        self.rfc = self.root / "rfc"
        self.draft = self.root / "draft"
        self.output = self.root / "output"
        self.draft_out = self.root / "output" / "draft"
        self.rfc_out = self.root / "output" / "rfc"

        self.draft.mkdir(exist_ok=True)
        self.rfc.mkdir(exist_ok=True)
        self.output.mkdir(exist_ok=True)
        self.draft_out.mkdir(exist_ok=True)
        self.rfc_out.mkdir(exist_ok=True)

    def __enter__(self):
        """Context manager constructor"""
        self.sync_time = datetime.utcnow()
        self._meta = None
        if self.sync.exists():
            with open(self.sync, 'r') as fp:
                self._meta = json.load(fp)
        return self

    def __exit__(self, ex_type, ex, ex_tb): 
        """Context manager destructor"""
        #print(f"ex-type --> {ex_type}, type --> {type(ex_type)}")
        #print(f"ex --> {ex}, type --> {type(ex)}")
        #print(f"ex-tb  --> {ex_tb}, type --> {type(ex_tb)}")
        pass

    def prev_sync_time(self,
                       doc_type: str,
                       override: Optional[str] = None) -> datetime: 
        """Returns last known time that parser tool was executed 
        within the context of this working directory
        
        If command-line override is provided for start time
        use it.  Otherwise if tool is executed for the first time
        return start time as epoch. 
        """
        if override:
            return datetime.strptime(override, "%Y-%m-%d %H:%M:%S")

        if self._meta == None:
            return datetime(year=1970,
                            month=1,
                            day=1,
                            hour=0,
                            minute=0,
                            second=0)

        if doc_type in self._meta:
            return datetime.strptime(self._meta[doc_type], "%Y-%m-%d %H:%M:%S")
        else:
            return datetime(year=1970,
                            month=1,
                            day=1,
                            hour=0,
                            minute=0,
                            second=0)

    def _new_sync(self) -> Dict[str, str]:
        """contruct and return a default json format for the .sync file"""
        start = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
        dt = start.strftime("%Y-%m-%d %H:%M:%S")
        return {"rfc": dt, "draft": dt}

    def update_sync_time(self, doc_type: str) -> None:
        """Insert / Update current time processing root directory was accessed"""
        if self._meta == None:
            self._meta = self._new_sync()

        if doc_type in self._meta or doc_type in self.doctypes:
            self._meta[doc_type] = self.sync_time.strftime("%Y-%m-%d %H:%M:%S")

        with open(self.sync, 'w') as fp:
            json.dump(self._meta, fp)


@dataclass(frozen=True)
class DownloadOptions:
    """Consolidated list of options to control download client""" 
    force: bool = False  # if set to True, override files in cache


@dataclass
class IETF_URI:
    """Container class to hold data about each document that is processed. 
    dtype - can be one of "draft" or "rfc"
    url - to be utilised in case document has to be accessed from a remote server.
          Not utilised for local files
    rev - only utilised in the case of drafts
    """
    name : str
    extn : str
    rev  : str = field(default=None)
    dtype: str = field(default=None)
    url  : str = field(default=None)

    def _document_name(self):
        return f"{self.name}-{self.rev}" if self.rev else f"{self.name}"

    def gen_filepath(self, root: pathlib.Path) -> pathlib.Path:
        """generate exact filepath from base of root for file
        based on whether document type has a revision or not
        """
        if self.rev:
            self.infile = root / self.name / self.rev / f"{self._document_name()}{self.extn}"
        else:
            self.infile = root / self.name / f"{self._document_name()}{self.extn}"
        return self.infile

    def set_filepath(self, filename: pathlib.Path) -> pathlib.Path:
        """override the standard path of an input file 
        and set the input file to an ad-hoc local file location. 
        Used when specifying local files as positional arguments to tool. 
        """
        self.infile = filename
        return filename

    def get_filepath(self) -> Optional[pathlib.Path]:
        return getattr(self, "infile", None)


@dataclass
class DownloadClient:
    """Client to download remote URL resources in batch"""
    fs   : RootWorkingDir
    dlopts: Optional[DownloadOptions] = field(default_factory=DownloadOptions)

    def __enter__(self) -> None:
        """Context manager constructor"""
        self.session = requests.Session()
        return self

    def __exit__(self, ex_type, ex, ex_tb) -> None:
        """Context manager destructor"""
        self.session.close()
        self.session = None

    def _write_file(self, file_path: pathlib.Path, data: str) -> bool:
        written = False
        file_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

        with open(str(file_path), "w") as fp:
            fp.write(data)
            written = True
        return written

    def _resolve_file_root(self, doc: IETF_URI) -> pathlib.Path:
        return self.fs.draft if doc.dtype == "draft" else self.fs.rfc

    def download_files(self, urls: List[IETF_URI]) -> List[IETF_URI]:
        """Batch download remote url objects"""
        doclist = list()
        for doc in urls:
            infile = doc.gen_filepath(self._resolve_file_root(doc))

            if not self.dlopts.force:
                if infile.exists():
                    continue

            dl = self.session.get(doc.url, verify=True, stream=False)
            if dl.status_code != 200:
                print(f"Error : {dl.status_code} while downloading {doc.url(self.base_uri)}")
                continue

            if self._write_file(infile, dl.text):
                doclist.append(doc)
                print(f"Stored input file {infile}")
            else:
                print("Error storing input file {infile}")
        return doclist


def fetch_new_drafts(since: datetime) -> List[IETF_URI]:
    """Fetch all new drafts since time 'since'""" 
    trk = datatracker.DataTracker()
    draft_itr = trk.documents(
        since=since.strftime("%Y-%m-%dT%H:%M:%S"),
        doctype=trk.document_type(datatracker.DocumentTypeURI("/api/v1/name/doctypename/draft/")))

    urls = []
    for draft in draft_itr:
        for uri in draft.submissions:
            submission = trk.submission(uri)
            if not submission:
                break

            urls += [ IETF_URI(submission.name,
                               _extn,
                               rev=submission.rev,
                               dtype="draft",
                               url=_url) 
                      for _extn, _url in submission.urls() 
                          if _extn in valid_extns
                    ]
    return urls


def fetch_new_rfcs(since: datetime) -> List[IETF_URI]:
    """Fetch all new rfcs since time 'since'""" 
    rfcIndex = rfcindex.RFCIndex()
    rfc_extn_convert = lambda _ext: ".txt" if _ext in [ "ASCII", "TEXT" ] else f".{_ext.lower()}"
    urls = []
    for rfc in rfcIndex.rfcs(since=since.strftime("%Y-%m")):
        for fmt in rfc.formats:
            extn = rfc_extn_convert(fmt)
            if extn not in valid_extns:
                continue
            urls.append( IETF_URI(rfc.doc_id.lower(),
                                  extn,
                                  rev=None,
                                  dtype="rfc",
                                  url=rfc.content_url(fmt)))
    return urls


class PositionalArg:
    """Resolve various modes of positional arguments 
    1. If positional argument is a local file 
       parse and generate code for this file
    2. If not a local file, then it is a remote draft/rfc name. 
        a) If a specific file type is specified, 
           download only the requested file type.
           In the case of drafts, unless a specific revision 
           is requested download all revisions of the draft 
           with the requested file-type. 
        b) Otherwise download all file types. In the case of
           drafts, unless a specific revision is specified, 
           download all allowed input file types of all revisions 
           of drafts. 
    """
    def __init__(self, arg):
        self.arg = arg

    def _match_name(self, fname: str) -> Tuple[str, str, str, str]:
        """Resolve whether spefified name is a draft or rfc and whether
        a revision has been specified. Also determine file 
        extension if specified
        """
        extn_str = functools.reduce(lambda x, y: x + f'|{y}', valid_extns)
        # document with revision
        regex_rev = re.compile(f"(?P<dtype>draft-|Draft-|DRAFT-)"
                               f"(?P<name>[a-zA-Z0-9_\-]+)"
                               f"-(?P<rev>[0-9]+)"
                               f"(?P<extn>{extn_str})?$")
        # document without revision
        regex_std = re.compile(f"(?P<dtype>draft-|Draft-|DRAFT-|rfc|RFC|Rfc)?"
                               f"(?P<name>[a-zA-Z0-9_\-]+)"
                               f"(?P<extn>{extn_str})?$")

        _match = regex_rev.match(fname)
        if _match != None:
            return ("draft", 
                    _match.group('dtype') + _match.group("name"),
                    _match.group("rev"), 
                    _match.group("extn"))

        _match = regex_std.match(fname)
        if _match != None:
            dtype = None
            if _match.group('dtype'):
                if _match.group('dtype').lower() == "draft-":
                    dtype = "draft"
                elif _match.group('dtype').lower() == "rfc":
                    dtype = "rfc"
            return (dtype, 
                    _match.group("dtype") + _match.group("name"), 
                    None,
                    _match.group("extn"))
        return None

    def resolve_argtype(self):
        ret_type, urls = "", []
        fp = pathlib.Path(self.arg).resolve()

        if fp.exists() and fp.is_file():
            # This is a local file. Use as is
            assert fp.suffix in valid_extns, f"File {fp} does not have a valid extension type -- {valid_extns}"
            ret_type = "local"
            rname = self._match_name(fp.name)
            if rname:
                dtype, name, rev, extn = rname
                ietf_uri = IETF_URI(name, extn, rev=rev, dtype=dtype)
            else:
                ietf_uri = IETF_URI(fp.stem, fp.suffix, rev=None, dtype=None)
            ietf_uri.set_filepath(fp)   # override standard file-system structure 
            urls.append(ietf_uri)
        else:
            # Remote file - resolve all details from draft/rfc name 
            # and fetch all relevant input files
            ret_type = "remote"
            rname = self._match_name(fp.name)
            assert rname != None, f"remote-uri {self.arg} misformed. Cannot resolve with datatracker"
            dtype, name, rev, extn = rname
            urls += self._query_datatracker(dtype, name, rev, extn)
        return (ret_type, urls)

    def _query_datatracker(self, doctype, name, rev, extn):
        assert doctype in ['draft', 'rfc'], f"Could not resolve document type {dtype}.Only draft,rfc supported."
        urls = []

        if doctype == 'draft':
            trk = datatracker.DataTracker()
            draft = trk.document_from_draft(name)
            assert draft != None, f"Could not resolve remote draft -- name = {name} , rev = {rev}, extension = {extn}"
            for uri in draft.submissions:
                submission = trk.submission(uri)
                if not submission:
                    continue

                if rev and rev != submission.rev:
                    continue

                if extn == None:
                    urls += [ IETF_URI(submission.name,
                                       _ext,
                                       rev=submission.rev,
                                       dtype="draft",
                                       url=_url) 
                              for _ext, _url in submission.urls() 
                                  if _ext in valid_extns
                            ]
                elif extn in valid_extns:
                    for _sub_extn, _sub_url in submission.urls():
                        if _sub_extn != extn:
                            continue
                        urls.append( IETF_URI(submission.name,
                                              extn,
                                              rev=submission.rev,
                                              dtype="draft",
                                              url=_sub_url))

        elif doctype == 'rfc':
            trk = rfcindex.RFCIndex()
            rfc = trk.rfc(name.upper())
            assert rfc != None, f"Invalid rfc -- {name}"

            rfc_txt_label = lambda fmt: ("ASCII" if "ASCII" in fmt else "TEXT" )
            extn_rfc_convert = lambda _ext: rfc_txt_label(rfc.formats) if _ext == ".txt" else _ext[ 1:].upper()
            rfc_extn_convert = lambda _ext: ".txt" if _ext in ["ASCII", "TEXT"] else f".{_ext.lower()}"

            rfc_extensions = [rfc_extn_convert(_ext) for _ext in rfc.formats]
            dt_extns = [_ext for _ext in rfc_extensions if _ext in valid_extns]

            if extn:
                assert extn in dt_extns, f"File format extn of {name}{extn} not amongst {dt_extns}"
                urls.append( IETF_URI(name,
                                      extn,
                                      rev=None,
                                      dtype="rfc",
                                      url=rfc.content_url(extn_rfc_convert(extn))))
            else:
                urls += [ IETF_URI(name,
                                   _extn,
                                   rev=None,
                                   dtype="rfc",
                                   url=rfc.content_url(extn_rfc_convert(_extn)))
                          for _extn in dt_extns
                        ]
        return urls


def parse_cmdline():
    epoch = '1970-01-01 00:00:00'
    ap = argparse.ArgumentParser(description=f"Parse ietf drafts and rfcs "
                                             f"and autogenerate protocol parsers")

    ap.add_argument(
        "-nd",
        "--newdraft",
        metavar="from",
        nargs='?',
        const=epoch,
        help=f"Get all new drafts from ietf data tracker. "
        f"If from date is provided, pick up drafts from given date "
        f"(fmt 'yyyy-mm-dd hh:mm:ss').")
    ap.add_argument(
        "-nr",
        "--newrfc",
        metavar="from",
        nargs='?',
        const=epoch,
        help=f"Get all new rfcs from ietf data tracker. "
        f"If from date is provided, pick up drafts from given date "
        f"(fmt 'yyyy-mm-dd hh:mm:ss'). ")
    ap.add_argument("-d",
                    "--dir",
                    metavar="dir",
                    nargs=1,
                    default=str(pathlib.Path().cwd() / "ietf_data_cache"),
                    help=f"Root directory for all files")
    ap.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=f"Downloaded files will overwrite files in data directory")
    ap.add_argument("uri",
                    metavar='uri',
                    nargs="*",
                    help="provide draft[-rev][.extn]/ rfc[.extn]/ file-name ")

    _obj = ap.parse_args()
    infiles = []

    root_dir = pathlib.Path(_obj.dir[0])
    dlopts = DownloadOptions(force=_obj.force)

    if _obj.newdraft:
        fromdate = datetime.strptime(_obj.newdraft, "%Y-%m-%d %H:%M:%S")
        with RootWorkingDir(root=root_dir) as rwd, DownloadClient(fs=rwd, dlopts=dlopts) as dlclient:
            # preprocessing before actual parser call
            drafts = fetch_new_drafts( rwd.prev_sync_time( 'draft', None if _obj.newdraft == epoch else _obj.newdraft))
            for _idx, u in enumerate(drafts):
                print(f"Draft [{_idx}] --> {u}")
            dlclient.download_files(drafts)

            infiles += drafts

            # post-processing starts here
            # update meta data within cached filesys
            rwd.update_sync_time("draft")
    elif _obj.newrfc:
        fromdate = datetime.strptime(_obj.newrfc, "%Y-%m-%d %H:%M:%S")
        with RootWorkingDir(root=root_dir) as rwd, DownloadClient(fs=rwd, dlopts=dlopts) as dlclient:
            # preprocessing before actual parser call
            rfcs = fetch_new_rfcs( rwd.prev_sync_time('rfc', None if _obj.newrfc == epoch else _obj.newrfc))
            for _idx, u in enumerate(rfcs):
                print(f"RFC [{_idx}]  --> {u}")
            dlclient.download_files(rfcs)

            infiles += rfcs

            # post-processing starts here
            # update meta data within cached filesys
            rwd.update_sync_time("rfc")
    elif _obj.uri:
        remote, local = [], []
        for arg in [PositionalArg(uri) for uri in _obj.uri]:
            uri_type, urls = arg.resolve_argtype()
            if uri_type == 'remote':
                remote += urls
            elif uri_type == 'local':
                local += urls
        else:
            infiles += local

        with RootWorkingDir(root=root_dir) as rwd, DownloadClient(
                fs=rwd, dlopts=dlopts) as dlclient:
            dlclient.download_files(remote)
            infiles += remote

        for idx, inf in enumerate(infiles):
            print(f"File [{idx}]  --> {inf.get_filepath()}")


if __name__ == '__main__':
    parse_cmdline()
