#!/usr/bin/python3

import argparse
import pathlib
from datetime import datetime 
from typing import List
from ietfdata import datatracker
import ciserver.fs as fs
import ciserver.dlclient as dl


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

            urls += [ dl.IETF_URI( submission.name , extn,  submission.rev ) for extn in submission.file_types.split(sep=',') ] 
    return urls

def parse_cmdline():
    epoch = '1970-01-01 00:00:00',
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
    ap.add_argument("uri",
                    metavar='uri',
                    nargs="*",
                    help="provide draft[-rev][.extn]/ rfc[.extn]/ file-name ")

    _obj = ap.parse_args()
    if _obj.newdraft:
        fromdate = datetime.strptime( _obj.newdraft , "%Y-%m-%d %H:%M:%S")
        with fs.RootWorkingDir(root=pathlib.Path(pathlib.Path.cwd(), "nci")) as rwd, dl.DownloadClient(fs=rwd) as dlclient :
            # preprocessing before actual parser call
            drafts = fetch_new_drafts( rwd.prev_sync_time('draft', None if _obj.newdraft == epoch else _obj.newdraft ))
            for u in drafts : 
                print(f"Draft --> {u}")
            dlclient.download_files( drafts )

            # to-do call parser

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
        for arg in _obj_uri :
            if resolve_argtype(arg) == 'remote' :
                remote.append( arg )
            else : 
                local.append( arg )
        print(f"We got positional arguments uri = {_obj.uri}")


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
