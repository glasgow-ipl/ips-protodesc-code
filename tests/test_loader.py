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

import hashlib
import os
import sys
import unittest

from npt.loader import InputFile, load_file

class Test_Loader(unittest.TestCase):
    def test_load_file_txt(self):
        inf = load_file("examples/draft-mcquistin-augmented-ascii-diagrams-05.txt")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "2c7f591835d6beb7eda63d9796c10ee77537cbe96c63448e6cc72ce9477b4443")
        else:
            self.fail("Cannot load .txt file")


    def test_load_file_xml(self):
        inf = load_file("examples/draft-mcquistin-augmented-ascii-diagrams-05.xml")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "884ee0f2388512ce66bd9cb35ac364da9c05c46732df59897cc69c13626802ec")
        else:
            self.fail("Cannot load .xml file")


    def test_load_draft_txt(self):
        inf = load_file("draft-perkins-avtcore-rtp-circuit-breakers")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "66a39d0863bc641a772b600c72fb064d0d6e95c3547471a1b173267a06714deb")
        else:
            self.fail("Cannot fetch .txt draft")


    def test_load_draft_xml(self):
        inf = load_file("draft-fairhurst-tsvwg-transport-encrypt")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "decd6339c8f31b053727a3a0533bfd55cc3b568aaaedc03ad9ce789ec39e159b")
        else:
            self.fail("Cannot fetch .xml draft")


    def test_load_draft_txt_version(self):
        inf = load_file("draft-mcquistin-augmented-ascii-diagrams-05.txt")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "2c7f591835d6beb7eda63d9796c10ee77537cbe96c63448e6cc72ce9477b4443")
        else:
            self.fail("Cannot fetch .txt draft version")


    def test_load_draft_xml_version(self):
        inf = load_file("draft-mcquistin-augmented-ascii-diagrams-05.xml")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "884ee0f2388512ce66bd9cb35ac364da9c05c46732df59897cc69c13626802ec")
        else:
            self.fail("Cannot load .xml draft version")


    def test_load_rfc_txt(self):
        inf = load_file("rfc9000.txt")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "f88aae47f8b18e102024916e975e919201d8dde689cba79b01079eaedd402e22")
        else:
            self.fail("Cannot load .txt RFC")


    def test_load_rfc_xml(self):
        inf = load_file("rfc9000.xml")
        if inf is not None:
            hash = hashlib.sha256(inf.data).hexdigest()
            self.assertEqual(hash, "78bf03d20155947b5613e942b513b37b6b25229940002e00124bcfc1856a32a9")
        else:
            self.fail("Cannot load .xml RFC")


if __name__ == '__main__':
    unittest.main()

