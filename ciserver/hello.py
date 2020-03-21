from dataclasses import dataclass
from ietfdata import datatracker

import pathlib 

@dataclass(frozen=True)
class Draft :
    xml : str 
    text : str 

@dataclass
class RFC:
    xml : str 
    text : str 

@dataclass 
class Test:
    url : str


@dataclass(frozen=True)
class RootWorkingDir:
    root : str = field(default_factory = lambda : pathlib.Path.cwd())

def debug1():
    track = datatracker.DataTracker() 
    k = track.documents(
            since="2020-03-18T00:00:00", doctype= track.document_type("draft"))
    for idx, itr in enumerate(k) : 
        #print("Doc -- [{0:03d}] --> {1}".format(idx,itr))
        print("Doc{0} -- url = {1}".format( idx,  itr.document_url() ))

def debug():
    r1 = RootWorkingDir()
    r2 = RootWorkingDir("/is/this/the/default")
    print(f"root working directory r1 = {r1.root} , r2 = {r2.root}")
    
if __name__ == '__main__':
    debug()


