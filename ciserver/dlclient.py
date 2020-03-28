#!/usr/bin/python3

import pathlib
import requests
import logging
from dataclasses import dataclass, field
from collections import OrderedDict
from typing import List, Iterator, Tuple, Optional, TypeVar
from ietfdata import datatracker
import paths  

T = TypeVar('T') 

@dataclass(frozen=True)
class URI:
    uri: str


@dataclass(frozen=True)
class DocURI(URI):
    def __post_init__(self) -> None:
        assert self.uri.startswith("https://www.ietf.org/archive/id")

@dataclass(frozen=True)
class URIxml(DocURI):
    extn : str =  field(default='.xml', init=False)

    def __post_init__(self) -> None :
        assert pathlib.Path( self.uri ).suffix == self.extn, f"uri {self.uri} does not end in .xml"

@dataclass(frozen=True)
class xmlFile(URI):
    extn : str =  field(default='.xml', init=False)

    def __post_init__(self) -> None :
        assert pathlib.Path( self.uri ).suffix == self.extn, f"uri {self.uri} does not end in .xml"

@dataclass(frozen=True)
class txtFile(URI):
    extn : str =  field(default='.txt', init=False)

    def __post_init__(self) -> None :
        assert pathlib.Path( self.uri ).suffix == self.extn, f"uri {self.uri} does not end in .xml"

@dataclass(frozen=True)
class URItext(DocURI):
    extn : str =  field(default='.txt', init=False)

    def __post_init__(self) -> None :
        assert pathlib.Path( self.uri ).suffix  == self.extn, f"uri {self.uri} does not end in .txt"


WebURITypes = [URIxml, URItext]
FileURITypes = [xmlFile, txtFile]

@dataclass(frozen=True)
class DownloadOptions:
    force: bool = False  # if set to True, override files in cache


@dataclass
class DownloadClient:
    fslock: paths.FileSysLock
    dlopts: Optional[DownloadOptions] = field(default_factory=DownloadOptions)

    def __enter__(self) -> None:
        self.session = requests.Session() 
        return self

    def __exit__(self, ex_type, ex, ex_tb) -> None:
        self.session.close() 
        self.session = None

    def _gen_alt_url(self, url:str, old_extn : str, webURI:T) -> str :
        _index = url.rfind(old_extn)
        assert _index != -1, f"Could not find extension {old_extn} in url {url}"
        return webURI( url[:_index] + webURI.extn )

    def _write_file(self, file_uri:str , data:str) -> bool : 
        written = False 
        # put  any caching and optional checking in this function 
        with open(file_uri.uri, "w") as fp :
            fp.write( data )
            written = True
        return written 

    def _download_pref_url(self, url: str) -> Tuple[int, str, str, str]:
        preferred_doctype = zip( WebURITypes, FileURITypes )
        orig_extn = pathlib.Path(url).suffix

        try :
            while True : 
                webURI, fileURI = next(preferred_doctype) 
                pref_url = self._gen_alt_url(url, orig_extn, webURI ) 
                dl = self.session.get(pref_url.uri, verify=True, stream=False) 
                if dl.status_code != 200 :
                    continue

                logging.debug(f"Downloaded url -- {pref_url}")
                file_path = fileURI( self.fslock.fs.drafts / (pathlib.Path( url ).stem + fileURI.extn))
                if self._write_file( file_path, dl.text ):
                    return file_path  
                else : 
                    logging.critical(f"Error writing File {file_path.uri}"
                                     f"after downloading url -- {pref_url}")
                    raise RuntimeError
        except StopIteration as si_excpt : 
            logging.error(f"Could not find any document types corresponding to url {url}")
            logging.error("Document types searched for = {0}".format( [ obj.extn for obj in self.dlopts.doc_pref])) 
            return None  

    def download_docs(self, urls: List[str]) -> None:
        dl_files = list() 
        for url in urls :
            dl_file = self._download_pref_url(url) 
            if dl_file != None : 
                dl_files.append( dl_file )

def download_draft_daterange(
        since: str = "1970-01-01T00:00:00",
        until: str = "2038-01-19T03:14:07",
        dlopts: DownloadOptions = DownloadOptions()) -> None:
    track = datatracker.DataTracker()
    draft_itr = track.documents(since=since,
                                until=until,
                                doctype=track.document_type("draft"))
    urls = []
    for draft in draft_itr:
        _url = draft.document_url()
        if not dlopts.force:
            # TODO : check whether the file was already downloaded
            # We could use an initial synchronisation run to sha-256 every file in the directory
            # to ensure consistency
            # For now just check the file names
            pass
        urls.append(_url)

    # Download files
    with paths.FileSysLock( paths.RootWorkingDir(pathlib.Path.cwd() / "test_dir")) as fslock, \
                    DownloadClient( fslock) as dlclient: 
        logging.basicConfig(filename=fslock.fs.log, filemode='a', format="%(asctime)s | %(levelname)s : %(message)s", datefmt="%y-%m-%d %H:%M:%S", level=logging.INFO )
        dlclient.download_docs(urls)



if __name__ == '__main__':
    download_draft_daterange(since="2020-03-27T00:00:00")
