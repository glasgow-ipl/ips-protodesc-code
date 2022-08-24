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


class Loader:
    docname : str

    def __init__(self, docname:str) -> None:
        """
        A loader for an RFC or Internet draft.

        The `docname` is either a local filename representing an RFC or internet-draft,
        an RFC name with an optional extension, such as "rfc9293" or "rfc9293.xml", or
        an internet-draft name with an optional version number and extension, such as
        "draft-ietf-quic-transport", "draft-ietf-quic-transport-15", or
        "draft-ietf-quic-transport-15.txt". If the extension or version number are not
        specified, they will default to the most recent version and most semantically
        rich format available. If the document does not exist as a local file, it will
        be fetched.
        """
        self.docname = docname


    def _is_local_file(self) -> bool:
        return Path(self.docname).exists()


    def _url_draft(self) -> Optional[str]:
        assert not self._is_local_file()
        if self.docname.endswith(".txt"):
            return f"https://www.ietf.org/archive/id/{self.docname}"
        elif self.docname.endswith(".xml"):
            return f"https://www.ietf.org/archive/id/{self.docname}"
        else:
            dt = DataTracker()
            if self.docname[-3] == "-" and self.docname[-2].isdecimal() and self.docname[-1].isdecimal():
                doc = dt.document_from_draft(self.docname[:-3])
                rev = self.docname[-2:]
            else:
                doc = dt.document_from_draft(self.docname)
                rev = None
            if doc is None:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT) ,self.docname)
            if rev == None:
                rev = doc.rev
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
                            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.docname)
            return f"https://www.ietf.org/archive/id/{doc.name}-{rev}.txt"


    def _url_rfc(self) -> Optional[str]:
        assert not self._is_local_file()
        if self.docname.endswith(".txt"):
            return f"https://www.rfc-editor.org/rfc/{self.docname}"
        elif self.docname.endswith(".xml"):
            return f"https://www.rfc-editor.org/rfc/{self.docname}"
        else:
            with requests.Session() as session:
                response = session.get(f"https://www.rfc-editor.org/rfc/{self.docname}.json", verify=True)
                if response.status_code == 200:
                    meta = json.loads(response.text)
                    if "XML" in meta['format']:
                        return f"https://www.rfc-editor.org/rfc/{self.docname}.xml"
                    elif "TXT" in meta['format']:
                        return f"https://www.rfc-editor.org/rfc/{self.docname}.txt"
                    elif "ASCII" in meta['format']:
                        return f"https://www.rfc-editor.org/rfc/{self.docname}.txt"
                    else:
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.docname)
                else:
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.docname)


    def _url(self) -> Optional[str]:
        assert not self._is_local_file()
        if self.docname.lower().startswith("draft-"):
            return self._url_draft()
        if self.docname.lower().startswith("rfc"):
            return self._url_rfc()
        return None


    def load(self, verbose:Optional[bool] = False) -> Document:
        if self._is_local_file():
            if verbose:
                print(f"Loading {self.docname}")
            if self.docname.endswith(".txt"):
                with open(self.docname, "r") as inf:
                    return load_txt(inf.read())
            if self.docname.endswith(".xml"):
                with open(self.docname, "rb") as inf:
                    return load_xml(inf.read())
        else:
            url = self._url()
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

