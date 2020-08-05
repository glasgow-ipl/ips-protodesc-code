# =================================================================================================
# Copyright (C) 2018-2020 University of Glasgow
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

import xml.etree.ElementTree as ET

from npt.protocol import *

# RFC DOM input parsers
import npt.rfc as rfc
import npt.parser_rfc_xml
#import npt.parser_rfc_txt

#from npt.parser               import Parser
#from npt.parser_asciidiagrams import AsciiDiagramsParser

from typing import Union, Optional, List, Tuple


class Test_Parse_XML_Aug_Ascii(unittest.TestCase):
    def test_rfc_head(self) :
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            node = npt.parser_rfc_xml.parse_rfc(xml_tree)


        # No links are present in document
        self.assertIsInstance( node.links, list)
        self.assertEqual( len(node.links), 0 )


        # Test whether front node has been parsed 
        self.assertIsInstance( node.front , rfc.Front )


        # Test whether middle node has been parsed 
        self.assertIsInstance( node.middle , rfc.Middle )

        # Back node is optional -- augmented ascii diagrams contains it
        self.assertIsNotNone( node.back)
        self.assertIsInstance( node.back, rfc.Back )


        # Test attributes
        # TO DO - test each attribute in RFC node attribute

        # category
        category = xml_tree.attrib.get("category", None)
        if category is None :
            self.assertIsNone( node.category )
        else :
            self.assertIsNotNone( node.category )
            self.assertIsInstance( node.category, str)
            self.assertIn( node.category, [ "std", "bcp", "info", "exp", "historic" ])
        


    def test_rfc_front(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            content = npt.parser_rfc_xml.parse_rfc(xml_tree)
            node = content.front

        #print(f">{node.title.content.content}<")
        #print(">\n            Describing Protocol Data Units with Augmented Packet Header Diagrams\n        <")

        # Test whether the title has been parsed correctly
        self.assertIsInstance( node.title , rfc.Title )
        self.assertIsInstance( node.title.content, rfc.Text )
        self.assertIsInstance( node.title.content.content, str )
        self.assertEqual( node.title.content.content.lstrip().rstrip() , 
                "Describing Protocol Data Units with Augmented Packet Header Diagrams")
