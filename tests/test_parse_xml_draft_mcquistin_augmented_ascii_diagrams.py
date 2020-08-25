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
        self.assertIsInstance( back.refs[0].content[1].content,list)
        self.assertEqual(len(back.refs[0].content[1].content), 1)

        self.assertIsInstance ( back.refs[0].content[1].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[1].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[1].content[0].asciiName,  "Internet-Draft")
        self.assertEqual      ( back.refs[0].content[1].content[0].asciiValue, "draft-ietf-quic-transport-27")
        self.assertEqual      ( back.refs[0].content[1].content[0].name,       "Internet-Draft")
        self.assertIsNone     ( back.refs[0].content[1].content[0].status)
        self.assertEqual      ( back.refs[0].content[1].content[0].value,      "draft-ietf-quic-transport-27")
        self.assertIsNone     ( back.refs[0].content[1].content[0].stream)

        # reference -- 01 - anchor
        self.assertEqual(back.refs[0].content[1].anchor, "QUIC-TRANSPORT")
        # reference -- 01 - quoteTitle
        self.assertEqual(back.refs[0].content[1].quoteTitle, True)
        # reference -- 01 - target
        self.assertEqual(back.refs[0].content[1].target, "http://www.ietf.org/internet-drafts/draft-ietf-quic-transport-27.txt")



        # reference -- 02
        self.assertIsInstance( back.refs[0].content[2], rfc.Reference)
        if not isinstance( back.refs[0].content[2], rfc.Reference): # type-check
            return
        # reference -- 02 - front
        self.assertIsInstance( back.refs[0].content[2].front, rfc.Front)
        # reference -- 02 - front.title
        self.assertIsInstance( back.refs[0].content[2].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[2].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[2].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[2].front.title.content.content , "RTP Control Protocol (RTCP) Extended Report (XR) Block for Burst/Gap Loss Metric Reporting")
        # reference -- 02 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[2].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[2].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[2].front.seriesInfo), 0)
        # reference -- 02 - front.authors
        self.assertEqual    ( len(back.refs[0].content[2].front.authors), 4)
        # reference -- 02 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[2].front.authors[0].org)
        if back.refs[0].content[2].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[2].front.authors[0].fullname, "Alan Clark" )
        self.assertEqual    ( back.refs[0].content[2].front.authors[0].initials, "A" )
        self.assertIsNone   ( back.refs[0].content[2].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[2].front.authors[0].surname, "Clark" )
        # reference -- 02 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[2].front.authors[1].org)
        if back.refs[0].content[2].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[2].front.authors[1].fullname, "Sunshine Zhang" )
        self.assertEqual    ( back.refs[0].content[2].front.authors[1].initials, "S" )
        self.assertIsNone   ( back.refs[0].content[2].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[2].front.authors[1].surname,  "Zhang" )
        # reference -- 02 - front.author - 2
        self.assertIsNotNone( back.refs[0].content[2].front.authors[2].org)
        if back.refs[0].content[2].front.authors[2].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.content)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].org.ascii)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].address)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].asciiSurname)
        self.assertEqual    ( back.refs[0].content[2].front.authors[2].fullname, "Jing Zhao" )
        self.assertEqual    ( back.refs[0].content[2].front.authors[2].initials, "J" )
        self.assertIsNone   ( back.refs[0].content[2].front.authors[2].role)
        self.assertEqual    ( back.refs[0].content[2].front.authors[2].surname,  "Zhao" )
        # reference -- 02 - front.author - 3
        self.assertIsNotNone( back.refs[0].content[2].front.authors[3].org)
        if back.refs[0].content[2].front.authors[3].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.content)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].org.ascii)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].address)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].asciiSurname)
        self.assertEqual    ( back.refs[0].content[2].front.authors[3].fullname, "Qin Wu" )
        self.assertEqual    ( back.refs[0].content[2].front.authors[3].initials, "Q" )
        self.assertIsNone   ( back.refs[0].content[2].front.authors[3].role)
        self.assertEqual    ( back.refs[0].content[2].front.authors[3].surname,  "Wu" )
        # reference -- 02 - front.date
        self.assertIsInstance( back.refs[0].content[2].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[2].front.date, rfc.Date) : # type-check
            return
        self.assertIsNone( back.refs[0].content[2].front.date.day)
        self.assertEqual( back.refs[0].content[2].front.date.month, "May")
        self.assertEqual( back.refs[0].content[2].front.date.year, "2013")
        # reference -- 02 - front.areas
        self.assertIsInstance( back.refs[0].content[2].front.areas, list)
        if not isinstance( back.refs[0].content[2].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[2].front.areas), 0)
        # reference -- 02 - front.workgroups
        self.assertIsInstance( back.refs[0].content[2].front.workgroups, list)
        if not isinstance( back.refs[0].content[2].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[2].front.workgroups), 0)
        # reference -- 02 - front.keywords
        self.assertIsInstance( back.refs[0].content[2].front.keywords, list)
        if not isinstance( back.refs[0].content[2].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[2].front.keywords), 0)
        # reference -- 02 - front.abstract
        self.assertIsNone( back.refs[0].content[2].front.abstract)
        # reference -- 02 - front.notes
        self.assertIsInstance( back.refs[0].content[2].front.notes, list)
        if not isinstance( back.refs[0].content[2].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[2].front.notes), 0)
        # reference -- 02 - front.boilerplate
        self.assertIsNone( back.refs[0].content[2].front.boilerplate)


        # reference -- 02 - seriesInfo
        self.assertIsInstance( back.refs[0].content[2].content,list)
        self.assertEqual(len(back.refs[0].content[2].content), 1)

        self.assertIsInstance ( back.refs[0].content[2].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[2].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[2].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[2].content[0].asciiValue, "6958")
        self.assertEqual      ( back.refs[0].content[2].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[2].content[0].status)
        self.assertEqual      ( back.refs[0].content[2].content[0].value,      "6958")
        self.assertIsNone     ( back.refs[0].content[2].content[0].stream)

        # reference -- 02 - anchor
        self.assertEqual(back.refs[0].content[2].anchor, "RFC6958")
        # reference -- 02 - quoteTitle
        self.assertEqual(back.refs[0].content[2].quoteTitle, True)
        # reference -- 02 - target
        self.assertEqual(back.refs[0].content[2].target, "https://www.rfc-editor.org/info/rfc6958")




        # reference -- 03
        self.assertIsInstance( back.refs[0].content[3], rfc.Reference)
        if not isinstance( back.refs[0].content[3], rfc.Reference): # type-check
            return
        # reference -- 03 - front
        self.assertIsInstance( back.refs[0].content[3].front, rfc.Front)
        # reference -- 03 - front.title
        self.assertIsInstance( back.refs[0].content[3].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[3].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[3].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[3].front.title.content.content , "The YANG 1.1 Data Modeling Language")
        # reference -- 03 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[3].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[3].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[3].front.seriesInfo), 0)
        # reference -- 03 - front.authors
        self.assertEqual    ( len(back.refs[0].content[3].front.authors), 1)
        # reference -- 03 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[3].front.authors[0].org)
        if back.refs[0].content[3].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[3].front.authors[0].fullname, "Martin Bjorklund" )
        self.assertEqual    ( back.refs[0].content[3].front.authors[0].initials, "M" )
        self.assertIsNone   ( back.refs[0].content[3].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[3].front.authors[0].surname, "Bjorklund" )
        # reference -- 03 - front.date
        self.assertIsInstance( back.refs[0].content[3].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[3].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[3].front.date.day)
        self.assertEqual( back.refs[0].content[3].front.date.month, "August")
        self.assertEqual( back.refs[0].content[3].front.date.year, "2016")
        # reference -- 03 - front.areas
        self.assertIsInstance( back.refs[0].content[3].front.areas, list)
        if not isinstance( back.refs[0].content[3].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[3].front.areas), 0)
        # reference -- 03 - front.workgroups
        self.assertIsInstance( back.refs[0].content[3].front.workgroups, list)
        if not isinstance( back.refs[0].content[3].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[3].front.workgroups), 0)
        # reference -- 03 - front.keywords
        self.assertIsInstance( back.refs[0].content[3].front.keywords, list)
        if not isinstance( back.refs[0].content[3].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[3].front.keywords), 0)
        # reference -- 03 - front.abstract
        self.assertIsNone( back.refs[0].content[3].front.abstract)
        # reference -- 03 - front.notes
        self.assertIsInstance( back.refs[0].content[3].front.notes, list)
        if not isinstance( back.refs[0].content[3].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[3].front.notes), 0)
        # reference -- 03 - front.boilerplate
        self.assertIsNone( back.refs[0].content[3].front.boilerplate)


        # reference -- 03 - seriesInfo
        self.assertIsInstance( back.refs[0].content[3].content,list)
        self.assertEqual(len(back.refs[0].content[3].content), 1)

        self.assertIsInstance ( back.refs[0].content[3].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[3].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[3].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[3].content[0].asciiValue, "7950")
        self.assertEqual      ( back.refs[0].content[3].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[3].content[0].status)
        self.assertEqual      ( back.refs[0].content[3].content[0].value,      "7950")
        self.assertIsNone     ( back.refs[0].content[3].content[0].stream)

        # reference -- 03 - anchor
        self.assertEqual(back.refs[0].content[3].anchor, "RFC7950")
        # reference -- 03 - quoteTitle
        self.assertEqual(back.refs[0].content[3].quoteTitle, True)
        # reference -- 03 - target
        self.assertEqual(back.refs[0].content[3].target, "https://www.rfc-editor.org/info/rfc7950")



        # reference -- 04
        self.assertIsInstance( back.refs[0].content[4], rfc.Reference)
        if not isinstance( back.refs[0].content[4], rfc.Reference): # type-check
            return
        # reference -- 04 - front
        self.assertIsInstance( back.refs[0].content[4].front, rfc.Front)
        # reference -- 04 - front.title
        self.assertIsInstance( back.refs[0].content[4].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[4].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[4].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[4].front.title.content.content , "The Transport Layer Security (TLS) Protocol Version 1.3")
        # reference -- 04 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[4].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[4].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[4].front.seriesInfo), 0)
        # reference -- 04 - front.authors
        self.assertEqual    ( len(back.refs[0].content[4].front.authors), 1)
        # reference -- 04 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[4].front.authors[0].org)
        if back.refs[0].content[4].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[4].front.authors[0].fullname, "Eric Rescorla" )
        self.assertEqual    ( back.refs[0].content[4].front.authors[0].initials, "E" )
        self.assertIsNone   ( back.refs[0].content[4].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[4].front.authors[0].surname, "Rescorla" )
        # reference -- 04 - front.date
        self.assertIsInstance( back.refs[0].content[4].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[4].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[4].front.date.day)
        self.assertEqual( back.refs[0].content[4].front.date.month, "August")
        self.assertEqual( back.refs[0].content[4].front.date.year, "2018")
        # reference -- 04 - front.areas
        self.assertIsInstance( back.refs[0].content[4].front.areas, list)
        if not isinstance( back.refs[0].content[4].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[4].front.areas), 0)
        # reference -- 04 - front.workgroups
        self.assertIsInstance( back.refs[0].content[4].front.workgroups, list)
        if not isinstance( back.refs[0].content[4].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[4].front.workgroups), 0)
        # reference -- 04 - front.keywords
        self.assertIsInstance( back.refs[0].content[4].front.keywords, list)
        if not isinstance( back.refs[0].content[4].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[4].front.keywords), 0)
        # reference -- 04 - front.abstract
        self.assertIsNone( back.refs[0].content[4].front.abstract)
        # reference -- 04 - front.notes
        self.assertIsInstance( back.refs[0].content[4].front.notes, list)
        if not isinstance( back.refs[0].content[4].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[4].front.notes), 0)
        # reference -- 04 - front.boilerplate
        self.assertIsNone( back.refs[0].content[4].front.boilerplate)


        # reference -- 04 - seriesInfo
        self.assertIsInstance( back.refs[0].content[4].content,list)
        self.assertEqual(len(back.refs[0].content[4].content), 1)

        self.assertIsInstance ( back.refs[0].content[4].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[4].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[4].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[4].content[0].asciiValue, "8446")
        self.assertEqual      ( back.refs[0].content[4].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[4].content[0].status)
        self.assertEqual      ( back.refs[0].content[4].content[0].value,      "8446")
        self.assertIsNone     ( back.refs[0].content[4].content[0].stream)

        # reference -- 04 - anchor
        self.assertEqual(back.refs[0].content[4].anchor, "RFC8446")
        # reference -- 04 - quoteTitle
        self.assertEqual(back.refs[0].content[4].quoteTitle, True)
        # reference -- 04 - target
        self.assertEqual(back.refs[0].content[4].target, "https://www.rfc-editor.org/info/rfc8446")



        # reference -- 05
        self.assertIsInstance( back.refs[0].content[5], rfc.Reference)
        if not isinstance( back.refs[0].content[5], rfc.Reference): # type-check
            return
        # reference -- 05 - front
        self.assertIsInstance( back.refs[0].content[5].front, rfc.Front)
        # reference -- 05 - front.title
        self.assertIsInstance( back.refs[0].content[5].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[5].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[5].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[5].front.title.content.content , "Augmented BNF for Syntax Specifications: ABNF")
        # reference -- 05 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[5].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[5].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[5].front.seriesInfo), 0)
        # reference -- 05 - front.authors
        self.assertEqual    ( len(back.refs[0].content[5].front.authors), 2)
        # reference -- 05 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[5].front.authors[0].org)
        if back.refs[0].content[5].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[5].front.authors[0].fullname, "Dave Crocker" )
        self.assertEqual    ( back.refs[0].content[5].front.authors[0].initials, "D" )
        self.assertIsNone   ( back.refs[0].content[5].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[5].front.authors[0].surname, "Crocker" )
        # reference -- 05 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[5].front.authors[1].org)
        if back.refs[0].content[5].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[5].front.authors[1].fullname, "Paul Overell" )
        self.assertEqual    ( back.refs[0].content[5].front.authors[1].initials, "P" )
        self.assertIsNone   ( back.refs[0].content[5].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[5].front.authors[1].surname,  "Overell" )
        # reference -- 05 - front.date
        self.assertIsInstance( back.refs[0].content[5].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[5].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[5].front.date.day)
        self.assertEqual( back.refs[0].content[5].front.date.month, "January")
        self.assertEqual( back.refs[0].content[5].front.date.year, "2008")
        # reference -- 05 - front.areas
        self.assertIsInstance( back.refs[0].content[5].front.areas, list)
        if not isinstance( back.refs[0].content[5].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[5].front.areas), 0)
        # reference -- 05 - front.workgroups
        self.assertIsInstance( back.refs[0].content[5].front.workgroups, list)
        if not isinstance( back.refs[0].content[5].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[5].front.workgroups), 0)
        # reference -- 05 - front.keywords
        self.assertIsInstance( back.refs[0].content[5].front.keywords, list)
        if not isinstance( back.refs[0].content[5].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[5].front.keywords), 0)
        # reference -- 05 - front.abstract
        self.assertIsNone( back.refs[0].content[5].front.abstract)
        # reference -- 05 - front.notes
        self.assertIsInstance( back.refs[0].content[5].front.notes, list)
        if not isinstance( back.refs[0].content[5].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[5].front.notes), 0)
        # reference -- 05 - front.boilerplate
        self.assertIsNone( back.refs[0].content[5].front.boilerplate)


        # reference -- 05 - seriesInfo
        self.assertIsInstance( back.refs[0].content[5].content,list)
        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
        self.assertEqual(len(back.refs[0].content[5].content), 1)

        self.assertIsInstance ( back.refs[0].content[5].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[5].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[5].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[5].content[0].asciiValue, "5234")
        self.assertEqual      ( back.refs[0].content[5].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[5].content[0].status)
        self.assertEqual      ( back.refs[0].content[5].content[0].value,      "5234")
        self.assertIsNone     ( back.refs[0].content[5].content[0].stream)

        # reference -- 05 - anchor
        self.assertEqual(back.refs[0].content[5].anchor, "RFC5234")
        # reference -- 05 - quoteTitle
        self.assertEqual(back.refs[0].content[5].quoteTitle, True)
        # reference -- 05 - target
        self.assertEqual(back.refs[0].content[5].target, "https://www.rfc-editor.org/info/rfc5234")


        # reference -- 06
        self.assertIsInstance( back.refs[0].content[6], rfc.Reference)
        if not isinstance( back.refs[0].content[6], rfc.Reference): # type-check
            return
        # reference -- 06 - front
        self.assertIsInstance( back.refs[0].content[6].front, rfc.Front)
        # reference -- 06 - front.title
        self.assertIsInstance( back.refs[0].content[6].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[6].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[6].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[6].front.title.content.content , "ITU-T Recommendation X.680, X.681, X.682, and X.683")
        # reference -- 06 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[6].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[6].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[6].front.seriesInfo), 0)
        # reference -- 06 - front.authors
        self.assertEqual    ( len(back.refs[0].content[6].front.authors), 1)
        # reference -- 06 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[6].front.authors[0].org)
        if back.refs[0].content[6].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[6].front.authors[0].fullname, "ITU-T")
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].initials)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].role)
        self.assertIsNone   ( back.refs[0].content[6].front.authors[0].surname)
        # reference -- 06 - front.date
        self.assertIsNone( back.refs[0].content[6].front.date)
        # reference -- 06 - front.areas
        self.assertIsInstance( back.refs[0].content[6].front.areas, list)
        if not isinstance( back.refs[0].content[6].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[6].front.areas), 0)
        # reference -- 06 - front.workgroups
        self.assertIsInstance( back.refs[0].content[6].front.workgroups, list)
        if not isinstance( back.refs[0].content[6].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[6].front.workgroups), 0)
        # reference -- 06 - front.keywords
        self.assertIsInstance( back.refs[0].content[6].front.keywords, list)
        if not isinstance( back.refs[0].content[6].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[6].front.keywords), 0)
        # reference -- 06 - front.abstract
        self.assertIsNone( back.refs[0].content[6].front.abstract)
        # reference -- 06 - front.notes
        self.assertIsInstance( back.refs[0].content[6].front.notes, list)
        if not isinstance( back.refs[0].content[6].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[6].front.notes), 0)
        # reference -- 06 - front.boilerplate
        self.assertIsNone( back.refs[0].content[6].front.boilerplate)


        # reference -- 06 - seriesInfo
        self.assertIsInstance( back.refs[0].content[6].content,list)
        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
        self.assertEqual(len(back.refs[0].content[6].content), 1)

        self.assertIsInstance ( back.refs[0].content[6].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[6].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[6].content[0].asciiName,  "ITU-T Recommendation")
        self.assertEqual      ( back.refs[0].content[6].content[0].asciiValue, "X.680, X.681, X.682, and X.683")
        self.assertEqual      ( back.refs[0].content[6].content[0].name,       "ITU-T Recommendation")
        self.assertIsNone     ( back.refs[0].content[6].content[0].status)
        self.assertEqual      ( back.refs[0].content[6].content[0].value,      "X.680, X.681, X.682, and X.683")
        self.assertIsNone     ( back.refs[0].content[6].content[0].stream)

        # reference -- 06 - anchor
        self.assertEqual(back.refs[0].content[6].anchor, "ASN1")
        # reference -- 06 - quoteTitle
        self.assertEqual(back.refs[0].content[6].quoteTitle, True)
        # reference -- 06 - target
        self.assertIsNone(back.refs[0].content[6].target)


        # reference -- 07
        self.assertIsInstance( back.refs[0].content[7], rfc.Reference)
        if not isinstance( back.refs[0].content[7], rfc.Reference): # type-check
            return
        # reference -- 07 - front
        self.assertIsInstance( back.refs[0].content[7].front, rfc.Front)
        # reference -- 07 - front.title
        self.assertIsInstance( back.refs[0].content[7].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[7].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[7].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[7].front.title.content.content , "Concise Binary Object Representation (CBOR)")
        # reference -- 07 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[7].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[7].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[7].front.seriesInfo), 0)
        # reference -- 07 - front.authors
        self.assertEqual    ( len(back.refs[0].content[7].front.authors), 2)
        # reference -- 07 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[7].front.authors[0].org)
        if back.refs[0].content[7].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[7].front.authors[0].fullname, "Carsten Bormann" )
        self.assertEqual    ( back.refs[0].content[7].front.authors[0].initials, "C" )
        self.assertIsNone   ( back.refs[0].content[7].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[7].front.authors[0].surname, "Bormann" )
        # reference -- 07 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[7].front.authors[1].org)
        if back.refs[0].content[7].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[7].front.authors[1].fullname, "Paul Hoffman" )
        self.assertEqual    ( back.refs[0].content[7].front.authors[1].initials, "P" )
        self.assertIsNone   ( back.refs[0].content[7].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[7].front.authors[1].surname,  "Hoffman" )
        # reference -- 07 - front.date
        self.assertIsInstance( back.refs[0].content[7].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[7].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[7].front.date.day)
        self.assertEqual( back.refs[0].content[7].front.date.month, "October")
        self.assertEqual( back.refs[0].content[7].front.date.year, "2013")
        # reference -- 07 - front.areas
        self.assertIsInstance( back.refs[0].content[7].front.areas, list)
        if not isinstance( back.refs[0].content[7].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[7].front.areas), 0)
        # reference -- 07 - front.workgroups
        self.assertIsInstance( back.refs[0].content[7].front.workgroups, list)
        if not isinstance( back.refs[0].content[7].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[7].front.workgroups), 0)
        # reference -- 07 - front.keywords
        self.assertIsInstance( back.refs[0].content[7].front.keywords, list)
        if not isinstance( back.refs[0].content[7].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[7].front.keywords), 0)
        # reference -- 07 - front.abstract
        self.assertIsNone( back.refs[0].content[7].front.abstract)
        # reference -- 07 - front.notes
        self.assertIsInstance( back.refs[0].content[7].front.notes, list)
        if not isinstance( back.refs[0].content[7].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[7].front.notes), 0)
        # reference -- 07 - front.boilerplate
        self.assertIsNone( back.refs[0].content[7].front.boilerplate)


        # reference -- 07 - seriesInfo
        self.assertIsInstance( back.refs[0].content[7].content,list)
        self.assertEqual(len(back.refs[0].content[7].content), 1)

        self.assertIsInstance ( back.refs[0].content[7].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[7].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[7].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[7].content[0].asciiValue, "7049")
        self.assertEqual      ( back.refs[0].content[7].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[7].content[0].status)
        self.assertEqual      ( back.refs[0].content[7].content[0].value,      "7049")
        self.assertIsNone     ( back.refs[0].content[7].content[0].stream)

        # reference -- 07 - anchor
        self.assertEqual(back.refs[0].content[7].anchor, "RFC7049")
        # reference -- 07 - quoteTitle
        self.assertEqual(back.refs[0].content[7].quoteTitle, True)
        # reference -- 07 - target
        self.assertEqual(back.refs[0].content[7].target, "https://www.rfc-editor.org/info/rfc7049")




        # reference -- 08
        self.assertIsInstance( back.refs[0].content[8], rfc.Reference)
        if not isinstance( back.refs[0].content[8], rfc.Reference): # type-check
            return
        # reference -- 08 - front
        self.assertIsInstance( back.refs[0].content[8].front, rfc.Front)
        # reference -- 08 - front.title
        self.assertIsInstance( back.refs[0].content[8].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[8].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[8].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[8].front.title.content.content , "RTP: A Transport Protocol for Real-Time Applications")
        # reference -- 08 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[8].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[8].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[8].front.seriesInfo), 0)
        # reference -- 08 - front.authors
        self.assertEqual    ( len(back.refs[0].content[8].front.authors), 4)
        # reference -- 08 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[8].front.authors[0].org)
        if back.refs[0].content[8].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[8].front.authors[0].fullname, "Henning Schulzrinne" )
        self.assertEqual    ( back.refs[0].content[8].front.authors[0].initials, "H" )
        self.assertIsNone   ( back.refs[0].content[8].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[8].front.authors[0].surname, "Schulzrinne" )
        # reference -- 08 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[8].front.authors[1].org)
        if back.refs[0].content[8].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[8].front.authors[1].fullname, "Stephen L. Casner" )
        self.assertEqual    ( back.refs[0].content[8].front.authors[1].initials, "S" )
        self.assertIsNone   ( back.refs[0].content[8].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[8].front.authors[1].surname,  "Casner" )
        # reference -- 08 - front.author - 2
        self.assertIsNotNone( back.refs[0].content[8].front.authors[2].org)
        if back.refs[0].content[8].front.authors[2].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.content)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].org.ascii)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].address)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].asciiSurname)
        self.assertEqual    ( back.refs[0].content[8].front.authors[2].fullname, "Ron Frederick" )
        self.assertEqual    ( back.refs[0].content[8].front.authors[2].initials, "R" )
        self.assertIsNone   ( back.refs[0].content[8].front.authors[2].role)
        self.assertEqual    ( back.refs[0].content[8].front.authors[2].surname,  "Frederick" )
        # reference -- 08 - front.author - 3
        self.assertIsNotNone( back.refs[0].content[8].front.authors[3].org)
        if back.refs[0].content[8].front.authors[3].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.content)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].org.ascii)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].address)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].asciiSurname)
        self.assertEqual    ( back.refs[0].content[8].front.authors[3].fullname, "Van Jacobson" )
        self.assertEqual    ( back.refs[0].content[8].front.authors[3].initials, "V" )
        self.assertIsNone   ( back.refs[0].content[8].front.authors[3].role)
        self.assertEqual    ( back.refs[0].content[8].front.authors[3].surname,  "Jacobson" )
        # reference -- 08 - front.date
        self.assertIsInstance( back.refs[0].content[8].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[8].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[8].front.date.day)
        self.assertEqual( back.refs[0].content[8].front.date.month, "July")
        self.assertEqual( back.refs[0].content[8].front.date.year, "2003")
        # reference -- 08 - front.areas
        self.assertIsInstance( back.refs[0].content[8].front.areas, list)
        if not isinstance( back.refs[0].content[8].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[8].front.areas), 0)
        # reference -- 08 - front.workgroups
        self.assertIsInstance( back.refs[0].content[8].front.workgroups, list)
        if not isinstance( back.refs[0].content[8].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[8].front.workgroups), 0)
        # reference -- 08 - front.keywords
        self.assertIsInstance( back.refs[0].content[8].front.keywords, list)
        if not isinstance( back.refs[0].content[8].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[8].front.keywords), 0)
        # reference -- 08 - front.abstract
        self.assertIsNone( back.refs[0].content[8].front.abstract)
        # reference -- 08 - front.notes
        self.assertIsInstance( back.refs[0].content[8].front.notes, list)
        if not isinstance( back.refs[0].content[8].front.notes, list): #type-check
            return
        self.assertEqual( len(back.refs[0].content[8].front.notes), 0)
        # reference -- 08 - front.boilerplate
        self.assertIsNone( back.refs[0].content[8].front.boilerplate)


        # reference -- 08 - seriesInfo
        self.assertIsInstance( back.refs[0].content[8].content,list)
        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
        self.assertEqual(len(back.refs[0].content[8].content), 1)

        self.assertIsInstance ( back.refs[0].content[8].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[8].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[8].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[8].content[0].asciiValue, "3550")
        self.assertEqual      ( back.refs[0].content[8].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[8].content[0].status)
        self.assertEqual      ( back.refs[0].content[8].content[0].value,      "3550")
        self.assertIsNone     ( back.refs[0].content[8].content[0].stream)

        # reference -- 08 - anchor
        self.assertEqual(back.refs[0].content[8].anchor, "RFC3550")
        # reference -- 08 - quoteTitle
        self.assertEqual(back.refs[0].content[8].quoteTitle, True)
        # reference -- 08 - target
        self.assertEqual(back.refs[0].content[8].target, "https://www.rfc-editor.org/info/rfc3550")


        # reference -- 09
        self.assertIsInstance( back.refs[0].content[9], rfc.Reference)
        if not isinstance( back.refs[0].content[9], rfc.Reference): # type-check
            return
        # reference -- 09 - front
        self.assertIsInstance( back.refs[0].content[9].front, rfc.Front)
        # reference -- 09 - front.title
        self.assertIsInstance( back.refs[0].content[9].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[9].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[9].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[9].front.title.content.content , "Session Traversal Utilities for NAT (STUN)")
        # reference -- 09 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[9].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[9].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[9].front.seriesInfo), 0)
        # reference -- 09 - front.authors
        self.assertEqual    ( len(back.refs[0].content[9].front.authors), 6)
        # reference -- 09 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[9].front.authors[0].org)
        if back.refs[0].content[9].front.authors[0].org is None : # type-check
                return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[0].fullname, "Marc Petit-Huguenin")
        self.assertEqual    ( back.refs[0].content[9].front.authors[0].initials, "M" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[0].surname, "Petit-Huguenin" )
        # reference -- 09 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[9].front.authors[1].org)
        if back.refs[0].content[9].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[1].fullname, "Gonzalo Salgueiro" )
        self.assertEqual    ( back.refs[0].content[9].front.authors[1].initials, "G" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[1].surname,  "Salgueiro" )
        # reference -- 09 - front.author - 2
        self.assertIsNotNone( back.refs[0].content[9].front.authors[2].org)
        if back.refs[0].content[9].front.authors[2].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[2].fullname, "Jonathan Rosenberg" )
        self.assertEqual    ( back.refs[0].content[9].front.authors[2].initials, "J" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[2].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[2].surname,  "Rosenberg" )
        # reference -- 09 - front.author - 3
        self.assertIsNotNone( back.refs[0].content[9].front.authors[3].org)
        if back.refs[0].content[9].front.authors[3].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[3].fullname, "Dan Wing" )
        self.assertEqual    ( back.refs[0].content[9].front.authors[3].initials, "D" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[3].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[3].surname,  "Wing" )
        # reference -- 09 - front.author - 4
        self.assertIsNotNone( back.refs[0].content[9].front.authors[4].org)
        if back.refs[0].content[9].front.authors[4].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[4].fullname, "Rohan Mahy" )
        self.assertEqual    ( back.refs[0].content[9].front.authors[4].initials, "R" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[4].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[4].surname,  "Mahy" )
        # reference -- 09 - front.author - 5
        self.assertIsNotNone( back.refs[0].content[9].front.authors[5].org)
        if back.refs[0].content[9].front.authors[5].org is None : # typecheck
            return
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.content)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].org.ascii)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].address)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].asciiSurname)
        self.assertEqual    ( back.refs[0].content[9].front.authors[5].fullname, "Philip Matthews" )
        self.assertEqual    ( back.refs[0].content[9].front.authors[5].initials, "P" )
        self.assertIsNone   ( back.refs[0].content[9].front.authors[5].role)
        self.assertEqual    ( back.refs[0].content[9].front.authors[5].surname,  "Matthews" )
        # reference -- 09 - front.date
        self.assertIsInstance( back.refs[0].content[9].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[9].front.date, rfc.Date): # type-check
            return
        self.assertEqual( back.refs[0].content[9].front.date.day, "21")
        self.assertEqual( back.refs[0].content[9].front.date.month, "March")
        self.assertEqual( back.refs[0].content[9].front.date.year, "2019")
        # reference -- 09 - front.areas
        self.assertIsInstance( back.refs[0].content[9].front.areas, list)
        if not isinstance( back.refs[0].content[9].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[9].front.areas), 0)
        # reference -- 09 - front.workgroups
        self.assertIsInstance( back.refs[0].content[9].front.workgroups, list)
        if not isinstance( back.refs[0].content[9].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[9].front.workgroups), 0)
        # reference -- 09 - front.keywords
        self.assertIsInstance( back.refs[0].content[9].front.keywords, list)
        if not isinstance( back.refs[0].content[9].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[9].front.keywords), 0)
        # reference -- 09 - front.abstract
        self.assertIsNone( back.refs[0].content[9].front.abstract)
        # reference -- 09 - front.notes
        self.assertIsInstance( back.refs[0].content[9].front.notes, list)
        if not isinstance( back.refs[0].content[9].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[9].front.notes), 0)
        # reference -- 09 - front.boilerplate
        self.assertIsNone( back.refs[0].content[9].front.boilerplate)


        # reference -- 09 - seriesInfo
        self.assertIsInstance( back.refs[0].content[9].content,list)
        self.assertEqual(len(back.refs[0].content[9].content), 1)

        self.assertIsInstance ( back.refs[0].content[9].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[9].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[9].content[0].asciiName,  "Internet-Draft")
        self.assertEqual      ( back.refs[0].content[9].content[0].asciiValue, "draft-ietf-tram-stunbis-21")
        self.assertEqual      ( back.refs[0].content[9].content[0].name,       "Internet-Draft")
        self.assertIsNone     ( back.refs[0].content[9].content[0].status)
        self.assertEqual      ( back.refs[0].content[9].content[0].value,      "draft-ietf-tram-stunbis-21")
        self.assertIsNone     ( back.refs[0].content[9].content[0].stream)

        # reference -- 09 - anchor
        self.assertEqual(back.refs[0].content[9].anchor, "draft-ietf-tram-stunbis-21")
        # reference -- 09 - quoteTitle
        self.assertEqual(back.refs[0].content[9].quoteTitle, True)
        # reference -- 09 - target
        self.assertEqual(back.refs[0].content[9].target, "http://www.ietf.org/internet-drafts/draft-ietf-tram-stunbis-21.txt")



        # reference -- 10
        self.assertIsInstance( back.refs[0].content[10], rfc.Reference)
        if not isinstance( back.refs[0].content[10], rfc.Reference): # type-check
            return
        # reference -- 10 - front
        self.assertIsInstance( back.refs[0].content[10].front, rfc.Front)
        # reference -- 10 - front.title
        self.assertIsInstance( back.refs[0].content[10].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[10].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[10].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[10].front.title.content.content , "Internet Protocol")
        # reference -- 10 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[10].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[10].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[10].front.seriesInfo), 0)
        # reference -- 10 - front.authors
        self.assertEqual    ( len(back.refs[0].content[10].front.authors), 1)
        # reference -- 10 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[10].front.authors[0].org)
        if back.refs[0].content[10].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[10].front.authors[0].fullname, "Jon Postel" )
        self.assertEqual    ( back.refs[0].content[10].front.authors[0].initials, "J" )
        self.assertIsNone   ( back.refs[0].content[10].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[10].front.authors[0].surname, "Postel" )
        # reference -- 10 - front.date
        self.assertIsInstance( back.refs[0].content[10].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[10].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[10].front.date.day)
        self.assertEqual( back.refs[0].content[10].front.date.month, "September")
        self.assertEqual( back.refs[0].content[10].front.date.year, "1981")
        # reference -- 10 - front.areas
        self.assertIsInstance( back.refs[0].content[10].front.areas, list)
        if not isinstance( back.refs[0].content[10].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[10].front.areas), 0)
        # reference -- 10 - front.workgroups
        self.assertIsInstance( back.refs[0].content[10].front.workgroups, list)
        if not isinstance( back.refs[0].content[10].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[10].front.workgroups), 0)
        # reference -- 10 - front.keywords
        self.assertIsInstance( back.refs[0].content[10].front.keywords, list)
        if not isinstance( back.refs[0].content[10].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[10].front.keywords), 0)
        # reference -- 10 - front.abstract
        self.assertIsNone( back.refs[0].content[10].front.abstract)
        # reference -- 10 - front.notes
        self.assertIsInstance( back.refs[0].content[10].front.notes, list)
        if not isinstance( back.refs[0].content[10].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[10].front.notes), 0)
        # reference -- 10 - front.boilerplate
        self.assertIsNone( back.refs[0].content[10].front.boilerplate)


        # reference -- 10 - seriesInfo
        self.assertIsInstance( back.refs[0].content[10].content,list)
        self.assertEqual(len(back.refs[0].content[10].content), 1)

        self.assertIsInstance ( back.refs[0].content[10].content[0],            rfc.SeriesInfo)
        if not isinstance( back.refs[0].content[10].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[10].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[10].content[0].asciiValue, "791")
        self.assertEqual      ( back.refs[0].content[10].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[10].content[0].status)
        self.assertEqual      ( back.refs[0].content[10].content[0].value,      "791")
        self.assertIsNone     ( back.refs[0].content[10].content[0].stream)

        # reference -- 10 - anchor
        self.assertEqual(back.refs[0].content[10].anchor, "RFC791")
        # reference -- 10 - quoteTitle
        self.assertEqual(back.refs[0].content[10].quoteTitle, True)
        # reference -- 10 - target
        self.assertEqual(back.refs[0].content[10].target, "https://www.rfc-editor.org/info/rfc791")




        # reference -- 11
        self.assertIsInstance( back.refs[0].content[11], rfc.Reference)
        if not isinstance( back.refs[0].content[11], rfc.Reference): # type-check
            return
        # reference -- 11 - front
        self.assertIsInstance( back.refs[0].content[11].front, rfc.Front)
        # reference -- 11 - front.title
        self.assertIsInstance( back.refs[0].content[11].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[11].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[11].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[11].front.title.content.content , "Transmission Control Protocol")
        # reference -- 11 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[11].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[11].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[11].front.seriesInfo), 0)
        # reference -- 11 - front.authors
        self.assertEqual    ( len(back.refs[0].content[11].front.authors), 1)
        # reference -- 11 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[11].front.authors[0].org)
        if back.refs[0].content[11].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[11].front.authors[0].fullname, "Jon Postel" )
        self.assertEqual    ( back.refs[0].content[11].front.authors[0].initials, "J" )
        self.assertIsNone   ( back.refs[0].content[11].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[11].front.authors[0].surname, "Postel" )
        # reference -- 11 - front.date
        self.assertIsInstance( back.refs[0].content[11].front.date, rfc.Date)
        if not isinstance( back.refs[0].content[11].front.date, rfc.Date): # type-check
            return
        self.assertIsNone( back.refs[0].content[11].front.date.day)
        self.assertEqual( back.refs[0].content[11].front.date.month, "September")
        self.assertEqual( back.refs[0].content[11].front.date.year, "1981")
        # reference -- 11 - front.areas
        self.assertIsInstance( back.refs[0].content[11].front.areas, list)
        if not isinstance( back.refs[0].content[11].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[11].front.areas), 0)
        # reference -- 11 - front.workgroups
        self.assertIsInstance( back.refs[0].content[11].front.workgroups, list)
        if not isinstance( back.refs[0].content[11].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[11].front.workgroups), 0)
        # reference -- 11 - front.keywords
        self.assertIsInstance( back.refs[0].content[11].front.keywords, list)
        if not isinstance( back.refs[0].content[11].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[11].front.keywords), 0)
        # reference -- 11 - front.abstract
        self.assertIsNone( back.refs[0].content[11].front.abstract)
        # reference -- 11 - front.notes
        self.assertIsInstance( back.refs[0].content[11].front.notes, list)
        if not isinstance( back.refs[0].content[11].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[11].front.notes), 0)
        # reference -- 11 - front.boilerplate
        self.assertIsNone( back.refs[0].content[11].front.boilerplate)


        # reference -- 11 - seriesInfo
        self.assertIsInstance( back.refs[0].content[11].content,list)
        # FIXME : parser_rfc_xml.py line 1324 seriesinfo -> seriesInfo
        self.assertEqual(len(back.refs[0].content[11].content), 1)

        self.assertIsInstance ( back.refs[0].content[11].content[0],            rfc.SeriesInfo)
        if not isinstance(back.refs[0].content[11].content[0], rfc.SeriesInfo): # type-check
            return
        self.assertEqual      ( back.refs[0].content[11].content[0].asciiName,  "RFC")
        self.assertEqual      ( back.refs[0].content[11].content[0].asciiValue, "793")
        self.assertEqual      ( back.refs[0].content[11].content[0].name,       "RFC")
        self.assertIsNone     ( back.refs[0].content[11].content[0].status)
        self.assertEqual      ( back.refs[0].content[11].content[0].value,      "793")
        self.assertIsNone     ( back.refs[0].content[11].content[0].stream)

        # reference -- 11 - anchor
        self.assertEqual(back.refs[0].content[11].anchor, "RFC793")
        # reference -- 11 - quoteTitle
        self.assertEqual(back.refs[0].content[11].quoteTitle, True)
        # reference -- 11 - target
        self.assertEqual(back.refs[0].content[11].target, "https://www.rfc-editor.org/info/rfc793")




        # reference -- 12
        self.assertIsInstance( back.refs[0].content[12], rfc.Reference)
        if not isinstance( back.refs[0].content[12], rfc.Reference): # type-check
            return
        # reference -- 12 - front
        self.assertIsInstance( back.refs[0].content[12].front, rfc.Front)
        # reference -- 12 - front.title
        self.assertIsInstance( back.refs[0].content[12].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[12].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[12].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[12].front.title.content.content , "LANGSEC: Language-theoretic Security")
        # reference -- 12 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[12].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[12].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[12].front.seriesInfo), 0)
        # reference -- 12 - front.authors
        self.assertEqual    ( len(back.refs[0].content[12].front.authors), 1)
        # reference -- 12 - front.author - 0
        self.assertIsNone( back.refs[0].content[12].front.authors[0].org)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[12].front.authors[0].fullname, "LANGSEC" )
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].initials)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].role)
        self.assertIsNone   ( back.refs[0].content[12].front.authors[0].surname)
        # reference -- 12 - front.date
        self.assertIsNone( back.refs[0].content[12].front.date)
        # reference -- 12 - front.areas
        self.assertIsInstance( back.refs[0].content[12].front.areas, list)
        if not isinstance( back.refs[0].content[12].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[12].front.areas), 0)
        # reference -- 12 - front.workgroups
        self.assertIsInstance( back.refs[0].content[12].front.workgroups, list)
        if not isinstance( back.refs[0].content[12].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[12].front.workgroups), 0)
        # reference -- 12 - front.keywords
        self.assertIsInstance( back.refs[0].content[12].front.keywords, list)
        if not isinstance( back.refs[0].content[12].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[12].front.keywords), 0)
        # reference -- 12 - front.abstract
        self.assertIsNone( back.refs[0].content[12].front.abstract)
        # reference -- 12 - front.notes
        self.assertIsInstance( back.refs[0].content[12].front.notes, list)
        if not isinstance( back.refs[0].content[12].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[12].front.notes), 0)
        # reference -- 12 - front.boilerplate
        self.assertIsNone( back.refs[0].content[12].front.boilerplate)


        # reference -- 12 - seriesInfo
        self.assertIsInstance( back.refs[0].content[12].content,list)
        self.assertEqual(len(back.refs[0].content[12].content), 0)

        # reference -- 12 - anchor
        self.assertEqual(back.refs[0].content[12].anchor, "LANGSEC")
        # reference -- 12 - quoteTitle
        self.assertEqual(back.refs[0].content[12].quoteTitle, True)
        # reference -- 12 - target
        self.assertEqual(back.refs[0].content[12].target, "http://langsec.org")


        # reference -- 13
        self.assertIsInstance( back.refs[0].content[13], rfc.Reference)
        if not isinstance( back.refs[0].content[13], rfc.Reference): # type-check
            return
        # reference -- 13 - front
        self.assertIsInstance( back.refs[0].content[13].front, rfc.Front)
        # reference -- 13 - front.title
        self.assertIsInstance( back.refs[0].content[13].front.title,  rfc.Title)
        self.assertIsInstance( back.refs[0].content[13].front.title.content ,  rfc.Text)
        self.assertIsInstance( back.refs[0].content[13].front.title.content.content ,  str)
        self.assertEqual( back.refs[0].content[13].front.title.content.content , "The Halting Problems of Network Stack Insecurity")
        # reference -- 13 - front.seriesInfo
        self.assertIsInstance( back.refs[0].content[13].front.seriesInfo, list)
        if not isinstance( back.refs[0].content[13].front.seriesInfo, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[13].front.seriesInfo), 0)
        # reference -- 13 - front.authors
        self.assertEqual    ( len(back.refs[0].content[13].front.authors), 4)
        # reference -- 13 - front.author - 0
        self.assertIsNotNone( back.refs[0].content[13].front.authors[0].org)
        if back.refs[0].content[13].front.authors[0].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.content)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].org.ascii)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].address)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].asciiSurname)
        self.assertEqual    ( back.refs[0].content[13].front.authors[0].fullname, "Len Sassaman" )
        self.assertEqual    ( back.refs[0].content[13].front.authors[0].initials, "L" )
        self.assertIsNone   ( back.refs[0].content[13].front.authors[0].role)
        self.assertEqual    ( back.refs[0].content[13].front.authors[0].surname, "Sassaman" )
        # reference -- 13 - front.author - 1
        self.assertIsNotNone( back.refs[0].content[13].front.authors[1].org)
        if back.refs[0].content[13].front.authors[1].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.content)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].org.ascii)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].address)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].asciiSurname)
        self.assertEqual    ( back.refs[0].content[13].front.authors[1].fullname, "Meredith L. Patterson" )
        self.assertEqual    ( back.refs[0].content[13].front.authors[1].initials, "M. L" )
        self.assertIsNone   ( back.refs[0].content[13].front.authors[1].role)
        self.assertEqual    ( back.refs[0].content[13].front.authors[1].surname,  "Patterson" )
        # reference -- 13 - front.author - 2
        self.assertIsNotNone( back.refs[0].content[13].front.authors[2].org)
        if back.refs[0].content[13].front.authors[2].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.content)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].org.ascii)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].address)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].asciiSurname)
        self.assertEqual    ( back.refs[0].content[13].front.authors[2].fullname, "Sergey Bratus" )
        self.assertEqual    ( back.refs[0].content[13].front.authors[2].initials, "S" )
        self.assertIsNone   ( back.refs[0].content[13].front.authors[2].role)
        self.assertEqual    ( back.refs[0].content[13].front.authors[2].surname,  "Bratus" )
        # reference -- 13 - front.author - 3
        self.assertIsNotNone( back.refs[0].content[13].front.authors[3].org)
        if back.refs[0].content[13].front.authors[3].org is None : # type-check
            return
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.content)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.abbrev)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].org.ascii)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].address)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiFullname)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiInitials)
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].asciiSurname)
        self.assertEqual    ( back.refs[0].content[13].front.authors[3].fullname, "Anna Shubina" )
        self.assertEqual    ( back.refs[0].content[13].front.authors[3].initials, "A" )
        self.assertIsNone   ( back.refs[0].content[13].front.authors[3].role)
        self.assertEqual    ( back.refs[0].content[13].front.authors[3].surname,  "Shubina" )
        # reference -- 13 - front.date
        self.assertIsNone( back.refs[0].content[13].front.date)
        # reference -- 13 - front.areas
        self.assertIsInstance( back.refs[0].content[13].front.areas, list)
        if not isinstance( back.refs[0].content[13].front.areas, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[13].front.areas), 0)
        # reference -- 13 - front.workgroups
        self.assertIsInstance( back.refs[0].content[13].front.workgroups, list)
        if not isinstance( back.refs[0].content[13].front.workgroups, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[13].front.workgroups), 0)
        # reference -- 13 - front.keywords
        self.assertIsInstance( back.refs[0].content[13].front.keywords, list)
        if not isinstance( back.refs[0].content[13].front.keywords, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[13].front.keywords), 0)
        # reference -- 13 - front.abstract
        self.assertIsNone( back.refs[0].content[13].front.abstract)
        # reference -- 13 - front.notes
        self.assertIsInstance( back.refs[0].content[13].front.notes, list)
        if not isinstance( back.refs[0].content[13].front.notes, list): # type-check
            return
        self.assertEqual( len(back.refs[0].content[13].front.notes), 0)
        # reference -- 13 - front.boilerplate
        self.assertIsNone( back.refs[0].content[13].front.boilerplate)


        # reference -- 13 - seriesInfo
        self.assertIsInstance( back.refs[0].content[13].content,list)
        self.assertEqual(len(back.refs[0].content[13].content), 1)

        self.assertIsInstance ( back.refs[0].content[13].content[0],              rfc.RefContent)
        if not isinstance( back.refs[0].content[13].content[0], rfc.RefContent): # type-check
            return
        self.assertIsInstance ( back.refs[0].content[13].content[0].content,      list)
        self.assertEqual      ( len(back.refs[0].content[13].content[0].content), 1)
        self.assertIsInstance ( back.refs[0].content[13].content[0].content[0], rfc.Text)
        self.assertEqual      ( back.refs[0].content[13].content[0].content[0].content, ";login: -- December 2011, Volume 36, Number 6")

        # reference -- 13 - anchor
        self.assertEqual(back.refs[0].content[13].anchor, "SASSAMAN")
        # reference -- 13 - quoteTitle
        self.assertEqual(back.refs[0].content[13].quoteTitle, True)
        # reference -- 13 - target
        self.assertEqual(back.refs[0].content[13].target, "https://www.usenix.org/publications/login/december-2011-volume-36-number-6/halting-problems-network-stack-insecurity")


        # sections
        self.assertIsInstance(back.sections, list)
        if not isinstance(back.sections, list): # type-check
            return
        self.assertEqual(len(back.sections), 2)

        # section-00
        self.assertIsInstance(back.sections[0], rfc.Section)
        # section-00 name
        self.assertIsInstance(back.sections[0].name, rfc.Name)
        if not isinstance(back.sections[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance(back.sections[0].name.content, list)
        self.assertEqual(len(back.sections[0].name.content), 1)
        self.assertIsInstance(back.sections[0].name.content[0], rfc.Text)
        self.assertEqual(back.sections[0].name.content[0].content, "ABNF specification")
        # section-00 content
        self.assertIsInstance(back.sections[0].content, list)
        self.assertEqual(len(back.sections[0].content), 0)
        # section-00 -- (sub) sections
        self.assertIsInstance(back.sections[0].sections, list)
        if not isinstance(back.sections[0].sections, list): # type-check
            return
        self.assertEqual(len(back.sections[0].sections), 2)
        # section-00 -- (sub) section 00
        self.assertIsInstance(back.sections[0].sections[0], rfc.Section)
        # section-00 -- (sub) section 00 name
        self.assertIsInstance(back.sections[0].sections[0].name, rfc.Name)
        if not isinstance(back.sections[0].sections[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].name.content, list)
        self.assertEqual(len(back.sections[0].sections[0].name.content), 1)
        self.assertIsInstance(back.sections[0].sections[0].name.content[0], rfc.Text)
        self.assertEqual(back.sections[0].sections[0].name.content[0].content, "Constraint Expressions")
        # section-00 -- (sub) section 00 -- content
        self.assertIsInstance(back.sections[0].sections[0].content, list)
        self.assertEqual(len(back.sections[0].sections[0].content), 1)
        self.assertIsInstance(back.sections[0].sections[0].content[0], rfc.SourceCode)
        if not isinstance(back.sections[0].sections[0].content[0], rfc.SourceCode): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].content[0].content, rfc.Text)
        self.assertEqual(back.sections[0].sections[0].content[0].content.content, """
    cond-expr = eq-expr "?" cond-expr ":" eq-expr
    eq-expr   = bool-expr eq-op   bool-expr
    bool-expr = ord-expr  bool-op ord-expr
    ord-expr  = add-expr  ord-op  add-expr

    add-expr  = mul-expr  add-op  mul-expr
    mul-expr  = expr      mul-op  expr
    expr      = *DIGIT / field-name /
                field-name-ws / "(" expr ")"

    field-name    = *ALPHA
    field-name-ws = *(field-name " ")

    mul-op  = "*" / "/" / "%"
    add-op  = "+" / "-"
    ord-op  = "<=" / "<" / ">=" / ">"
    bool-op = "&&" / "||" / "!"
    eq-op   = "==" / "!="
                """)
        # section-00 -- (sub) section-00 -- sourcecode anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(back.sections[0].sections[0].content[0].anchor)
        self.assertIsNone(back.sections[0].sections[0].content[0].name)
        self.assertIsNone(back.sections[0].sections[0].content[0].src)
        self.assertEqual(back.sections[0].sections[0].content[0].type, "abnf")


        # section-00 -- (sub) section 00 -- sections
        self.assertIsInstance(back.sections[0].sections[0].sections, list)
        if not isinstance(back.sections[0].sections[0].sections, list): # type-check
            return
        self.assertEqual(len(back.sections[0].sections[0].sections), 0)
        # section-00 -- (sub) section 00 -- anchor, numbered, removeInRFC, title, toc
        self.assertEqual(back.sections[0].sections[0].anchor, "ABNF-constraints")
        self.assertTrue(back.sections[0].sections[0].numbered)
        self.assertFalse(back.sections[0].sections[0].removeInRFC)
        self.assertIsNone(back.sections[0].sections[0].title)
        self.assertEqual(back.sections[0].sections[0].toc, "default" )


        # section-00 -- (sub) section 01
        self.assertIsInstance(back.sections[0].sections[1], rfc.Section)
        # section-00 -- (sub) section 01 name
        # FIXME : parse_section line 975 : name is not parsed
        self.assertIsInstance(back.sections[0].sections[1].name, rfc.Name)
        if not isinstance(back.sections[0].sections[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[1].name.content, list)
        self.assertEqual(len(back.sections[0].sections[1].name.content), 1)
        self.assertIsInstance(back.sections[0].sections[1].name.content[0], rfc.Text)
        self.assertEqual(back.sections[0].sections[1].name.content[0].content, "Augmented packet diagrams")
        # section-00 -- (sub) section 01 -- content
        self.assertIsInstance(back.sections[0].sections[1].content, list)
        self.assertEqual(len(back.sections[0].sections[1].content), 1)
        self.assertIsInstance(back.sections[0].sections[1].content[0], rfc.T)
        if not isinstance(back.sections[0].sections[1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[1].content[0].content, list)

        self.assertEqual(len(back.sections[0].sections[1].content[0].content), 6)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[0], rfc.Text): # type-check
            return
        #FIXME -- lstrip and rstrip each text ?
        self.assertEqual(back.sections[0].sections[1].content[0].content[0].content, """
                    Future revisions of this draft will include an ABNF specification for
                    the augmented packet diagram format described in
                    """)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[1], rfc.XRef)
        if not isinstance(back.sections[0].sections[1].content[0].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone(back.sections[0].sections[1].content[0].content[1].content)
        # FIXME : should default to "default" RFC7991 2.66.1
        self.assertIsNone(back.sections[0].sections[1].content[0].content[1].format)
        self.assertFalse(back.sections[0].sections[1].content[0].content[1].pageno)
        self.assertEqual(back.sections[0].sections[1].content[0].content[1].target, "augmentedascii")
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[2], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[2], rfc.Text): # type-check
            return
        #FIXME -- lstrip and rstrip each text ?
        self.assertEqual(back.sections[0].sections[1].content[0].content[2].content, """. Such a specification is omitted from
                    this draft given that the format is likely to change as its syntax is
                    developed. Given the visual nature of the format, it is more
                    appropriate for discussion to focus on the examples given in
                    """)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[3], rfc.XRef)
        if not isinstance(back.sections[0].sections[1].content[0].content[3], rfc.XRef): # type-check
            return
        self.assertIsNone(back.sections[0].sections[1].content[0].content[3].content)
        # FIXME : should default to "default" RFC7991 2.66.1
        self.assertIsNone(back.sections[0].sections[1].content[0].content[3].format)
        self.assertFalse(back.sections[0].sections[1].content[0].content[3].pageno)
        self.assertEqual(back.sections[0].sections[1].content[0].content[3].target, "augmentedascii")
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[4], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[4], rfc.Text): # type-check
            return
        #FIXME -- lstrip and rstrip each text ?
        self.assertEqual(back.sections[0].sections[1].content[0].content[4].content, """.
                """)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[5], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[5], rfc.Text): # type-check
            return
        #FIXME -- This extra newline -- where does it come from ? -- looks like the tail of the paragraph
        self.assertEqual(back.sections[0].sections[1].content[0].content[5].content, """
            """)


        # section-00 -- (sub) section 00 -- content -- anchor, hangText , keepWithNext, keepWithPrevious
        self.assertIsNone(back.sections[0].sections[1].content[0].anchor)
        self.assertIsNone(back.sections[0].sections[1].content[0].hangText)
        self.assertFalse(back.sections[0].sections[1].content[0].keepWithNext)
        self.assertFalse(back.sections[0].sections[1].content[0].keepWithPrevious)

        # section-00 -- (sub) section 01 -- sections
        self.assertIsInstance(back.sections[0].sections[1].sections, list)
        if not isinstance(back.sections[0].sections[1].sections, list): # type-check
            return
        self.assertEqual(len(back.sections[0].sections[1].sections), 0)
        # section-00 -- (sub) section 00 -- anchor, numbered, removeInRFC, title, toc
        self.assertEqual(back.sections[0].sections[1].anchor, "ABNF-diagrams")
        self.assertTrue(back.sections[0].sections[1].numbered)
        self.assertFalse(back.sections[0].sections[1].removeInRFC)
        self.assertIsNone(back.sections[0].sections[1].title)
        self.assertEqual(back.sections[0].sections[1].toc, "default" )

        # section-00 anchor, numbered, removeInRFC, title, toc
        self.assertEqual(back.sections[0].anchor, "ABNF")
        self.assertTrue(back.sections[0].numbered)
        self.assertFalse(back.sections[0].removeInRFC)
        self.assertIsNone(back.sections[0].title)
        self.assertEqual(back.sections[0].toc, "default" )


        # section-01
        self.assertIsInstance(back.sections[1], rfc.Section)
        # section-01 name
        self.assertIsInstance(back.sections[1].name, rfc.Name)
        if not isinstance(back.sections[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(back.sections[1].name.content, list)
        self.assertEqual(len(back.sections[1].name.content), 1)
        self.assertIsInstance(back.sections[1].name.content[0], rfc.Text)
        self.assertEqual(back.sections[1].name.content[0].content, "Source code repository")
        # section-01 content
        self.assertIsInstance(back.sections[1].content, list)
        self.assertEqual(len(back.sections[1].content), 2)
        # section-01 content[0]
        self.assertIsInstance(back.sections[1].content[0], rfc.T)
        if not isinstance(back.sections[1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[1].content[0].content, list)
        self.assertEqual(len(back.sections[1].content[0].content), 4)
        # section-01 content[0] content[0]
        self.assertIsInstance(back.sections[1].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[0].content[0].content, """
                The source for this draft is available from
                """)
        # section-01 content[0] content[1]
        self.assertIsInstance(back.sections[1].content[0].content[1], rfc.ERef)
        if not isinstance(back.sections[1].content[0].content[1], rfc.ERef): # type-check
            return
        self.assertIsNone(back.sections[1].content[0].content[1].content)
        self.assertEqual(back.sections[1].content[0].content[1].target, "https://github.com/glasgow-ipl/draft-mcquistin-augmented-ascii-diagrams")
        # section-01 content[0] content[2]
        self.assertIsInstance(back.sections[1].content[0].content[2], rfc.Text)
        if not isinstance(back.sections[1].content[0].content[2], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[0].content[2].content, """.
            """)
        # section-01 content[0] content[3]
        self.assertIsInstance(back.sections[1].content[0].content[3], rfc.Text)
        if not isinstance(back.sections[1].content[0].content[3], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[0].content[3].content, """
            """)

        # section-01 content[0] anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone(back.sections[1].content[0].anchor)
        self.assertIsNone(back.sections[1].content[0].hangText)
        self.assertFalse(back.sections[1].content[0].keepWithNext)
        self.assertFalse(back.sections[1].content[0].keepWithPrevious)


        # section-01 content[1]
        self.assertIsInstance(back.sections[1].content[1], rfc.T)
        if not isinstance(back.sections[1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[1].content[1].content, list)
        self.assertEqual(len(back.sections[1].content[1].content), 4)
        # section-01 content[1] content[0]
        self.assertIsInstance(back.sections[1].content[1].content[0], rfc.Text)
        if not isinstance(back.sections[1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[1].content[0].content, """
                The source code for tooling that can be used to parse this document is available
                from """)
        # section-01 content[0] content[1]
        self.assertIsInstance(back.sections[1].content[1].content[1], rfc.ERef)
        if not isinstance(back.sections[1].content[1].content[1], rfc.ERef): # type-check
            return
        self.assertIsNone(back.sections[1].content[1].content[1].content)
        self.assertEqual(back.sections[1].content[1].content[1].target, "https://github.com/glasgow-ipl/ips-protodesc-code")
        # section-01 content[0] content[2]
        self.assertIsInstance(back.sections[1].content[1].content[2], rfc.Text)
        if not isinstance(back.sections[1].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[1].content[2].content, """.
            """)
        # section-01 content[0] content[3]
        self.assertIsInstance(back.sections[1].content[1].content[3], rfc.Text)
        if not isinstance(back.sections[1].content[1].content[3], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[1].content[3].content, """
        """)


        # section-01 content[0] anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone(back.sections[1].content[0].anchor)
        self.assertIsNone(back.sections[1].content[0].hangText)
        self.assertFalse(back.sections[1].content[0].keepWithNext)
        self.assertFalse(back.sections[1].content[0].keepWithPrevious)

        # section-01 -- (sub) sections
        self.assertIsInstance(back.sections[1].sections, list)
        if not isinstance(back.sections[1].sections, list): # type-check
            return
        self.assertEqual(len(back.sections[1].sections), 0)

        # section-01 anchor, numbered, removeInRFC, title, toc
        self.assertEqual(back.sections[1].anchor, "source")
        self.assertTrue(back.sections[1].numbered)
        self.assertFalse(back.sections[1].removeInRFC)
        self.assertIsNone(back.sections[1].title)
        self.assertEqual(back.sections[1].toc, "default" )


    def test_rfc_middle(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            middle = npt.parser_rfc_xml.parse_rfc(xml_tree).middle

        # Test whether the title has been parsed correctly
        # For now, this just checks that the correct nodes are parsed
        self.assertEqual(len(middle.content), 8)
        # sec-00
        self.assertIsInstance(middle.content[0], rfc.Section)

        # sec-00  name 
        self.assertIsNotNone( middle.content[0].name) 
        self.assertIsInstance( middle.content[0].name, rfc.Name)
        if not isinstance(middle.content[0].name, rfc.Name):
            return
        self.assertIsInstance( middle.content[0].name.content, list)
        self.assertEqual( len(middle.content[0].name.content), 1)
        self.assertIsInstance( middle.content[0].name.content[0], rfc.Text)
        self.assertEqual( middle.content[0].name.content[0].content, "Introduction") 
        # sec-00  content 
        self.assertIsInstance( middle.content[0].content, list)
        self.assertEqual( len(middle.content[0].content), 7)
        # sec-00  content[0] <T> 
        self.assertIsInstance( middle.content[0].content[0], rfc.T)
        if not isinstance(middle.content[0].content[0], rfc.T): # type-check
            return
        # sec-00  content[0] <T>  Text
        self.assertIsInstance( middle.content[0].content[0].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[0].content), 2)
        self.assertIsInstance( middle.content[0].content[0].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[0].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[0].content[0].content[0].content, """
                Packet header diagrams have become a widely used format for
                describing the syntax of binary protocols. In otherwise largely textual
                documents, they allow for the visualisation of packet formats, reducing
                human error, and aiding in the implementation of parsers for the protocols
                that they specify.
            """)
        #FIXME - unnecessary empty tag 
        self.assertIsInstance(middle.content[0].content[0].content[1], rfc.Text) 
        if not isinstance(middle.content[0].content[0].content[1], rfc.Text) : # type-check
            return
        self.assertEqual(middle.content[0].content[0].content[1].content, """
            """)
        # sec-00  content[0] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[0].anchor)
        self.assertIsNone( middle.content[0].content[0].hangText)
        self.assertFalse( middle.content[0].content[0].keepWithNext)
        self.assertFalse( middle.content[0].content[0].keepWithPrevious)


        # sec-00  content[1] <T> 
        self.assertIsInstance( middle.content[0].content[1], rfc.T)
        if not isinstance( middle.content[0].content[1], rfc.T): # type-check
            return
        # sec-00  content[1] <T>  Text
        self.assertIsInstance( middle.content[0].content[1].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[1].content), 4)
        self.assertIsInstance( middle.content[0].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[1].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[0].content[1].content[0].content, """
                """)
        self.assertIsInstance( middle.content[0].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[0].content[1].content[1], rfc.XRef):  #type-check
            return
        self.assertIsNone( middle.content[0].content[1].content[1].content)
        #FIXME :  format defaults to "default" RFC 7991 sec 2.66.1
        self.assertIsNone( middle.content[0].content[1].content[1].format)
        self.assertFalse( middle.content[0].content[1].content[1].pageno)
        self.assertEqual( middle.content[0].content[1].content[1].target, "tcp-header-format")
        self.assertIsInstance( middle.content[0].content[1].content[2], rfc.Text) 
        if not isinstance( middle.content[0].content[1].content[2], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[0].content[1].content[2].content, """ gives an example of how packet
                header diagrams are used to define binary protocol formats. The format
                has an obvious structure: the diagram clearly delineates each field,
                showing its width and its position within the header. This type of diagram is
                designed for human readers, but is consistent enough that it should
                be possible to develop a tool that generates a parser for the packet
                format from the diagram.

            """)
        self.assertIsInstance( middle.content[0].content[1].content[3], rfc.Text) 
        if not isinstance( middle.content[0].content[1].content[3], rfc.Text) : # type-check
            return
        #FIXME - unnecessary empty tag 
        self.assertEqual( middle.content[0].content[1].content[3].content, """
        """)
        # sec-00  content[1] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[1].anchor)
        self.assertIsNone( middle.content[0].content[1].hangText)
        self.assertFalse( middle.content[0].content[1].keepWithNext)
        self.assertFalse( middle.content[0].content[1].keepWithPrevious)




        # sec-00  content[2] <Figure> 
        self.assertIsInstance( middle.content[0].content[2], rfc.Figure)
        if not isinstance( middle.content[0].content[2], rfc.Figure): # type-check
            return
        # sec-00  content[2] <Figure>  name
        self.assertIsInstance( middle.content[0].content[2].name, rfc.Name)
        if not isinstance( middle.content[0].content[2].name, rfc.Name): # type-check
            return
        self.assertIsInstance( middle.content[0].content[2].name.content, list)
        self.assertEqual( len(middle.content[0].content[2].name.content), 2)
        self.assertIsInstance( middle.content[0].content[2].name.content[0], rfc.Text)
        self.assertEqual( middle.content[0].content[2].name.content[0].content, "TCP's header format (from ")
        self.assertIsInstance( middle.content[0].content[2].name.content[1], rfc.XRef)
        if not isinstance( middle.content[0].content[2].name.content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[0].content[2].name.content[1].content)
        #FIXME :  format defaults to "default" RFC 7991 sec 2.66.1
        self.assertIsNone( middle.content[0].content[2].name.content[1].format)
        self.assertFalse( middle.content[0].content[2].name.content[1].pageno)
        self.assertEqual( middle.content[0].content[2].name.content[1].target, "RFC793")
        # sec-00  content[2] <Figure>  irefs
        self.assertIsInstance( middle.content[0].content[2].irefs, list)
        if not isinstance( middle.content[0].content[2].irefs, list): # type-check
            return
        self.assertEqual( len(middle.content[0].content[2].irefs), 0)
        # sec-00  content[2] <Figure>  preamble
        self.assertIsNone( middle.content[0].content[2].preamble)
        # sec-00  content[2] <Figure>  artwork
        self.assertIsInstance( middle.content[0].content[2].content, list)
        self.assertEqual( len(middle.content[0].content[2].content), 1)
        self.assertIsInstance( middle.content[0].content[2].content[0], rfc.Artwork)
        if not isinstance( middle.content[0].content[2].content[0], rfc.Artwork): # type-check
            return
        self.assertIsInstance( middle.content[0].content[2].content[0].content , rfc.Text)
        if not isinstance( middle.content[0].content[2].content[0].content , rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[2].content[0].content.content , """
:    0                   1                   2                   3
:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |          Source Port          |       Destination Port        |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                        Sequence Number                        |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                    Acknowledgment Number                      |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |  Data |           |U|A|P|R|S|F|                               |
:   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
:   |       |           |G|K|H|T|N|N|                               |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |           Checksum            |         Urgent Pointer        |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                    Options                    |    Padding    |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                             data                              |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            """)
        self.assertEqual( middle.content[0].content[2].content[0].align, "left")
        self.assertIsNone( middle.content[0].content[2].content[0].alt)
        self.assertIsNone( middle.content[0].content[2].content[0].anchor)
        self.assertIsNone( middle.content[0].content[2].content[0].height)
        self.assertIsNone( middle.content[0].content[2].content[0].name)
        self.assertIsNone( middle.content[0].content[2].content[0].src)
        self.assertIsNone( middle.content[0].content[2].content[0].type)
        self.assertIsNone( middle.content[0].content[2].content[0].width)
        self.assertIsNone( middle.content[0].content[2].content[0].xmlSpace)
        # sec-00  content[2] <Figure>  postamble
        self.assertIsNone( middle.content[0].content[2].postamble)
        # sec-00  content[2] <Figure>  align, alt, anchor, height, src, suppress
        self.assertEqual( middle.content[0].content[2].align, "left")
        self.assertIsNone( middle.content[0].content[2].alt)
        self.assertIsNotNone( middle.content[0].content[2].anchor)
        self.assertEqual( middle.content[0].content[2].anchor, "tcp-header-format")
        self.assertIsNone( middle.content[0].content[2].height)
        self.assertIsNone( middle.content[0].content[2].src)
        self.assertIsInstance( middle.content[0].content[2].suppressTitle, bool)
        self.assertFalse( middle.content[0].content[2].suppressTitle, False)
        self.assertIsNone( middle.content[0].content[2].title)
        self.assertIsNone( middle.content[0].content[2].width)


        # sec-00  content[3] <T> 
        self.assertIsInstance(middle.content[0].content[3], rfc.T)
        if not isinstance(middle.content[0].content[3], rfc.T): #type-check
            return
        # sec-00  content[3] <T>  Text
        self.assertIsInstance( middle.content[0].content[3].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[3].content), 2)
        self.assertIsInstance( middle.content[0].content[3].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[3].content[0], rfc.Text): # type-check 
            return

        self.assertEqual( middle.content[0].content[3].content[0].content, """
                Unfortunately, the format of such packet diagrams varies both within
                and between documents. This variation makes it difficult to build
                tools to generate parsers from the specifications. Better tooling
                could be developed if protocol specifications adopted a consistent
                format for their packet descriptions. Indeed,
                this underpins the format described by this draft: we want to
                retain the benefits that packet header diagrams provide, while identifying
                the benefits of adopting a consistent format.
             """)
        self.assertIsInstance( middle.content[0].content[3].content[1], rfc.Text) 
        if not isinstance( middle.content[0].content[3].content[1], rfc.Text) : # type-check
            return
        #FIXME - unnecessary empty tag 
        self.assertEqual( middle.content[0].content[3].content[1].content, """
            """)
        # sec-00  content[3] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[3].anchor)
        self.assertIsNone( middle.content[0].content[3].hangText)
        self.assertFalse( middle.content[0].content[3].keepWithNext)
        self.assertFalse( middle.content[0].content[3].keepWithPrevious)

        # sec-00  content[4] <T> 
        self.assertIsInstance(middle.content[0].content[4], rfc.T)
        if not isinstance(middle.content[0].content[4], rfc.T): #type-check
            return
        # sec-00  content[4] <T>  Text
        self.assertIsInstance( middle.content[0].content[4].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[4].content), 2)
        self.assertIsInstance( middle.content[0].content[4].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[4].content[0], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[0].content[4].content[0].content, """
                This document describes a consistent packet header diagram format and
                accompanying structured text constructs that allow for the parsing process
                of protocol headers to be fully specified. This provides support for the
                automatic generation of parser code. Broad design principles, that seek
                to maintain the primacy of human readability and flexibility in
                writing, are described, before the format itself is given.
            """)

        self.assertIsInstance( middle.content[0].content[4].content[1], rfc.Text) 
        if not isinstance( middle.content[0].content[4].content[1], rfc.Text) : # type-check
            return
        #FIXME - unnecessary empty tag 
        self.assertEqual( middle.content[0].content[4].content[1].content, """
            """)
        # sec-00  content[4] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[4].anchor)
        self.assertIsNone( middle.content[0].content[4].hangText)
        self.assertFalse( middle.content[0].content[4].keepWithNext)
        self.assertFalse( middle.content[0].content[4].keepWithPrevious)


        # sec-00  content[5] <T> 
        self.assertIsInstance(middle.content[0].content[5], rfc.T)
        if not isinstance(middle.content[0].content[5], rfc.T): # type-check
            return
        # sec-00  content[5] <T>  Text
        self.assertIsInstance( middle.content[0].content[5].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[5].content), 2)
        self.assertIsInstance( middle.content[0].content[5].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[5].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[5].content[0].content, """
                This document is itself an example of the approach that it describes, with
                the packet header diagrams and structured text format described by example.
                Examples that do not form part of the protocol description language are
                marked by a colon at the beginning of each line; this prevents them from
                being parsed by the accompanying tooling.
            """)
        #FIXME - unnecessary empty tag 
        self.assertIsInstance( middle.content[0].content[5].content[1], rfc.Text) 
        if not isinstance( middle.content[0].content[5].content[1], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[0].content[5].content[1].content, """
            """)
        # sec-00  content[5] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[5].anchor)
        self.assertIsNone( middle.content[0].content[5].hangText)
        self.assertFalse( middle.content[0].content[5].keepWithNext)
        self.assertFalse( middle.content[0].content[5].keepWithPrevious)


        # sec-00  content[6] <T> 
        self.assertIsInstance(middle.content[0].content[6], rfc.T)
        if not isinstance(middle.content[0].content[6], rfc.T): # type-check
            return
        # sec-00  content[6] <T>  Text
        self.assertIsInstance( middle.content[0].content[6].content, list)
        # FIXME : unnecessary single newline - strip empty tail
        self.assertEqual( len(middle.content[0].content[6].content), 6)
        self.assertIsInstance( middle.content[0].content[6].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[6].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[6].content[0].content, """
                This draft describes early work. As consensus builds around the
                particular syntax of the format described, both a formal ABNF
                specification (""")
        self.assertIsInstance( middle.content[0].content[6].content[1], rfc.XRef)
        if not isinstance( middle.content[0].content[6].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[0].content[6].content[1].content)
        #FIXME :  format defaults to "default" RFC 7991 sec 2.66.1
        self.assertIsNone( middle.content[0].content[6].content[1].format)
        self.assertFalse( middle.content[0].content[6].content[1].pageno)
        self.assertEqual( middle.content[0].content[6].content[1].target, "ABNF")
        self.assertIsInstance( middle.content[0].content[6].content[2], rfc.Text)
        if not isinstance( middle.content[0].content[6].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[6].content[2].content, ") and code (")
        self.assertIsInstance( middle.content[0].content[6].content[3], rfc.XRef)
        if not isinstance( middle.content[0].content[6].content[3], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[0].content[6].content[3].content)
        #FIXME :  format defaults to "default" RFC 7991 sec 2.66.1
        self.assertIsNone( middle.content[0].content[6].content[3].format)
        self.assertFalse( middle.content[0].content[6].content[3].pageno)
        self.assertEqual( middle.content[0].content[6].content[3].target, "source")
        self.assertIsInstance( middle.content[0].content[6].content[4], rfc.Text)
        if not isinstance( middle.content[0].content[6].content[4], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[6].content[4].content, """) that
                parses it (and, as described above, this document) will be provided.
            """)
        #FIXME - unnecessary empty tag 
        self.assertIsInstance( middle.content[0].content[6].content[5], rfc.Text) 
        if not isinstance( middle.content[0].content[6].content[5], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[0].content[6].content[5].content, """
        """)

        # sec-00  content[6] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[6].anchor)
        self.assertIsNone( middle.content[0].content[6].hangText)
        self.assertFalse( middle.content[0].content[6].keepWithNext)
        self.assertFalse( middle.content[0].content[6].keepWithPrevious)



        # sec-00  sections 
        self.assertIsInstance(middle.content[0].sections, list)
        if not isinstance(middle.content[0].sections, list): # type-check
            return
        self.assertEqual(len(middle.content[0].sections), 0)
        # sec-00  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[0].anchor, "intro")
        self.assertTrue(middle.content[0].numbered)
        self.assertFalse(middle.content[0].removeInRFC)
        self.assertIsNone(middle.content[0].title)
        self.assertEqual(middle.content[0].toc, "default" )



        # sec-01
        self.assertIsInstance(middle.content[1], rfc.Section)
        # sec-01  name 
        self.assertIsNotNone( middle.content[1].name) 
        self.assertIsInstance( middle.content[1].name, rfc.Name) 
        if not isinstance( middle.content[1].name, rfc.Name) : # type-check
            return
        self.assertEqual( len(middle.content[1].name.content), 1) 
        self.assertIsInstance( middle.content[1].name.content[0], rfc.Text) 
        self.assertEqual( middle.content[1].name.content[0].content, "Background") 
        # sec-01  content
        self.assertIsInstance( middle.content[1].content, list) 
        self.assertEqual( len(middle.content[1].content), 2) 
        # sec-01  content[0] <T>
        self.assertIsInstance( middle.content[1].content[0], rfc.T) 
        if not isinstance( middle.content[1].content[0], rfc.T) : # type-check
            return
        self.assertIsInstance( middle.content[1].content[0].content, list) 
        self.assertEqual( len(middle.content[1].content[0].content), 2) 
        self.assertIsInstance( middle.content[1].content[0].content[0], rfc.Text) 
        if not isinstance( middle.content[1].content[0].content[0], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[1].content[0].content[0].content, """
                This section begins by considering how packet header diagrams are
                used in existing documents. This exposes the limitations that the current
                usage has in terms of machine-readability, guiding the design of the
                format that this document proposes.
            """)
        #FIXME :  unused newline within tag
        self.assertIsInstance( middle.content[1].content[0].content[1], rfc.Text) 
        if not isinstance( middle.content[1].content[0].content[1], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[1].content[0].content[1].content, """
            """)
        # sec-01  content[0] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].content[0].anchor)
        self.assertIsNone( middle.content[1].content[0].hangText)
        self.assertFalse( middle.content[1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].content[0].keepWithPrevious)

        # sec-01  content[1] <T>
        self.assertIsInstance( middle.content[1].content[1], rfc.T) 
        if not isinstance( middle.content[1].content[1], rfc.T) : # type-check
            return
        self.assertIsInstance( middle.content[1].content[1].content, list) 
        self.assertEqual( len(middle.content[1].content[1].content), 2) 
        self.assertIsInstance( middle.content[1].content[1].content[0], rfc.Text) 
        if not isinstance( middle.content[1].content[1].content[0], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[1].content[1].content[0].content, """
                While this document focuses on the machine-readability of packet format
                diagrams, this section also discusses the use of other structured or formal
                languages within IETF documents. Considering how and why these languages
                are used provides an instructive contrast to the relatively incremental
                approach proposed here.
            """)
        #FIXME :  unused newline within tag
        self.assertIsInstance( middle.content[1].content[1].content[1], rfc.Text) 
        if not isinstance( middle.content[1].content[1].content[1], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[1].content[1].content[1].content, """

            """)
        # sec-01  content[1] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].content[1].anchor)
        self.assertIsNone( middle.content[1].content[1].hangText)
        self.assertFalse( middle.content[1].content[1].keepWithNext)
        self.assertFalse( middle.content[1].content[1].keepWithPrevious)

        # sec-01  sections
        self.assertIsInstance( middle.content[1].sections, list) 
        if not isinstance( middle.content[1].sections, list) : # type-check
            return
        self.assertEqual( len(middle.content[1].sections), 2) 
        # sec-01  sub-sec[0] 
        self.assertIsInstance( middle.content[1].sections[0], rfc.Section) 
        # sec-01  sub-sec[0] name
        self.assertIsNotNone( middle.content[1].sections[0].name)
        self.assertIsInstance( middle.content[1].sections[0].name, rfc.Name) 
        if not isinstance( middle.content[1].sections[0].name, rfc.Name) : # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].name.content, list) 
        self.assertEqual( len(middle.content[1].sections[0].name.content), 1) 
        self.assertIsInstance( middle.content[1].sections[0].name.content[0],  rfc.Text) 
        self.assertEqual( middle.content[1].sections[0].name.content[0].content, "Limitations of Current Packet Format Diagrams" ) 
        # sec-01  sub-sec[0] content
        self.assertIsInstance( middle.content[1].sections[0].content, list)
        self.assertEqual( len( middle.content[1].sections[0].content), 5)
        # sec-01  sub-sec[0] content[0] <Figure>
        self.assertIsInstance( middle.content[1].sections[0].content[0], rfc.Figure)
        if not isinstance( middle.content[1].sections[0].content[0], rfc.Figure): # type-check
            return
        # sec-01  sub-sec[0] content[0] <Figure> name 
        self.assertIsNotNone( middle.content[1].sections[0].content[0].name)
        self.assertIsInstance( middle.content[1].sections[0].content[0].name, rfc.Name)
        if not isinstance( middle.content[1].sections[0].content[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[0].name.content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[0].name.content), 2)
        self.assertIsInstance( middle.content[1].sections[0].content[0].name.content[0], rfc.Text)
        self.assertEqual( middle.content[1].sections[0].content[0].name.content[0].content, "QUIC's RESET_STREAM frame format (from ")
        self.assertIsInstance( middle.content[1].sections[0].content[0].name.content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[0].name.content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[0].name.content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[0].name.content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[0].name.content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[0].name.content[1].target, "QUIC-TRANSPORT")
        # sec-01  sub-sec[0] content[0] <Figure> irefs
        self.assertIsInstance( middle.content[1].sections[0].content[0].irefs, list)
        if not isinstance( middle.content[1].sections[0].content[0].irefs, list): # type-check
            return
        self.assertEqual( len(middle.content[1].sections[0].content[0].irefs), 0)
        # sec-01  sub-sec[0] content[0] <Figure> preamble
        self.assertIsNone( middle.content[1].sections[0].content[0].preamble)
        # sec-01  sub-sec[0] content[0] <Figure> content
        self.assertIsInstance( middle.content[1].sections[0].content[0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[0].content[0], rfc.Artwork)
        if not isinstance( middle.content[1].sections[0].content[0].content[0], rfc.Artwork): # type-check
            return
        # sec-01  sub-sec[0] content[0] <Figure> content[0] <artwork> content
        self.assertIsInstance( middle.content[1].sections[0].content[0].content[0].content, rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[0].content[0].content, rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[0].content[0].content.content, """
:   The RESET_STREAM frame is as follows:
:
:    0                   1                   2                   3
:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                        Stream ID (i)                        ...
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |  Application Error Code (16)  |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |                        Final Size (i)                       ...
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:
:   RESET_STREAM frames contain the following fields:
:
:   Stream ID:  A variable-length integer encoding of the Stream ID
:      of the stream being terminated.
:
:   Application Protocol Error Code:  A 16-bit application protocol
:      error code (see Section 20.1) which indicates why the stream
:      is being closed.
:
:   Final Size: A variable-length integer indicating the final size
:      of the stream by the RESET_STREAM sender, in unit of bytes.
                  """)
        # sec-01  sub-sec[0] content[0] <Figure> content[0] <artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual( middle.content[1].sections[0].content[0].content[0].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].alt)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].height)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].name)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].src)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].type)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].width)
        self.assertIsNone( middle.content[1].sections[0].content[0].content[0].xmlSpace)
        # sec-01  sub-sec[0] content[0] <Figure> postamble
        self.assertIsNone( middle.content[1].sections[0].content[0].postamble)
        # sec-01  sub-sec[0] content[0] <Figure> align, alt, anchor, height, src, suppressTitle, title, width
        self.assertEqual( middle.content[1].sections[0].content[0].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[0].alt)
        self.assertIsNotNone( middle.content[1].sections[0].content[0].anchor)
        self.assertEqual( middle.content[1].sections[0].content[0].anchor, "quic-reset-stream")
        self.assertIsNone( middle.content[1].sections[0].content[0].height)
        self.assertIsNone( middle.content[1].sections[0].content[0].src )
        self.assertIsInstance( middle.content[1].sections[0].content[0].suppressTitle, bool)
        self.assertFalse( middle.content[1].sections[0].content[0].suppressTitle, False)
        self.assertIsNone( middle.content[1].sections[0].content[0].title)
        self.assertIsNone( middle.content[1].sections[0].content[0].width)

        # sec-01  sub-sec[0] content[1] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[1], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[1], rfc.T): # type-check
            return
        # sec-01  sub-sec[0] content[1] <T> content
        self.assertIsInstance( middle.content[1].sections[0].content[1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[1].content), 4)
        self.assertIsInstance( middle.content[1].sections[0].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[1].content[0].content, """
                  Packet header diagrams are frequently used in IETF standards to describe the
                  format of binary protocols. While there is no standard for how
                  these diagrams should be formatted, they have a broadly similar structure,
                  where the layout of a protocol data unit (PDU) or structure is shown in
                  diagrammatic form, followed by a description list of the fields that it
                  contains. An example of this format, taken from the QUIC specification,
                  is given in """)
        self.assertIsInstance( middle.content[1].sections[0].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[1].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[1].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[1].content[1].target, "quic-reset-stream")
        self.assertIsInstance( middle.content[1].sections[0].content[1].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[1].content[2].content, """.
                """)
        self.assertIsInstance( middle.content[1].sections[0].content[1].content[3], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[1].content[3], rfc.Text): # type-check
            return
        #FIXME : unnecessary newline 
        self.assertEqual( middle.content[1].sections[0].content[1].content[3].content, """

                """)
        # sec-01  sub-sec[0] content[2] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[1].anchor) 
        self.assertIsNone( middle.content[1].sections[0].content[1].hangText) 
        self.assertFalse( middle.content[1].sections[0].content[1].keepWithNext) 
        self.assertFalse( middle.content[1].sections[0].content[1].keepWithPrevious) 


        # sec-01  sub-sec[0] content[2] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[2], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[2], rfc.T): # type-check
            return
        # sec-01  sub-sec[0] content[2] <T> content <Text>
        self.assertIsInstance( middle.content[1].sections[0].content[2].content, list)
        #FIXME : extra newline 
        self.assertEqual( len(middle.content[1].sections[0].content[2].content), 2)
        self.assertIsInstance( middle.content[1].sections[0].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[2].content[0].content, """
                  These packet header diagrams, and the accompanying descriptions, are
                  formatted for human readers rather than for automated processing. As
                  a result, while there is rough consistency in how packet header diagrams are
                  formatted, there are a number of limitations that make them difficult
                  to work with programmatically:
                """)
        self.assertIsInstance( middle.content[1].sections[0].content[2].content[1], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[2].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[2].content[1].content, """
                """)
        # sec-01  sub-sec[0] content[2] <T>  anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[2].anchor) 
        self.assertIsNone( middle.content[1].sections[0].content[2].hangText) 
        self.assertFalse( middle.content[1].sections[0].content[2].keepWithNext) 
        self.assertFalse( middle.content[1].sections[0].content[2].keepWithPrevious) 

        # sec-01  sub-sec[0] content[3] <DL>
        self.assertIsInstance( middle.content[1].sections[0].content[3], rfc.DL) 
        if not isinstance( middle.content[1].sections[0].content[3], rfc.DL) : # type-check
            return
        # sec-01  sub-sec[0] content[3] <DL> content
        self.assertIsInstance( middle.content[1].sections[0].content[3].content, list) 
        self.assertEqual( len(middle.content[1].sections[0].content[3].content), 4) 
        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0], tuple)
        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [0] <DT> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][0], rfc.DT)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][0].content[0].content, """
                    Inconsistent syntax:
                  """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][0].anchor)
        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1], rfc.DD)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content, list)
        # FIXME !!! <Tuple<DT,DD>>  not being parsed for <T> 
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content), 3)
        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[0] <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[0].content), 2)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0].content, """
                      There are two classes of consistency that are needed to support
                      automated processing of specifications: internal consistency
                      within a diagram or document, and external consistency across
                      all documents.
                    """)
        # FIXME : extra line item in tag <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[0].content[1].content, """
                      """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[0].keepWithPrevious)

        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[1] <T> 
        # FIXME !!! <Tuple<DT,DD>>  not being parsed for <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[1].content), 8)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0].content, """
                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].target, "quic-reset-stream")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[2].content, 
                        """ gives an example of internal
                        inconsistency. Here, the packet diagram shows a field labelled
                        "Application Error Code", while the accompanying description lists
                        the field as "Application Protocol Error Code". The use of an
                        abbreviated name is suitable for human readers, but makes parsing
                        the structure difficult for machines.

                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3].target, "dhcpv6-relaysrcopt")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[4], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[4], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[4].content, 
                        """ gives a further example, where
                        the description includes an "Option-Code" field that does not appear
                        in the packet diagram; and where the description states that
                        each field is 16 bits in length, but the diagram shows
                        the OPTION_RELAY_PORT as 13 bits, and Option-Len as 19 bits.

                        Another example is """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5].target, "RFC6958")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[6], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[6], rfc.Text): #type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[6].content, 
                      """, where the packet
                        format diagram showing the structure of the Burst/Gap Loss Metrics
                        Report Block shows the Number of Bursts field as being 12 bits wide
                        but the corresponding text describes it as 16 bits.
                      """)
        # FIXME : extra line item in tag <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[7], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[7], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[7].content, """

                      """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].keepWithPrevious)

        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[2] <T> 
        # FIXME !!! <Tuple<DT,DD>>  not being parsed for <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content, list)
        #FIXME :  class <T> additional line due to newline
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[2].content), 6)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0].content, """
                        Comparing """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].target, "quic-reset-stream")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[2].content, """ with
                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3].target, "dhcpv6-relaysrcopt")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[4], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[4], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[4].content, """ exposes external
                        inconsistency across documents. While the packet format
                        diagrams are broadly similar, the surrounding text is
                        formatted differently. If machine parsing is to be made
                        possible, then this text must be structured consistently.
                      """)
        #FIXME :  class <T> additional line due to newline
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[5], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[5], rfc.Text): #type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[5].content, """
                    """)

        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[2].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[2].keepWithPrevious)

        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].anchor)



        # sec-01  sub-sec[0] content[3] <DL> content[1] <tuple<DT,DD>>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1], tuple)
        # sec-01  sub-sec[0] content[3] <DL> content[1] <tuple<DT,DD>>  [0] <DT> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][0], rfc.DT)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[1][0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[1][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[1][0].content[0].content, """
                      Ambiguous constraints:
                    """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[1][0].anchor)
        # sec-01  sub-sec[0] content[3] <DL> content[1] <tuple<DT,DD>>  [1] <DD> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][1], rfc.DD)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][1].content, list)
        # FIXME !!! <Tuple<DT,DD>>  not being parsed for <T> 
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[1][1].content), 3)
        # sec-01  sub-sec[0] content[3] <DL> content[1] <tuple<DT,DD>>  [1] <DD> content[0] <Text> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[1][1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[1][1].content[0].content, """
                      The constraints that are enforced on a particular field are often
                      described ambiguously, or in a way that cannot be parsed easily.
                      In """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[1][1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[1][1].content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[1][1].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[1][1].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[1][1].content[1].target, "dhcpv6-relaysrcopt")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[1][1].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[1][1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[1][1].content[2].content,
                    """, each of the three fields
                      in the structure is constrained. The first two fields
                      ("Option-Code" and "Option-Len") are to be set to constant values
                      (note the inconsistency in how these constraints are expressed in
                      the description). However, the third field ("Downstream Source
                      Port") can take a value from a constrained set. This constraint
                      is expressed in prose that cannot readily by understood by machine.
                    """)

        self.assertIsNone( middle.content[1].sections[0].content[3].content[1][1].anchor)
                    

        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2], tuple)
        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>  [0] <DT> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][0], rfc.DT)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][0].content[0].content, """
                      Poor linking between sub-structures:
                    """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][0].anchor)
        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>  [1] <DD> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1], rfc.DD)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][1].content), 2)
        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>  [1] <DD> [0] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[0], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[0].content, list)
        #FIXME : <T>  remove empty tail
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][1].content[0].content), 2)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[0].content[0].content, """
                        Protocol data units and other structures are often comprised of
                        sub-structures that are defined elsewhere, either in the same
                        document, or within another document. Chaining these structures
                        together is essential for machine parsing: the parsing process for
                        a protocol data unit is only fully expressed if all elements can
                        be parsed.
                      """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[0].content[1].content, """
                      """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[0].keepWithPrevious)
        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>  [1] <DD> [1] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content, list)
        #FIXME : <T>  remove empty tail
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][1].content[1].content), 4)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0], rfc.Text): # type-check 
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0].content, """
                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].target, "quic-reset-stream")
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[2].content, 
                      """ highlights the difficulty that
                        machine parsers have in chaining structures together. Two fields
                        ("Stream ID" and "Final Size") are described as being encoded as
                        variable-length integers; this is a structure described elsewhere
                        in the same document. Structured text is required both alongside
                        the definition of the containing structure and with the definition
                        of the sub-structure, to allow a parser to link the two together.
                      """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[3], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[3], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[3].content, """
                    """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[1].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[1].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[1].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[1].keepWithPrevious)

        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].anchor)

        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3], tuple)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DT> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][0], rfc.DT)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[3][0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][0].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][0].content[0].content, """
                        Lack of extension and evolution syntax:
                    """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][0].anchor)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1], rfc.DD)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[3][1].content), 1)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0],  rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][1].content[0],  rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content, list)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> content
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[3][1].content[0].content), 4)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> content[0] <Text>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][1].content[0].content[0].content, """
                            Protocols are often specified across multiple documents, either
                            because the protocol explicitly includes extension points (e.g.,
                            profiles and payload format specifications in RTP
                            """)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> content[1] <XRef>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1].target, "RFC3550")
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> content[2] <Text>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][1].content[0].content[2].content, 
                        """) or because definition of a protocol
                            data unit has changed and evolved over time. As a result, it is
                            essential that syntax be provided to allow for a complete
                            definition of a protocol's parsing process to be constructed
                            across multiple documents.
                        """)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> content[3] <Text>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[3], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[3][1].content[0].content[3], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][1].content[0].content[3].content, """
                    """)
        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> content[0] <T> 
        # anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[3][1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[3][1].content[0].keepWithPrevious)

        # sec-01  sub-sec[0] content[3] <DL> content[3] <tuple<DT,DD>>  [0] <DD> anchor
        self.assertIsNone( middle.content[1].sections[0].content[3].content[3][1].anchor)

        # sec-01  sub-sec[0] content[3] <DL> anchor, hanging, spacing
        self.assertIsNone( middle.content[1].sections[0].content[3].anchor)
        self.assertTrue( middle.content[1].sections[0].content[3].hanging)
        self.assertEqual( middle.content[1].sections[0].content[3].spacing, "normal")


        # sec-01  sub-sec[0] content[4] <Figure>
        self.assertIsInstance( middle.content[1].sections[0].content[4], rfc.Figure)
        if not isinstance( middle.content[1].sections[0].content[4], rfc.Figure): # type-check
            return
        # sec-01  sub-sec[0] content[4] <Figure> name 
        self.assertIsNotNone( middle.content[1].sections[0].content[4].name)
        self.assertIsInstance( middle.content[1].sections[0].content[4].name, rfc.Name)
        if not isinstance( middle.content[1].sections[0].content[4].name, rfc.Name): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[4].name.content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[4].name.content), 2)
        self.assertIsInstance( middle.content[1].sections[0].content[4].name.content[0], rfc.Text)
        self.assertEqual( middle.content[1].sections[0].content[4].name.content[0].content, "DHCPv6's Relay Source Port Option (from ")
        self.assertIsInstance( middle.content[1].sections[0].content[4].name.content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[4].name.content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[4].name.content[1].content)
        self.assertIsNone( middle.content[1].sections[0].content[4].name.content[1].format)
        self.assertFalse( middle.content[1].sections[0].content[4].name.content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[4].name.content[1].target, "RFC8357")
        # sec-01  sub-sec[0] content[4] <Figure> irefs
        self.assertIsInstance( middle.content[1].sections[0].content[4].irefs, list)
        if not isinstance( middle.content[1].sections[0].content[4].irefs, list): # type-check
            return
        self.assertEqual( len(middle.content[1].sections[0].content[4].irefs), 0)
        # sec-01  sub-sec[0] content[4] <Figure> preamble
        self.assertIsNone( middle.content[1].sections[0].content[4].preamble)
        # sec-01  sub-sec[0] content[4] <Figure> content
        self.assertIsInstance( middle.content[1].sections[0].content[4].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[4].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[4].content[0], rfc.Artwork)
        if not isinstance( middle.content[1].sections[0].content[4].content[0], rfc.Artwork): # type-check
            return
        # sec-01  sub-sec[0] content[4] <Figure> content[0] <artwork> content
        self.assertIsInstance( middle.content[1].sections[0].content[4].content[0].content, rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[4].content[0].content, rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[4].content[0].content.content, """
:   The format of the "Relay Source Port Option" is shown below:
:
:    0                   1                   2                   3
:    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |    OPTION_RELAY_PORT    |         Option-Len                  |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:   |    Downstream Source Port     |
:   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
:
:   Where:
:
:   Option-Code:  OPTION_RELAY_PORT. 16-bit value, 135.
:
:   Option-Len:  16-bit value to be set to 2.
:
:   Downstream Source Port:  16-bit value.  To be set by the IPv6
:      relay either to the downstream relay agent's UDP source port
:      used for the UDP packet, or to zero if only the local relay
:      agent uses the non-DHCP UDP port (not 547).
                  """)
        # sec-01  sub-sec[0] content[4] <Figure> content[4] <artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual( middle.content[1].sections[0].content[4].content[0].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].alt)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].height)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].name)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].src)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].type)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].width)
        self.assertIsNone( middle.content[1].sections[0].content[4].content[0].xmlSpace)
        # sec-01  sub-sec[0] content[4] <Figure> postamble
        self.assertIsNone( middle.content[1].sections[0].content[4].postamble)
        # sec-01  sub-sec[0] content[4] <Figure> align, alt, anchor, height, src, suppressTitle, title, width
        self.assertEqual( middle.content[1].sections[0].content[4].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[4].alt)
        self.assertIsNotNone( middle.content[1].sections[0].content[4].anchor)
        self.assertEqual( middle.content[1].sections[0].content[4].anchor, "dhcpv6-relaysrcopt")
        self.assertIsNone( middle.content[1].sections[0].content[4].height)
        self.assertIsNone( middle.content[1].sections[0].content[4].src )
        self.assertIsInstance( middle.content[1].sections[0].content[4].suppressTitle, bool)
        self.assertFalse( middle.content[1].sections[0].content[4].suppressTitle, False)
        self.assertIsNone( middle.content[1].sections[0].content[4].title)
        self.assertIsNone( middle.content[1].sections[0].content[4].width)

        # sec-01  sub-sec[0] sections
        self.assertIsInstance( middle.content[1].sections[0].sections, list)
        if not isinstance( middle.content[1].sections[0].sections, list): # type-check 
            return
        self.assertEqual( len( middle.content[1].sections[0].sections), 0)
        # sec-01  sub-sec[0] anchor, numbered, removeInRFC, title, toc
        self.assertEqual(middle.content[1].sections[0].anchor, "background-ascii")
        self.assertTrue(middle.content[1].sections[0].numbered)
        self.assertFalse(middle.content[1].sections[0].removeInRFC)
        self.assertIsNone(middle.content[1].sections[0].title)
        self.assertEqual(middle.content[1].sections[0].toc, "default" )

        # sec-01  sub-sec[1] 
        self.assertIsInstance(middle.content[1].sections[1], rfc.Section)
        # sec-01  sub-sec[1] name 
        self.assertIsInstance(middle.content[1].sections[1].name, rfc.Name)
        if not isinstance(middle.content[1].sections[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[1].sections[1].name.content, list)
        self.assertEqual( len(middle.content[1].sections[1].name.content), 1)
        self.assertIsInstance( middle.content[1].sections[1].name.content[0], rfc.Text)
        self.assertEqual( middle.content[1].sections[1].name.content[0].content, "Formal languages in standards documents")
        # sec-01  sub-sec[1] content 
        self.assertIsInstance( middle.content[1].sections[1].content, list)
        self.assertEqual( len(middle.content[1].sections[1].content), 1)
        # FIXME : Additional element from <T> tail
        self.assertIsInstance( middle.content[1].sections[1].content[0], rfc.T)
        if not isinstance( middle.content[1].sections[1].content[0], rfc.T): # type-check
            return
        # FIXME : Additional element from <T> tail content
        self.assertIsInstance( middle.content[1].sections[1].content[0].content, list)
        self.assertEqual( len(middle.content[1].sections[1].content[0].content), 12)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[0], rfc.Text): # type-check 
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[0].content, """
                    A small proportion of IETF standards documents contain
                    structured and formal languages, including ABNF """)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[1].content[0].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[1].content[0].content[1].content)
        self.assertIsNone( middle.content[1].sections[1].content[0].content[1].format)
        self.assertFalse( middle.content[1].sections[1].content[0].content[1].pageno)
        self.assertEqual( middle.content[1].sections[1].content[0].content[1].target, "RFC5234")
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[2].content, """,
                    ASN.1 """)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[3], rfc.XRef)
        if not isinstance( middle.content[1].sections[1].content[0].content[3], rfc.XRef):  # type-check
             return
        self.assertIsNone( middle.content[1].sections[1].content[0].content[3].content)
        self.assertIsNone( middle.content[1].sections[1].content[0].content[3].format)
        self.assertFalse( middle.content[1].sections[1].content[0].content[3].pageno)
        self.assertEqual( middle.content[1].sections[1].content[0].content[3].target, "ASN1")
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[4], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[4], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[4].content, """, C, CBOR """)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[5], rfc.XRef)
        if not isinstance( middle.content[1].sections[1].content[0].content[5], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[1].content[0].content[5].content)
        self.assertIsNone( middle.content[1].sections[1].content[0].content[5].format)
        self.assertFalse( middle.content[1].sections[1].content[0].content[5].pageno)
        self.assertEqual( middle.content[1].sections[1].content[0].content[5].target, "RFC7049")
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[6], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[6], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[6].content, """, JSON,
                    the TLS presentation language """)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[7], rfc.XRef)
        if not isinstance( middle.content[1].sections[1].content[0].content[7], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[1].content[0].content[7].content)
        self.assertIsNone( middle.content[1].sections[1].content[0].content[7].format)
        self.assertFalse( middle.content[1].sections[1].content[0].content[7].pageno)
        self.assertEqual( middle.content[1].sections[1].content[0].content[7].target, "RFC8446")
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[8], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[8], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[8].content, """, YANG models
                    """)
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[9], rfc.XRef)
        if not isinstance( middle.content[1].sections[1].content[0].content[9], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[1].content[0].content[9].content)
        self.assertIsNone( middle.content[1].sections[1].content[0].content[9].format)
        self.assertFalse( middle.content[1].sections[1].content[0].content[9].pageno)
        self.assertEqual( middle.content[1].sections[1].content[0].content[9].target, "RFC7950")
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[10], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[10], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[10].content, """, and XML. While this broad
                    range of languages may be problematic for the development of tooling
                    to parse specifications, these, and other, languages serve a range of
                    different use cases. ABNF, for example, is typically used to specify
                    text protocols, while ASN.1 is used to specify data structure
                    serialisation. This document specifies a structured language for specifying
                    the parsing of binary protocol data units.
                """)
        # FIXME : Additional element from <T> tail content[11] <Text>
        self.assertIsInstance( middle.content[1].sections[1].content[0].content[11], rfc.Text)
        if not isinstance( middle.content[1].sections[1].content[0].content[11], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[1].content[0].content[11].content, """
            """)
        # sec-01  sub-sec[1] content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[1].content[0].keepWithPrevious)

        # sec-01  sub-sec[1] sections 
        self.assertIsInstance( middle.content[1].sections[1].sections, list)
        if not isinstance( middle.content[1].sections[1].sections, list): # type-check
            return
        self.assertEqual( len(middle.content[1].sections[1].sections), 0)

        # sec-01  sub-sec[1] anchor, numbered, removeInRFC, title, toc
        self.assertEqual(middle.content[1].sections[1].anchor, "background-others")
        self.assertTrue(middle.content[1].sections[1].numbered)
        self.assertFalse(middle.content[1].sections[1].removeInRFC)
        self.assertIsNone(middle.content[1].sections[1].title)
        self.assertEqual(middle.content[1].sections[1].toc, "default" )

        # sec-01  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[1].anchor, "background")
        self.assertTrue(middle.content[1].numbered)
        self.assertFalse(middle.content[1].removeInRFC)
        self.assertIsNone(middle.content[1].title)
        self.assertEqual(middle.content[1].toc, "default" )

        # sec-02
        self.assertIsInstance(middle.content[2], rfc.Section)
        # sec-02 name
        self.assertIsNotNone( middle.content[2].name) 
        self.assertIsInstance( middle.content[2].name, rfc.Name) 
        if not isinstance( middle.content[2].name, rfc.Name) : # type-check
            return
        self.assertEqual( len(middle.content[2].name.content), 1) 
        self.assertIsInstance( middle.content[2].name.content[0], rfc.Text) 
        self.assertEqual( middle.content[2].name.content[0].content, "Design Principles") 

        # sec-02 content
        self.assertIsInstance( middle.content[2].content, list)
        self.assertEqual( len(middle.content[2].content), 5)
        # sec-02 content[0] <T>
        self.assertIsInstance( middle.content[2].content[0], rfc.T)
        if not isinstance( middle.content[2].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[0].content, list)
        # FIXME : <T> element tail has extra space
        self.assertEqual( len(middle.content[2].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[0].content[0].content, """
                The use of structures that are designed to support machine readability
                might potentially interfere with the existing ways in which protocol
                specifications are used and authored. To the extent that these existing uses
                are more important than machine readability, such interference must be
                minimised.
            """)
        # FIXME : <T> element tail has extra space
        self.assertIsInstance( middle.content[2].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[0].content[1], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[2].content[0].content[1].content, """
            """)
        # sec-02  content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[0].anchor)
        self.assertIsNone( middle.content[2].content[0].hangText)
        self.assertFalse( middle.content[2].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[0].keepWithPrevious)

        # sec-02 content[1] <T>
        self.assertIsInstance( middle.content[2].content[1], rfc.T)
        if not isinstance( middle.content[2].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[1].content, list)
        # FIXME : <T> element tail has extra space
        self.assertEqual( len(middle.content[2].content[1].content), 2)
        self.assertIsInstance( middle.content[2].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[1].content[0].content, """
                In this section, the broad design principles that underpin the format
                described by this document are given. However, these principles apply more
                generally to any approach that introduces structured and formal languages
                into standards documents.
            """)
        # FIXME : <T> element tail has extra space
        self.assertIsInstance( middle.content[2].content[1].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[1].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[1].content[1].content, """
            """)
        # sec-02  content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[1].anchor)
        self.assertIsNone( middle.content[2].content[1].hangText)
        self.assertFalse( middle.content[2].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[1].keepWithPrevious)

        # sec-02 content[2] <T>
        self.assertIsInstance( middle.content[2].content[2], rfc.T)
        if not isinstance( middle.content[2].content[2], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[2].content, list)
        # FIXME : <T> element tail has extra space
        self.assertEqual( len(middle.content[2].content[2].content), 2)
        self.assertIsInstance( middle.content[2].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[2].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[2].content[2].content[0].content, """
                It should be noted that these are design principles: they expose the
                trade-offs that are inherent within any given approach. Violating these
                principles is sometimes necessary and beneficial, and this document sets
                out the potential consequences of doing so.
            """)
        # FIXME : <T> element tail has extra space
        self.assertIsInstance( middle.content[2].content[2].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[2].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[2].content[1].content, """
            """)
        # sec-02  content[2] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[2].anchor)
        self.assertIsNone( middle.content[2].content[2].hangText)
        self.assertFalse( middle.content[2].content[2].keepWithNext)
        self.assertFalse( middle.content[2].content[2].keepWithPrevious)


        # sec-02 content[3] <T>
        self.assertIsInstance( middle.content[2].content[3], rfc.T)
        if not isinstance( middle.content[2].content[3], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[3].content, list)
        # FIXME : <T> element tail has extra space
        self.assertEqual( len(middle.content[2].content[3].content), 2)
        self.assertIsInstance( middle.content[2].content[3].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[3].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[3].content[0].content, """
                The central tenet that underpins these design principles is a recognition
                that the standardisation process is not broken, and so does not need to be
                fixed. Failure to recognise this will likely lead to approaches that are
                incompatible with the standards process, or that will see limited
                adoption. However, the standards process can be improved with appropriate
                approaches, as guided by the following broad design principles:
            """)

        # FIXME : <T> element tail has extra space
        self.assertIsInstance( middle.content[2].content[3].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[3].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[3].content[1].content, """
            """)
        # sec-02  content[3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[3].anchor)
        self.assertIsNone( middle.content[2].content[3].hangText)
        self.assertFalse( middle.content[2].content[3].keepWithNext)
        self.assertFalse( middle.content[2].content[3].keepWithPrevious)





        # sec-02 content[4] <DL>
        self.assertIsInstance( middle.content[2].content[4], rfc.DL)
        if not isinstance( middle.content[2].content[4], rfc.DL): # type-check
            return
        self.assertIsInstance( middle.content[2].content[4].content, list)
        self.assertEqual( len(middle.content[2].content[4].content), 5)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL>
        self.assertIsInstance( middle.content[2].content[4].content[0], tuple)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [0] <DT>
        self.assertIsInstance( middle.content[2].content[4].content[0], tuple)
        self.assertIsInstance( middle.content[2].content[4].content[0][0], rfc.DT)
        self.assertIsInstance( middle.content[2].content[4].content[0][0].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[0][0].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[0][0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][0].content[0].content, """
                    Most readers are human:
                """)
        self.assertIsNone( middle.content[2].content[4].content[0][0].anchor)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD>
        self.assertIsInstance( middle.content[2].content[4].content[0][1], rfc.DD)
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[0][1].content), 2)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD> content [0] <T>
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[0], rfc.T)
        if not isinstance( middle.content[2].content[4].content[0][1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[0].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[0][1].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][1].content[0].content[0].content, """
                        Primarily, standards documents should be written for people, who
                        require text and diagrams that they can understand. Structures that
                        cannot be easily parsed by people should be avoided, and if
                        included, should be clearly delineated from human-readable
                        content.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][1].content[0].content[1].content, """
                    """)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD> content [0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[0][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[0][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[0][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[0][1].content[0].keepWithPrevious)

        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD> content [1] <T>
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[1], rfc.T)
        if not isinstance( middle.content[2].content[4].content[0][1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[1].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[0][1].content[1].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][1].content[1].content[0].content, """
                        Any approach that shifts this balance -- that is, that primarily
                        targets machine readers -- is likely to be disruptive to the
                        standardisation process, which relies upon discussion centered
                        around documents written in prose.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[1].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][1].content[1].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][1].content[1].content[1].content, """
                """)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD> content [0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[0][1].content[1].anchor)
        self.assertIsNone( middle.content[2].content[4].content[0][1].content[1].hangText)
        self.assertFalse( middle.content[2].content[4].content[0][1].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[0][1].content[1].keepWithPrevious)

        self.assertIsNone( middle.content[2].content[4].content[0][1].anchor)


        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL>
        self.assertIsInstance( middle.content[2].content[4].content[1], tuple)
        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL> [0] <DT>
        self.assertIsInstance( middle.content[2].content[4].content[1][0], rfc.DT)
        self.assertIsInstance( middle.content[2].content[4].content[1][0].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[1][0].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[1][0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[1][0].content[0].content, """
                    Writing tools are diverse:
                """)
        self.assertIsNone( middle.content[2].content[4].content[1][0].anchor)
        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL> [1] <DD>
        self.assertIsInstance( middle.content[2].content[4].content[1][1], rfc.DD)
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[1][1].content), 2)
        # sec-02 content[4] <DL> content[0] <Tuple<DT,DL> [1] <DD> content [0] <T>
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[0], rfc.T)
        if not isinstance( middle.content[2].content[4].content[1][1].content[0], rfc.T):  # type-check
             return
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[0].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[1][1].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][1].content[0].content[0], rfc.Text):  # type-check
             return
        self.assertEqual( middle.content[2].content[4].content[1][1].content[0].content[0].content, """
                        Standards document writing is a distributed process that involves a diverse set of
                        tools and workflows. The introduction of machine-readable
                        structures into specifications should not require that specific tools are
                        used to produce standards documents, to ensure that disruption to
                        existing workflows is minimised. This does not preclude the
                        development of optional, supplementary tools that aid in the
                        authoring machine-readable structures.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[1][1].content[0].content[1].content, """
                    """)
        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL> [1] <DD> content [0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[1][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[1][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[1][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[1][1].content[0].keepWithPrevious)

        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL> [1] <DD> content [1] <T>
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[1], rfc.T)
        if not isinstance( middle.content[2].content[4].content[1][1].content[1], rfc.T):  # type-check
            return
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[1].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[1][1].content[1].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[1][1].content[1].content[0].content, """
                        The immediate impact of requiring specific tooling is that
                        adoption is likely to be limited. A long-term impact might be that
                        authors whose workflows are incompatible might be alienated from
                        the process.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[1].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][1].content[1].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[1][1].content[1].content[1].content, """
                """)
        # sec-02 content[4] <DL> content[1] <Tuple<DT,DL> [1] <DD> content [1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[1][1].content[1].anchor)
        self.assertIsNone( middle.content[2].content[4].content[1][1].content[1].hangText)
        self.assertFalse( middle.content[2].content[4].content[1][1].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[1][1].content[1].keepWithPrevious)

        self.assertIsNone( middle.content[2].content[4].content[1][1].anchor)


        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL>
        self.assertIsInstance( middle.content[2].content[4].content[2], tuple)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [0] <DT>
        self.assertIsInstance( middle.content[2].content[4].content[2][0], rfc.DT)
        self.assertIsInstance( middle.content[2].content[4].content[2][0].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[2][0].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[2][0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[2][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[2][0].content[0].content, """
                    Canonical specifications:
                """)
        self.assertIsNone( middle.content[2].content[4].content[2][0].anchor)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [1] <DD>
        self.assertIsInstance( middle.content[2].content[4].content[2][1], rfc.DD)
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[2][1].content), 2)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [1] <DD> content [0] <T>
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[0], rfc.T)
        if not isinstance( middle.content[2].content[4].content[2][1].content[0], rfc.T): # type-check
             return
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[0].content, list)
        if not isinstance( middle.content[2].content[4].content[2][1].content[0].content, list): # type-check
            return
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[2][1].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[2][1].content[0].content[0], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[2].content[4].content[2][1].content[0].content[0].content, """
                        As far as possible, machine-readable structures should not
                        replicate the human readable specification of the protocol
                        within the same document. Machine-readable structures should form part
                        of a canonical specification of the protocol. Adding supplementary
                        machine-readable structures, in parallel to the existing
                        human readable text, is undesirable because it creates
                        the potential for inconsistency.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[2][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[2][1].content[0].content[1].content, """
                    """)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [1] <DD> content [0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[2][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[2][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[2][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[2][1].content[0].keepWithPrevious)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [1] <DD> content [1] <T>
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[1], rfc.T)
        if not isinstance( middle.content[2].content[4].content[2][1].content[1], rfc.T): # return
            return
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[1].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[2][1].content[1].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[2][1].content[1].content[0], rfc.Text): #type-check
             return
        self.assertEqual( middle.content[2].content[4].content[2][1].content[1].content[0].content, """
                        As an example, program code that describes how a protocol data
                        unit can be parsed might be provided as an appendix within a
                        standards document. This code would provide a specification of
                        the protocol that is separate to the prose description in the
                        main body of the document. This has the undesirable effect of
                        introducing the potential for the program code to specify behaviour
                        that the prose-based specification does not, and vice-versa.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[1].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[2][1].content[1].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[2][1].content[1].content[1].content, """
                """)
        # sec-02 content[4] <DL> content[2] <Tuple<DT,DL> [1] <DD> content [1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[2][1].content[1].anchor)
        self.assertIsNone( middle.content[2].content[4].content[2][1].content[1].hangText)
        self.assertFalse( middle.content[2].content[4].content[2][1].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[2][1].content[1].keepWithPrevious)
        self.assertIsNone( middle.content[2].content[4].content[2][1].anchor)

        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL>
        self.assertIsInstance( middle.content[2].content[4].content[3], tuple)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [0] <DT>
        self.assertIsInstance( middle.content[2].content[4].content[3][0], rfc.DT)
        self.assertIsInstance( middle.content[2].content[4].content[3][0].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[3][0].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[3][0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][0].content[0].content, """
                    Expressiveness:
                """)
        self.assertIsNone( middle.content[2].content[4].content[3][0].anchor)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD>
        self.assertIsInstance( middle.content[2].content[4].content[3][1], rfc.DD)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content), 3)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [0] <T>
        self.assertIsInstance( middle.content[2].content[4].content[2][1].content[0], rfc.T)
        if not isinstance( middle.content[2].content[4].content[3][1].content[0], rfc.T): #type-check
            return
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[0].content[0].content, """
                        Any approach should be expressive enough to capture the syntax
                        and parsing process for the majority of binary protocols. If a
                        given language is not sufficiently expressive, then adoption is
                        likely to be limited. At the limits of what can be expressed by
                        the language, authors are likely to revert to defining the
                        protocol in prose: this undermines the broad goal of using
                        structured and formal languages. Equally, though, understandable
                        specifications and ease of use are critical for adoption. A
                        tool that is simple to use and addresses the most common use
                        cases might be preferred to a complex tool that addresses all
                        use cases.
                    """)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[0].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[0].content[1].content, """
                    """)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[0].keepWithPrevious)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [1] <T>
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1], rfc.T)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1], rfc.T): # type-check
             return
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[1].content), 4)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1].content[0], rfc.Text): 
             return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[1].content[0].content, """
                        It may be desirable to restrict expressiveness, however, to
                        guarantee intrinsic safety, security, and computability
                        properties of both the generated parser code for the protocol,
                        and the parser of the description language itself. In
                        much the same way as the language-theoretic security
                        (""")
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1].content[1], rfc.XRef): #type -check
            return
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].content[1].content)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].content[1].format)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[1].content[1].pageno)
        self.assertEqual( middle.content[2].content[4].content[3][1].content[1].content[1].target, "LANGSEC")
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1].content[2], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[1].content[2].content, 
                    """) community advocates for programming
                        language design to be informed by the desired properties of
                        the parsers for those languages, protocol designers should be
                        aware of the implications of their design choices. The
                        expressiveness of the protocol description languages that they use to
                        define their protocols can force such awareness.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1].content[3], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1].content[3], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[1].content[3].content, """
                    """)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [1] <T> anchor, handText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].anchor)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].hangText)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[1].keepWithPrevious)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [2] <T>
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2], rfc.T)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2], rfc.T): # type-check
            return
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[2].content), 4)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[0].content, """
                        Broadly, those languages that have grammars which are more expressive tend to
                        have parsers that are more complex and less safe. As a
                        result, while considering the other goals described in
                        this document, protocol description languages should attempt to be
                        minimally expressive, and either restrict protocol designs to
                        those for which safe and secure parsers can be generated, or
                        as a minimum, ensure that protocol designers are aware of the boundaries their
                        designs cross, in terms of computability and decidability """)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2].content[1], rfc.XRef)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2].content[1], rfc.XRef): # type-check
             return
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[2].content[1].content)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[2].content[1].format)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[2].content[1].pageno)
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[1].target, """SASSAMAN""")
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2].content[2], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[2].content, """.
                    """)
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2].content[3], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2].content[3], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[3].content, """
                """)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[2].anchor)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[2].hangText)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[2].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[2].keepWithPrevious)

        self.assertIsNone( middle.content[2].content[4].content[3][1].anchor)


        # sec-02 content[4] <DL> content[4] <Tuple<DT,DL>
        self.assertIsInstance( middle.content[2].content[4].content[4], tuple)
        # sec-02 content[4] <DL> content[4] <Tuple<DT,DL> [0] <DT>
        self.assertIsInstance( middle.content[2].content[4].content[4][0], rfc.DT)
        self.assertIsInstance( middle.content[2].content[4].content[4][0].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[4][0].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[4][0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[4][0].content[0], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[2].content[4].content[4][0].content[0].content, """
                    Minimise required change:
                """)
        self.assertIsNone( middle.content[2].content[4].content[4][0].anchor)
        # sec-02 content[4] <DL> content[4] <Tuple<DT,DL> [1] <DD>
        self.assertIsInstance( middle.content[2].content[4].content[4][1], rfc.DD)
        self.assertIsInstance( middle.content[2].content[4].content[4][1].content, list)
        self.assertEqual( len(middle.content[2].content[4].content[4][1].content), 1)
        # sec-02 content[4] <DL> content[4] <Tuple<DT,DL> [1] <DD> content [0] <T>
        self.assertIsInstance( middle.content[2].content[4].content[4][1].content[0], rfc.T)
        if not isinstance( middle.content[2].content[4].content[4][1].content[0], rfc.T):  # type-check
            return
        self.assertIsInstance( middle.content[2].content[4].content[4][1].content[0].content, list)
        # FIXME : <T>  extra line in tail 
        self.assertEqual( len(middle.content[2].content[4].content[4][1].content[0].content), 2)
        self.assertIsInstance( middle.content[2].content[4].content[4][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[4][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[4][1].content[0].content[0].content, """
                        Any approach should require as few changes as possible to the way
                        that documents are formatted, authored, and published. Forcing adoption
                        of a particular structured or formal language is incompatible with
                        the IETF's standardisation process: there are very few components
                        of standards documents that are non-optional.
                    """)
        # FIXME : <T>  extra line in tail 
        self.assertIsInstance( middle.content[2].content[4].content[4][1].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[4][1].content[0].content[1], rfc.Text):  #  type-check
            return
        self.assertEqual( middle.content[2].content[4].content[4][1].content[0].content[1].content, """
                """)
        self.assertIsNone( middle.content[2].content[4].content[4][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[4][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[4][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[4][1].content[0].keepWithPrevious)
        self.assertIsNone( middle.content[2].content[4].content[4][1].anchor)

        # sec-02 content[4] <DL> anchor, hanging, spacing
        self.assertIsNone( middle.content[2].content[4].anchor)
        self.assertTrue( middle.content[2].content[4].hanging) 
        self.assertEqual( middle.content[2].content[4].spacing, "normal") 


        # sec-02 sections
        self.assertIsInstance( middle.content[2].sections, list)
        if not isinstance( middle.content[2].sections, list): # type-check
            return
        self.assertEqual( len(middle.content[2].sections), 0)

        # sec-02  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[2].anchor, "designprinciples")
        self.assertTrue(middle.content[2].numbered)
        self.assertFalse(middle.content[2].removeInRFC)
        self.assertIsNone(middle.content[2].title)
        self.assertEqual(middle.content[2].toc, "default" )


        # sec-03
        self.assertIsInstance(middle.content[3], rfc.Section)
        # sec-03 name
        self.assertIsNotNone( middle.content[3].name) 
        self.assertIsInstance( middle.content[3].name, rfc.Name) 
        if not isinstance( middle.content[3].name, rfc.Name) : # type-check
            return
        self.assertEqual( len(middle.content[3].name.content), 1) 
        self.assertIsInstance( middle.content[3].name.content[0], rfc.Text) 
        self.assertEqual( middle.content[3].name.content[0].content, "Augmented Packet Header Diagrams")

        # sec-03 content
        self.assertIsInstance( middle.content[3].content, list) 
        self.assertEqual( len(middle.content[3].content), 3) 
        # sec-03 content[0] <T>
        self.assertIsInstance( middle.content[3].content[0], rfc.T) 
        if not isinstance( middle.content[3].content[0], rfc.T) : # type-check
            return
        # sec-03 content[0] <T> content
        self.assertIsInstance( middle.content[3].content[0].content, list) 
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].content[0].content), 4) 
        self.assertIsInstance( middle.content[3].content[0].content[0], rfc.Text )
        if not isinstance( middle.content[3].content[0].content[0], rfc.Text ): # type-check
            return
        self.assertEqual( middle.content[3].content[0].content[0].content, """
                The design principles described in """)
        self.assertIsInstance( middle.content[3].content[0].content[1], rfc.XRef )
        if not isinstance( middle.content[3].content[0].content[1], rfc.XRef ): # type-check
            return
        self.assertIsNone( middle.content[3].content[0].content[1].content)
        self.assertIsNone( middle.content[3].content[0].content[1].format)
        self.assertFalse( middle.content[3].content[0].content[1].pageno)
        self.assertEqual( middle.content[3].content[0].content[1].target, """designprinciples""")
        self.assertIsInstance( middle.content[3].content[0].content[2], rfc.Text )
        if not isinstance( middle.content[3].content[0].content[2], rfc.Text ): # type-check
            return
        self.assertEqual( middle.content[3].content[0].content[2].content,
            """ can
                largely be met by the existing uses of packet header diagrams. These
                diagrams aid human readability, do not require new or specialised
                tools to write, do not split the specification into multiple parts,
                can express most binary protocol features, and require no changes to
                existing publication processes.
            """)
        self.assertIsInstance( middle.content[3].content[0].content[3], rfc.Text )
        if not isinstance( middle.content[3].content[0].content[3], rfc.Text ): # type-check
            return
        # FIXME : <T> extra line in tail
        self.assertEqual( middle.content[3].content[0].content[3].content, """
            """)
        # sec-03 content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].content[0].anchor) 
        self.assertIsNone( middle.content[3].content[0].hangText)
        self.assertFalse( middle.content[3].content[0].keepWithNext)
        self.assertFalse( middle.content[3].content[0].keepWithPrevious)

        # sec-03 content[1] <T>
        self.assertIsInstance( middle.content[3].content[1], rfc.T) 
        if not isinstance( middle.content[3].content[1], rfc.T) : # type-check
            return
        # sec-03 content[1] <T> content
        self.assertIsInstance( middle.content[3].content[1].content, list) 
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].content[1].content), 4) 
        self.assertIsInstance( middle.content[3].content[1].content[0], rfc.Text )
        if not isinstance( middle.content[3].content[1].content[0], rfc.Text ): # type-check
            return
        self.assertEqual( middle.content[3].content[1].content[0].content, """
                However, as discussed in """)
        self.assertIsInstance( middle.content[3].content[1].content[1], rfc.XRef )
        if not isinstance( middle.content[3].content[1].content[1], rfc.XRef ): # type-check
            return
        self.assertIsNone( middle.content[3].content[1].content[1].content)
        self.assertIsNone( middle.content[3].content[1].content[1].format)
        self.assertFalse( middle.content[3].content[1].content[1].pageno)
        self.assertEqual( middle.content[3].content[1].content[1].target, """background-ascii""")
        self.assertIsInstance( middle.content[3].content[1].content[2], rfc.Text )
        if not isinstance( middle.content[3].content[1].content[2], rfc.Text ): # type-check 
            return
        self.assertEqual( middle.content[3].content[1].content[2].content,
            """ there are
                limitations to how packet header diagrams are used that must be addressed if they
                are to be parsed by machine. In this section, an augmented packet
                header diagram format is described.
            """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].content[1].content[3], rfc.Text )
        if not isinstance( middle.content[3].content[1].content[3], rfc.Text ): #  type-check
            return
        self.assertEqual( middle.content[3].content[1].content[3].content, """
            """)
        # sec-03 content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].content[1].anchor) 
        self.assertIsNone( middle.content[3].content[1].hangText)
        self.assertFalse( middle.content[3].content[1].keepWithNext)
        self.assertFalse( middle.content[3].content[1].keepWithPrevious)

###### FROM HERE 
        # sec-03 content[2] <T>
        self.assertIsInstance( middle.content[3].content[2], rfc.T) 
        if not isinstance( middle.content[3].content[2], rfc.T) : # type-check
            return
        # sec-03 content[2] <T> content
        self.assertIsInstance( middle.content[3].content[2].content, list) 
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].content[2].content), 4) 
        self.assertIsInstance( middle.content[3].content[2].content[0], rfc.Text )
        if not isinstance( middle.content[3].content[2].content[0], rfc.Text ):
            return
        self.assertEqual( middle.content[3].content[2].content[0].content, """
                The concept is first illustrated by example. This is appropriate, given the visual
                nature of the language. In future drafts, these examples will be parsable using
                provided tools, and a formal specification of the augmented packet
                diagrams will be given in """)
        self.assertIsInstance( middle.content[3].content[2].content[1], rfc.XRef )
        if not isinstance( middle.content[3].content[2].content[1], rfc.XRef ): 
            return
        self.assertIsNone( middle.content[3].content[2].content[1].content)
        self.assertIsNone( middle.content[3].content[2].content[1].format)
        self.assertFalse( middle.content[3].content[2].content[1].pageno)
        self.assertEqual( middle.content[3].content[2].content[1].target, """ABNF""")
        self.assertIsInstance( middle.content[3].content[2].content[2], rfc.Text )
        if not isinstance( middle.content[3].content[2].content[2], rfc.Text ):
            return
        self.assertEqual( middle.content[3].content[2].content[2].content, """.
            """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].content[2].content[3], rfc.Text )
        if not isinstance( middle.content[3].content[2].content[3], rfc.Text ):
            return
        self.assertEqual( middle.content[3].content[2].content[3].content, """

            """)
        # sec-03 content[2] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].content[2].anchor) 
        self.assertIsNone( middle.content[3].content[2].hangText)
        self.assertFalse( middle.content[3].content[2].keepWithNext)
        self.assertFalse( middle.content[3].content[2].keepWithPrevious)

        # sec-03 sub-sec
        self.assertIsInstance( middle.content[3].sections, list) 
        if not isinstance( middle.content[3].sections, list) :
            return
        self.assertEqual( len(middle.content[3].sections), 10) 
        # sec-03 sub-sec[0] 
        self.assertIsInstance( middle.content[3].sections[0], rfc.Section)
        # sec-03 sub-sec[0] name 
        self.assertIsInstance( middle.content[3].sections[0].name, rfc.Name)
        if not isinstance( middle.content[3].sections[0].name, rfc.Name): #type-check
            return
        self.assertIsInstance( middle.content[3].sections[0].name.content, list)
        self.assertEqual( len(middle.content[3].sections[0].name.content), 1)
        self.assertIsInstance( middle.content[3].sections[0].name.content[0], rfc.Text)
        self.assertEqual( middle.content[3].sections[0].name.content[0].content, "PDUs with Fixed and Variable-Width Fields")
        # sec-03 sub-sec[0] content 
        self.assertIsInstance( middle.content[3].sections[0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content), 10)

        # sec-03 sub-sec[0] content [0] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[0], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[0], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [0] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[0].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[0].content), 2)
        self.assertIsInstance( middle.content[3].sections[0].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[0].content[0], rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[0].content[0].content[0].content, """
                  The simplest PDU is one that contains only a set of fixed-width
                  fields in a known order, with no optional fields or variation
                  in the packet format.
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[0].content[1], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[0].content[1], rfc.Text):
             return
        self.assertEqual( middle.content[3].sections[0].content[0].content[1].content, """

                """)
        # sec-03 sub-sec[0] content [0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[0].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[0].hangText)
        self.assertFalse( middle.content[3].sections[0].content[0].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[0].keepWithPrevious)

        # sec-03 sub-sec[0] content [1] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[1], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[1], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [1] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[1].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[1].content), 2)
        self.assertIsInstance( middle.content[3].sections[0].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[1].content[0], rfc.Text): #type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[1].content[0].content, """
                  Some packet formats include variable-width fields, where
                  the size of a field is either derived from the value of
                  some previous field, or is unspecified and inferred from
                  the total size of the packet and the size of the other
                  fields.
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[1].content[1], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[1].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[1].content[1].content, """

                """)
        # sec-03 sub-sec[0] content [1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[1].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[1].hangText)
        self.assertFalse( middle.content[3].sections[0].content[1].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[1].keepWithPrevious)

        # sec-03 sub-sec[0] content [2] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[2], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[2], rfc.T):  # type-check
            return
        # sec-03 sub-sec[0] content [2] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[2].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[2].content), 2)
        self.assertIsInstance( middle.content[3].sections[0].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[2].content[0].content, """
                  To ensure that there is no ambiguity, a PDU description
                  can contain only one field whose length is unspecified.
                  The length of a single field, where all other fields are
                  of known (but perhaps variable) length, can be inferred
                  from the total size of the containing PDU.
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[2].content[1], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[2].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[2].content[1].content, """

                """)
        # sec-03 sub-sec[0] content [2] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[2].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[2].hangText)
        self.assertFalse( middle.content[3].sections[0].content[2].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[2].keepWithPrevious)

        # sec-03 sub-sec[0] content [3] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[3], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[3], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [3] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[3].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[3].content), 2)
        self.assertIsInstance( middle.content[3].sections[0].content[3].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[3].content[0], rfc.Text): #  type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[3].content[0].content, """
                  A PDU description is introduced by the exact phrase "A/An
                  _______ is formatted as follows:" at the end of a paragraph.
                  This is followed by the PDU description itself, as a packet
                  diagram within an <artwork> element in the XML representation,
                  starting with a header line to show the bit width of the diagram.
                  The description of the fields follows the diagram, as an XML
                  <dl> list, after a paragraph containing the text "where:".
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[3].content[1], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[3].content[1], rfc.Text):  # type-check
             return
        self.assertEqual( middle.content[3].sections[0].content[3].content[1].content, """

                """)
        # sec-03 sub-sec[0] content [3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[3].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[3].hangText)
        self.assertFalse( middle.content[3].sections[0].content[3].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[3].keepWithPrevious)

        # sec-03 sub-sec[0] content [4] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[4], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[4], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [4] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[4].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[4].content), 4)
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[4].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[4].content[0].content, """
                  PDU names must be unique, both within a document, and across
                  all documents that are linked together (i.e., using the
                  structured language defined in """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[1], rfc.XRef)
        if not isinstance( middle.content[3].sections[0].content[4].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[3].sections[0].content[4].content[1].content)
        self.assertIsNone( middle.content[3].sections[0].content[4].content[1].format)
        self.assertFalse( middle.content[3].sections[0].content[4].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[4].content[1].target, """ascii-import""")
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[4].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[4].content[2].content, """).
                """)
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[3], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[4].content[3], rfc.Text): # type-check
            return
        # FIXME : <T> extra line in tail
        self.assertEqual( middle.content[3].sections[0].content[4].content[3].content, """

                """)
        # sec-03 sub-sec[0] content [4] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[4].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[4].hangText)
        self.assertFalse( middle.content[3].sections[0].content[4].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[4].keepWithPrevious)



        # sec-03 sub-sec[0] content [5] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[5], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[5], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [5] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[5].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[5].content), 4)
        self.assertIsInstance( middle.content[3].sections[0].content[5].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[5].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[5].content[0].content, """
                  Each field of the description starts with a <dt> tag
                  comprising the field name and an optional short name in
                  parenthesis. These are followed by a colon, the field
                  length, an optional presence expression (described in
                  """)
        self.assertIsInstance( middle.content[3].sections[0].content[5].content[1], rfc.XRef)
        if not isinstance( middle.content[3].sections[0].content[5].content[1], rfc.XRef): # type-check
             return
        self.assertIsNone( middle.content[3].sections[0].content[5].content[1].content)
        self.assertIsNone( middle.content[3].sections[0].content[5].content[1].format)
        self.assertFalse( middle.content[3].sections[0].content[5].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[5].content[1].target, """ascii-xref""")
        self.assertIsInstance( middle.content[3].sections[0].content[5].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[5].content[2], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[3].sections[0].content[5].content[2].content,
                """), and a terminating period. The following <dd>
                  tag contains a prose description of the field. Field names
                  cannot be the same as a previously defined PDU name, and must
                  be unique within a given structure definition.
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[5].content[3], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[5].content[3], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[5].content[3].content, """

                """)
        # sec-03 sub-sec[0] content [5] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[5].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[5].hangText)
        self.assertFalse( middle.content[3].sections[0].content[5].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[5].keepWithPrevious)

        # sec-03 sub-sec[0] content [6] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[6], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[6], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [6] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[6].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[6].content), 4)
        self.assertIsInstance( middle.content[3].sections[0].content[6].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[6].content[0], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[6].content[0].content, """
                 For example, this can be illustrated using the IPv4 Header
                 Format """)
        self.assertIsInstance( middle.content[3].sections[0].content[6].content[1], rfc.XRef)
        if not isinstance( middle.content[3].sections[0].content[6].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[3].sections[0].content[6].content[1].content)
        self.assertIsNone( middle.content[3].sections[0].content[6].content[1].format)
        self.assertFalse( middle.content[3].sections[0].content[6].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[6].content[1].target, """RFC791""")
        self.assertIsInstance( middle.content[3].sections[0].content[6].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[6].content[2], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[6].content[2].content,
                """. An IPv4 Header is formatted
                 as follows:
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[6].content[3], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[6].content[3], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[3].sections[0].content[6].content[3].content, """
                """)
        # sec-03 sub-sec[0] content [6] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[6].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[6].hangText)
        self.assertFalse( middle.content[3].sections[0].content[6].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[6].keepWithPrevious)

        # sec-03 sub-sec[0] content [7] <Artwork>
        self.assertIsInstance( middle.content[3].sections[0].content[7], rfc.Artwork)
        if not isinstance( middle.content[3].sections[0].content[7], rfc.Artwork): # type-check
            return
        # sec-03 sub-sec[0] content [7] <Artwork> content
        self.assertIsInstance( middle.content[3].sections[0].content[7].content, rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[7].content, rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[7].content.content, """
     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |Version|   IHL |    DSCP   |ECN|         Total Length          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |         Identification        |Flags|     Fragment Offset     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Time to Live  |    Protocol   |        Header Checksum        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                         Source Address                        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                      Destination Address                      |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                            Options                          ...
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               :
    :                            Payload                            :
    :                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                """)
        # sec-03 sub-sec[0] content [7] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual( middle.content[3].sections[0].content[7].align , "left" )
        self.assertIsNone( middle.content[3].sections[0].content[7].alt)
        self.assertIsNone( middle.content[3].sections[0].content[7].anchor)
        self.assertIsNone( middle.content[3].sections[0].content[7].height)
        self.assertIsNone( middle.content[3].sections[0].content[7].name)
        self.assertIsNone( middle.content[3].sections[0].content[7].src)
        self.assertIsNone( middle.content[3].sections[0].content[7].type)
        self.assertIsNone( middle.content[3].sections[0].content[7].width)
        self.assertIsNone( middle.content[3].sections[0].content[7].xmlSpace)

        # sec-03 sub-sec[0] content [8] <T>
        self.assertIsInstance( middle.content[3].sections[0].content[8], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[8], rfc.T):  # type-check
            return
        # sec-03 sub-sec[0] content [8] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[8].content, list)
        # FIXME : <T> extra line in tail
        self.assertEqual( len(middle.content[3].sections[0].content[8].content), 2)
        self.assertIsInstance( middle.content[3].sections[0].content[8].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[8].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[8].content[0].content, """
                    where:
                """)
        # FIXME : <T> extra line in tail
        self.assertIsInstance( middle.content[3].sections[0].content[8].content[1], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[8].content[1], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[8].content[1].content, """
                """)
        # sec-03 sub-sec[0] content [8] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[8].anchor) 
        self.assertIsNone( middle.content[3].sections[0].content[8].hangText)
        self.assertFalse( middle.content[3].sections[0].content[8].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[8].keepWithPrevious)

        # sec-03 sub-sec[0] content [9] <DL>
        self.assertIsInstance( middle.content[3].sections[0].content[9], rfc.DL)
        if not isinstance( middle.content[3].sections[0].content[9], rfc.DL) : # type-check
            return
        # sec-03 sub-sec[0] content [9] <DL> content 
        self.assertIsInstance( middle.content[3].sections[0].content[9].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content), 15)
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # DJ section-03 subsection[0] content[9] DL --- continue 
        # sec-03 sub-sec[0] content [9] <DL> anchor, hanging, spacing
        self.assertIsNone( middle.content[3].sections[0].content[9].anchor)
        self.assertTrue( middle.content[3].sections[0].content[9].hanging) 
        self.assertEqual( middle.content[3].sections[0].content[9].spacing, "normal") 

        # sec-03 sub-sec[0] sections 
        self.assertIsInstance( middle.content[3].sections[0].sections, list)
        if not isinstance( middle.content[3].sections[0].sections, list): # type-check
            return
        self.assertEqual( len(middle.content[3].sections[0].sections), 0)
        # sec-03  sub-sec[0] anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[3].sections[0].anchor, "ascii-simple")
        self.assertTrue(middle.content[3].sections[0].numbered)
        self.assertFalse(middle.content[3].sections[0].removeInRFC)
        self.assertIsNone(middle.content[3].sections[0].title)
        self.assertEqual(middle.content[3].sections[0].toc, "default")

        # sec-03 sub-sec[1] 
        self.assertIsInstance( middle.content[3].sections[1], rfc.Section)
        # sec-03 sub-sec[2] 
        self.assertIsInstance( middle.content[3].sections[2], rfc.Section)
        # sec-03 sub-sec[3] 
        self.assertIsInstance( middle.content[3].sections[3], rfc.Section)
        # sec-03 sub-sec[4] 
        self.assertIsInstance( middle.content[3].sections[4], rfc.Section)
        # sec-03 sub-sec[5] 
        self.assertIsInstance( middle.content[3].sections[5], rfc.Section)
        # sec-03 sub-sec[6] 
        self.assertIsInstance( middle.content[3].sections[6], rfc.Section)
        # sec-03 sub-sec[7] 
        self.assertIsInstance( middle.content[3].sections[7], rfc.Section)
        # sec-03 sub-sec[8] 
        self.assertIsInstance( middle.content[3].sections[8], rfc.Section)
        # sec-03 sub-sec[9] 
        self.assertIsInstance( middle.content[3].sections[9], rfc.Section)

#----------
        # DJ section-03 
#----------



        # sec-03  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[3].anchor, "augmentedascii")
        self.assertTrue(middle.content[3].numbered)
        self.assertFalse(middle.content[3].removeInRFC)
        self.assertIsNone(middle.content[3].title)
        self.assertEqual(middle.content[3].toc, "default" )
        # ...
        self.assertIsInstance(middle.content[4], rfc.Section)
        # ...
        self.assertIsInstance(middle.content[5], rfc.Section)
        # ...
        self.assertIsInstance(middle.content[6], rfc.Section)
        # ...
        self.assertIsInstance(middle.content[7], rfc.Section)
        # ...

