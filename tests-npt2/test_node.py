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

from npt2.document       import Node

class TestNode(unittest.TestCase):
    def test_node___init__(self) -> None:
        n = Node("test")
        self.assertEqual(n.tag(),        "test")
        self.assertEqual(n.parent(),     None)
        self.assertEqual(n.attributes(), {})
        self.assertEqual(n.text(),       "")
        self.assertEqual(n.children(),   [])


    def test_node_attributes(self) -> None:
        n = Node("test")
        self.assertEqual(n.has_attribute("category"), False)

        n.add_attribute("category", "test")
        self.assertEqual(n.has_attribute("category"), True)
        self.assertEqual(n.attribute("category"), "test")

        n.remove_attribute("category")
        self.assertEqual(n.has_attribute("category"), False)


    def test_node_text(self) -> None:
        n = Node("test")
        self.assertEqual(n.text(), "")

        n.add_text("Sample text")
        self.assertEqual(n.text(), "Sample text")

        n.remove_text()
        self.assertEqual(n.text(), "")


    def test_node_children(self) -> None:
        p = Node("test")
        self.assertEqual(p.children(), [])

        c1 = Node("child")
        p.add_child(c1)
        self.assertEqual(p.children(), [c1])
        self.assertEqual(c1.parent(), p)

        c2 = Node("child")
        p.add_child(c2)
        self.assertEqual(p.children(), [c1, c2])
        self.assertEqual(c2.parent(), p)

        c3 = Node("child")
        p.add_child_after(c3, c1)
        self.assertEqual(p.children(), [c1, c3, c2])
        self.assertEqual(c3.parent(), p)

        p.remove_child(c3)
        self.assertEqual(p.children(), [c1, c2])

        p.replace_child(c2, c3)
        self.assertEqual(p.children(), [c1, c3])
        self.assertEqual(c3.parent(), p)


    def test_node_children_recursive(self) -> None:
        p = Node("test")
        self.assertEqual(p.children(), [])

        c1 = Node("child")
        p.add_child(c1)
        self.assertEqual(p.children(), [c1])

        c2 = Node("child-two")
        p.add_child(c2)
        self.assertEqual(p.children(), [c1, c2])

        c3 = Node("child")
        c1.add_child(c3)
        self.assertEqual(p.children(recursive = False), [c1, c2])
        self.assertEqual(p.children(recursive =  True), [c1, c3, c2])
        self.assertEqual(c1.children(), [c3])

        c4 = Node("subchild")
        c3.add_child(c4)
        self.assertEqual(p.children(recursive = False), [c1, c2])
        self.assertEqual(p.children(recursive =  True), [c1, c3, c4, c2])
        self.assertEqual(c1.children(), [c3])
        self.assertEqual(c3.children(), [c4])

        self.assertEqual(p.children(recursive = False, with_tag = "child"), [c1])
        self.assertEqual(p.children(recursive =  True, with_tag = "child"), [c1, c3])



