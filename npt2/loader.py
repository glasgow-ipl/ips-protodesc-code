# =================================================================================================
# Copyright (C) 2022 University of Glasgow
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

import errno
import json
import os
import requests

from ietfdata.datatracker import DataTracker
from pathlib              import Path
from typing               import List, Union, Optional, Tuple, Dict, Iterator

from npt2.document        import Node, Document
from npt2.loader_txt      import load_txt
from npt2.loader_xml      import load_xml

# =================================================================================================
# Supporting functions:

def url_for_draft(draftname: str) -> str:
    assert draftname.startswith("draft-")
    if draftname.endswith(".txt"):
        return f"https://www.ietf.org/archive/id/{draftname}"
    elif draftname.endswith(".xml"):
        return f"https://www.ietf.org/archive/id/{draftname}"
    else:
        dt = DataTracker()
        prefix = draftname[:-3]
        suffix = draftname[-3:]
        if suffix[0] == "-" and suffix[1].isdecimal() and suffix[2].isdecimal():
            doc = dt.document_from_draft(prefix)
            rev = suffix[1:]
        else:
            doc = dt.document_from_draft(draftname)
            rev = doc.rev
        if doc is None:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT) ,draftname)
        if doc.submissions != []:
            for submission_uri in doc.submissions:
                submission = dt.submission(submission_uri)
                assert submission is not None
                if submission.rev == rev:
                    if ".xml" in submission.file_types.split(","):
                        return f"https://www.ietf.org/archive/id/{submission.name}-{submission.rev}.xml"
                    elif ".txt" in submission.file_types.split(","):
                        return f"https://www.ietf.org/archive/id/{submission.name}-{submission.rev}.txt"
                    else:
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), draftname)
        else:
            return f"https://www.ietf.org/archive/id/{doc.name}-{rev}.txt"


def url_for_rfc(rfc: str) -> str:
    assert rfc.lower().startswith("rfc")
    if rfc.endswith(".txt"):
        return f"https://www.rfc-editor.org/rfc/{rfc}"
    elif rfc.endswith(".xml"):
        return f"https://www.rfc-editor.org/rfc/{rfc}"
    else:
        with requests.Session() as session:
            response = session.get(f"https://www.rfc-editor.org/rfc/{rfc}.json", verify=True)
            if response.status_code == 200:
                meta = json.loads(response.text)
                if "XML" in meta['format']:
                    return f"https://www.rfc-editor.org/rfc/{rfc}.xml"
                elif "TXT" in meta['format']:
                    # Text derived from XML source
                    return f"https://www.rfc-editor.org/rfc/{rfc}.txt"
                elif "ASCII" in meta['format']:
                    # Text derived from non-XML source
                    return f"https://www.rfc-editor.org/rfc/{rfc}.txt"
                else:
                    print(meta)
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), rfc)
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), rfc)



# =================================================================================================
# The Loader class:

class Loader:
    docname : str

    def __init__(self, docname:str) -> None:
        self.docname = docname


    def load(self, verbose:Optional[bool] = False) -> Document:
        if Path(self.docname).exists():
            if verbose:
                print(f"Loading {self.docname}")
            if self.docname.endswith(".txt"):
                with open(self.docname, "r") as inf:
                    return load_txt(inf.read())
            if self.docname.endswith(".xml"):
                with open(self.docname, "rb") as inf:
                    return load_xml(inf.read())
        else:
            url = None
            if self.docname.lower().startswith("draft-"):
                url = url_for_draft(self.docname)
            if self.docname.lower().startswith("rfc"):
                url = url_for_rfc(self.docname)
            if url is not None:
                if verbose:
                    print(f"Loading {url}")
                with requests.Session() as session:
                    response = session.get(url, verify=True)
                    if response.status_code == 200:
                        if url.endswith(".txt"):
                            return load_txt(response.text)
                        if url.endswith(".xml"):
                            return load_xml(response.content)
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.docname)

