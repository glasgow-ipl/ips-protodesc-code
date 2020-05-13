# =================================================================================================
# Copyright (C) 2018-2019 University of Glasgow
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

import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.append('.')

from protocol import *

# RFC DOM input parsers
import parsers.parser
import parsers.rfc.rfc as rfc
import parsers.rfc.rfc_txt_parser
import parsers.rfc.rfc_xml_parser
import parsers.asciidiagrams.asciidiagrams_parser

class TestParsers(unittest.TestCase):
    def setUp(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as example_file:
            raw_content = example_file.read()
            xml_tree = ET.fromstring(raw_content)
            self.content = parsers.rfc.rfc_xml_parser.parse_rfc(xml_tree)

    def test_asciidiagram_parser(self):
        ascii_diagram_parser = parsers.asciidiagrams.asciidiagrams_parser.AsciiDiagramsParser()
        protocol = ascii_diagram_parser.build_protocol(None, self.content)
        self.assertEqual(protocol.get_protocol_name(),  "Example")
        self.assertEqual(len(protocol.get_pdu_names()), 4)
        #TODO
