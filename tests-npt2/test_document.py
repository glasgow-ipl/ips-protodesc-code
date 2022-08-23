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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib       import Path

from npt2.loader   import Loader
from npt2.document import Document, Node


class TestDocument(unittest.TestCase):
    doc : Document

    @classmethod
    def setUp(self) -> None:
        self.doc = Loader("/Users/csp/Documents/IETF/RFC/rfc9000.xml").load()


    def test_root(self) -> None:
        root = self.doc.root()
        self.assertEqual(root.tag(), "rfc")


    def test_children(self) -> None:
        root  = self.doc.root()
        nodes = list(root.children())
        self.assertEqual(len(nodes), 6)
        self.assertEqual(nodes[0].tag(), "link")
        self.assertEqual(nodes[1].tag(), "link")
        self.assertEqual(nodes[2].tag(), "link")
        self.assertEqual(nodes[3].tag(), "front")
        self.assertEqual(nodes[4].tag(), "middle")
        self.assertEqual(nodes[5].tag(), "back")


    def test_children_recursive(self) -> None:
        root  = self.doc.root()
        nodes = root.children(recursive=True)
        self.assertEqual(len(nodes), 7669)


    def test_find_child(self) -> None:
        root  = self.doc.root()
        front = root.child("front")
        self.assertEqual(front.tag(), "front")


