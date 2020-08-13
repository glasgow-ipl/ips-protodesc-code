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


class Test_Parse_XML_Draft_McQuistin_Augmented_Ascii_Diagrams(unittest.TestCase):
    def test_rfc_head(self) :
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            node = npt.parser_rfc_xml.parse_rfc(xml_tree)

        self.assertIsInstance( node.links, list)
        if isinstance( node.links, list) :  # type-check
            self.assertEqual( len(node.links), 0 )


        self.assertIsInstance(node.front,  rfc.Front )
        self.assertIsInstance(node.middle, rfc.Middle )
        self.assertIsInstance(node.back,   rfc.Back )

        self.assertIsNotNone(node.front)
        self.assertIsNotNone(node.middle)
        self.assertIsNotNone(node.back)

        self.assertEqual(node.category, "exp")
        self.assertFalse(node.consensus)
        self.assertEqual(node.docName, "draft-mcquistin-augmented-ascii-diagrams-05")
        self.assertTrue(node.indexInclude)
        self.assertEqual(node.ipr, 'trust200902')
        self.assertIsNone(node.iprExtract)
        self.assertIsNone(node.number)
        self.assertIsNone(node.obsoletes)
        self.assertIsNone(node.prepTime)
        self.assertIsNone(node.seriesNo)
        self.assertFalse(node.sortRefs)
        self.assertEqual(node.submissionType, "IETF")
        self.assertTrue(node.symRefs)
        # FIXME - RFC7991 2.45.14  - default should be "3"
        self.assertEqual(node.tocDepth, None)   # FixMe - RFC7991 2.45.14 
        self.assertTrue(node.tocInclude)
        self.assertIsNone(node.updates)
        self.assertEqual(node.version, "3")


    def test_rfc_front(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            node = npt.parser_rfc_xml.parse_rfc(xml_tree).front

        # Test whether the title has been parsed correctly
        self.assertIsInstance(node.title, rfc.Title )
        self.assertIsInstance(node.title.content, rfc.Text )
        self.assertIsInstance(node.title.content.content, str )
        self.assertEqual(node.title.content.content,"""
            Describing Protocol Data Units with Augmented Packet Header Diagrams
        """)

        self.assertEqual(node.title.abbrev, "Augmented Packet Diagrams")

        # seriesInfo elements
        self.assertIsInstance( node.seriesInfo, list)
        if not isinstance( node.seriesInfo, list) :  #type-check 
            return

        self.assertEqual(len(node.seriesInfo), 1)
        self.assertEqual(node.seriesInfo[0].name,   "Internet-Draft")
        self.assertEqual(node.seriesInfo[0].value,  "draft-mcquistin-augmented-ascii-diagrams-05")
        self.assertEqual(node.seriesInfo[0].status, "experimental")

        # authors 
        self.assertEqual(len(node.authors), 4)
        #author-0
        self.assertIsNotNone(node.authors[0].org)
        if node.authors[0].org is None : # type-check
            return
        self.assertEqual    ( node.authors[0].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone( node.authors[0].address)
        if node.authors[0].address is None : # type-check
            return

        street: rfc.Street   = rfc.Street(content=rfc.Text("School of Computing Science"), ascii=None)
        city: rfc.City       = rfc.City(content=rfc.Text("Glasgow"), ascii=None)
        code: rfc.Code       = rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None)
        country: rfc.Country = rfc.Country(content=rfc.Text("UK"), ascii=None)
        postal_address : List[Union[rfc.City, rfc.Code, rfc.Country, rfc.Region, rfc.Street]] = [ street, city, code, country ]

        self.assertIsInstance( node.authors[0].address.postal, rfc.Postal)
        self.assertEqual     ( node.authors[0].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( node.authors[0].address.phone)
        self.assertIsNone    ( node.authors[0].address.facsimile)
        self.assertEqual     ( node.authors[0].address.email, rfc.Email(content=rfc.Text("sm@smcquistin.uk"), ascii=None)) 
        self.assertIsNone    ( node.authors[0].address.uri)
        self.assertIsNone    ( node.authors[0].asciiFullname)
        self.assertIsNone    ( node.authors[0].asciiInitials)
        self.assertIsNone    ( node.authors[0].asciiSurname)
        self.assertEqual     ( node.authors[0].fullname, "Stephen McQuistin")
        self.assertEqual     ( node.authors[0].initials, "S.")
        self.assertEqual     ( node.authors[0].surname,  "McQuistin")
        self.assertIsNone    ( node.authors[0].role)

        #author-1
        self.assertIsNotNone(node.authors[1].org)
        if node.authors[1].org is None : # type-check
            return
        self.assertEqual     ( node.authors[1].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( node.authors[1].address)
        if node.authors[1].address is None : # type-check
            return
        self.assertIsInstance( node.authors[1].address.postal, rfc.Postal)
        self.assertEqual     ( node.authors[1].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( node.authors[1].address.phone)
        self.assertIsNone    ( node.authors[1].address.facsimile)
        self.assertEqual     ( node.authors[1].address.email,rfc.Email(content=rfc.Text("vivianband0@gmail.com"), ascii=None)) 
        self.assertIsNone    ( node.authors[1].address.uri)
        self.assertIsNone    ( node.authors[1].asciiFullname)
        self.assertIsNone    ( node.authors[1].asciiInitials)
        self.assertIsNone    ( node.authors[1].asciiSurname)
        self.assertEqual     ( node.authors[1].fullname, "Vivian Band")
        self.assertEqual     ( node.authors[1].initials, "V.")
        self.assertEqual     ( node.authors[1].surname,  "Band")
        self.assertIsNone    ( node.authors[1].role)

        #author-2
        self.assertIsNotNone(node.authors[2].org)
        if node.authors[2].org is None : # type-check
            return
        self.assertEqual     ( node.authors[2].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( node.authors[2].address)
        if node.authors[2].address is None : # type-check
            return
        self.assertIsInstance( node.authors[2].address.postal, rfc.Postal)
        self.assertEqual     ( node.authors[2].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( node.authors[2].address.phone)
        self.assertIsNone    ( node.authors[2].address.facsimile)
        self.assertEqual     ( node.authors[2].address.email,rfc.Email(content=rfc.Text("d.jacob.1@research.gla.ac.uk"), ascii=None)) 
        self.assertIsNone    ( node.authors[2].address.uri)
        self.assertIsNone    ( node.authors[2].asciiFullname)
        self.assertIsNone    ( node.authors[2].asciiInitials)
        self.assertIsNone    ( node.authors[2].asciiSurname)
        self.assertEqual     ( node.authors[2].fullname, "Dejice Jacob")
        self.assertEqual     ( node.authors[2].initials, "D.")
        self.assertEqual     ( node.authors[2].surname,  "Jacob")
        self.assertIsNone    ( node.authors[2].role)

        #author-3
        self.assertIsNotNone(node.authors[3].org)
        if node.authors[3].org is None : # type-check
            return
        self.assertEqual     ( node.authors[3].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( node.authors[3].address)
        if node.authors[3].address is None : # type-check
            return
        self.assertIsInstance( node.authors[3].address.postal, rfc.Postal)
        self.assertEqual     ( node.authors[3].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( node.authors[3].address.phone)
        self.assertIsNone    ( node.authors[3].address.facsimile)
        self.assertEqual     ( node.authors[3].address.email,rfc.Email(content=rfc.Text("csp@csperkins.org"), ascii=None)) 
        self.assertIsNone    ( node.authors[3].address.uri)
        self.assertIsNone    ( node.authors[3].asciiFullname)
        self.assertIsNone    ( node.authors[3].asciiInitials)
        self.assertIsNone    ( node.authors[3].asciiSurname)
        self.assertEqual     ( node.authors[3].fullname, "Colin Perkins")
        self.assertEqual     ( node.authors[3].initials, "C. S.")
        self.assertEqual     ( node.authors[3].surname,  "Perkins")
        self.assertIsNone    ( node.authors[3].role)

        # date
        self.assertIsNone( node.date, rfc.Date)

        # areas 
        self.assertIsInstance( node.areas, list)
        if not isinstance( node.areas, list) :  #type-check 
            return
        self.assertEqual( len(node.areas), 0)

        # workgroups
        self.assertIsInstance( node.workgroups, list)
        if not isinstance( node.workgroups, list) :  #type-check 
            return
        self.assertEqual( len(node.workgroups), 0)

        # keywords
        self.assertIsInstance( node.keywords, list)
        if not isinstance( node.keywords, list) :  #type-check 
            return
        self.assertEqual( len(node.keywords), 0)

        # abstract
        self.assertIsNotNone( node.abstract)
        if node.abstract is None : #type-check
            return 
        self.assertIsInstance( node.abstract, rfc.Abstract)
        self.assertIsNone( node.abstract.anchor)
        self.assertIsInstance( node.abstract.content, list) 
        self.assertEqual( len(node.abstract.content), 1) 
        self.assertIsInstance( node.abstract.content[0] , rfc.T) 

        # abstract-t element
        self.assertIsInstance( node.abstract.content[0] , rfc.T) 
        self.assertIsInstance( node.abstract.content[0].content , list) 

        # FIXME : Only one paragraph should be here. Parser should eliminate next empty new-lines 
        self.assertEqual     ( len(node.abstract.content[0].content) , 2)
        self.assertIsInstance( node.abstract.content[0].content[0] , rfc.Text)
        if not isinstance( node.abstract.content[0].content[0], rfc.Text) :
            return 
        self.assertIsInstance( node.abstract.content[0].content[0].content , str) 
        self.assertEqual     ( node.abstract.content[0].content[0].content, """
              This document describes a machine-readable format for specifying
              the syntax of protocol data units within a protocol specification.
              This format is comprised of a consistently formatted packet header
              diagram, followed by structured explanatory text. It is
              designed to maintain human readability while enabling support for
              automated parser generation from the specification document. This
              document is itself an example of how the format can be used.
            """)

        self.assertIsInstance( node.abstract.content[0], rfc.T)
        if not isinstance( node.abstract.content[0], rfc.T): # type-check
            return
        self.assertIsNone( node.abstract.content[0].anchor)
        self.assertIsNone( node.abstract.content[0].hangText)
        self.assertFalse ( node.abstract.content[0].keepWithNext)
        self.assertFalse ( node.abstract.content[0].keepWithPrevious)


        # notes
        self.assertIsInstance( node.notes, list)
        if not isinstance( node.notes, list) : # type-check 
            return
        self.assertEqual( len(node.notes), 0)

        # boilerplate
        self.assertIsNone( node.boilerplate)
