#!/usr/bin/python3


import requests
import pathlib
from dataclasses import dataclass, field
from typing import Optional, List
#List, Iterator, Tuple, Optional, TypeVar, Dict, Union
import ciserver.fs as filesys
from ietfdata import datatracker

@dataclass(frozen=True)
class DownloadOptions:
    force: bool = False  # if set to True, override files in cache


@dataclass
class IETF_URI: 
    name : str 
    extn : str 
    rev  : str  = field(default=None)
    dtype: str  = field(default=None)

    def _document_name(self):
        return f"{self.name}-{self.rev}" if self.rev else f"{self.name}"

    def gen_filepath(self, root : pathlib.Path ) -> pathlib.Path :
        if self.rev : 
            self.infile = root / self.name / self.rev / f"{self._document_name()}{self.extn}"
        else : 
            self.infile = root / self.name / f"{self._document_name()}{self.extn}"
        return self.infile 

    def url(self):
        base_url = { "draft" : "https://www.ietf.org/archive/id" , 
                     "rfc"   : "https://www.rfc-editor.org/rfc" } 
        return base_url[self.dtype] + f"/{self._document_name()}{self.extn}"

    def set_filepath(self, filename : pathlib.Path ) -> pathlib.Path :
        self.infile = filename 
        return filename 

    def get_filepath( self ) -> Optional[pathlib.Path] :
        return getattr(self, "infile", None)


@dataclass
class DownloadClient:
    fs: filesys.RootWorkingDir
    dlopts: Optional[DownloadOptions] = field(default_factory=DownloadOptions)

    def __enter__(self) -> None:
        self.session = requests.Session()
        return self

    def __exit__(self, ex_type, ex, ex_tb) -> None:
        self.session.close()
        self.session = None

    def _write_file(self, file_path: pathlib.Path , data: str) -> bool:
        written = False
        file_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

        with open(str(file_path), "w") as fp:
            fp.write(data)
            written = True
        return written

    def _resolve_file_root(self, doc : IETF_URI ) -> pathlib.Path :
        return self.fs.draft if doc.dtype == "draft" else self.fs.rfc 


    def download_files(self, urls: List[IETF_URI]) -> List[IETF_URI]:
        doclist = list()
        for doc in urls: 
            infile = doc.gen_filepath(self._resolve_file_root(doc))

            if not self.dlopts.force : 
                if infile.exists() : 
                    continue 

            dl = self.session.get(doc.url() , verify=True, stream=False) 
            if dl.status_code != 200: 
                print(f"Error : {dl.status_code} while downloading {doc.url(self.base_uri)}")
                continue 

            if self._write_file(infile, dl.text): 
                doclist.append(doc)
                print(f"Stored input file {infile}")
            else : 
                print("Error storing input file {infile}")
        return doclist
