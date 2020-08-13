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


    def test_rfc_back(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            back = npt.parser_rfc_xml.parse_rfc(xml_tree).back

        self.assertIsInstance(back, rfc.Back)
        self.assertIsNotNone(back)
        if back is None :  # type-check
            return

        # displayrefs 
        self.assertIsInstance(back.displayrefs, list)
        if not isinstance(back.displayrefs, list):  # type-check 
            return 
        self.assertEqual(len(back.displayrefs), 0)

        # references 
        self.assertIsInstance(back.refs, list)
        if not isinstance( back.refs, list) : # type-check
            return
        self.assertEqual(len(back.refs), 1)

        #references name 
        self.assertIsInstance( back.refs[0].name             , rfc.Name)
        self.assertIsNotNone( back.refs[0].name)
        if back.refs[0].name is None : # type-check
            return
        self.assertIsInstance( back.refs[0].name.content     , list)
        self.assertEqual     ( len(back.refs[0].name.content), 1)
        self.assertIsInstance( back.refs[0].name.content[0]  , rfc.Text)
        self.assertEqual     ( back.refs[0].name.content[0].content, "Informative References")

        # references anchor 
        self.assertIsNone(back.refs[0].anchor)
        # references title 
        self.assertIsNone(back.refs[0].title)

        #references content 
        self.assertIsInstance( back.refs[0].content     , list)
        self.assertEqual     ( len(back.refs[0].content), 14)

        # reference -- 00 
        self.assertIsInstance( back.refs[0].content[0], rfc.Reference)
        # reference -- 00 - front
        if not isinstance( back.refs[0].content[0], rfc.Reference) : # type-check
            return
        self.assertIsInstance( back.refs[0].content[0].front, rfc.Front)
        # reference -- 00 - front.title
        self.assertIsInstance( back.refs[0].content[0].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[0].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[0].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[0].front.title.content.content , "Generalized UDP Source Port for DHCP Relay")
        # reference -- 00 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[0].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[0].front.seriesInfo, list) : # type-check
            return
        self.assertEqual( len(back.refs[0].content[0].front.seriesInfo), 0)
        # reference -- 00 - front.authors 
        self.assertEqual    ( len(back.refs[0].content[0].front.authors), 2)
        # reference -- 00 - front.author - 0 
        self.assertIsNotNone( back.refs[0].content[0].front.authors[0].org)
        if back.refs[0].content[0].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[0].front.authors[0].fullname, "S. Deering" )
        self.assertEqual    ( back.refs[0].content[0].front.authors[0].initials, "S." )
        self.assertIsNone   ( back.refs[0].content[0].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[0].front.authors[0].surname, "Deering" )
        # reference -- 00 - front.author - 1 
        self.assertIsNotNone( back.refs[0].content[0].front.authors[1].org)
        if back.refs[0].content[0].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[0].front.authors[1].fullname, "R. Hinden" )
        self.assertEqual    ( back.refs[0].content[0].front.authors[1].initials, "R." )
        self.assertIsNone   ( back.refs[0].content[0].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[0].front.authors[1].surname,  "Hinden" )
        # reference -- 00 - front.date
        self.assertIsInstance( back.refs[0].content[0].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[0].front.date, rfc.Date) : # type-check
            return
        self.assertIsNone( back.refs[0].content[0].front.date.day)
        self.assertEqual( back.refs[0].content[0].front.date.month, "March")
        self.assertEqual( back.refs[0].content[0].front.date.year, "2018")
        # reference -- 00 - front.areas
        self.assertIsInstance( back.refs[0].content[0].front.areas, list)
        if not isinstance( back.refs[0].content[0].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[0].front.areas), 0)
        # reference -- 00 - front.workgroups
        self.assertIsInstance( back.refs[0].content[0].front.workgroups, list)
        if not isinstance( back.refs[0].content[0].front.workgroups, list): # type-check 
            return
        self.assertEqual( len(back.refs[0].content[0].front.workgroups), 0)
        # reference -- 00 - front.keywords
        self.assertIsInstance( back.refs[0].content[0].front.keywords, list)
        if not isinstance( back.refs[0].content[0].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[0].front.keywords), 0)
        # reference -- 00 - front.abstract
        self.assertIsNone( back.refs[0].content[0].front.abstract)
        # reference -- 00 - front.notes
        self.assertIsInstance( back.refs[0].content[0].front.notes, list)
        if not isinstance( back.refs[0].content[0].front.notes, list):
            return
        self.assertEqual( len(back.refs[0].content[0].front.notes), 0)
        # reference -- 00 - front.boilerplate
        self.assertIsNone( back.refs[0].content[0].front.boilerplate)


        # reference -- 00 - seriesInfo
        self.assertIsInstance( back.refs[0].content[0].content,list)
        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
        self.assertEqual(len(back.refs[0].content[0].content), 1)

        self.assertIsInstance ( back.refs[0].content[0].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[0].content[0], rfc.SeriesInfo) : # type-info
            return
        self.assertEqual      ( back.refs[0].content[0].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[0].content[0].asciiValue, "8357")
        self.assertEqual      ( back.refs[0].content[0].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[0].content[0].status)
        self.assertEqual      ( back.refs[0].content[0].content[0].value,      "8357")
        self.assertIsNone     ( back.refs[0].content[0].content[0].stream)

        # reference -- 00 - anchor
        self.assertEqual(back.refs[0].content[0].anchor, "RFC8357")
        # reference -- 00 - quoteTitle
        self.assertEqual(back.refs[0].content[0].quoteTitle, True)
        # reference -- 00 - target
        self.assertEqual(back.refs[0].content[0].target, "https://www.rfc-editor.org/info/rfc8357")




        # reference -- 01 
        self.assertIsInstance( back.refs[0].content[1], rfc.Reference)
        if not isinstance( back.refs[0].content[1], rfc.Reference):
            return
        # reference -- 01 - front
        self.assertIsInstance( back.refs[0].content[1].front, rfc.Front)
        # reference -- 01 - front.title
        self.assertIsInstance( back.refs[0].content[1].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[1].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[1].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[1].front.title.content.content , "QUIC: A UDP-Based Multiplexed and Secure Transport")
        # reference -- 01 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[1].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[1].front.seriesInfo, list): # type-info
            return
        self.assertEqual( len(back.refs[0].content[1].front.seriesInfo), 0)
        # reference -- 01 - front.authors 
        self.assertEqual    ( len(back.refs[0].content[1].front.authors), 2)
        # reference -- 01 - front.author - 0 
        self.assertIsNotNone( back.refs[0].content[1].front.authors[0].org)
        if back.refs[0].content[1].front.authors[0].org is None : # type-info
            return
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[1].front.authors[0].fullname, "Jana Iyengar" )
        self.assertEqual    ( back.refs[0].content[1].front.authors[0].initials, "J" )
        self.assertIsNone   ( back.refs[0].content[1].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[1].front.authors[0].surname, "Iyengar" )
        # reference -- 01 - front.author - 1 
        self.assertIsNotNone( back.refs[0].content[1].front.authors[1].org)
        if back.refs[0].content[1].front.authors[1].org is None : #  type-check
            return
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[1].front.authors[1].fullname, "Martin Thomson" )
        self.assertEqual    ( back.refs[0].content[1].front.authors[1].initials, "M" )
        self.assertIsNone   ( back.refs[0].content[1].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[1].front.authors[1].surname,  "Thomson" )
        # reference -- 01 - front.date
        self.assertIsInstance( back.refs[0].content[1].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[1].front.date, rfc.Date): # type-check
            return
        self.assertEqual( back.refs[0].content[1].front.date.day, "21")
        self.assertEqual( back.refs[0].content[1].front.date.month, "February")
        self.assertEqual( back.refs[0].content[1].front.date.year, "2020")
        # reference -- 01 - front.areas
        self.assertIsInstance( back.refs[0].content[1].front.areas, list)
        if not isinstance( back.refs[0].content[1].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[1].front.areas), 0)
        # reference -- 01 - front.workgroups
        self.assertIsInstance( back.refs[0].content[1].front.workgroups, list)
        if not isinstance( back.refs[0].content[1].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[1].front.workgroups), 0)
        # reference -- 01 - front.keywords
        self.assertIsInstance( back.refs[0].content[1].front.keywords, list)
        if not isinstance( back.refs[0].content[1].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[1].front.keywords), 0)
        # reference -- 01 - front.abstract
        self.assertIsNone( back.refs[0].content[1].front.abstract)
        # reference -- 01 - front.notes
        self.assertIsInstance( back.refs[0].content[1].front.notes, list)
        if not isinstance( back.refs[0].content[1].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[1].front.notes), 0)
        # reference -- 01 - front.boilerplate
        self.assertIsNone( back.refs[0].content[1].front.boilerplate)


        # reference -- 01 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[1].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[1].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[1].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[1].content[0].asciiName,  "Internet-Draft")
