#!/usr/bin/python3

import argparse
import pathlib
import re
import functools
from datetime import datetime 
from typing import List,Tuple
from ietfdata import datatracker
import ciserver.fs as fs
import ciserver.dlclient as dl

# supported document extensions 
valid_extns = [".xml", ".txt"]

def fetch_new_drafts( since : datetime ) -> List[dl.IETF_URI] :
    trk = datatracker.DataTracker()
    draft_itr = trk.documents( since = since.strftime("%Y-%m-%dT%H:%M:%S") , 
                               doctype = trk.document_type( datatracker.DocumentTypeURI("/api/v1/name/doctypename/draft/")))
    urls = [] 
    for draft in draft_itr :
        for uri in draft.submissions:
            submission = trk.submission( uri )
            if not submission :
                break 

            urls += [ dl.IETF_URI( submission.name , extn,  rev= submission.rev, dtype="draft" ) 
                             for extn in submission.file_types.split(sep=',') if extn in valid_extns ] 
    return urls



class PositionalArg :
    def __init__(self, arg ): 
       self.arg = arg


    def _match_name( self , fname : str ) -> Tuple[str,str,str,str] :
        extn_str = functools.reduce( lambda x,y : x + f'|{y}', valid_extns) 
        # document with revision 
        regex_rev = re.compile(f"(?P<dtype>draft-|Draft-|DRAFT-)"
                               f"(?P<name>[a-zA-Z0-9_\-]+)"
                               f"-(?P<rev>[0-9]+)"
                               f"(?P<extn>{extn_str})?")
        # document without revision
        regex_std = re.compile(f"(?P<dtype>draft-|Draft-|DRAFT-|rfc|RFC|Rfc)?"
                               f"(?P<name>[a-zA-Z0-9_\-]+)"
                               f"(?P<extn>{extn_str})?")

        _match = regex_rev.match(fname) 
        if _match != None : 
            return ( "draft", _match.group("name") , _match.group("rev") , _match.group("extn")) 

        _match = regex_std.match(fname) 
        if _match != None :
            dtype = None
            if _match.group('dtype') : 
                if _match.group('dtype').lower() == "draft-" : 
                    dtype = "draft"
                elif _match.group('dtype').lower() == "rfc" : 
                    dtype = "rfc"
            return ( dtype , _match.group("name") , None , _match.group("extn")) 
        return None

    def resolve_argtype(self): 
        ret_type, urls  = "" , [] 
        fp = pathlib.Path( self.arg ).resolve() 

        if fp.exists() and fp.is_file(): 
            # Actual file passed in
            assert fp.suffix in valid_extns, f"File {fp} does not have a valid extension type -- {valid_extns}"
            ret_type = "local" 
            rname  = self._match_name(fp.name)
            if rname : 
                dtype, name , rev , extn = rname
                ietf_uri = dl.IETF_URI( name , extn , rev=rev , dtype=dtype)
            else : 
                ietf_uri = dl.IETF_URI( fp.stem , fp.suffix , rev=None ,dtype=None)
            ietf_uri.set_filepath( fp )
            urls.append( ietf_uri )
        else : 
            ret_type = "remote" 
            rname  = self._match_name(fp.name)
            assert rname != None, f"remote-uri {self.arg} misformed. Cannot resolve with datatracker"
            dtype, name , rev , extn = rname
            assert dtype in ['draft', 'rfc' ], f"only draft,rfc supported. Could not resolve document type {dtype}"
            assert False, f"search data tracker for {name} of type {dtype}"

        return ( ret_type , urls ) 


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
             f"(fmt 'yyyy-mm-dd hh:mm:ss'). "
    )
    ap.add_argument(
        "-nr",
        "--newrfc",
        metavar="from",
        nargs='?',
        const=epoch, 
        help=f"Get all new rfcs from ietf data tracker. "
             f"If from date is provided, pick up drafts from given date "
             f"(fmt 'yyyy-mm-dd hh:mm:ss'). "
    )
    ap.add_argument(
        "-d",
        "--dir",
        metavar="dir",
        nargs=1,
        default=str(pathlib.Path().cwd() / "ietf_data_cache"), 
        help=f"Root directory for all files"
    )
    ap.add_argument("uri",
                    metavar='uri',
                    nargs="*",
                    help="provide draft[-rev][.extn]/ rfc[.extn]/ file-name ")

    _obj = ap.parse_args()
    infiles = []

    root_dir = pathlib.Path(_obj.dir[0])

    if _obj.newdraft:
        fromdate = datetime.strptime( _obj.newdraft , "%Y-%m-%d %H:%M:%S")
        with fs.RootWorkingDir(root= root_dir) as rwd, dl.DownloadClient(fs=rwd) as dlclient :
            # preprocessing before actual parser call
            drafts = fetch_new_drafts( rwd.prev_sync_time('draft', None if _obj.newdraft == epoch else _obj.newdraft ))
            for u in drafts : 
                print(f"Draft --> {u}")
            dlclient.download_files( drafts )

            infiles += drafts 

            # post-processing starts here
            rwd.update_sync_time("draft")
    elif _obj.newrfc:
        print(f"We got nr = {_obj.newrfc}")
        # preprocessing before actual parser call

        # to-do call parser

        # post-processing starts here
        rwd.update_sync_time("rfc")
    elif _obj.uri:
        remote, local = [] , [] 
        for arg in [ PositionalArg(uri) for uri in _obj.uri ]  : 
            #with fs.RootWorkingDir(root= root_dir) as rwd : 
            #with dl.DownloadClient(fs=rwd) as dlclient : 
            uri_type, urls  = arg.resolve_argtype()
            if uri_type == 'remote' : 
                remote +=  urls 
            elif uri_type == 'local' : 
                local += urls 

        for i, r in enumerate(remote) : 
            print(f"remote [{i}] ->  {r}") 
        print(f"-----------------------------------") 
        for i, r in enumerate(local) : 
            print(f"local [{i}] ->  {r}") 
        print(f"-----------------------------------") 

if __name__ == '__main__':
    parse_cmdline()


#drafts = [ dl.IETF_URI(name='draft-bormann-t2trg-sworn', extn='.txt', rev='00'), 
#         dl.IETF_URI(name='draft-bormann-t2trg-sworn', extn='.txt', rev='01'), 
#         dl.IETF_URI(name='draft-bormann-t2trg-sworn', extn='.txt', rev='02'), 
#         dl.IETF_URI(name='draft-bormann-t2trg-sworn', extn='.txt', rev='03'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.txt', rev='00'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='00'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.txt', rev='01'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='01'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.txt', rev='02'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='02'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.txt', rev='03'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='03'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.txt', rev='04'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='04'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='05'), 
#         dl.IETF_URI(name='draft-www-bess-yang-vpn-service-pm', extn='.xml', rev='06') ]
