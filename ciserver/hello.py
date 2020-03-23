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


def debug():
    track = datatracker.DataTracker() 
    k = track.documents(
            since="2020-03-20T00:00:00", doctype= track.document_type("draft"))
    for idx, itr in enumerate(k) : 
        #print("Doc -- [{0:03d}] --> {1}".format(idx,itr))
        print("Doc{0} -- url = {1}".format( idx,  itr.document_url() ))

    
if __name__ == '__main__':
    debug()


