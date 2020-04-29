#!/usr/bin/python3

import pathlib
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class RootWorkingDir:
    root  : pathlib.Path
    doctypes : List[str]  = field( default_factory = lambda: [ "rfc", "draft" ] )

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
        self.sync_time = datetime.utcnow()
        self._meta = None
        if self.sync.exists(): 
            with open(self.sync, 'r') as fp: 
                self._meta = json.load(fp)
        return self


    def __exit__(self, ex_type, ex, ex_tb):
        #print(f"ex-type --> {ex_type}, type --> {type(ex_type)}")
        #print(f"ex --> {ex}, type --> {type(ex)}")
        #print(f"ex-tb  --> {ex_tb}, type --> {type(ex_tb)}")
        pass


    def prev_sync_time(self, doc_type : str , override: Optional[str] = None ) -> datetime :
        if override : 
            return datetime.strptime( override, "%Y-%m-%d %H:%M:%S") 

        if self._meta == None :
            return datetime(year=1970,month=1,day=1,hour=0,minute=0,second=0)

        if doc_type in self._meta :
            return datetime.strptime( self._meta[doc_type], "%Y-%m-%d %H:%M:%S")
        else : 
            return datetime(year=1970,month=1,day=1,hour=0,minute=0,second=0)

    def _new_sync(self) -> Dict[str,str]:
        start = datetime(year=1970,month=1,day=1,hour=0,minute=0,second=0)
        dt = start.strftime("%Y-%m-%d %H:%M:%S")
        return  { "rfc" : dt , "draft" : dt }

    def update_sync_time(self, doc_type : str ) -> None:
        if self._meta == None :
            self._meta = self._new_sync()

        if doc_type in self._meta or doc_type in self.doctypes :
            self._meta[doc_type] = self.sync_time.strftime("%Y-%m-%d %H:%M:%S")

        with open(self.sync, 'w') as fp: 
            json.dump(self._meta,fp)
