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

import os
import sys
import unittest

from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from npt2.loader import Loader

class TestLoader(unittest.TestCase):
    def test_loader___is_local_file(self) -> None:
        loader = Loader("examples/rfc/rfc9293/rfc9293.xml")
        self.assertTrue(loader._is_local_file())
        loader = Loader("rfc9293.xml")
        self.assertFalse(loader._is_local_file())


    def test_loader___url_rfc_xml(self) -> None:
        # Test URL for an XML format RFC:
        loader = Loader("rfc9293.xml")
        self.assertEqual(loader._url(), "https://www.rfc-editor.org/rfc/rfc9293.xml")


    def test_loader___url_rfc_txt(self) -> None:
        # Test URL for a text format RFC:
        loader = Loader("rfc9293.txt")
        self.assertEqual(loader._url(), "https://www.rfc-editor.org/rfc/rfc9293.txt")


    def test_loader___url_rfc_inferred_xml(self) -> None:
        # Test URL for an RFC with no format specified, that's recent enough to have XML available:
        loader = Loader("rfc9293")
        self.assertEqual(loader._url(), "https://www.rfc-editor.org/rfc/rfc9293.xml")


    def test_loader___url_rfc_inferred_txt(self) -> None:
        # Test URL for an RFC with no format specified, that's too old to have XML available
        loader = Loader("rfc3550")
        self.assertEqual(loader._url(), "https://www.rfc-editor.org/rfc/rfc3550.txt")


    def test_loader___url_draft_version_xml(self) -> None:
        # Test URL for an XML format Internet-draft with version number:
        loader = Loader("draft-ietf-quic-transport-29.xml")
        self.assertEqual(loader._url(), "https://www.ietf.org/archive/id/draft-ietf-quic-transport-29.xml")


    def test_loader___url_draft_version_txt(self) -> None:
        # Test URL for a text format Internet-draft with version number:
        loader = Loader("draft-ietf-quic-transport-29.txt")
        self.assertEqual(loader._url(), "https://www.ietf.org/archive/id/draft-ietf-quic-transport-29.txt")


    def test_loader___url_draft_version(self) -> None:
        # Test URL for an Internet-draft with version number but no format:
        loader = Loader("draft-ietf-quic-transport-29")
        self.assertEqual(loader._url(), "https://www.ietf.org/archive/id/draft-ietf-quic-transport-29.xml")


    def test_loader___url_draft_noversion_xml(self) -> None:
        # Test URL for an Internet-draft no version number or format:
        loader = Loader("draft-ietf-quic-transport")
        self.assertEqual(loader._url(), "https://www.ietf.org/archive/id/draft-ietf-quic-transport-34.xml")


    def test_loader___url_draft_noversion_txt(self) -> None:
        # Test URL for an Internet-draft no version number or format, that's old enough to only have text available:
        loader = Loader("draft-ietf-avt-rtp-new")
        self.assertEqual(loader._url(), "https://www.ietf.org/archive/id/draft-ietf-avt-rtp-new-12.txt")


    def test_loader__load_local(self) -> None:
        # Trivial test for the Loader, to demonstrate that it can read from
        # a local file. See test_loader_rfcXXX.py for more extensive tests.
        d = Loader("examples/rfc/rfc9293/rfc9293.xml").load()
        r = d.root()
        self.assertEqual(r.tag(), "rfc")


    def test_loader__load_remote(self) -> None:
        # Trivial test for the Loader, to demonstrate that it can read from
        # a remote URL.  See test_loader_rfcXXX.py for more extensive tests.
        d = Loader("rfc9293.xml").load()
        r = d.root()
        self.assertEqual(r.tag(), "rfc")