#        self.assertEqual      ( back.refs[0].content[1].content[0].asciiValue, "draft-ietf-quic-transport-27")
#        self.assertEqual      ( back.refs[0].content[1].content[0].name,       "Internet-Draft")
#        self.assertIsNone     ( back.refs[0].content[1].content[0].status)
#        self.assertEqual      ( back.refs[0].content[1].content[0].value,      "draft-ietf-quic-transport-27")
#        self.assertIsNone     ( back.refs[0].content[1].content[0].stream)
#
#        # reference -- 01 - anchor
#        self.assertEqual(back.refs[0].content[1].anchor, "QUIC-TRANSPORT")
#        # reference -- 01 - quoteTitle
#        self.assertEqual(back.refs[0].content[1].quoteTitle, True)
#        # reference -- 01 - target
#        self.assertEqual(back.refs[0].content[1].target, "http://www.ietf.org/internet-drafts/draft-ietf-quic-transport-27.txt")
#
#
#
#        # reference -- 02 
#        self.assertIsInstance( back.refs[0].content[2], rfc.Reference)
#        # reference -- 02 - front
#        self.assertIsInstance( back.refs[0].content[2].front, rfc.Front)
#        # reference -- 02 - front.title
#        self.assertIsInstance( back.refs[0].content[2].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[2].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[2].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[2].front.title.content.content , "RTP Control Protocol (RTCP) Extended Report (XR) Block for Burst/Gap Loss Metric Reporting")
#        # reference -- 02 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[2].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[2].front.seriesInfo), 0)
#        # reference -- 02 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[2].front.authors), 4)
#        # reference -- 02 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[2].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[0].fullname, "Alan Clark" )
#        self.assertEqual    ( back.refs[0].content[2].front.authors[0].initials, "A" )
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[0].surname, "Clark" )
#        # reference -- 02 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[2].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[1].fullname, "Sunshine Zhang" )
#        self.assertEqual    ( back.refs[0].content[2].front.authors[1].initials, "S" )
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[1].surname,  "Zhang" )
#        # reference -- 02 - front.author - 2 
#        self.assertIsNotNone( back.refs[0].content[2].front.authors[2].org)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.content)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].address)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[2].fullname, "Jing Zhao" )
#        self.assertEqual    ( back.refs[0].content[2].front.authors[2].initials, "J" )
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].role)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[2].surname,  "Zhao" )
#        # reference -- 02 - front.author - 3 
#        self.assertIsNotNone( back.refs[0].content[2].front.authors[3].org)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.content)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].address)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[3].fullname, "Qin Wu" )
#        self.assertEqual    ( back.refs[0].content[2].front.authors[3].initials, "Q" )
#        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].role)
#        self.assertEqual    ( back.refs[0].content[2].front.authors[3].surname,  "Wu" )
#        # reference -- 02 - front.date
#        self.assertIsInstance( back.refs[0].content[2].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[2].front.date.day)
#        self.assertEqual( back.refs[0].content[2].front.date.month, "May")
#        self.assertEqual( back.refs[0].content[2].front.date.year, "2013")
#        # reference -- 02 - front.areas
#        self.assertIsInstance( back.refs[0].content[2].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[2].front.areas), 0)
#        # reference -- 02 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[2].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[2].front.workgroups), 0)
#        # reference -- 02 - front.keywords
#        self.assertIsInstance( back.refs[0].content[2].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[2].front.keywords), 0)
#        # reference -- 02 - front.abstract
#        self.assertIsNone( back.refs[0].content[2].front.abstract)
#        # reference -- 02 - front.notes
#        self.assertIsInstance( back.refs[0].content[2].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[2].front.notes), 0)
#        # reference -- 02 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[2].front.boilerplate)
#
#
#        # reference -- 02 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[2].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[2].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[2].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[2].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[2].content[0].asciiValue, "6958")
#        self.assertEqual      ( back.refs[0].content[2].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[2].content[0].status)
#        self.assertEqual      ( back.refs[0].content[2].content[0].value,      "6958")
#        self.assertIsNone     ( back.refs[0].content[2].content[0].stream)
#
#        # reference -- 02 - anchor
#        self.assertEqual(back.refs[0].content[2].anchor, "RFC6958")
#        # reference -- 02 - quoteTitle
#        self.assertEqual(back.refs[0].content[2].quoteTitle, True)
#        # reference -- 02 - target
#        self.assertEqual(back.refs[0].content[2].target, "https://www.rfc-editor.org/info/rfc6958")
#
#
#
#
#        # reference -- 03 
#        self.assertIsInstance( back.refs[0].content[3], rfc.Reference)
#        # reference -- 03 - front
#        self.assertIsInstance( back.refs[0].content[3].front, rfc.Front)
#        # reference -- 03 - front.title
#        self.assertIsInstance( back.refs[0].content[3].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[3].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[3].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[3].front.title.content.content , "The YANG 1.1 Data Modeling Language")
#        # reference -- 03 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[3].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[3].front.seriesInfo), 0)
#        # reference -- 03 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[3].front.authors), 1)
#        # reference -- 03 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[3].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[3].front.authors[0].fullname, "Martin Bjorklund" )
#        self.assertEqual    ( back.refs[0].content[3].front.authors[0].initials, "M" )
#        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[3].front.authors[0].surname, "Bjorklund" )
#        # reference -- 03 - front.date
#        self.assertIsInstance( back.refs[0].content[3].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[3].front.date.day)
#        self.assertEqual( back.refs[0].content[3].front.date.month, "August")
#        self.assertEqual( back.refs[0].content[3].front.date.year, "2016")
#        # reference -- 03 - front.areas
#        self.assertIsInstance( back.refs[0].content[3].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[3].front.areas), 0)
#        # reference -- 03 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[3].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[3].front.workgroups), 0)
#        # reference -- 03 - front.keywords
#        self.assertIsInstance( back.refs[0].content[3].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[3].front.keywords), 0)
#        # reference -- 03 - front.abstract
#        self.assertIsNone( back.refs[0].content[3].front.abstract)
#        # reference -- 03 - front.notes
#        self.assertIsInstance( back.refs[0].content[3].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[3].front.notes), 0)
#        # reference -- 03 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[3].front.boilerplate)
#
#
#        # reference -- 03 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[3].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[3].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[3].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[3].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[3].content[0].asciiValue, "7950")
#        self.assertEqual      ( back.refs[0].content[3].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[3].content[0].status)
#        self.assertEqual      ( back.refs[0].content[3].content[0].value,      "7950")
#        self.assertIsNone     ( back.refs[0].content[3].content[0].stream)
#
#        # reference -- 03 - anchor
#        self.assertEqual(back.refs[0].content[3].anchor, "RFC7950")
#        # reference -- 03 - quoteTitle
#        self.assertEqual(back.refs[0].content[3].quoteTitle, True)
#        # reference -- 03 - target
#        self.assertEqual(back.refs[0].content[3].target, "https://www.rfc-editor.org/info/rfc7950")
#
#
#
#        # reference -- 04 
#        self.assertIsInstance( back.refs[0].content[4], rfc.Reference)
#        # reference -- 04 - front
#        self.assertIsInstance( back.refs[0].content[4].front, rfc.Front)
#        # reference -- 04 - front.title
#        self.assertIsInstance( back.refs[0].content[4].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[4].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[4].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[4].front.title.content.content , "The Transport Layer Security (TLS) Protocol Version 1.3")
#        # reference -- 04 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[4].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[4].front.seriesInfo), 0)
#        # reference -- 04 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[4].front.authors), 1)
#        # reference -- 04 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[4].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[4].front.authors[0].fullname, "Eric Rescorla" )
#        self.assertEqual    ( back.refs[0].content[4].front.authors[0].initials, "E" )
#        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[4].front.authors[0].surname, "Rescorla" )
#        # reference -- 04 - front.date
#        self.assertIsInstance( back.refs[0].content[4].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[4].front.date.day)
#        self.assertEqual( back.refs[0].content[4].front.date.month, "August")
#        self.assertEqual( back.refs[0].content[4].front.date.year, "2018")
#        # reference -- 04 - front.areas
#        self.assertIsInstance( back.refs[0].content[4].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[4].front.areas), 0)
#        # reference -- 04 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[4].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[4].front.workgroups), 0)
#        # reference -- 04 - front.keywords
#        self.assertIsInstance( back.refs[0].content[4].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[4].front.keywords), 0)
#        # reference -- 04 - front.abstract
#        self.assertIsNone( back.refs[0].content[4].front.abstract)
#        # reference -- 04 - front.notes
#        self.assertIsInstance( back.refs[0].content[4].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[4].front.notes), 0)
#        # reference -- 04 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[4].front.boilerplate)
#
#
#        # reference -- 04 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[4].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[4].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[4].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[4].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[4].content[0].asciiValue, "8446")
#        self.assertEqual      ( back.refs[0].content[4].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[4].content[0].status)
#        self.assertEqual      ( back.refs[0].content[4].content[0].value,      "8446")
#        self.assertIsNone     ( back.refs[0].content[4].content[0].stream)
#
#        # reference -- 04 - anchor
#        self.assertEqual(back.refs[0].content[4].anchor, "RFC8446")
#        # reference -- 04 - quoteTitle
#        self.assertEqual(back.refs[0].content[4].quoteTitle, True)
#        # reference -- 04 - target
#        self.assertEqual(back.refs[0].content[4].target, "https://www.rfc-editor.org/info/rfc8446")
#
#
#
#        # reference -- 05 
#        self.assertIsInstance( back.refs[0].content[5], rfc.Reference)
#        # reference -- 05 - front
#        self.assertIsInstance( back.refs[0].content[5].front, rfc.Front)
#        # reference -- 05 - front.title
#        self.assertIsInstance( back.refs[0].content[5].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[5].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[5].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[5].front.title.content.content , "Augmented BNF for Syntax Specifications: ABNF")
#        # reference -- 05 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[5].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[5].front.seriesInfo), 0)
#        # reference -- 05 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[5].front.authors), 2)
#        # reference -- 05 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[5].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[5].front.authors[0].fullname, "Dave Crocker" )
#        self.assertEqual    ( back.refs[0].content[5].front.authors[0].initials, "D" )
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[5].front.authors[0].surname, "Crocker" )
#        # reference -- 05 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[5].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[5].front.authors[1].fullname, "Paul Overell" )
#        self.assertEqual    ( back.refs[0].content[5].front.authors[1].initials, "P" )
#        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[5].front.authors[1].surname,  "Overell" )
#        # reference -- 05 - front.date
#        self.assertIsInstance( back.refs[0].content[5].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[5].front.date.day)
#        self.assertEqual( back.refs[0].content[5].front.date.month, "January")
#        self.assertEqual( back.refs[0].content[5].front.date.year, "2008")
#        # reference -- 05 - front.areas
#        self.assertIsInstance( back.refs[0].content[5].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[5].front.areas), 0)
#        # reference -- 05 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[5].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[5].front.workgroups), 0)
#        # reference -- 05 - front.keywords
#        self.assertIsInstance( back.refs[0].content[5].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[5].front.keywords), 0)
#        # reference -- 05 - front.abstract
#        self.assertIsNone( back.refs[0].content[5].front.abstract)
#        # reference -- 05 - front.notes
#        self.assertIsInstance( back.refs[0].content[5].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[5].front.notes), 0)
#        # reference -- 05 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[5].front.boilerplate)
#
#
#        # reference -- 05 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[5].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[5].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[5].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[5].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[5].content[0].asciiValue, "5234")
#        self.assertEqual      ( back.refs[0].content[5].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[5].content[0].status)
#        self.assertEqual      ( back.refs[0].content[5].content[0].value,      "5234")
#        self.assertIsNone     ( back.refs[0].content[5].content[0].stream)
#
#        # reference -- 05 - anchor
#        self.assertEqual(back.refs[0].content[5].anchor, "RFC5234")
#        # reference -- 05 - quoteTitle
#        self.assertEqual(back.refs[0].content[5].quoteTitle, True)
#        # reference -- 05 - target
#        self.assertEqual(back.refs[0].content[5].target, "https://www.rfc-editor.org/info/rfc5234")
#
#
#        # reference -- 06 
#        self.assertIsInstance( back.refs[0].content[6], rfc.Reference)
#        # reference -- 06 - front
#        self.assertIsInstance( back.refs[0].content[6].front, rfc.Front)
#        # reference -- 06 - front.title
#        self.assertIsInstance( back.refs[0].content[6].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[6].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[6].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[6].front.title.content.content , "ITU-T Recommendation X.680, X.681, X.682, and X.683")
#        # reference -- 06 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[6].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[6].front.seriesInfo), 0)
#        # reference -- 06 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[6].front.authors), 1)
#        # reference -- 06 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[6].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[6].front.authors[0].fullname, "ITU-T")
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].initials)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].role)
#        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].surname)
#        # reference -- 06 - front.date
#        self.assertIsNone( back.refs[0].content[6].front.date)
#        # reference -- 06 - front.areas
#        self.assertIsInstance( back.refs[0].content[6].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[6].front.areas), 0)
#        # reference -- 06 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[6].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[6].front.workgroups), 0)
#        # reference -- 06 - front.keywords
#        self.assertIsInstance( back.refs[0].content[6].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[6].front.keywords), 0)
#        # reference -- 06 - front.abstract
#        self.assertIsNone( back.refs[0].content[6].front.abstract)
#        # reference -- 06 - front.notes
#        self.assertIsInstance( back.refs[0].content[6].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[6].front.notes), 0)
#        # reference -- 06 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[6].front.boilerplate)
#
#
#        # reference -- 06 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[6].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[6].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[6].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[6].content[0].asciiName,  "ITU-T Recommendation")
#        self.assertEqual      ( back.refs[0].content[6].content[0].asciiValue, "X.680, X.681, X.682, and X.683")
#        self.assertEqual      ( back.refs[0].content[6].content[0].name,       "ITU-T Recommendation")
#        self.assertIsNone     ( back.refs[0].content[6].content[0].status)
#        self.assertEqual      ( back.refs[0].content[6].content[0].value,      "X.680, X.681, X.682, and X.683")
#        self.assertIsNone     ( back.refs[0].content[6].content[0].stream)
#
#        # reference -- 06 - anchor
#        self.assertEqual(back.refs[0].content[6].anchor, "ASN1")
#        # reference -- 06 - quoteTitle
#        self.assertEqual(back.refs[0].content[6].quoteTitle, True)
#        # reference -- 06 - target
#        self.assertIsNone(back.refs[0].content[6].target)
#
#
#        # reference -- 07 
#        self.assertIsInstance( back.refs[0].content[7], rfc.Reference)
#        # reference -- 07 - front
#        self.assertIsInstance( back.refs[0].content[7].front, rfc.Front)
#        # reference -- 07 - front.title
#        self.assertIsInstance( back.refs[0].content[7].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[7].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[7].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[7].front.title.content.content , "Concise Binary Object Representation (CBOR)")
#        # reference -- 07 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[7].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[7].front.seriesInfo), 0)
#        # reference -- 07 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[7].front.authors), 2)
#        # reference -- 07 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[7].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[7].front.authors[0].fullname, "Carsten Bormann" )
#        self.assertEqual    ( back.refs[0].content[7].front.authors[0].initials, "C" )
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[7].front.authors[0].surname, "Bormann" )
#        # reference -- 07 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[7].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[7].front.authors[1].fullname, "Paul Hoffman" )
#        self.assertEqual    ( back.refs[0].content[7].front.authors[1].initials, "P" )
#        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[7].front.authors[1].surname,  "Hoffman" )
#        # reference -- 07 - front.date
#        self.assertIsInstance( back.refs[0].content[7].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[7].front.date.day)
#        self.assertEqual( back.refs[0].content[7].front.date.month, "October")
#        self.assertEqual( back.refs[0].content[7].front.date.year, "2013")
#        # reference -- 07 - front.areas
#        self.assertIsInstance( back.refs[0].content[7].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[7].front.areas), 0)
#        # reference -- 07 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[7].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[7].front.workgroups), 0)
#        # reference -- 07 - front.keywords
#        self.assertIsInstance( back.refs[0].content[7].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[7].front.keywords), 0)
#        # reference -- 07 - front.abstract
#        self.assertIsNone( back.refs[0].content[7].front.abstract)
#        # reference -- 07 - front.notes
#        self.assertIsInstance( back.refs[0].content[7].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[7].front.notes), 0)
#        # reference -- 07 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[7].front.boilerplate)
#
#
#        # reference -- 07 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[7].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[7].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[7].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[7].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[7].content[0].asciiValue, "7049")
#        self.assertEqual      ( back.refs[0].content[7].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[7].content[0].status)
#        self.assertEqual      ( back.refs[0].content[7].content[0].value,      "7049")
#        self.assertIsNone     ( back.refs[0].content[7].content[0].stream)
#
#        # reference -- 07 - anchor
#        self.assertEqual(back.refs[0].content[7].anchor, "RFC7049")
#        # reference -- 07 - quoteTitle
#        self.assertEqual(back.refs[0].content[7].quoteTitle, True)
#        # reference -- 07 - target
#        self.assertEqual(back.refs[0].content[7].target, "https://www.rfc-editor.org/info/rfc7049")
#
#
#
#
#        # reference -- 08 
#        self.assertIsInstance( back.refs[0].content[8], rfc.Reference)
#        # reference -- 08 - front
#        self.assertIsInstance( back.refs[0].content[8].front, rfc.Front)
#        # reference -- 08 - front.title
#        self.assertIsInstance( back.refs[0].content[8].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[8].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[8].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[8].front.title.content.content , "RTP: A Transport Protocol for Real-Time Applications")
#        # reference -- 08 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[8].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[8].front.seriesInfo), 0)
#        # reference -- 08 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[8].front.authors), 4)
#        # reference -- 08 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[8].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[0].fullname, "Henning Schulzrinne" )
#        self.assertEqual    ( back.refs[0].content[8].front.authors[0].initials, "H" )
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[0].surname, "Schulzrinne" )
#        # reference -- 08 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[8].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[1].fullname, "Stephen L. Casner" )
#        self.assertEqual    ( back.refs[0].content[8].front.authors[1].initials, "S" )
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[1].surname,  "Casner" )
#        # reference -- 08 - front.author - 2 
#        self.assertIsNotNone( back.refs[0].content[8].front.authors[2].org)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.content)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].address)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[2].fullname, "Ron Frederick" )
#        self.assertEqual    ( back.refs[0].content[8].front.authors[2].initials, "R" )
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].role)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[2].surname,  "Frederick" )
#        # reference -- 08 - front.author - 3 
#        self.assertIsNotNone( back.refs[0].content[8].front.authors[3].org)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.content)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].address)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[3].fullname, "Van Jacobson" )
#        self.assertEqual    ( back.refs[0].content[8].front.authors[3].initials, "V" )
#        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].role)
#        self.assertEqual    ( back.refs[0].content[8].front.authors[3].surname,  "Jacobson" )
#        # reference -- 08 - front.date
#        self.assertIsInstance( back.refs[0].content[8].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[8].front.date.day)
#        self.assertEqual( back.refs[0].content[8].front.date.month, "July")
#        self.assertEqual( back.refs[0].content[8].front.date.year, "2003")
#        # reference -- 08 - front.areas
#        self.assertIsInstance( back.refs[0].content[8].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[8].front.areas), 0)
#        # reference -- 08 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[8].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[8].front.workgroups), 0)
#        # reference -- 08 - front.keywords
#        self.assertIsInstance( back.refs[0].content[8].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[8].front.keywords), 0)
#        # reference -- 08 - front.abstract
#        self.assertIsNone( back.refs[0].content[8].front.abstract)
#        # reference -- 08 - front.notes
#        self.assertIsInstance( back.refs[0].content[8].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[8].front.notes), 0)
#        # reference -- 08 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[8].front.boilerplate)
#
#
#        # reference -- 08 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[8].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[8].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[8].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[8].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[8].content[0].asciiValue, "3550")
#        self.assertEqual      ( back.refs[0].content[8].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[8].content[0].status)
#        self.assertEqual      ( back.refs[0].content[8].content[0].value,      "3550")
#        self.assertIsNone     ( back.refs[0].content[8].content[0].stream)
#
#        # reference -- 08 - anchor
#        self.assertEqual(back.refs[0].content[8].anchor, "RFC3550")
#        # reference -- 08 - quoteTitle
#        self.assertEqual(back.refs[0].content[8].quoteTitle, True)
#        # reference -- 08 - target
#        self.assertEqual(back.refs[0].content[8].target, "https://www.rfc-editor.org/info/rfc3550")
#
#
#        # reference -- 09 
#        self.assertIsInstance( back.refs[0].content[9], rfc.Reference)
#        # reference -- 09 - front
#        self.assertIsInstance( back.refs[0].content[9].front, rfc.Front)
#        # reference -- 09 - front.title
#        self.assertIsInstance( back.refs[0].content[9].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[9].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[9].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[9].front.title.content.content , "Session Traversal Utilities for NAT (STUN)")
#        # reference -- 09 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[9].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[9].front.seriesInfo), 0)
#        # reference -- 09 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[9].front.authors), 6)
#        # reference -- 09 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[0].fullname, "Marc Petit-Huguenin")
#        self.assertEqual    ( back.refs[0].content[9].front.authors[0].initials, "M" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[0].surname, "Petit-Huguenin" )
#        # reference -- 09 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[1].fullname, "Gonzalo Salgueiro" )
#        self.assertEqual    ( back.refs[0].content[9].front.authors[1].initials, "G" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[1].surname,  "Salgueiro" )
#        # reference -- 09 - front.author - 2 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[2].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[2].fullname, "Jonathan Rosenberg" )
#        self.assertEqual    ( back.refs[0].content[9].front.authors[2].initials, "J" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[2].surname,  "Rosenberg" )
#        # reference -- 09 - front.author - 3 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[3].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[3].fullname, "Dan Wing" )
#        self.assertEqual    ( back.refs[0].content[9].front.authors[3].initials, "D" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[3].surname,  "Wing" )
#        # reference -- 09 - front.author - 4 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[4].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[4].fullname, "Rohan Mahy" )
#        self.assertEqual    ( back.refs[0].content[9].front.authors[4].initials, "R" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[4].surname,  "Mahy" )
#        # reference -- 09 - front.author - 5 
#        self.assertIsNotNone( back.refs[0].content[9].front.authors[5].org)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.content)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].address)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[5].fullname, "Philip Matthews" )
#        self.assertEqual    ( back.refs[0].content[9].front.authors[5].initials, "P" )
#        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].role)
#        self.assertEqual    ( back.refs[0].content[9].front.authors[5].surname,  "Matthews" )
#        # reference -- 09 - front.date
#        self.assertIsInstance( back.refs[0].content[9].front.date, rfc.Date)
#        self.assertEqual( back.refs[0].content[9].front.date.day, "21")
#        self.assertEqual( back.refs[0].content[9].front.date.month, "March")
#        self.assertEqual( back.refs[0].content[9].front.date.year, "2019")
#        # reference -- 09 - front.areas
#        self.assertIsInstance( back.refs[0].content[9].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[9].front.areas), 0)
#        # reference -- 09 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[9].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[9].front.workgroups), 0)
#        # reference -- 09 - front.keywords
#        self.assertIsInstance( back.refs[0].content[9].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[9].front.keywords), 0)
#        # reference -- 09 - front.abstract
#        self.assertIsNone( back.refs[0].content[9].front.abstract)
#        # reference -- 09 - front.notes
#        self.assertIsInstance( back.refs[0].content[9].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[9].front.notes), 0)
#        # reference -- 09 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[9].front.boilerplate)
#
#
#        # reference -- 09 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[9].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[9].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[9].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[9].content[0].asciiName,  "Internet-Draft")
#        self.assertEqual      ( back.refs[0].content[9].content[0].asciiValue, "draft-ietf-tram-stunbis-21")
#        self.assertEqual      ( back.refs[0].content[9].content[0].name,       "Internet-Draft")
#        self.assertIsNone     ( back.refs[0].content[9].content[0].status)
#        self.assertEqual      ( back.refs[0].content[9].content[0].value,      "draft-ietf-tram-stunbis-21")
#        self.assertIsNone     ( back.refs[0].content[9].content[0].stream)
#
#        # reference -- 09 - anchor
#        self.assertEqual(back.refs[0].content[9].anchor, "draft-ietf-tram-stunbis-21")
#        # reference -- 09 - quoteTitle
#        self.assertEqual(back.refs[0].content[9].quoteTitle, True)
#        # reference -- 09 - target
#        self.assertEqual(back.refs[0].content[9].target, "http://www.ietf.org/internet-drafts/draft-ietf-tram-stunbis-21.txt")
#
#
#
#
#
#        # reference -- 10 
#        self.assertIsInstance( back.refs[0].content[10], rfc.Reference)
#        # reference -- 10 - front
#        self.assertIsInstance( back.refs[0].content[10].front, rfc.Front)
#        # reference -- 10 - front.title
#        self.assertIsInstance( back.refs[0].content[10].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[10].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[10].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[10].front.title.content.content , "Internet Protocol")
#        # reference -- 10 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[10].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[10].front.seriesInfo), 0)
#        # reference -- 10 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[10].front.authors), 1)
#        # reference -- 10 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[10].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[10].front.authors[0].fullname, "Jon Postel" )
#        self.assertEqual    ( back.refs[0].content[10].front.authors[0].initials, "J" )
#        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[10].front.authors[0].surname, "Postel" )
#        # reference -- 10 - front.date
#        self.assertIsInstance( back.refs[0].content[10].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[10].front.date.day)
#        self.assertEqual( back.refs[0].content[10].front.date.month, "September")
#        self.assertEqual( back.refs[0].content[10].front.date.year, "1981")
#        # reference -- 10 - front.areas
#        self.assertIsInstance( back.refs[0].content[10].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[10].front.areas), 0)
#        # reference -- 10 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[10].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[10].front.workgroups), 0)
#        # reference -- 10 - front.keywords
#        self.assertIsInstance( back.refs[0].content[10].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[10].front.keywords), 0)
#        # reference -- 10 - front.abstract
#        self.assertIsNone( back.refs[0].content[10].front.abstract)
#        # reference -- 10 - front.notes
#        self.assertIsInstance( back.refs[0].content[10].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[10].front.notes), 0)
#        # reference -- 10 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[10].front.boilerplate)
#
#
#        # reference -- 10 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[10].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[10].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[10].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[10].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[10].content[0].asciiValue, "791")
#        self.assertEqual      ( back.refs[0].content[10].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[10].content[0].status)
#        self.assertEqual      ( back.refs[0].content[10].content[0].value,      "791")
#        self.assertIsNone     ( back.refs[0].content[10].content[0].stream)
#
#        # reference -- 10 - anchor
#        self.assertEqual(back.refs[0].content[10].anchor, "RFC791")
#        # reference -- 10 - quoteTitle
#        self.assertEqual(back.refs[0].content[10].quoteTitle, True)
#        # reference -- 10 - target
#        self.assertEqual(back.refs[0].content[10].target, "https://www.rfc-editor.org/info/rfc791")
#
#
#
#
#        # reference -- 11 
#        self.assertIsInstance( back.refs[0].content[11], rfc.Reference)
#        # reference -- 11 - front
#        self.assertIsInstance( back.refs[0].content[11].front, rfc.Front)
#        # reference -- 11 - front.title
#        self.assertIsInstance( back.refs[0].content[11].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[11].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[11].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[11].front.title.content.content , "Transmission Control Protocol")
#        # reference -- 11 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[11].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[11].front.seriesInfo), 0)
#        # reference -- 11 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[11].front.authors), 1)
#        # reference -- 11 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[11].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[11].front.authors[0].fullname, "Jon Postel" )
#        self.assertEqual    ( back.refs[0].content[11].front.authors[0].initials, "J" )
#        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[11].front.authors[0].surname, "Postel" )
#        # reference -- 11 - front.date
#        self.assertIsInstance( back.refs[0].content[11].front.date, rfc.Date)
#        self.assertIsNone( back.refs[0].content[11].front.date.day)
#        self.assertEqual( back.refs[0].content[11].front.date.month, "September")
#        self.assertEqual( back.refs[0].content[11].front.date.year, "1981")
#        # reference -- 11 - front.areas
#        self.assertIsInstance( back.refs[0].content[11].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[11].front.areas), 0)
#        # reference -- 11 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[11].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[11].front.workgroups), 0)
#        # reference -- 11 - front.keywords
#        self.assertIsInstance( back.refs[0].content[11].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[11].front.keywords), 0)
#        # reference -- 11 - front.abstract
#        self.assertIsNone( back.refs[0].content[11].front.abstract)
#        # reference -- 11 - front.notes
#        self.assertIsInstance( back.refs[0].content[11].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[11].front.notes), 0)
#        # reference -- 11 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[11].front.boilerplate)
#
#
#        # reference -- 11 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[11].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[11].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[11].content[0],            rfc.SeriesInfo)
#        self.assertEqual      ( back.refs[0].content[11].content[0].asciiName,  "RFC")
#        self.assertEqual      ( back.refs[0].content[11].content[0].asciiValue, "793")
#        self.assertEqual      ( back.refs[0].content[11].content[0].name,       "RFC")
#        self.assertIsNone     ( back.refs[0].content[11].content[0].status)
#        self.assertEqual      ( back.refs[0].content[11].content[0].value,      "793")
#        self.assertIsNone     ( back.refs[0].content[11].content[0].stream)
#
#        # reference -- 11 - anchor
#        self.assertEqual(back.refs[0].content[11].anchor, "RFC793")
#        # reference -- 11 - quoteTitle
#        self.assertEqual(back.refs[0].content[11].quoteTitle, True)
#        # reference -- 11 - target
#        self.assertEqual(back.refs[0].content[11].target, "https://www.rfc-editor.org/info/rfc793")
#
#
#
#
#
#
#
#        # reference -- 12 
#        self.assertIsInstance( back.refs[0].content[12], rfc.Reference)
#        # reference -- 12 - front
#        self.assertIsInstance( back.refs[0].content[12].front, rfc.Front)
#        # reference -- 12 - front.title
#        self.assertIsInstance( back.refs[0].content[12].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[12].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[12].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[12].front.title.content.content , "LANGSEC: Language-theoretic Security")
#        # reference -- 12 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[12].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[12].front.seriesInfo), 0)
#        # reference -- 12 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[12].front.authors), 1)
#        # reference -- 12 - front.author - 0 
#        self.assertIsNone( back.refs[0].content[12].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[12].front.authors[0].fullname, "LANGSEC" )
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].initials)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].role)
#        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].surname)
#        # reference -- 12 - front.date
#        self.assertIsNone( back.refs[0].content[12].front.date)
#        # reference -- 12 - front.areas
#        self.assertIsInstance( back.refs[0].content[12].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[12].front.areas), 0)
#        # reference -- 12 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[12].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[12].front.workgroups), 0)
#        # reference -- 12 - front.keywords
#        self.assertIsInstance( back.refs[0].content[12].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[12].front.keywords), 0)
#        # reference -- 12 - front.abstract
#        self.assertIsNone( back.refs[0].content[12].front.abstract)
#        # reference -- 12 - front.notes
#        self.assertIsInstance( back.refs[0].content[12].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[12].front.notes), 0)
#        # reference -- 12 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[12].front.boilerplate)
#
#
#        # reference -- 12 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[12].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[12].content), 0)
#
#        # reference -- 12 - anchor
#        self.assertEqual(back.refs[0].content[12].anchor, "LANGSEC")
#        # reference -- 12 - quoteTitle
#        self.assertEqual(back.refs[0].content[12].quoteTitle, True)
#        # reference -- 12 - target
#        self.assertEqual(back.refs[0].content[12].target, "http://langsec.org")
#
#
#        # reference -- 13 
#        self.assertIsInstance( back.refs[0].content[13], rfc.Reference)
#        # reference -- 13 - front
#        self.assertIsInstance( back.refs[0].content[13].front, rfc.Front)
#        # reference -- 13 - front.title
#        self.assertIsInstance( back.refs[0].content[13].front.title,  rfc.Title)
#        self.assertIsInstance( back.refs[0].content[13].front.title.content ,  rfc.Text)
#        self.assertIsInstance( back.refs[0].content[13].front.title.content.content ,  str)
#        self.assertEqual( back.refs[0].content[13].front.title.content.content , "The Halting Problems of Network Stack Insecurity")
#        # reference -- 13 - front.seriesInfo
#        self.assertIsInstance( back.refs[0].content[13].front.seriesInfo, list)
#        self.assertEqual( len(back.refs[0].content[13].front.seriesInfo), 0)
#        # reference -- 13 - front.authors 
#        self.assertEqual    ( len(back.refs[0].content[13].front.authors), 4)
#        # reference -- 13 - front.author - 0 
#        self.assertIsNotNone( back.refs[0].content[13].front.authors[0].org)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.content)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].address)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[0].fullname, "Len Sassaman" )
#        self.assertEqual    ( back.refs[0].content[13].front.authors[0].initials, "L" )
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].role)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[0].surname, "Sassaman" )
#        # reference -- 13 - front.author - 1 
#        self.assertIsNotNone( back.refs[0].content[13].front.authors[1].org)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.content)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].address)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[1].fullname, "Meredith L. Patterson" )
#        self.assertEqual    ( back.refs[0].content[13].front.authors[1].initials, "M. L" )
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].role)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[1].surname,  "Patterson" )
#        # reference -- 13 - front.author - 2 
#        self.assertIsNotNone( back.refs[0].content[13].front.authors[2].org)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.content)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].address)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[2].fullname, "Sergey Bratus" )
#        self.assertEqual    ( back.refs[0].content[13].front.authors[2].initials, "S" )
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].role)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[2].surname,  "Bratus" )
#        # reference -- 13 - front.author - 3 
#        self.assertIsNotNone( back.refs[0].content[13].front.authors[3].org)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.content)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.abbrev)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.ascii)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].address)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiFullname)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiInitials)
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiSurname)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[3].fullname, "Anna Shubina" )
#        self.assertEqual    ( back.refs[0].content[13].front.authors[3].initials, "A" )
#        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].role)
#        self.assertEqual    ( back.refs[0].content[13].front.authors[3].surname,  "Shubina" )
#        # reference -- 13 - front.date
#        self.assertIsNone( back.refs[0].content[13].front.date)
#        # reference -- 13 - front.areas
#        self.assertIsInstance( back.refs[0].content[13].front.areas, list)
#        self.assertEqual( len(back.refs[0].content[13].front.areas), 0)
#        # reference -- 13 - front.workgroups
#        self.assertIsInstance( back.refs[0].content[13].front.workgroups, list)
#        self.assertEqual( len(back.refs[0].content[13].front.workgroups), 0)
#        # reference -- 13 - front.keywords
#        self.assertIsInstance( back.refs[0].content[13].front.keywords, list)
#        self.assertEqual( len(back.refs[0].content[13].front.keywords), 0)
#        # reference -- 13 - front.abstract
#        self.assertIsNone( back.refs[0].content[13].front.abstract)
#        # reference -- 13 - front.notes
#        self.assertIsInstance( back.refs[0].content[13].front.notes, list)
#        self.assertEqual( len(back.refs[0].content[13].front.notes), 0)
#        # reference -- 13 - front.boilerplate
#        self.assertIsNone( back.refs[0].content[13].front.boilerplate)
#
#
#        # reference -- 13 - seriesInfo
#        self.assertIsInstance( back.refs[0].content[13].content,list)
#        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
#        self.assertEqual(len(back.refs[0].content[13].content), 1)
#
#        self.assertIsInstance ( back.refs[0].content[13].content[0],              rfc.RefContent)
#        self.assertIsInstance ( back.refs[0].content[13].content[0].content,      list)
#        self.assertEqual      ( len(back.refs[0].content[13].content[0].content), 1)
#        self.assertIsInstance ( back.refs[0].content[13].content[0].content[0], rfc.Text)
#        self.assertEqual      ( back.refs[0].content[13].content[0].content[0].content, ";login: -- December 2011, Volume 36, Number 6")
#
#        # reference -- 13 - anchor
#        self.assertEqual(back.refs[0].content[13].anchor, "SASSAMAN")
#        # reference -- 13 - quoteTitle
#        self.assertEqual(back.refs[0].content[13].quoteTitle, True)
#        # reference -- 13 - target
#        self.assertEqual(back.refs[0].content[13].target, "https://www.usenix.org/publications/login/december-2011-volume-36-number-6/halting-problems-network-stack-insecurity")
#
#
#        # sections 
#        self.assertIsInstance(back.sections, list)
#        self.assertEqual(len(back.sections), 2)
#
#        # section-00 
#        self.assertIsInstance(back.sections[0], rfc.Section)
#        # section-00 name
#        # FIXME : parse_section line 975 : name is not parsed
#        self.assertIsInstance(back.sections[0].name, rfc.Name)
#        self.assertIsInstance(back.sections[0].name.content, list)
#        self.assertEqual(len(back.sections[0].name.content), 1)
#        self.assertIsInstance(back.sections[0].name.content[0], rfc.Text)
#        self.assertEqual(back.sections[0].name.content[0].content, "ABNF specification")
#        # section-00 content
#        self.assertIsInstance(back.sections[0].content, list)
#        self.assertEqual(len(back.sections[0].content), 0)
#        # section-00 -- (sub) sections
#        self.assertIsInstance(back.sections[0].sections, list)
#        self.assertEqual(len(back.sections[0].sections), 2)
#        # section-00 -- (sub) section 00
#        self.assertIsInstance(back.sections[0].sections[0], rfc.Section)
#        # section-00 -- (sub) section 00 name 
#        # FIXME : parse_section line 975 : name is not parsed
#        self.assertIsInstance(back.sections[0].sections[0].name, rfc.Name)
#        self.assertIsInstance(back.sections[0].sections[0].name.content, list)
#        self.assertEqual(len(back.sections[0].sections[0].name.content), 1)
#        self.assertIsInstance(back.sections[0].sections[0].name.content[0], rfc.Text)
#        self.assertEqual(back.sections[0].sections[0].name.content[0].content, "Constraint Expressions")
#        # section-00 -- (sub) section 00 -- content  
#        self.assertIsInstance(back.sections[0].sections[0].content, list)
#        self.assertEqual(len(back.sections[0].sections[0].content), 1)
#        self.assertIsInstance(back.sections[0].sections[0].content[0], rfc.SourceCode)
#        self.assertIsInstance(back.sections[0].sections[0].content[0].content, rfc.Text)
#        self.assertEqual(back.sections[0].sections[0].content[0].content.content, """
#    cond-expr = eq-expr "?" cond-expr ":" eq-expr
#    eq-expr   = bool-expr eq-op   bool-expr
#    bool-expr = ord-expr  bool-op ord-expr
#    ord-expr  = add-expr  ord-op  add-expr
#
#    add-expr  = mul-expr  add-op  mul-expr
#    mul-expr  = expr      mul-op  expr
#    expr      = *DIGIT / field-name /
#                field-name-ws / "(" expr ")"
#
#    field-name    = *ALPHA
#    field-name-ws = *(field-name " ")
#
#    mul-op  = "*" / "/" / "%"
#    add-op  = "+" / "-"
#    ord-op  = "<=" / "<" / ">=" / ">"
#    bool-op = "&&" / "||" / "!"
#    eq-op   = "==" / "!="
#                """)
#        # section-00 -- (sub) section-00 -- sourcecode anchor, numbered, removeInRFC, title, toc
#        self.assertIsNone(back.sections[0].sections[0].content[0].anchor)
#        self.assertIsNone(back.sections[0].sections[0].content[0].name)
#        self.assertIsNone(back.sections[0].sections[0].content[0].src)
#        self.assertEqual(back.sections[0].sections[0].content[0].type, "abnf")
#
#
#        # section-00 -- (sub) section 00 -- sections  
#        self.assertIsInstance(back.sections[0].sections[0].sections, list)
#        self.assertEqual(len(back.sections[0].sections[0].sections), 0)
#        # section-00 -- (sub) section 00 -- anchor, numbered, removeInRFC, title, toc
#        self.assertEqual(back.sections[0].sections[0].anchor, "ABNF-constraints")
#        self.assertTrue(back.sections[0].sections[0].numbered)
#        self.assertFalse(back.sections[0].sections[0].removeInRFC)
#        self.assertIsNone(back.sections[0].sections[0].title)
#        self.assertEqual(back.sections[0].sections[0].toc, "default" )
#
#
#        # section-00 -- (sub) section 01
#        self.assertIsInstance(back.sections[0].sections[1], rfc.Section)
#        # section-00 -- (sub) section 01 name 
#        # FIXME : parse_section line 975 : name is not parsed
#        self.assertIsInstance(back.sections[0].sections[1].name, rfc.Name)
#        self.assertIsInstance(back.sections[0].sections[1].name.content, list)
#        self.assertEqual(len(back.sections[0].sections[1].name.content), 1)
#        self.assertIsInstance(back.sections[0].sections[1].name.content[0], rfc.Text)
#        self.assertEqual(back.sections[0].sections[1].name.content[0].content, "Augmented packet diagrams")
#        # section-00 -- (sub) section 01 -- content  
#        self.assertIsInstance(back.sections[0].sections[1].content, list)
#        self.assertEqual(len(back.sections[0].sections[1].content), 1)
#        self.assertIsInstance(back.sections[0].sections[1].content[0], rfc.T)
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content, list)
#
#        self.assertEqual(len(back.sections[0].sections[1].content[0].content), 6)
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[0], rfc.Text)
#        #FIXME -- lstrip and rstrip each text ? 
#        self.assertEqual(back.sections[0].sections[1].content[0].content[0].content, """
#                    Future revisions of this draft will include an ABNF specification for
#                    the augmented packet diagram format described in
#                    """)
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[1], rfc.XRef)
#        self.assertIsNone(back.sections[0].sections[1].content[0].content[1].content)
#        self.assertIsNone(back.sections[0].sections[1].content[0].content[1].format)
#        self.assertFalse(back.sections[0].sections[1].content[0].content[1].pageno)
#        self.assertEqual(back.sections[0].sections[1].content[0].content[1].target, "augmentedascii")
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[2], rfc.Text)
#        #FIXME -- lstrip and rstrip each text ? 
#        self.assertEqual(back.sections[0].sections[1].content[0].content[2].content, """. Such a specification is omitted from
#                    this draft given that the format is likely to change as its syntax is
#                    developed. Given the visual nature of the format, it is more
#                    appropriate for discussion to focus on the examples given in
#                    """)
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[3], rfc.XRef)
#        self.assertIsNone(back.sections[0].sections[1].content[0].content[3].content)
#        self.assertIsNone(back.sections[0].sections[1].content[0].content[3].format)
#        self.assertFalse(back.sections[0].sections[1].content[0].content[3].pageno)
#        self.assertEqual(back.sections[0].sections[1].content[0].content[3].target, "augmentedascii")
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[4], rfc.Text)
#        #FIXME -- lstrip and rstrip each text ? 
#        self.assertEqual(back.sections[0].sections[1].content[0].content[4].content, """.
#                """)
#        self.assertIsInstance(back.sections[0].sections[1].content[0].content[5], rfc.Text)
#        self.maxDiff = None
#        #FIXME -- This extra newline -- where does it come from ? -- looks like the tail of the paragraph
#        self.assertEqual(back.sections[0].sections[1].content[0].content[5].content, """
#            """)
#
#
#        # section-00 -- (sub) section 00 -- content -- anchor, hangText , keepWithNext, keepWithPrevious
#        self.assertIsNone(back.sections[0].sections[1].content[0].anchor)
#        self.assertIsNone(back.sections[0].sections[1].content[0].hangText)
#        self.assertFalse(back.sections[0].sections[1].content[0].keepWithNext)
#        self.assertFalse(back.sections[0].sections[1].content[0].keepWithPrevious)
#
#        # section-00 -- (sub) section 01 -- sections  
#        self.assertIsInstance(back.sections[0].sections[1].sections, list)
#        self.assertEqual(len(back.sections[0].sections[1].sections), 0)
#        # section-00 -- (sub) section 00 -- anchor, numbered, removeInRFC, title, toc
#        self.assertEqual(back.sections[0].sections[1].anchor, "ABNF-diagrams")
#        self.assertTrue(back.sections[0].sections[1].numbered)
#        self.assertFalse(back.sections[0].sections[1].removeInRFC)
#        self.assertIsNone(back.sections[0].sections[1].title)
#        self.assertEqual(back.sections[0].sections[1].toc, "default" )
#
#        # section-00 anchor, numbered, removeInRFC, title, toc
#        self.assertEqual(back.sections[0].anchor, "ABNF")
#        self.assertTrue(back.sections[0].numbered)
#        self.assertFalse(back.sections[0].removeInRFC)
#        self.assertIsNone(back.sections[0].title)
#        self.assertEqual(back.sections[0].toc, "default" )
#
#
#        # section-01 
#        self.assertIsInstance(back.sections[1], rfc.Section)
#        # section-01 name
#        # FIXME : parse_section line 975 : name is not parsed
#        self.assertIsInstance(back.sections[1].name, rfc.Name)
#        self.assertIsInstance(back.sections[1].name.content, list)
#        self.assertEqual(len(back.sections[1].name.content), 1)
#        self.assertIsInstance(back.sections[1].name.content[0], rfc.Text)
#        self.assertEqual(back.sections[1].name.content[0].content, "Source code repository")
#        # section-01 content
#        self.assertIsInstance(back.sections[1].content, list)
#        self.assertEqual(len(back.sections[1].content), 2)
#        # section-01 content[0] 
#        self.assertIsInstance(back.sections[1].content[0], rfc.T)
#        self.assertIsInstance(back.sections[1].content[0].content, list)
#        self.assertEqual(len(back.sections[1].content[0].content), 4)
#        # section-01 content[0] content[0]
#        self.assertIsInstance(back.sections[1].content[0].content[0], rfc.Text)
#        self.assertEqual(back.sections[1].content[0].content[0].content, """
#                The source for this draft is available from
#                """)
#        # section-01 content[0] content[1]
#        self.assertIsInstance(back.sections[1].content[0].content[1], rfc.ERef)
#        self.assertIsNone(back.sections[1].content[0].content[1].content)
#        self.assertEqual(back.sections[1].content[0].content[1].target, "https://github.com/glasgow-ipl/draft-mcquistin-augmented-ascii-diagrams")
#        # section-01 content[0] content[2]
#        self.assertIsInstance(back.sections[1].content[0].content[2], rfc.Text)
#        self.assertEqual(back.sections[1].content[0].content[2].content, """.
#            """)
#        # section-01 content[0] content[3]
#        self.assertIsInstance(back.sections[1].content[0].content[3], rfc.Text)
#        self.assertEqual(back.sections[1].content[0].content[3].content, """
#            """)
#
#        # section-01 content[0] anchor, hangText, keepWithNext, keepWithPrevious
#        self.assertIsNone(back.sections[1].content[0].anchor)
#        self.assertIsNone(back.sections[1].content[0].hangText)
#        self.assertFalse(back.sections[1].content[0].keepWithNext)
#        self.assertFalse(back.sections[1].content[0].keepWithPrevious)
#
#
#        # section-01 content[1] 
#        self.assertIsInstance(back.sections[1].content[1], rfc.T)
#        self.assertIsInstance(back.sections[1].content[1].content, list)
#        self.assertEqual(len(back.sections[1].content[1].content), 4)
#        # section-01 content[1] content[0]
#        self.assertIsInstance(back.sections[1].content[1].content[0], rfc.Text)
#        self.assertEqual(back.sections[1].content[1].content[0].content, """
#                The source code for tooling that can be used to parse this document is available
#                from """)
#        # section-01 content[0] content[1]
#        self.assertIsInstance(back.sections[1].content[1].content[1], rfc.ERef)
#        self.assertIsNone(back.sections[1].content[1].content[1].content)
#        self.assertEqual(back.sections[1].content[1].content[1].target, "https://github.com/glasgow-ipl/ips-protodesc-code")
#        # section-01 content[0] content[2]
#        self.assertIsInstance(back.sections[1].content[1].content[2], rfc.Text)
#        self.assertEqual(back.sections[1].content[1].content[2].content, """.
#            """)
#        # section-01 content[0] content[3]
#        self.assertIsInstance(back.sections[1].content[1].content[3], rfc.Text)
#        self.assertEqual(back.sections[1].content[1].content[3].content, """
#        """)
#          
#
#        # section-01 content[0] anchor, hangText, keepWithNext, keepWithPrevious
#        self.assertIsNone(back.sections[1].content[0].anchor)
#        self.assertIsNone(back.sections[1].content[0].hangText)
#        self.assertFalse(back.sections[1].content[0].keepWithNext)
#        self.assertFalse(back.sections[1].content[0].keepWithPrevious)
#
#        # section-01 -- (sub) sections
#        self.assertIsInstance(back.sections[1].sections, list)
#        self.assertEqual(len(back.sections[1].sections), 0)
#
#        # section-01 anchor, numbered, removeInRFC, title, toc
#        self.assertEqual(back.sections[1].anchor, "source")
#        self.assertTrue(back.sections[1].numbered)
#        self.assertFalse(back.sections[1].removeInRFC)
#        self.assertIsNone(back.sections[1].title)
#        self.assertEqual(back.sections[1].toc, "default" )
