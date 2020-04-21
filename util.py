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
    print(f" since date = {since.strftime('%Y-%m-%dT%H:%M:%S')}  -- type = {type( since.strftime('%Y-%m-%dT%H:%M:%S'))}")
    draft_itr = trk.documents( since = since.strftime("%Y-%m-%dT%H:%M:%S") , 
                               doctype = trk.document_type( "draft" ))    # old code 
    #                           doctype = trk.document_type( datatracker.DocumentTypeURI("/api/v1/name/doctypename/draft/"))) # new-code
    urls = [] 
    for draft in draft_itr :
        print(f"adding draft -- {draft}\n")

        for uri in draft.submissions:
            submission = trk.submission( uri )
            if not submission :
                break 

            for extn in submission.file_types.split() : 
                urls.append( dl.IETF_URI( submission.name , submission.rev , extn ))
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
        with fs.RootWorkingDir(root=pathlib.Path(pathlib.Path.cwd(), "nci")) as rwd: 
            drafts = fetch_new_drafts( rwd.prev_sync_time('draft', None if _obj.newdraft == epoch else _obj.newdraft ))
            for it in drafts : 
                print(f"fetch {it}") 

            print(f"Within new-draft block -- " 
                  f"prev draft time = {rwd.prev_sync_time('draft', None if _obj.newdraft == epoch else _obj.newdraft )}, "
                  f"prev rfc time = {rwd.prev_sync_time('rfc')} ")
            rwd.update_sync_time("draft")
    elif _obj.newrfc:
        print(f"We got nr = {_obj.newrfc}")
    elif _obj.uri:
        print(f"We got positional arguments uri = {_obj.uri}")


if __name__ == '__main__':
    parse_cmdline()
