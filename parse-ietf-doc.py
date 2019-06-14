#!/usr/bin/env python3.7
# =================================================================================================
# Copyright (C) 2019 University of Glasgow
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

from ietfdata.ietfdata import datatracker
import argparse
import rfc
import requests
import parse_rfc_xml
import xml.etree.ElementTree as ET

ACTIVE_ID_URL   = "https://ietf.org/id/"
ARCHIVED_ID_URL = "https://ietf.org/archive/id/"

def main():
    argparser = argparse.ArgumentParser()
    docnameparser = argparser.add_mutually_exclusive_group(required=True)
    docnameparser.add_argument("--docname", type=str)
    docnameparser.add_argument("--rfc",     type=str)
    docnameparser.add_argument("--bcp",     type=str)
    docnameparser.add_argument("--std",     type=str)
    docnameparser.add_argument("--xml",     type=str)
    docnameparser.add_argument("--txt",     type=str)
    args = argparser.parse_args()
    
    xml = None
    txt = None
    
    if args.docname is not None or args.rfc is not None or args.bcp is not None:
        dt = datatracker.DataTracker()
        if args.docname is not None:
            doc = dt.document("/api/v1/doc/document/%s/" % (args.docname))
            sub = dt.submission(doc.submissions[-1])
            if ".xml" in sub.file_types:
                #FIXME: check status
                xmlReq = requests.get(ACTIVE_ID_URL + sub.name + "-" + sub.rev + ".xml")
                if xmlReq.status_code == 200:
                    xml = xmlReq.text
    
    if xml is not None:
        rfcXml = ET.fromstring(xml)
        parsed_rfc = parse_rfc_xml.parse_rfc(rfcXml)      
    elif txt is not None:
        parsed_rfc = None
        #TODO
    
    print(parsed_rfc)          

if __name__ == "__main__":
    main()