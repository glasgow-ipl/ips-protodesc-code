# =================================================================================================
# Copyright (C) 2021 University of Glasgow
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

import requests

from dataclasses          import dataclass
from ietfdata.datatracker import DataTracker
from ietfdata.rfcindex    import RFCIndex
from pathlib              import Path
from typing               import Optional


@dataclass
class InputFile:
    fmt : str
    data : bytes


def _load_file(name: str) -> Optional[InputFile]:
    #print(f"Loading local file: {name}")
    with open(name, "rb") as inf:
        data = inf.read()
    return InputFile(Path(name).suffix, data)



def _load_draft(name: str) -> Optional[InputFile]:
    if name.endswith(".txt"):
        fmt = ".txt"
        url = f"https://www.ietf.org/archive/id/{name}"
    elif name.endswith(".xml"):
        fmt = ".xml"
        url = f"https://www.ietf.org/archive/id/{name}"
    else:
        dt = DataTracker()
        if name[-1].isdecimal() and name[-2].isdecimal() and name[-3] == "-":
            doc = dt.document_from_draft(name[:-3])
            if doc is None:
                return None
            rev = name[-2:]
        else:
            doc = dt.document_from_draft(name)
            if doc is None:
                return None
            rev = doc.rev

        if doc.submissions != []:
            for submission_uri in doc.submissions:
                submission = dt.submission(submission_uri)
                assert submission is not None
                if submission.rev == rev:
                    if ".xml" in submission.file_types.split(","):
                        fmt = ".xml"
                        url = f"https://www.ietf.org/archive/id/{submission.name}-{submission.rev}.xml"
                    elif ".txt" in submission.file_types.split(","):
                        fmt = ".txt"
                        url = f"https://www.ietf.org/archive/id/{submission.name}-{submission.rev}.txt"
                    else:
                        return None
        else:
            fmt = ".txt"
            url = f"https://www.ietf.org/archive/id/{doc.name}-{rev}.txt"
    with requests.Session() as session:
        #print(f"Download {url}")
        response = session.get(url, verify=True)
        if response.status_code == 200:
            return InputFile(fmt, response.content)
        else:
            return None


def _load_rfc(name: str) -> Optional[InputFile]:
    url = None
    if name.endswith(".txt"):
        fmt = ".txt"
        url = f"https://www.rfc-editor.org/rfc/{name}"
    elif name.endswith(".xml"):
        fmt = ".xml"
        url = f"https://www.rfc-editor.org/rfc/{name}"
    else:
        #print(f"Download https://www.rfc-editor.org/rfc-index.xml")
        entry = RFCIndex().rfc(name.upper())
        if entry is None:
            return None
        fmt = ".xml"
        url = entry.content_url("XML")
        if url is None:
            fmt = ".txt"
            url = entry.content_url("ASCII")
            if url is None:
                raise KeyError(f"no known format for {name}")
    with requests.Session() as session:
        #print(f"Download {url}")
        response = session.get(url, verify=True)
        if response.status_code == 200:
            return InputFile(fmt, response.content)
        else:
            return None


def load_file(name: str) -> Optional[InputFile]:
    if Path(name).exists():
        return _load_file(name)
    elif name.lower().startswith("draft-"):
        return _load_draft(name.lower())
    elif name.lower().startswith("rfc"):
        return _load_rfc(name.lower())
    else:
        return None


