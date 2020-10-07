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
import npt.parser_rfc_txt

#from npt.parser               import Parser
#from npt.parser_asciidiagrams import AsciiDiagramsParser

from typing import Union, Optional, List, Tuple


class Test_Parse_Draft_McQuistin_Augmented_Ascii_Diagrams(unittest.TestCase):
    def test_xml_rfc_root(self) :
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            node = npt.parser_rfc_xml.parse_rfc(xml_tree)
            self._verify_rfc_dom_root(node, True)

    def test_xml_rfc_front(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            node = npt.parser_rfc_xml.parse_rfc(xml_tree).front
            self._verify_rfc_dom_front(node)

    def test_xml_rfc_middle(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            middle = npt.parser_rfc_xml.parse_rfc(xml_tree).middle
            self._verify_rfc_middle(middle)


    def test_xml_rfc_back(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            back = npt.parser_rfc_xml.parse_rfc(xml_tree).back 
            if back is not None : 
                self._verify_rfc_dom_back(back)

    def test_txt_rfc_root(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.txt" , 'r') as fd:
            content = fd.readlines()
            root = npt.parser_rfc_txt.parse_rfc(content)
            self.assertIsInstance(root, rfc.RFC)
            self._verify_rfc_dom_root(root, False)


    def test_txt_rfc_front(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.txt" , 'r') as fd:
            content = fd.readlines()
            root = npt.parser_rfc_txt.parse_rfc(content)
            self.assertIsInstance(root, rfc.RFC)
            self._verify_rfc_txt_dom_front(root.front)

    def test_txt_rfc_middle(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.txt" , 'r') as fd:
            content = fd.readlines()
            root = npt.parser_rfc_txt.parse_rfc(content)
            self.assertIsInstance(root, rfc.RFC)
            self._verify_rfc_txt_dom_middle(root.middle)

    def test_txt_rfc_back(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.txt" , 'r') as fd:
            content = fd.readlines()
            root = npt.parser_rfc_txt.parse_rfc(content)
            self.assertIsInstance(root, rfc.RFC)
            self._verify_rfc_txt_dom_back(root.back)

    def _verify_rfc_dom_root(self, root: rfc.RFC, xml_doc: bool) :
        self.assertIsInstance( root.links, list)
        if isinstance( root.links, list) :  # type-check
            self.assertEqual( len(root.links), 0 )

        self.assertIsInstance( root.front,  rfc.Front )
        self.assertIsNotNone ( root.front)
        self.assertIsInstance( root.middle, rfc.Middle )
        self.assertIsNotNone ( root.middle)
        self.assertIsInstance( root.back,   rfc.Back )
        self.assertIsNotNone ( root.back)

        if xml_doc :
            self.assertEqual ( root.category, "exp")
        else : 
            self.assertIsNone ( root.category)
        self.assertFalse     ( root.consensus)
        self.assertEqual     ( root.docName, "draft-mcquistin-augmented-ascii-diagrams-05")
        self.assertTrue      ( root.indexInclude)
        self.assertEqual     ( root.ipr, 'trust200902')
        self.assertIsNone    ( root.iprExtract)
        self.assertIsNone    ( root.number)
        self.assertIsNone    ( root.obsoletes)
        self.assertIsNone    ( root.prepTime)
        self.assertIsNone    ( root.seriesNo)
        self.assertFalse     ( root.sortRefs)
        self.assertEqual     ( root.submissionType, "IETF")
        self.assertTrue      ( root.symRefs)
        self.assertEqual     ( root.tocDepth,"3")
        self.assertTrue      ( root.tocInclude)
        self.assertIsNone    ( root.updates)
        self.assertEqual     ( root.version, "3")


    def _verify_rfc_txt_dom_front(self, front: rfc.Front):
        # Test whether the title has been parsed correctly
        self.assertIsInstance(front.title, rfc.Title )
        self.assertIsInstance(front.title.content, rfc.Text )
        self.assertIsInstance(front.title.content.content, str )
        self.assertEqual(front.title.content.content,"Describing Protocol Data Units with Augmented Packet Header Diagrams")

        self.assertIsNone(front.title.abbrev)

        # seriesInfo elements
        self.assertIsInstance( front.seriesInfo, list)
        if not isinstance( front.seriesInfo, list) :  #type-check
            return

        self.assertEqual(len(front.seriesInfo), 1)
        self.assertEqual(front.seriesInfo[0].name,   "Internet-Draft")
        self.assertEqual(front.seriesInfo[0].value,  "draft-mcquistin-augmented-ascii-diagrams-05")
        self.assertIsNone(front.seriesInfo[0].status)

        # authors
        self.assertIsInstance(front.authors, list)
        self.assertEqual(len(front.authors), 0)    # Not yet disambiguating authors

        # date
        self.assertIsNone( front.date, rfc.Date)

        # areas
        self.assertIsInstance( front.areas, list)
        if not isinstance( front.areas, list) :  #type-check
            return
        self.assertEqual( len(front.areas), 0)

        # workgroups
        self.assertIsInstance( front.workgroups, list)
        if not isinstance( front.workgroups, list) :  #type-check
            return
        self.assertEqual( len(front.workgroups), 0)

        # keywords
        self.assertIsInstance( front.keywords, list)
        if not isinstance( front.keywords, list) :  #type-check
            return
        self.assertEqual( len(front.keywords), 0)

        # abstract
        self.assertIsNotNone( front.abstract)
        if front.abstract is None : #type-check
            return
        self.assertIsInstance( front.abstract, rfc.Abstract)
        self.assertIsNone( front.abstract.anchor)
        self.assertIsInstance( front.abstract.content, list)
        self.assertEqual( len(front.abstract.content), 1)
        self.assertIsInstance( front.abstract.content[0] , rfc.T)

        # abstract-t element
        self.assertIsInstance( front.abstract.content[0] , rfc.T)
        self.assertIsInstance( front.abstract.content[0].content , list)

        self.assertEqual     ( len(front.abstract.content[0].content) , 1)
        self.assertIsInstance( front.abstract.content[0].content[0] , rfc.Text)
        if not isinstance( front.abstract.content[0].content[0], rfc.Text) :
            return
        self.assertIsInstance( front.abstract.content[0].content[0].content , str)
        self.maxDiff = None 
        self.assertEqual     ( front.abstract.content[0].content[0].content,
"""This document describes a machine-readable format for specifying the
syntax of protocol data units within a protocol specification.  This
format is comprised of a consistently formatted packet header
diagram, followed by structured explanatory text.  It is designed to
maintain human readability while enabling support for automated
parser generation from the specification document.  This document is
itself an example of how the format can be used.
""")


        self.assertIsInstance( front.abstract.content[0], rfc.T)
        if not isinstance( front.abstract.content[0], rfc.T): # type-check
            return
        self.assertIsNone( front.abstract.content[0].anchor)
        self.assertIsNone( front.abstract.content[0].hangText)
        self.assertFalse ( front.abstract.content[0].keepWithNext)
        self.assertFalse ( front.abstract.content[0].keepWithPrevious)


        # notes
        self.assertIsInstance( front.notes, list)
        if not isinstance( front.notes, list) : # type-check
            return
        self.assertEqual( len(front.notes), 0)

        # boilerplate
        self.assertIsNone( front.boilerplate)


    def _verify_rfc_dom_front(self, front: rfc.Front) :
        # Test whether the title has been parsed correctly
        self.assertIsInstance(front.title, rfc.Title )
        self.assertIsInstance(front.title.content, rfc.Text )
        self.assertIsInstance(front.title.content.content, str )
        self.assertEqual(front.title.content.content,"""
            Describing Protocol Data Units with Augmented Packet Header Diagrams
        """)

        self.assertEqual(front.title.abbrev, "Augmented Packet Diagrams")

        # seriesInfo elements
        self.assertIsInstance( front.seriesInfo, list)
        if not isinstance( front.seriesInfo, list) :  #type-check
            return

        self.assertEqual(len(front.seriesInfo), 1)
        self.assertEqual(front.seriesInfo[0].name,   "Internet-Draft")
        self.assertEqual(front.seriesInfo[0].value,  "draft-mcquistin-augmented-ascii-diagrams-05")
        self.assertEqual(front.seriesInfo[0].status, "experimental")

        # authors
        self.assertEqual(len(front.authors), 4)
        #author-0
        self.assertIsNotNone(front.authors[0].org)
        if front.authors[0].org is None : # type-check
            return
        self.assertEqual    ( front.authors[0].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone( front.authors[0].address)
        if front.authors[0].address is None : # type-check
            return

        street: rfc.Street   = rfc.Street(content=rfc.Text("School of Computing Science"), ascii=None)
        city: rfc.City       = rfc.City(content=rfc.Text("Glasgow"), ascii=None)
        code: rfc.Code       = rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None)
        country: rfc.Country = rfc.Country(content=rfc.Text("UK"), ascii=None)
        postal_address : List[Union[rfc.City, rfc.Code, rfc.Country, rfc.Region, rfc.Street]] = [ street, city, code, country ]

        self.assertIsInstance( front.authors[0].address.postal, rfc.Postal)
        self.assertEqual     ( front.authors[0].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( front.authors[0].address.phone)
        self.assertIsNone    ( front.authors[0].address.facsimile)
        self.assertEqual     ( front.authors[0].address.email, rfc.Email(content=rfc.Text("sm@smcquistin.uk"), ascii=None))
        self.assertIsNone    ( front.authors[0].address.uri)
        self.assertIsNone    ( front.authors[0].asciiFullname)
        self.assertIsNone    ( front.authors[0].asciiInitials)
        self.assertIsNone    ( front.authors[0].asciiSurname)
        self.assertEqual     ( front.authors[0].fullname, "Stephen McQuistin")
        self.assertEqual     ( front.authors[0].initials, "S.")
        self.assertEqual     ( front.authors[0].surname,  "McQuistin")
        self.assertIsNone    ( front.authors[0].role)

        #author-1
        self.assertIsNotNone(front.authors[1].org)
        if front.authors[1].org is None : # type-check
            return
        self.assertEqual     ( front.authors[1].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( front.authors[1].address)
        if front.authors[1].address is None : # type-check
            return
        self.assertIsInstance( front.authors[1].address.postal, rfc.Postal)
        self.assertEqual     ( front.authors[1].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( front.authors[1].address.phone)
        self.assertIsNone    ( front.authors[1].address.facsimile)
        self.assertEqual     ( front.authors[1].address.email,rfc.Email(content=rfc.Text("vivianband0@gmail.com"), ascii=None))
        self.assertIsNone    ( front.authors[1].address.uri)
        self.assertIsNone    ( front.authors[1].asciiFullname)
        self.assertIsNone    ( front.authors[1].asciiInitials)
        self.assertIsNone    ( front.authors[1].asciiSurname)
        self.assertEqual     ( front.authors[1].fullname, "Vivian Band")
        self.assertEqual     ( front.authors[1].initials, "V.")
        self.assertEqual     ( front.authors[1].surname,  "Band")
        self.assertIsNone    ( front.authors[1].role)

        #author-2
        self.assertIsNotNone(front.authors[2].org)
        if front.authors[2].org is None : # type-check
            return
        self.assertEqual     ( front.authors[2].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( front.authors[2].address)
        if front.authors[2].address is None : # type-check
            return
        self.assertIsInstance( front.authors[2].address.postal, rfc.Postal)
        self.assertEqual     ( front.authors[2].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( front.authors[2].address.phone)
        self.assertIsNone    ( front.authors[2].address.facsimile)
        self.assertEqual     ( front.authors[2].address.email,rfc.Email(content=rfc.Text("d.jacob.1@research.gla.ac.uk"), ascii=None))
        self.assertIsNone    ( front.authors[2].address.uri)
        self.assertIsNone    ( front.authors[2].asciiFullname)
        self.assertIsNone    ( front.authors[2].asciiInitials)
        self.assertIsNone    ( front.authors[2].asciiSurname)
        self.assertEqual     ( front.authors[2].fullname, "Dejice Jacob")
        self.assertEqual     ( front.authors[2].initials, "D.")
        self.assertEqual     ( front.authors[2].surname,  "Jacob")
        self.assertIsNone    ( front.authors[2].role)

        #author-3
        self.assertIsNotNone(front.authors[3].org)
        if front.authors[3].org is None : # type-check
            return
        self.assertEqual     ( front.authors[3].org.content, rfc.Text(content="University of Glasgow"))
        self.assertIsNotNone ( front.authors[3].address)
        if front.authors[3].address is None : # type-check
            return
        self.assertIsInstance( front.authors[3].address.postal, rfc.Postal)
        self.assertEqual     ( front.authors[3].address.postal, rfc.Postal(postal_address))
        self.assertIsNone    ( front.authors[3].address.phone)
        self.assertIsNone    ( front.authors[3].address.facsimile)
        self.assertEqual     ( front.authors[3].address.email,rfc.Email(content=rfc.Text("csp@csperkins.org"), ascii=None))
        self.assertIsNone    ( front.authors[3].address.uri)
        self.assertIsNone    ( front.authors[3].asciiFullname)
        self.assertIsNone    ( front.authors[3].asciiInitials)
        self.assertIsNone    ( front.authors[3].asciiSurname)
        self.assertEqual     ( front.authors[3].fullname, "Colin Perkins")
        self.assertEqual     ( front.authors[3].initials, "C. S.")
        self.assertEqual     ( front.authors[3].surname,  "Perkins")
        self.assertIsNone    ( front.authors[3].role)

        # date
        self.assertIsNone( front.date, rfc.Date)

        # areas
        self.assertIsInstance( front.areas, list)
        if not isinstance( front.areas, list) :  #type-check
            return
        self.assertEqual( len(front.areas), 0)

        # workgroups
        self.assertIsInstance( front.workgroups, list)
        if not isinstance( front.workgroups, list) :  #type-check
            return
        self.assertEqual( len(front.workgroups), 0)

        # keywords
        self.assertIsInstance( front.keywords, list)
        if not isinstance( front.keywords, list) :  #type-check
            return
        self.assertEqual( len(front.keywords), 0)

        # abstract
        self.assertIsNotNone( front.abstract)
        if front.abstract is None : #type-check
            return
        self.assertIsInstance( front.abstract, rfc.Abstract)
        self.assertIsNone( front.abstract.anchor)
        self.assertIsInstance( front.abstract.content, list)
        self.assertEqual( len(front.abstract.content), 1)
        self.assertIsInstance( front.abstract.content[0] , rfc.T)

        # abstract-t element
        self.assertIsInstance( front.abstract.content[0] , rfc.T)
        self.assertIsInstance( front.abstract.content[0].content , list)

        self.assertEqual     ( len(front.abstract.content[0].content) , 1)
        self.assertIsInstance( front.abstract.content[0].content[0] , rfc.Text)
        if not isinstance( front.abstract.content[0].content[0], rfc.Text) :
            return
        self.assertIsInstance( front.abstract.content[0].content[0].content , str)
        self.assertEqual     ( front.abstract.content[0].content[0].content, """
              This document describes a machine-readable format for specifying
              the syntax of protocol data units within a protocol specification.
              This format is comprised of a consistently formatted packet header
              diagram, followed by structured explanatory text. It is
              designed to maintain human readability while enabling support for
              automated parser generation from the specification document. This
              document is itself an example of how the format can be used.
            """)

        self.assertIsInstance( front.abstract.content[0], rfc.T)
        if not isinstance( front.abstract.content[0], rfc.T): # type-check
            return
        self.assertIsNone( front.abstract.content[0].anchor)
        self.assertIsNone( front.abstract.content[0].hangText)
        self.assertFalse ( front.abstract.content[0].keepWithNext)
        self.assertFalse ( front.abstract.content[0].keepWithPrevious)


        # notes
        self.assertIsInstance( front.notes, list)
        if not isinstance( front.notes, list) : # type-check
            return
        self.assertEqual( len(front.notes), 0)

        # boilerplate
        self.assertIsNone( front.boilerplate)



    def _verify_rfc_dom_back(self, back: rfc.Back):
        self.assertIsInstance(back, rfc.Back)

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

        self.assertEqual(len(back.sections[0].sections[1].content[0].content), 5)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[0].sections[1].content[0].content[0].content, """
                    Future revisions of this draft will include an ABNF specification for
                    the augmented packet diagram format described in
                    """)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[1], rfc.XRef)
        if not isinstance(back.sections[0].sections[1].content[0].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone(back.sections[0].sections[1].content[0].content[1].content)
        self.assertEqual(back.sections[0].sections[1].content[0].content[1].format, "default")
        self.assertFalse(back.sections[0].sections[1].content[0].content[1].pageno)
        self.assertEqual(back.sections[0].sections[1].content[0].content[1].target, "augmentedascii")
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[2], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[2], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[0].sections[1].content[0].content[2].content, """. Such a specification is omitted from
                    this draft given that the format is likely to change as its syntax is
                    developed. Given the visual nature of the format, it is more
                    appropriate for discussion to focus on the examples given in
                    """)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[3], rfc.XRef)
        if not isinstance(back.sections[0].sections[1].content[0].content[3], rfc.XRef): # type-check
            return
        self.assertIsNone(back.sections[0].sections[1].content[0].content[3].content)
        self.assertEqual(back.sections[0].sections[1].content[0].content[3].format, "default")
        self.assertFalse(back.sections[0].sections[1].content[0].content[3].pageno)
        self.assertEqual(back.sections[0].sections[1].content[0].content[3].target, "augmentedascii")
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[4], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[4], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[0].sections[1].content[0].content[4].content, """.
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
        self.assertEqual(len(back.sections[1].content[0].content), 3)
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
        self.assertEqual(len(back.sections[1].content[1].content), 3)
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

    def _verify_rfc_txt_dom_back(self, back: rfc.Back):
        self.assertIsInstance(back, rfc.Back)

        # displayrefs
        self.assertIsInstance(back.displayrefs, list)
        if not isinstance(back.displayrefs, list):  # type-check
            return
        self.assertEqual(len(back.displayrefs), 0)   # parser not parsing this yet

        # references
        self.assertIsInstance(back.refs, list)
        if not isinstance( back.refs, list) : # type-check
            return
        self.assertEqual(len(back.refs), 0)   # parser not parsing this yet

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
        self.assertEqual(len(back.sections[0].sections[0].content), 4)
        # section-00 -- (sub) section 00 -- content[0] <T>
        self.assertIsInstance(back.sections[0].sections[0].content[0], rfc.T)
        if not isinstance(back.sections[0].sections[0].content[0], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].content[0].content, list)
        self.assertEqual(len(back.sections[0].sections[0].content[0].content), 1)
        self.assertIsInstance(back.sections[0].sections[0].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[0].content[0].content[0], rfc.Text): # type check
            return
        self.assertEqual(back.sections[0].sections[0].content[0].content[0].content,
"""cond-expr = eq-expr "?" cond-expr ":" eq-expr
eq-expr   = bool-expr eq-op   bool-expr
bool-expr = ord-expr  bool-op ord-expr
ord-expr  = add-expr  ord-op  add-expr
""")
        # section-00 -- (sub) section 00 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[0].sections[0].content[0].anchor)
        self.assertIsNone( back.sections[0].sections[0].content[0].hangText)
        self.assertFalse( back.sections[0].sections[0].content[0].keepWithNext)
        self.assertFalse( back.sections[0].sections[0].content[0].keepWithPrevious)

        # section-00 -- (sub) section 00 -- content[1] <T>
        self.assertIsInstance(back.sections[0].sections[0].content[1], rfc.T)
        if not isinstance(back.sections[0].sections[0].content[1], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].content[1].content, list)
        self.assertEqual(len(back.sections[0].sections[0].content[1].content), 1)
        self.assertIsInstance(back.sections[0].sections[0].content[1].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[0].content[1].content[0], rfc.Text): # type-check 
            return
        self.assertEqual(back.sections[0].sections[0].content[1].content[0].content,
"""add-expr  = mul-expr  add-op  mul-expr
mul-expr  = pow-expr  mul-op  pow-expr
pow-expr  = expr      pow-op  expr
expr      = *DIGIT / field-name /
field-name-ws / "(" expr ")"
""")
        # section-00 -- (sub) section 00 -- content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[0].sections[0].content[1].anchor)
        self.assertIsNone( back.sections[0].sections[0].content[1].hangText)
        self.assertFalse( back.sections[0].sections[0].content[1].keepWithNext)
        self.assertFalse( back.sections[0].sections[0].content[1].keepWithPrevious)

        # section-00 -- (sub) section 00 -- content[2] <T>
        self.assertIsInstance(back.sections[0].sections[0].content[2], rfc.T)
        if not isinstance(back.sections[0].sections[0].content[2], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].content[2].content, list)
        self.assertEqual(len(back.sections[0].sections[0].content[2].content), 1)
        self.assertIsInstance(back.sections[0].sections[0].content[2].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[0].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[0].sections[0].content[2].content[0].content,
"""field-name    = ALPHA *(ALPHA / DIGIT)
field-name-ws = *(field-name " ")
""")
        # section-00 -- (sub) section 00 -- content[2] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[0].sections[0].content[2].anchor)
        self.assertIsNone( back.sections[0].sections[0].content[2].hangText)
        self.assertFalse( back.sections[0].sections[0].content[2].keepWithNext)
        self.assertFalse( back.sections[0].sections[0].content[2].keepWithPrevious)

        # section-00 -- (sub) section 00 -- content[3] <T>
        self.assertIsInstance(back.sections[0].sections[0].content[3], rfc.T)
        if not isinstance(back.sections[0].sections[0].content[3], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[0].content[3].content, list)
        self.assertEqual(len(back.sections[0].sections[0].content[3].content), 1)
        self.assertIsInstance(back.sections[0].sections[0].content[3].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[0].content[3].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[0].sections[0].content[3].content[0].content,
"""pow-op  = "^"
mul-op  = "*" / "/" / "%"
add-op  = "+" / "-"
ord-op  = "<=" / "<" / ">=" / ">"
bool-op = "&&" / "||" / "!"
eq-op   = "==" / "!="
""")

        # section-00 -- (sub) section 00 -- content[3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[0].sections[0].content[3].anchor)
        self.assertIsNone( back.sections[0].sections[0].content[3].hangText)
        self.assertFalse( back.sections[0].sections[0].content[3].keepWithNext)
        self.assertFalse( back.sections[0].sections[0].content[3].keepWithPrevious)

        # section-00 -- (sub) section 00 anchor, numbered, removeInRFC, title, toc
        self.assertIsInstance( back.sections[0].sections[0].sections, list)
        if not isinstance( back.sections[0].sections[0].sections, list): # type-check
            return
        self.assertEqual( len(back.sections[0].sections[0].sections), 0 )
        # section-00 -- (sub) section 00 anchor, numbered, removeInRFC, title, toc
        self.assertIsNone( back.sections[0].sections[0].anchor)
        self.assertTrue(back.sections[0].sections[0].numbered)
        self.assertFalse(back.sections[0].sections[0].removeInRFC)
        self.assertIsNone(back.sections[0].sections[0].title)
        self.assertEqual(back.sections[0].sections[0].toc, "default" )


        # section-00 -- (sub) section 01
        self.assertIsInstance(back.sections[0].sections[1], rfc.Section)
        # section-00 -- (sub) section 01 name
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
        # section-00 -- (sub) section 00 -- content[0] <T>
        self.assertIsInstance(back.sections[0].sections[1].content[0], rfc.T)
        if not isinstance(back.sections[0].sections[1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[0].sections[1].content[0].content, list)
        self.assertEqual(len(back.sections[0].sections[1].content[0].content), 1)
        self.assertIsInstance(back.sections[0].sections[1].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[0].sections[1].content[0].content[0], rfc.Text): # type-check 
            return
        self.assertEqual(back.sections[0].sections[1].content[0].content[0].content,
"""Future revisions of this draft will include an ABNF specification for
the augmented packet diagram format described in Section 4.  Such a
specification is omitted from this draft given that the format is
likely to change as its syntax is developed.  Given the visual nature
of the format, it is more appropriate for discussion to focus on the
examples given in Section 4.
""")
        # section-00 -- (sub) section 01 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[0].sections[1].content[0].anchor)
        self.assertIsNone( back.sections[0].sections[1].content[0].hangText)
        self.assertFalse( back.sections[0].sections[1].content[0].keepWithNext)
        self.assertFalse( back.sections[0].sections[1].content[0].keepWithPrevious)

        # section-00 -- (sub) section 01 sections
        self.assertIsInstance( back.sections[0].sections[1].sections, list)
        if not isinstance( back.sections[0].sections[1].sections, list): # type-check
            return
        self.assertEqual( len(back.sections[0].sections[1].sections), 0)

        # section-00 --(sub)  section 01 anchor, numbered, removeInRFC, title, toc
        self.assertIsNone( back.sections[0].sections[1].anchor)
        self.assertTrue(back.sections[0].sections[1].numbered)
        self.assertFalse(back.sections[0].sections[1].removeInRFC)
        self.assertIsNone(back.sections[0].sections[1].title)
        self.assertEqual(back.sections[0].sections[1].toc, "default" )


        # section-00 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(back.sections[0].anchor)
        self.assertTrue(back.sections[0].numbered)
        self.assertFalse(back.sections[0].removeInRFC)
        self.assertIsNone(back.sections[0].title)
        self.assertEqual(back.sections[0].toc, "default" )

        # section-01 name
        self.assertIsInstance(back.sections[1].name, rfc.Name)
        if not isinstance(back.sections[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(back.sections[1].name.content, list)
        self.assertEqual(len(back.sections[1].name.content), 1)
        self.assertIsInstance(back.sections[1].name.content[0], rfc.Text)
        self.assertEqual(back.sections[1].name.content[0].content, "Source code repository")

        # section-01 -- content
        self.assertIsInstance( back.sections[1].content, list)
        self.assertEqual( len(back.sections[1].content), 2)
        # section-01 -- content[0] <T>
        self.assertIsInstance(back.sections[1].content[0], rfc.T)
        if not isinstance(back.sections[1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[1].content[0].content, list)
        self.assertEqual(len(back.sections[1].content[0].content), 1)
        self.assertIsInstance(back.sections[1].content[0].content[0], rfc.Text)
        if not isinstance(back.sections[1].content[0].content[0], rfc.Text):  # type-check
             return
        self.assertEqual(back.sections[1].content[0].content[0].content,
"""The source for this draft is available from https://github.com/
glasgow-ipl/draft-mcquistin-augmented-ascii-diagrams.
""")
        # section-01 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[1].content[0].anchor)
        self.assertIsNone( back.sections[1].content[0].hangText)
        self.assertFalse( back.sections[1].content[0].keepWithNext)
        self.assertFalse( back.sections[1].content[0].keepWithPrevious)

        # section-01 -- content[1] <T>
        self.assertIsInstance(back.sections[1].content[1], rfc.T)
        if not isinstance(back.sections[1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance(back.sections[1].content[1].content, list)
        self.assertEqual(len(back.sections[1].content[1].content), 1)
        self.assertIsInstance(back.sections[1].content[1].content[0], rfc.Text)
        if not isinstance(back.sections[1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual(back.sections[1].content[1].content[0].content,
"""The source code for tooling that can be used to parse this document
is available from https://github.com/glasgow-ipl/ips-protodesc-code.
""")
        # section-00 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( back.sections[1].content[1].anchor)
        self.assertIsNone( back.sections[1].content[1].hangText)
        self.assertFalse( back.sections[1].content[1].keepWithNext)
        self.assertFalse( back.sections[1].content[1].keepWithPrevious)

        # section-01 -- sections
        self.assertIsInstance( back.sections[1].sections, list)
        if not isinstance( back.sections[1].sections, list): # type-check
            return
        self.assertEqual( len(back.sections[1].sections), 0)
        # section-01 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(back.sections[1].anchor)
        self.assertTrue(back.sections[1].numbered)
        self.assertFalse(back.sections[1].removeInRFC)
        self.assertIsNone(back.sections[1].title)
        self.assertEqual(back.sections[1].toc, "default" )



    def _verify_rfc_middle(self, middle: rfc.Middle):
        self.assertIsNotNone(middle.content)
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
        self.assertEqual( len(middle.content[0].content[0].content), 1)
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
        self.assertEqual( len(middle.content[0].content[1].content), 3)
        self.assertIsInstance( middle.content[0].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[0].content[1].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[0].content[1].content[0].content, """
                """)
        self.assertIsInstance( middle.content[0].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[0].content[1].content[1], rfc.XRef):  #type-check
            return
        self.assertIsNone( middle.content[0].content[1].content[1].content)
        self.assertEqual( middle.content[0].content[1].content[1].format, "default")
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
        self.assertEqual( middle.content[0].content[2].name.content[1].format, "default")
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
        self.assertEqual( len(middle.content[0].content[3].content), 1)
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
        self.assertEqual( len(middle.content[0].content[4].content), 1)
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
        self.assertEqual( len(middle.content[0].content[5].content), 1)
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
        self.assertEqual( len(middle.content[0].content[6].content), 5)
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
        self.assertEqual( middle.content[0].content[6].content[1].format, "default")
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
        self.assertEqual( middle.content[0].content[6].content[3].format, "default")
        self.assertFalse( middle.content[0].content[6].content[3].pageno)
        self.assertEqual( middle.content[0].content[6].content[3].target, "source")
        self.assertIsInstance( middle.content[0].content[6].content[4], rfc.Text)
        if not isinstance( middle.content[0].content[6].content[4], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[0].content[6].content[4].content, """) that
                parses it (and, as described above, this document) will be provided.
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
        self.assertEqual( len(middle.content[1].content[0].content), 1) 
        self.assertIsInstance( middle.content[1].content[0].content[0], rfc.Text) 
        if not isinstance( middle.content[1].content[0].content[0], rfc.Text) : # type-check
            return
        self.assertEqual( middle.content[1].content[0].content[0].content, """
                This section begins by considering how packet header diagrams are
                used in existing documents. This exposes the limitations that the current
                usage has in terms of machine-readability, guiding the design of the
                format that this document proposes.
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
        self.assertEqual( len(middle.content[1].content[1].content), 1) 
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
        self.assertEqual( middle.content[1].sections[0].content[0].name.content[1].format, "default")
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
        self.assertEqual( len(middle.content[1].sections[0].content[1].content), 3)
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
        self.assertEqual( middle.content[1].sections[0].content[1].content[1].format, "default")
        self.assertFalse( middle.content[1].sections[0].content[1].content[1].pageno)
        self.assertEqual( middle.content[1].sections[0].content[1].content[1].target, "quic-reset-stream")
        self.assertIsInstance( middle.content[1].sections[0].content[1].content[2], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[1].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[1].content[2].content, """.
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
        self.assertEqual( len(middle.content[1].sections[0].content[2].content), 1)
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
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content), 3)
        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[0] <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[0].content), 1)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[0].content[0].content, """
                      There are two classes of consistency that are needed to support
                      automated processing of specifications: internal consistency
                      within a diagram or document, and external consistency across
                      all documents.
                    """)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[0].keepWithPrevious)

        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[1] <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[1].content), 7)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[0].content, """
                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].content)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[1].format, "default")
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
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[3].format, "default")
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
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[1].content[5].format, "default")
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
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[1].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[0][1].content[1].keepWithPrevious)

        # sec-01  sub-sec[0] content[3] <DL> content[0] <tuple<DT,DD>>  [1] <DD> content[2] <T> 
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[0][1].content[2].content), 5)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[0].content, """
                        Comparing """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].content)
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[1].format, "default")
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
        self.assertEqual( middle.content[1].sections[0].content[3].content[0][1].content[2].content[3].format, "default")
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
        self.assertEqual( middle.content[1].sections[0].content[3].content[1][1].content[1].format, "default")
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
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][1].content[0].content), 1)
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
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[0].hangText)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[0].keepWithNext)
        self.assertFalse( middle.content[1].sections[0].content[3].content[2][1].content[0].keepWithPrevious)
        # sec-01  sub-sec[0] content[3] <DL> content[2] <tuple<DT,DD>>  [1] <DD> [1] <T>
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1], rfc.T)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[2][1].content[1].content), 3)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0], rfc.Text): # type-check 
            return
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[0].content, """
                        """)
        self.assertIsInstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1], rfc.XRef)
        if not isinstance( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].content)
        self.assertEqual( middle.content[1].sections[0].content[3].content[2][1].content[1].content[1].format, "default")
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
        self.assertEqual( len(middle.content[1].sections[0].content[3].content[3][1].content[0].content), 3)
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
        self.assertEqual( middle.content[1].sections[0].content[3].content[3][1].content[0].content[1].format, "default")
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
        self.assertEqual( middle.content[1].sections[0].content[4].name.content[1].format, "default")
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
        self.assertIsInstance( middle.content[1].sections[1].content[0], rfc.T)
        if not isinstance( middle.content[1].sections[1].content[0], rfc.T): # type-check
            return
        self.assertIsInstance( middle.content[1].sections[1].content[0].content, list)
        self.assertEqual( len(middle.content[1].sections[1].content[0].content), 11)
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
        self.assertEqual( middle.content[1].sections[1].content[0].content[1].format, "default")
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
        self.assertEqual( middle.content[1].sections[1].content[0].content[3].format, "default")
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
        self.assertEqual( middle.content[1].sections[1].content[0].content[5].format, "default")
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
        self.assertEqual( middle.content[1].sections[1].content[0].content[7].format, "default")
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
        self.assertEqual( middle.content[1].sections[1].content[0].content[9].format, "default")
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
        self.assertEqual( len(middle.content[2].content[0].content), 1)
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
        self.assertEqual( len(middle.content[2].content[1].content), 1)
        self.assertIsInstance( middle.content[2].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[1].content[0].content, """
                In this section, the broad design principles that underpin the format
                described by this document are given. However, these principles apply more
                generally to any approach that introduces structured and formal languages
                into standards documents.
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
        self.assertEqual( len(middle.content[2].content[2].content), 1)
        self.assertIsInstance( middle.content[2].content[2].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[2].content[0], rfc.Text):  # type-check
            return
        self.assertEqual( middle.content[2].content[2].content[0].content, """
                It should be noted that these are design principles: they expose the
                trade-offs that are inherent within any given approach. Violating these
                principles is sometimes necessary and beneficial, and this document sets
                out the potential consequences of doing so.
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
        self.assertEqual( len(middle.content[2].content[3].content), 1)
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
        self.assertEqual( len(middle.content[2].content[4].content[0][1].content[0].content), 1)
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
        self.assertEqual( len(middle.content[2].content[4].content[0][1].content[1].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[0][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[0][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[0][1].content[1].content[0].content, """
                        Any approach that shifts this balance -- that is, that primarily
                        targets machine readers -- is likely to be disruptive to the
                        standardisation process, which relies upon discussion centered
                        around documents written in prose.
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
        self.assertEqual( len(middle.content[2].content[4].content[1][1].content[0].content), 1)
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
        self.assertEqual( len(middle.content[2].content[4].content[1][1].content[1].content), 1)
        self.assertIsInstance( middle.content[2].content[4].content[1][1].content[1].content[0], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[1][1].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[1][1].content[1].content[0].content, """
                        The immediate impact of requiring specific tooling is that
                        adoption is likely to be limited. A long-term impact might be that
                        authors whose workflows are incompatible might be alienated from
                        the process.
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
        self.assertEqual( len(middle.content[2].content[4].content[2][1].content[0].content), 1)
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
        self.assertEqual( len(middle.content[2].content[4].content[2][1].content[1].content), 1)
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
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[0].content), 1)
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
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[0].anchor)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[0].hangText)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[0].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[0].keepWithPrevious)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [1] <T>
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[1], rfc.T)
        if not isinstance( middle.content[2].content[4].content[3][1].content[1], rfc.T): # type-check
             return
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[1].content), 3)
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
        self.assertEqual( middle.content[2].content[4].content[3][1].content[1].content[1].format, "default")
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
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [1] <T> anchor, handText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].anchor)
        self.assertIsNone( middle.content[2].content[4].content[3][1].content[1].hangText)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[1].keepWithNext)
        self.assertFalse( middle.content[2].content[4].content[3][1].content[1].keepWithPrevious)
        # sec-02 content[4] <DL> content[3] <Tuple<DT,DL> [1] <DD> content [2] <T>
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2], rfc.T)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2], rfc.T): # type-check
            return
        self.assertEqual( len(middle.content[2].content[4].content[3][1].content[2].content), 3)
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
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[1].format, "default")
        self.assertFalse( middle.content[2].content[4].content[3][1].content[2].content[1].pageno)
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[1].target, """SASSAMAN""")
        self.assertIsInstance( middle.content[2].content[4].content[3][1].content[2].content[2], rfc.Text)
        if not isinstance( middle.content[2].content[4].content[3][1].content[2].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[2].content[4].content[3][1].content[2].content[2].content, """.
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
        self.assertEqual( len(middle.content[2].content[4].content[4][1].content[0].content), 1)
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
        self.assertEqual( len(middle.content[3].content[0].content), 3) 
        self.assertIsInstance( middle.content[3].content[0].content[0], rfc.Text )
        if not isinstance( middle.content[3].content[0].content[0], rfc.Text ): # type-check
            return
        self.assertEqual( middle.content[3].content[0].content[0].content, """
                The design principles described in """)
        self.assertIsInstance( middle.content[3].content[0].content[1], rfc.XRef )
        if not isinstance( middle.content[3].content[0].content[1], rfc.XRef ): # type-check
            return
        self.assertIsNone( middle.content[3].content[0].content[1].content)
        self.assertEqual( middle.content[3].content[0].content[1].format, "default")
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
        self.assertEqual( len(middle.content[3].content[1].content), 3) 
        self.assertIsInstance( middle.content[3].content[1].content[0], rfc.Text )
        if not isinstance( middle.content[3].content[1].content[0], rfc.Text ): # type-check
            return
        self.assertEqual( middle.content[3].content[1].content[0].content, """
                However, as discussed in """)
        self.assertIsInstance( middle.content[3].content[1].content[1], rfc.XRef )
        if not isinstance( middle.content[3].content[1].content[1], rfc.XRef ): # type-check
            return
        self.assertIsNone( middle.content[3].content[1].content[1].content)
        self.assertEqual( middle.content[3].content[1].content[1].format, "default")
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
        # sec-03 content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].content[1].anchor) 
        self.assertIsNone( middle.content[3].content[1].hangText)
        self.assertFalse( middle.content[3].content[1].keepWithNext)
        self.assertFalse( middle.content[3].content[1].keepWithPrevious)

        # sec-03 content[2] <T>
        self.assertIsInstance( middle.content[3].content[2], rfc.T) 
        if not isinstance( middle.content[3].content[2], rfc.T) : # type-check
            return
        # sec-03 content[2] <T> content
        self.assertIsInstance( middle.content[3].content[2].content, list) 
        self.assertEqual( len(middle.content[3].content[2].content), 3) 
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
        self.assertEqual( middle.content[3].content[2].content[1].format, "default")
        self.assertFalse( middle.content[3].content[2].content[1].pageno)
        self.assertEqual( middle.content[3].content[2].content[1].target, """ABNF""")
        self.assertIsInstance( middle.content[3].content[2].content[2], rfc.Text )
        if not isinstance( middle.content[3].content[2].content[2], rfc.Text ):
            return
        self.assertEqual( middle.content[3].content[2].content[2].content, """.
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
        self.assertEqual( len(middle.content[3].sections[0].content[0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[0].content[0], rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[0].content[0].content[0].content, """
                  The simplest PDU is one that contains only a set of fixed-width
                  fields in a known order, with no optional fields or variation
                  in the packet format.
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
        self.assertEqual( len(middle.content[3].sections[0].content[1].content), 1)
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
        self.assertEqual( len(middle.content[3].sections[0].content[2].content), 1)
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
        self.assertEqual( len(middle.content[3].sections[0].content[3].content), 1)
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
        self.assertEqual( len(middle.content[3].sections[0].content[4].content), 3)
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[4].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[4].content[0].content, """
                  PDU names must be unique, both within a document, and across
                  all documents that are linked together (i.e., using the
                  structured language defined in """)
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[1], rfc.XRef)
        if not isinstance( middle.content[3].sections[0].content[4].content[1], rfc.XRef): # type-check
            return
        self.assertIsNone( middle.content[3].sections[0].content[4].content[1].content)
        self.assertEqual( middle.content[3].sections[0].content[4].content[1].format, "default")
        self.assertFalse( middle.content[3].sections[0].content[4].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[4].content[1].target, """ascii-import""")
        self.assertIsInstance( middle.content[3].sections[0].content[4].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[4].content[2], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[4].content[2].content, """).
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
        self.assertEqual( len(middle.content[3].sections[0].content[5].content), 3)
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
        self.assertEqual( middle.content[3].sections[0].content[5].content[1].format, "default")
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
        self.assertEqual( len(middle.content[3].sections[0].content[6].content), 3)
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
        self.assertEqual( middle.content[3].sections[0].content[6].content[1].format, "default")
        self.assertFalse( middle.content[3].sections[0].content[6].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[6].content[1].target, """RFC791""")
        self.assertIsInstance( middle.content[3].sections[0].content[6].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[6].content[2], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[6].content[2].content,
                """. An IPv4 Header is formatted
                 as follows:
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
        self.assertEqual( len(middle.content[3].sections[0].content[8].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[8].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[8].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[8].content[0].content, """
                    where:
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

        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[0][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[0][0].content[0], rfc.Text): # type-check
             return 
        self.assertEqual( middle.content[3].sections[0].content[9].content[0][0].content[0].content, """
                        Version (V): 4 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[0][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>> [0] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[0][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][1].content[0], rfc.T)
        if not isinstance( middle.content[3].sections[0].content[9].content[0][1].content[0], rfc.T): # type-check
            return
        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>> [0] <DD> content[0] <T> content
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][1].content[0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[0][1].content[0].content), 1)
        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>> [0] <DD> content[0] <T> content[0]
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[0][1].content[0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[0][1].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[0][1].content[0].content[0].content, """
                            This is a fixed-width field, whose full label is shown
                            in the diagram. The field's width -- 4 bits -- is given
                            in the label of the description list, separated from the
                            field's label by a colon.
                        """)
        # sec-03 sub-sec[0] content [9] <DL> content [0] <Tuple<DL,DD>> [0] <DD> content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[3].sections[0].content[9].content[0][1].content[0].anchor)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[0][1].content[0].hangText)
        self.assertFalse( middle.content[3].sections[0].content[9].content[0][1].content[0].keepWithNext)
        self.assertFalse( middle.content[3].sections[0].content[9].content[0][1].content[0].keepWithPrevious)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[0][1].anchor)


        # sec-03 sub-sec[0] content [9] <DL> content [1] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [1] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[1][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[1][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[1][0].content[0].content, """
                        Internet Header Length (IHL): 4 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[1][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [1] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[1][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[1][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[1][1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[1][1].content[0].content, """
                        This is a shorter field, whose full label is too large to be
                        shown in the diagram. A short label (IHL) is used in the diagram, and this
                        short label is provided, in brackets, after the full label
                        in the description list.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[1][1].anchor)


        # sec-03 sub-sec[0] content [9] <DL> content [2] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [2] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[2][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[2][0].content[0], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[3].sections[0].content[9].content[2][0].content[0].content, """
                        Differentiated Services Code Point (DSCP): 6 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[2][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [2] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[2][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[2][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[2][1].content[0], rfc.Text): # typecheck
             return
        self.assertEqual( middle.content[3].sections[0].content[9].content[2][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[2][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [3] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [3] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[3][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[3][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[3][0].content[0].content, """
                        Explicit Congestion Notification (ECN): 2 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[3][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [3] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[3][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[3][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[3][1].content[0], rfc.Text): # type-check
             return
        self.assertEqual( middle.content[3].sections[0].content[9].content[3][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[3][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [4] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [4] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[4][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[4][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[4][0].content[0].content, """
                        Total Length (TL): 2 bytes.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[4][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [4] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[4][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[4][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[4][1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[4][1].content[0].content, """
                        This is a fixed-width field, as previously discussed. Where
                        fields are an integral number of bytes in size, the field
                        length can be given in bytes rather than in bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[4][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [5] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [5] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[5][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[5][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[5][0].content[0].content, """
                        Identification: 2 bytes.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[5][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [5] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[5][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[5][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[5][1].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[5][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[5][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [6] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [6] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[6][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[6][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[6][0].content[0].content, """
                        Flags: 3 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[6][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [6] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[6][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[6][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[6][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[6][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[6][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [7] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [7] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[7][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[7][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[7][0].content[0].content, """
                        Fragment Offset: 13 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[7][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [7] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[7][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[7][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[7][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[7][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[7][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [8] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [8] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[8][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[8][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[8][0].content[0].content, """
                        Time to Live (TTL): 1 byte.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[8][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [8] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[8][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[8][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[8][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[8][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[8][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [9] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [9] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[9][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[9][0].content[0], rfc.Text): # type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[9][0].content[0].content, """
                        Protocol: 1 byte.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[9][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [9] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[9][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[9][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[9][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[9][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[9][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [10] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [10] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[10][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[10][0].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[10][0].content[0].content, """
                        Header Checksum: 2 bytes.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[10][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [10] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[10][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[10][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[10][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[10][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[10][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [11] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [11] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[11][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[11][0].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[11][0].content[0].content, """
                        Source Address: 32 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[11][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [11] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[11][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[11][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[11][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[11][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[11][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [12] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [12] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[12][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[12][0].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[12][0].content[0].content, """
                        Destination Address: 32 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[12][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [12] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[12][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[12][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[12][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[12][1].content[0].content, """
                        This is a fixed-width field, as previously discussed.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[12][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [13] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [13] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[13][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[13][0].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[13][0].content[0].content, """
                        Options: (IHL-5)*32 bits.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[13][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [13] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[13][1].content), 3)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[13][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[13][1].content[0].content, """
                      This is a variable-length field, whose length is defined
                      by the value of the field with short label IHL (Internet
                      Header Length).  Constraint expressions can be used in place of
                      constant values: the grammar for the expression language is
                      defined in """)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][1].content[1], rfc.XRef)
        if not isinstance( middle.content[3].sections[0].content[9].content[13][1].content[1], rfc.XRef):# type-check
            return
        self.assertIsNone( middle.content[3].sections[0].content[9].content[13][1].content[1].content)
        self.assertEqual( middle.content[3].sections[0].content[9].content[13][1].content[1].format, "default")
        self.assertFalse( middle.content[3].sections[0].content[9].content[13][1].content[1].pageno)
        self.assertEqual( middle.content[3].sections[0].content[9].content[13][1].content[1].target, """ABNF-constraints""")
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[13][1].content[2], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[13][1].content[2], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[13][1].content[2].content,
                    """. Constraints can
                      include a previously defined field's short or full label, where one has been
                      defined. Short variable-length fields are indicated by "..."
                      instead of a pipe at the end of the row.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[13][1].anchor)



        # sec-03 sub-sec[0] content [9] <DL> content [14] <Tuple<DL,DD>>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14], tuple)
        # sec-03 sub-sec[0] content [9] <DL> content [14] <Tuple<DL,DD>> [0] <DT>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][0], rfc.DT)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][0].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[14][0].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][0].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[14][0].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[14][0].content[0].content, """
                        Payload: TL - ((IHL*32)/8) bytes.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[14][0].anchor)
        # sec-03 sub-sec[0] content [9] <DL> content [12] <Tuple<DL,DD>> [1] <DD>
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][1], rfc.DD)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][1].content, list)
        self.assertEqual( len(middle.content[3].sections[0].content[9].content[14][1].content), 1)
        self.assertIsInstance( middle.content[3].sections[0].content[9].content[14][1].content[0], rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[9].content[14][1].content[0], rfc.Text):# type-check
            return
        self.assertEqual( middle.content[3].sections[0].content[9].content[14][1].content[0].content, """
                      This is a multi-row variable-length field, constrained by
                      the values of fields TL and IHL.  Instead of the "..." notation,
                      ":" is used to indicate that the field is variable-length.
                      The use of ":" instead of "..." indicates the field is likely
                      to be a longer, multi-row field.  However, semantically, there
                      is no difference: these different notations are for the benefit
                      of human readers.
                    """)
        self.assertIsNone( middle.content[3].sections[0].content[9].content[14][1].anchor)


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
        # sec-03  sub-sec[1] anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[3].sections[1].anchor, "ascii-xref")
        self.assertTrue(middle.content[3].sections[1].numbered)
        self.assertFalse(middle.content[3].sections[1].removeInRFC)
        self.assertIsNone(middle.content[3].sections[1].title)
        self.assertEqual(middle.content[3].sections[1].toc, "default")


        # sec-03 sub-sec[2] 
        self.assertIsInstance( middle.content[3].sections[2], rfc.Section)
        # ...... 
        # sec-03 sub-sec[3] 
        self.assertIsInstance( middle.content[3].sections[3], rfc.Section)
        # ...... 
        # sec-03 sub-sec[4] 
        self.assertIsInstance( middle.content[3].sections[4], rfc.Section)
        # ...... 
        # sec-03 sub-sec[5] 
        self.assertIsInstance( middle.content[3].sections[5], rfc.Section)
        # ...... 
        # sec-03 sub-sec[6] 
        self.assertIsInstance( middle.content[3].sections[6], rfc.Section)
        # ...... 
        # sec-03 sub-sec[7] 
        self.assertIsInstance( middle.content[3].sections[7], rfc.Section)
        # ...... 
        # sec-03 sub-sec[8] 
        self.assertIsInstance( middle.content[3].sections[8], rfc.Section)
        # ...... 
        # sec-03 sub-sec[9] 
        self.assertIsInstance( middle.content[3].sections[9], rfc.Section)
        # ...... 


        # sec-03  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[3].anchor, "augmentedascii")
        self.assertTrue(middle.content[3].numbered)
        self.assertFalse(middle.content[3].removeInRFC)
        self.assertIsNone(middle.content[3].title)
        self.assertEqual(middle.content[3].toc, "default" )
        # ...



        # sec-04
        self.assertIsInstance(middle.content[4], rfc.Section)
        # sec-04  name 
        self.assertIsInstance(middle.content[4].name, rfc.Name)
        if not isinstance(middle.content[4].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[4].name.content, list)
        self.assertEqual(len(middle.content[4].name.content), 1)
        self.assertIsInstance(middle.content[4].name.content[0], rfc.Text)
        self.assertEqual(middle.content[4].name.content[0].content, "Open Issues")
        # sec-04  content 
        self.assertIsInstance(middle.content[4].content, list)
        self.assertEqual(len(middle.content[4].content), 1)
        # sec-04  content [0] <UL> 
        self.assertIsInstance(middle.content[4].content[0], rfc.UL)
        if not isinstance(middle.content[4].content[0], rfc.UL): # type-check
            return
        # sec-04  content [0] <UL> content 
        self.assertIsInstance(middle.content[4].content[0].content, list)
        self.assertEqual(len(middle.content[4].content[0].content), 3)
        # sec-04  content [0] <UL> content [0] <LI>
        self.assertIsInstance(middle.content[4].content[0].content[0], rfc.LI)
        self.assertIsInstance(middle.content[4].content[0].content[0].content, list)
        self.assertEqual(len(middle.content[4].content[0].content[0].content), 1)
        self.assertIsInstance(middle.content[4].content[0].content[0].content[0], rfc.Text)
        if not isinstance(middle.content[4].content[0].content[0].content[0], rfc.Text): # type-check
            return
        self.assertEqual(middle.content[4].content[0].content[0].content[0].content, """
              Need a simple syntax for defining a list of identical objects,
              and a way of referring to the size of the enclosing packet.
              The format cannot currently represent RFC 6716 section 3.2.3,
              and should be able to (the underlying type system can do so).
            """)
        self.assertIsNone(middle.content[4].content[0].content[0].anchor)
        # sec-04  content [0] <UL> content [1] <LI>
        self.assertIsInstance(middle.content[4].content[0].content[1], rfc.LI)
        self.assertIsInstance(middle.content[4].content[0].content[1].content, list)
        self.assertEqual(len(middle.content[4].content[0].content[1].content), 1)
        self.assertIsInstance(middle.content[4].content[0].content[1].content[0], rfc.Text)
        if not isinstance(middle.content[4].content[0].content[1].content[0], rfc.Text): # type-check
            return
        self.assertEqual(middle.content[4].content[0].content[1].content[0].content, """
              Need some discussion about the checks that the tooling might
              perform, and the implications of those checks. For example,
              the tooling checks for consistency between the diagram and
              the description list of fields, ensuring that fields match
              by name and width. -01 of this draft had a field that
              mismatched because of case: is this something that the
              tooling should identify? More broadly, what is the trade-off
              between the rigour that the tooling can enforce, and the
              flexibility desired/needed by authors?
            """)
        self.assertIsNone(middle.content[4].content[0].content[1].anchor)
        # sec-04  content [0] <UL> content [2] <LI>
        self.assertIsInstance(middle.content[4].content[0].content[2], rfc.LI)
        self.assertIsInstance(middle.content[4].content[0].content[2].content, list)
        self.assertEqual(len(middle.content[4].content[0].content[2].content), 1)
        self.assertIsInstance(middle.content[4].content[0].content[2].content[0], rfc.Text)
        if not isinstance(middle.content[4].content[0].content[2].content[0], rfc.Text): # type-check
            return
        self.assertEqual(middle.content[4].content[0].content[2].content[0].content, """
              Need to describe the rules governing the import of PDU definitions
              from other documents.
            """)
        self.assertIsNone(middle.content[4].content[0].content[2].anchor)
        # sec-04  content [0] <UL> anchor, empty, spacing
        self.assertIsInstance(middle.content[4].content[0], rfc.UL)
        self.assertIsNone(middle.content[4].content[0].anchor) 
        self.assertFalse(middle.content[4].content[0].empty) 
        self.assertEqual(middle.content[4].content[0].spacing, "normal") 

        # sec-04  sections 
        self.assertIsInstance(middle.content[4].sections, list)
        if not isinstance(middle.content[4].sections, list): # type-check
            return
        self.assertEqual(len(middle.content[4].sections), 0)

        # sec-04  anchor, numbered removeInRFC, title,  toc
        self.assertEqual(middle.content[4].anchor, "issues")
        self.assertTrue(middle.content[4].numbered)
        self.assertFalse(middle.content[4].removeInRFC)
        self.assertIsNone(middle.content[4].title)
        self.assertEqual(middle.content[4].toc, "default" )

        self.assertIsInstance(middle.content[5], rfc.Section)
        # ...
        self.assertIsInstance(middle.content[6], rfc.Section)

        self.assertIsInstance(middle.content[7], rfc.Section)
        # ...



    def _verify_rfc_txt_dom_middle(self, middle: rfc.Middle):
        self.assertIsNotNone(middle.content)
        self.assertIsInstance(middle.content, list)
        self.assertEqual(len(middle.content), 9)

        # sec-00
        self.assertIsInstance(middle.content[0], rfc.Section)
        # section-00 name
        self.assertIsInstance(middle.content[0].name, rfc.Name)
        if not isinstance(middle.content[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[0].name.content, list)
        self.assertEqual(len(middle.content[0].name.content), 1)
        self.assertIsInstance(middle.content[0].name.content[0], rfc.Text)
        self.assertEqual(middle.content[0].name.content[0].content, "Introduction")
        # section-00 -- content
        self.assertIsInstance(middle.content[0].content, list)
        self.assertEqual( len(middle.content[0].content), 8)

        # section-00 -- content[0] <T> 
        self.assertIsInstance(middle.content[0].content[0], rfc.T)
        if not isinstance(middle.content[0].content[0], rfc.T):
            return
        # section-00 -- content[0] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[0].content, list)
        self.assertEqual(len(middle.content[0].content[0].content), 1)
        self.assertIsInstance(middle.content[0].content[0].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[0].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[0].content[0].content,
"""Packet header diagrams have become a widely used format for
describing the syntax of binary protocols.  In otherwise largely
textual documents, they allow for the visualisation of packet
formats, reducing human error, and aiding in the implementation of
parsers for the protocols that they specify.
""")
        # section-00 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[0].anchor)
        self.assertIsNone( middle.content[0].content[0].hangText)
        self.assertFalse ( middle.content[0].content[0].keepWithNext)
        self.assertFalse ( middle.content[0].content[0].keepWithPrevious)

        # section-00 -- content[1] <T> 
        self.assertIsInstance(middle.content[0].content[1], rfc.T)
        if not isinstance(middle.content[0].content[1], rfc.T):
            return
        # section-00 -- content[1] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[1].content, list)
        self.assertEqual(len(middle.content[0].content[1].content), 1)
        self.assertIsInstance(middle.content[0].content[1].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[1].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[1].content[0].content,
"""Figure 1 gives an example of how packet header diagrams are used to
define binary protocol formats.  The format has an obvious structure:
the diagram clearly delineates each field, showing its width and its
position within the header.  This type of diagram is designed for
human readers, but is consistent enough that it should be possible to
develop a tool that generates a parser for the packet format from the
diagram.
""")
        # section-00 -- content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[1].anchor)
        self.assertIsNone( middle.content[0].content[1].hangText)
        self.assertFalse ( middle.content[0].content[1].keepWithNext)
        self.assertFalse ( middle.content[0].content[1].keepWithPrevious)

        # section-00 -- content[2] <T> content <Artwork>
        self.assertIsInstance( middle.content[0].content[2], rfc.Artwork)
        if not isinstance( middle.content[0].content[2], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[0].content[2].content, rfc.Text)
        if not isinstance( middle.content[0].content[2].content, rfc.Text):
            return
        self.assertEqual( middle.content[0].content[2].content.content,
""":    0                   1                   2                   3
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

        # section-00 -- content[2] <T> content <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[0].content[2].align, "left")
        self.assertIsNone( middle.content[0].content[2].alt)
        self.assertEqual ( middle.content[0].content[2].anchor, "Figure 1")
        self.assertIsNone( middle.content[0].content[2].height)
        self.assertEqual ( middle.content[0].content[2].name, "TCP's header format (from [RFC793])")
        self.assertIsNone( middle.content[0].content[2].src)
        self.assertIsNone( middle.content[0].content[2].type)
        self.assertIsNone( middle.content[0].content[2].width)
        self.assertIsNone( middle.content[0].content[2].xmlSpace)

        # section-00 -- content[3] <T> 
        self.assertIsInstance(middle.content[0].content[3], rfc.T)
        if not isinstance(middle.content[0].content[3], rfc.T):
            return
        # section-00 -- content[3] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[3].content, list)
        self.assertEqual(len(middle.content[0].content[3].content), 1)
        self.assertIsInstance(middle.content[0].content[3].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[3].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[3].content[0].content,
"""Unfortunately, the format of such packet diagrams varies both within
and between documents.  This variation makes it difficult to build
tools to generate parsers from the specifications.  Better tooling
could be developed if protocol specifications adopted a consistent
format for their packet descriptions.  Indeed, this underpins the
format described by this draft: we want to retain the benefits that
packet header diagrams provide, while identifying the benefits of
adopting a consistent format.
""")
        # section-00 -- content[3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[3].anchor)
        self.assertIsNone( middle.content[0].content[3].hangText)
        self.assertFalse ( middle.content[0].content[3].keepWithNext)
        self.assertFalse ( middle.content[0].content[3].keepWithPrevious)

        # section-00 -- content[4] <T> 
        self.assertIsInstance(middle.content[0].content[4], rfc.T)
        if not isinstance(middle.content[0].content[4], rfc.T):
            return
        # section-00 -- content[4] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[4].content, list)
        self.assertEqual(len(middle.content[0].content[4].content), 1)
        self.assertIsInstance(middle.content[0].content[4].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[4].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[4].content[0].content,
"""This document describes a consistent packet header diagram format and
accompanying structured text constructs that allow for the parsing
process of protocol headers to be fully specified.  This provides
support for the automatic generation of parser code.  Broad design
principles, that seek to maintain the primacy of human readability
and flexibility in writing, are described, before the format itself
is given.
""")
        # section-00 -- content[4] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[4].anchor)
        self.assertIsNone( middle.content[0].content[4].hangText)
        self.assertFalse ( middle.content[0].content[4].keepWithNext)
        self.assertFalse ( middle.content[0].content[4].keepWithPrevious)

        # section-00 -- content[5] <T> 
        self.assertIsInstance(middle.content[0].content[5], rfc.T)
        if not isinstance(middle.content[0].content[5], rfc.T):
            return
        # section-00 -- content[5] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[5].content, list)
        self.assertEqual(len(middle.content[0].content[5].content), 1)
        self.assertIsInstance(middle.content[0].content[5].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[5].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[5].content[0].content,
"""This document is itself an example of the approach that it describes,
with the packet header diagrams and structured text format described
by example.  Examples that do not form part of the protocol
description language are marked by a colon at the beginning of each
line; this prevents them from being parsed by the accompanying
tooling.
""")
        # section-00 -- content[5] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[5].anchor)
        self.assertIsNone( middle.content[0].content[5].hangText)
        self.assertFalse ( middle.content[0].content[5].keepWithNext)
        self.assertFalse ( middle.content[0].content[5].keepWithPrevious)

        # section-00 -- content[6] <T> 
        self.assertIsInstance(middle.content[0].content[6], rfc.T)
        if not isinstance(middle.content[0].content[6], rfc.T):
            return
        # section-00 -- content[6] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[6].content, list)
        self.assertEqual(len(middle.content[0].content[6].content), 1)
        self.assertIsInstance(middle.content[0].content[6].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[6].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[6].content[0].content,
"""This draft describes early work.  As consensus builds around the
particular syntax of the format described, both a formal ABNF
""")
        # section-00 -- content[6] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[6].anchor)
        self.assertIsNone( middle.content[0].content[6].hangText)
        self.assertFalse ( middle.content[0].content[6].keepWithNext)
        self.assertFalse ( middle.content[0].content[6].keepWithPrevious)

        # section-00 -- content[7] <T> 
        self.assertIsInstance(middle.content[0].content[7], rfc.T)
        if not isinstance(middle.content[0].content[7], rfc.T):
            return
        # section-00 -- content[7] <T> content <Text>
        self.assertIsInstance(middle.content[0].content[7].content, list)
        self.assertEqual(len(middle.content[0].content[7].content), 1)
        self.assertIsInstance(middle.content[0].content[7].content[0], rfc.Text)
        if not isinstance(middle.content[0].content[7].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[0].content[7].content[0].content,
"""specification (Appendix A) and code (Appendix B) that parses it (and,
as described above, this document) will be provided.
""")
        # section-00 -- content[7] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[0].content[7].anchor)
        self.assertIsNone( middle.content[0].content[7].hangText)
        self.assertFalse ( middle.content[0].content[7].keepWithNext)
        self.assertFalse ( middle.content[0].content[7].keepWithPrevious)

        # section-00 -- sections
        self.assertIsInstance(middle.content[0].sections, list)
        if not isinstance(middle.content[0].sections, list):
            return
        self.assertEqual( len(middle.content[0].sections), 0)
        # section-00 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[0].anchor)
        self.assertTrue(middle.content[0].numbered)
        self.assertFalse(middle.content[0].removeInRFC)
        self.assertIsNone(middle.content[0].title)
        self.assertEqual(middle.content[0].toc, "default" )

        # sec-01
        self.assertIsInstance(middle.content[1], rfc.Section)
        # section-01 name
        self.assertIsInstance(middle.content[1].name, rfc.Name)
        if not isinstance(middle.content[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[1].name.content, list)
        self.assertEqual(len(middle.content[1].name.content), 1)
        self.assertIsInstance(middle.content[1].name.content[0], rfc.Text)
        self.assertEqual(middle.content[1].name.content[0].content, "Background")

        # section-01 -- content
        self.assertIsInstance(middle.content[1].content, list)
        self.assertEqual( len(middle.content[1].content), 2)

        # section-01 -- content[0] <T> 
        self.assertIsInstance(middle.content[1].content[0], rfc.T)
        if not isinstance(middle.content[1].content[0], rfc.T):
            return
        # section-01 -- content[0] <T> content <Text>
        self.assertIsInstance(middle.content[1].content[0].content, list)
        self.assertEqual(len(middle.content[1].content[0].content), 1)
        self.assertIsInstance(middle.content[1].content[0].content[0], rfc.Text)
        if not isinstance(middle.content[1].content[0].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].content[0].content[0].content,
"""This section begins by considering how packet header diagrams are
used in existing documents.  This exposes the limitations that the
current usage has in terms of machine-readability, guiding the design
of the format that this document proposes.
""")
        # section-01 -- content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].content[0].anchor)
        self.assertIsNone( middle.content[1].content[0].hangText)
        self.assertFalse ( middle.content[1].content[0].keepWithNext)
        self.assertFalse ( middle.content[1].content[0].keepWithPrevious)


        # section-01 -- content[1] <T> 
        self.assertIsInstance(middle.content[1].content[1], rfc.T)
        if not isinstance(middle.content[1].content[1], rfc.T):
            return
        # section-01 -- content[1] <T> content <Text>
        self.assertIsInstance(middle.content[1].content[1].content, list)
        self.assertEqual(len(middle.content[1].content[1].content), 1)
        self.assertIsInstance(middle.content[1].content[1].content[0], rfc.Text)
        if not isinstance(middle.content[1].content[1].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].content[1].content[0].content,
"""While this document focuses on the machine-readability of packet
format diagrams, this section also discusses the use of other
structured or formal languages within IETF documents.  Considering
how and why these languages are used provides an instructive contrast
to the relatively incremental approach proposed here.
""")
        # section-01 -- content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].content[1].anchor)
        self.assertIsNone( middle.content[1].content[1].hangText)
        self.assertFalse ( middle.content[1].content[1].keepWithNext)
        self.assertFalse ( middle.content[1].content[1].keepWithPrevious)


        # section-01 -- sections 
        self.assertIsInstance(middle.content[1].sections, list)
        if not isinstance(middle.content[1].sections, list):
            return
        self.assertEqual( len(middle.content[1].sections), 2)
        # section-01 -- section [0] 
        self.assertIsInstance(middle.content[1].sections[0], rfc.Section)
        # section-01 -- section [0] name 
        self.assertIsInstance(middle.content[1].sections[0].name, rfc.Name)
        if not isinstance(middle.content[1].sections[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[1].sections[0].name.content, list)
        self.assertEqual(len(middle.content[1].sections[0].name.content), 1)
        self.assertIsInstance(middle.content[1].sections[0].name.content[0], rfc.Text)
        self.assertEqual(middle.content[1].sections[0].name.content[0].content, "Limitations of Current Packet Format Diagrams")

        # section-01 -- subsection [0] content 
        self.assertIsInstance(middle.content[1].sections[0].content, list)
        self.assertEqual( len(middle.content[1].sections[0].content), 13)


        # section-01 -- subsection [0] content [0] <Artwork> content
        self.assertIsInstance( middle.content[1].sections[0].content[0], rfc.Artwork)
        if not isinstance( middle.content[1].sections[0].content[0], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[1].sections[0].content[0].content, rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[0].content, rfc.Text):
            return
        self.assertEqual( middle.content[1].sections[0].content[0].content.content,
""":   The RESET_STREAM frame is as follows:
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

        # section-01 -- subsection [0] content [0] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[1].sections[0].content[0].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[0].alt)
        self.assertEqual ( middle.content[1].sections[0].content[0].anchor, "Figure 2")
        self.assertIsNone( middle.content[1].sections[0].content[0].height)
        self.assertEqual ( middle.content[1].sections[0].content[0].name, "QUIC's RESET_STREAM frame format (from [QUIC-TRANSPORT])")
        self.assertIsNone( middle.content[1].sections[0].content[0].src)
        self.assertIsNone( middle.content[1].sections[0].content[0].type)
        self.assertIsNone( middle.content[1].sections[0].content[0].width)
        self.assertIsNone( middle.content[1].sections[0].content[0].xmlSpace)


        # section-01 -- subsection[0] content [1] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[1], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[1], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[1].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[1].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[1].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[1].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[1].content[0].content,
"""Packet header diagrams are frequently used in IETF standards to
describe the format of binary protocols.  While there is no standard
for how these diagrams should be formatted, they have a broadly
similar structure, where the layout of a protocol data unit (PDU) or
""")
        # section-01 -- subsection[0] content[1] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[1].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[1].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[1].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[1].keepWithPrevious)

        # section-01 -- subsection[0] content [2] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[2], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[2], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[2].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[2].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[2].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[2].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[2].content[0].content,
"""structure is shown in diagrammatic form, followed by a description
list of the fields that it contains.  An example of this format,
taken from the QUIC specification, is given in Figure 2.
""")
        # section-01 -- subsection[0] content[2] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[2].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[2].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[2].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[2].keepWithPrevious)

        # section-01 -- subsection[0] content [3] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[3], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[3], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[3].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[3].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[3].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[3].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[3].content[0].content,
"""These packet header diagrams, and the accompanying descriptions, are
formatted for human readers rather than for automated processing.  As
a result, while there is rough consistency in how packet header
diagrams are formatted, there are a number of limitations that make
them difficult to work with programmatically:
""")
        # section-01 -- subsection[0] content[3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[3].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[3].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[3].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[3].keepWithPrevious)

        # section-01 -- subsection[0] content [4] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[4], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[4], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[4].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[4].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[4].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[4].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[4].content[0].content,
"""Inconsistent syntax:  There are two classes of consistency that are
needed to support automated processing of specifications: internal
consistency within a diagram or document, and external consistency
across all documents.
""")
        # section-01 -- subsection[0] content[3] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[4].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[4].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[4].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[4].keepWithPrevious)


        # section-01 -- subsection[0] content [5] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[5], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[5], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[5].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[5].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[5].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[5].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[5].content[0].content,
"""Figure 2 gives an example of internal inconsistency.  Here, the
packet diagram shows a field labelled "Application Error Code",
while the accompanying description lists the field as "Application
Protocol Error Code".  The use of an abbreviated name is suitable
for human readers, but makes parsing the structure difficult for
machines.  Figure 3 gives a further example, where the description
includes an "Option-Code" field that does not appear in the packet
diagram; and where the description states that each field is 16
bits in length, but the diagram shows the OPTION_RELAY_PORT as 13
bits, and Option-Len as 19 bits.  Another example is [RFC6958],
where the packet format diagram showing the structure of the
Burst/Gap Loss Metrics Report Block shows the Number of Bursts
field as being 12 bits wide but the corresponding text describes
it as 16 bits.
""")
        # section-01 -- subsection[0] content[5] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[5].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[5].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[5].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[5].keepWithPrevious)

        # section-01 -- subsection[0] content [6] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[6], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[6], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[6].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[6].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[6].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[6].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[6].content[0].content,
"""Comparing Figure 2 with Figure 3 exposes external inconsistency
across documents.  While the packet format diagrams are broadly
similar, the surrounding text is formatted differently.  If
machine parsing is to be made possible, then this text must be
structured consistently.
""")
        # section-01 -- subsection[0] content[6] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[6].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[6].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[6].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[6].keepWithPrevious)


        # section-01 -- subsection[0] content [7] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[7], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[7], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[7].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[7].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[7].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[7].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[7].content[0].content,
"""Ambiguous constraints:  The constraints that are enforced on a
particular field are often described ambiguously, or in a way that
cannot be parsed easily.  In Figure 3, each of the three fields in
the structure is constrained.  The first two fields ("Option-Code"
and "Option-Len") are to be set to constant values (note the
inconsistency in how these constraints are expressed in the
description).  However, the third field ("Downstream Source Port")
can take a value from a constrained set.  This constraint is
expressed in prose that cannot readily by understood by machine.
""")
        # section-01 -- subsection[0] content[7] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[7].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[7].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[7].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[7].keepWithPrevious)

        # section-01 -- subsection[0] content [8] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[8], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[8], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[8].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[8].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[8].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[8].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[8].content[0].content,
"""Poor linking between sub-structures:  Protocol data units and other
structures are often comprised of sub-structures that are defined
""")
        # section-01 -- subsection[0] content[8] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[8].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[8].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[8].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[8].keepWithPrevious)

        # section-01 -- subsection[0] content [9] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[9], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[9], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[9].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[9].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[9].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[9].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[9].content[0].content,
"""elsewhere, either in the same document, or within another
document.  Chaining these structures together is essential for
machine parsing: the parsing process for a protocol data unit is
only fully expressed if all elements can be parsed.
""")
        # section-01 -- subsection[0] content[9] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[9].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[9].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[9].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[9].keepWithPrevious)

        # section-01 -- subsection[0] content [10] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[10], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[10], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[10].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[10].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[10].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[10].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[10].content[0].content,
"""Figure 2 highlights the difficulty that machine parsers have in
chaining structures together.  Two fields ("Stream ID" and "Final
Size") are described as being encoded as variable-length integers;
this is a structure described elsewhere in the same document.
Structured text is required both alongside the definition of the
containing structure and with the definition of the sub-structure,
to allow a parser to link the two together.
""")
        # section-01 -- subsection[0] content[10] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[10].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[10].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[10].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[10].keepWithPrevious)


        # section-01 -- subsection[0] content [11] <T> 
        self.assertIsInstance(middle.content[1].sections[0].content[11], rfc.T)
        if not isinstance(middle.content[1].sections[0].content[11], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[0].content[11].content, list)
        self.assertEqual(len(middle.content[1].sections[0].content[11].content), 1)
        self.assertIsInstance(middle.content[1].sections[0].content[11].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[0].content[11].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[0].content[11].content[0].content,
"""Lack of extension and evolution syntax:  Protocols are often
specified across multiple documents, either because the protocol
explicitly includes extension points (e.g., profiles and payload
format specifications in RTP [RFC3550]) or because definition of a
protocol data unit has changed and evolved over time.  As a
result, it is essential that syntax be provided to allow for a
complete definition of a protocol's parsing process to be
constructed across multiple documents.
""")
        # section-01 -- subsection[0] content[11] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[0].content[11].anchor)
        self.assertIsNone( middle.content[1].sections[0].content[11].hangText)
        self.assertFalse ( middle.content[1].sections[0].content[11].keepWithNext)
        self.assertFalse ( middle.content[1].sections[0].content[11].keepWithPrevious)

        # section-01 -- subsection[0] content [12] <Artwork> 
        self.assertIsInstance(middle.content[1].sections[0].content[12], rfc.Artwork)
        if not isinstance(middle.content[1].sections[0].content[12], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[1].sections[0].content[12].content, rfc.Text)
        if not isinstance( middle.content[1].sections[0].content[12].content, rfc.Text):
            return
        self.assertEqual( middle.content[1].sections[0].content[12].content.content,
""":   The format of the "Relay Source Port Option" is shown below:
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

        # section-01 -- subsection [0] content [12] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[1].sections[0].content[12].align, "left")
        self.assertIsNone( middle.content[1].sections[0].content[12].alt)
        self.assertEqual ( middle.content[1].sections[0].content[12].anchor, "Figure 3")
        self.assertIsNone( middle.content[1].sections[0].content[12].height)
        self.assertEqual ( middle.content[1].sections[0].content[12].name, "DHCPv6's Relay Source Port Option (from [RFC8357])")
        self.assertIsNone( middle.content[1].sections[0].content[12].src)
        self.assertIsNone( middle.content[1].sections[0].content[12].type)
        self.assertIsNone( middle.content[1].sections[0].content[12].width)
        self.assertIsNone( middle.content[1].sections[0].content[12].xmlSpace)


        # section-01 -- section [0] sections 
        self.assertIsInstance(middle.content[1].sections[0].sections, list)
        if not isinstance(middle.content[1].sections[0].sections, list):
            return
        self.assertEqual( len(middle.content[1].sections[0].sections), 0)
        # section-01 -- section [0] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[1].sections[0].anchor)
        self.assertTrue(middle.content[1].sections[0].numbered)
        self.assertFalse(middle.content[1].sections[0].removeInRFC)
        self.assertIsNone(middle.content[1].sections[0].title)
        self.assertEqual(middle.content[1].sections[0].toc, "default" )


        # section-01 -- subsection [1] 
        self.assertIsInstance(middle.content[1].sections[1], rfc.Section)
        # section-01 -- subsection [1] content 
        self.assertIsInstance(middle.content[1].sections[1].content, list)
        self.assertEqual( len(middle.content[1].sections[1].content), 1)
        # section-01 -- subsection [1] content [0] <T>
        self.assertIsInstance(middle.content[1].sections[1].content[0], rfc.T)
        if not isinstance(middle.content[1].sections[1].content[0], rfc.T):
            return
        self.assertIsInstance(middle.content[1].sections[1].content[0].content, list)
        self.assertEqual(len(middle.content[1].sections[1].content[0].content), 1)
        self.assertIsInstance(middle.content[1].sections[1].content[0].content[0], rfc.Text)
        if not isinstance(middle.content[1].sections[1].content[0].content[0], rfc.Text):
            return
        self.assertEqual(middle.content[1].sections[1].content[0].content[0].content,
"""A small proportion of IETF standards documents contain structured and
formal languages, including ABNF [RFC5234], ASN.1 [ASN1], C, CBOR
[RFC7049], JSON, the TLS presentation language [RFC8446], YANG models
[RFC7950], and XML.  While this broad range of languages may be
problematic for the development of tooling to parse specifications,
these, and other, languages serve a range of different use cases.
ABNF, for example, is typically used to specify text protocols, while
ASN.1 is used to specify data structure serialisation.  This document
specifies a structured language for specifying the parsing of binary
protocol data units.
""")
        # section-01 -- subsection[1] content[0] <T> anchor, hangText, keepWithNext, keepWithPrevious
        self.assertIsNone( middle.content[1].sections[1].content[0].anchor)
        self.assertIsNone( middle.content[1].sections[1].content[0].hangText)
        self.assertFalse ( middle.content[1].sections[1].content[0].keepWithNext)
        self.assertFalse ( middle.content[1].sections[1].content[0].keepWithPrevious)


        # section-01 -- subsection [1] sections 
        self.assertIsInstance(middle.content[1].sections[1].sections, list)
        if not isinstance(middle.content[1].sections[1].sections, list):
            return
        self.assertEqual( len(middle.content[1].sections[1].sections), 0)
        # section-01 -- subsection [1] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[1].sections[1].anchor)
        self.assertTrue(middle.content[1].sections[1].numbered)
        self.assertFalse(middle.content[1].sections[1].removeInRFC)
        self.assertIsNone(middle.content[1].sections[1].title)
        self.assertEqual(middle.content[1].sections[1].toc, "default" )


        # section-01 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[1].anchor)
        self.assertTrue(middle.content[1].numbered)
        self.assertFalse(middle.content[1].removeInRFC)
        self.assertIsNone(middle.content[1].title)
        self.assertEqual(middle.content[1].toc, "default" )





        # sec-02
        self.assertIsInstance(middle.content[2], rfc.Section)
        # section-02 name
        self.assertIsInstance(middle.content[2].name, rfc.Name)
        if not isinstance(middle.content[2].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[2].name.content, list)
        self.assertEqual(len(middle.content[2].name.content), 1)
        self.assertIsInstance(middle.content[2].name.content[0], rfc.Text)
        self.assertEqual(middle.content[2].name.content[0].content, "Design Principles")

        # section-02 -- content
        self.assertIsInstance(middle.content[2].content, list)
        self.assertEqual( len(middle.content[2].content), 16)
        self.assertIsInstance(middle.content[2].content[0], rfc.T)
        self.assertIsInstance(middle.content[2].content[1], rfc.T)
        self.assertIsInstance(middle.content[2].content[2], rfc.T)
        self.assertIsInstance(middle.content[2].content[3], rfc.T)
        self.assertIsInstance(middle.content[2].content[4], rfc.T)
        self.assertIsInstance(middle.content[2].content[5], rfc.T)
        self.assertIsInstance(middle.content[2].content[6], rfc.T)
        self.assertIsInstance(middle.content[2].content[7], rfc.T)
        self.assertIsInstance(middle.content[2].content[8], rfc.T)
        self.assertIsInstance(middle.content[2].content[9], rfc.T)
        self.assertIsInstance(middle.content[2].content[10], rfc.T)
        self.assertIsInstance(middle.content[2].content[11], rfc.T)
        self.assertIsInstance(middle.content[2].content[12], rfc.T)
        self.assertIsInstance(middle.content[2].content[13], rfc.T)
        self.assertIsInstance(middle.content[2].content[14], rfc.T)
        self.assertIsInstance(middle.content[2].content[15], rfc.T)
        # section-02 -- sections
        self.assertIsInstance(middle.content[2].sections, list)
        if not isinstance(middle.content[2].sections, list):
            return
        self.assertEqual( len(middle.content[2].sections), 0)
        # section-02 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[2].anchor)
        self.assertTrue(middle.content[2].numbered)
        self.assertFalse(middle.content[2].removeInRFC)
        self.assertIsNone(middle.content[2].title)
        self.assertEqual(middle.content[2].toc, "default" )

        # sec-03
        self.assertIsInstance(middle.content[3], rfc.Section)
        # section-03 name
        self.assertIsInstance(middle.content[3].name, rfc.Name)
        if not isinstance(middle.content[3].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[3].name.content, list)
        self.assertEqual(len(middle.content[3].name.content), 1)
        self.assertIsInstance(middle.content[3].name.content[0], rfc.Text)
        self.assertEqual(middle.content[3].name.content[0].content, "Augmented Packet Header Diagrams")
        # section-03 -- content
        self.assertIsInstance(middle.content[3].content, list)
        self.assertEqual( len(middle.content[3].content), 3)
        self.assertIsInstance(middle.content[3].content[0], rfc.T)
        self.assertIsInstance(middle.content[3].content[1], rfc.T)
        self.assertIsInstance(middle.content[3].content[2], rfc.T)
        # section-03 -- sections
        self.assertIsInstance(middle.content[3].sections, list)
        if not isinstance(middle.content[3].sections, list):
            return
        self.assertEqual( len(middle.content[3].sections), 10)
        # section-03 -- sub-section[0]
        self.assertIsInstance(middle.content[3].sections[0], rfc.Section)
        self.assertIsInstance(middle.content[3].sections[0].name, rfc.Name)
        if not isinstance(middle.content[3].sections[0].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[3].sections[0].name.content, list)
        self.assertEqual(len(middle.content[3].sections[0].name.content), 1)
        self.assertIsInstance(middle.content[3].sections[0].name.content[0], rfc.Text)
        self.assertEqual(middle.content[3].sections[0].name.content[0].content, "PDUs with Fixed and Variable-Width Fields")
        # section-03 -- sub-section[0] content 
        self.assertIsInstance(middle.content[3].sections[0].content, list)
        self.assertEqual(len(middle.content[3].sections[0].content), 24)
        # section-03 -- sub-section[0] content[0--6] <T> 
        self.assertIsInstance(middle.content[3].sections[0].content[0], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[1], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[2], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[3], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[4], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[5], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[6], rfc.T)
        # section-03 -- sub-section[0] content[7] <Artwork> 
        self.assertIsInstance(middle.content[3].sections[0].content[7], rfc.Artwork)
        if not isinstance(middle.content[3].sections[0].content[7], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[3].sections[0].content[7].content, rfc.Text)
        if not isinstance( middle.content[3].sections[0].content[7].content, rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[0].content[7].content.content, 
"""0                   1                   2                   3
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
        # section-03 -- sub-section[0] content[7] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[3].sections[0].content[7].align, "left")
        self.assertIsNone( middle.content[3].sections[0].content[7].alt)
        self.assertIsNone( middle.content[3].sections[0].content[7].anchor)
        self.assertIsNone( middle.content[3].sections[0].content[7].height) 
        self.assertIsNone( middle.content[3].sections[0].content[7].name)
        self.assertIsNone( middle.content[3].sections[0].content[7].src)
        self.assertIsNone( middle.content[3].sections[0].content[7].type) 
        self.assertIsNone( middle.content[3].sections[0].content[7].width) 
        self.assertIsNone( middle.content[3].sections[0].content[7].xmlSpace) 


        # section-03 -- sub-section[0] content[8--23] <T> 
        self.assertIsInstance(middle.content[3].sections[0].content[8], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[9], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[10], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[11], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[12], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[13], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[14], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[15], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[16], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[18], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[19], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[20], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[21], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[22], rfc.T)
        self.assertIsInstance(middle.content[3].sections[0].content[23], rfc.T)



        # section-03 -- sub-section[0] sections 
        self.assertIsInstance(middle.content[3].sections[0].sections, list)
        if not isinstance(middle.content[3].sections[0].sections, list):
            return
        self.assertEqual(len(middle.content[3].sections[0].sections), 0)
        # section-03 -- sub-section[0] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[3].sections[0].anchor)
        self.assertTrue(middle.content[3].sections[0].numbered)
        self.assertFalse(middle.content[3].sections[0].removeInRFC)
        self.assertIsNone(middle.content[3].sections[0].title)
        self.assertEqual(middle.content[3].sections[0].toc, "default" )

        # section-03 -- sub-section[1]
        self.assertIsInstance(middle.content[3].sections[1], rfc.Section)
        self.assertIsInstance(middle.content[3].sections[1].name, rfc.Name)
        if not isinstance(middle.content[3].sections[1].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[3].sections[1].name.content, list)
        self.assertEqual(len(middle.content[3].sections[1].name.content), 1)
        self.assertIsInstance(middle.content[3].sections[1].name.content[0], rfc.Text)
        self.assertEqual(middle.content[3].sections[1].name.content[0].content, "PDUs That Cross-Reference Previously Defined Fields")

        # section-03 -- sub-section[1] content 
        self.assertIsInstance(middle.content[3].sections[1].content, list)
        self.assertEqual(len(middle.content[3].sections[1].content), 24)

        # section-03 -- sub-section[1] sections 
        self.assertIsInstance(middle.content[3].sections[1].sections, list)
        if not isinstance(middle.content[3].sections[1].sections, list):
            return
        self.assertEqual(len(middle.content[3].sections[1].sections), 0)
        # section-03 -- sub-section[0] content[0] <T> 
        self.assertIsInstance(middle.content[3].sections[1].content[0], rfc.T)

        # section-03 -- sub-section[1] content[1] <Artwork> 
        self.assertIsInstance(middle.content[3].sections[1].content[1], rfc.Artwork)
        if not isinstance(middle.content[3].sections[1].content[1], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[3].sections[1].content[1].content, rfc.Text)
        if not isinstance( middle.content[3].sections[1].content[1].content, rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[1].content[1].content.content, 
"""0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               SSRC                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
""")
        # section-03 -- sub-section[1] content[1] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[3].sections[1].content[1].align, "left")
        self.assertIsNone( middle.content[3].sections[1].content[1].alt)
        self.assertIsNone( middle.content[3].sections[1].content[1].anchor)
        self.assertIsNone( middle.content[3].sections[1].content[1].height) 
        self.assertIsNone( middle.content[3].sections[1].content[1].name)
        self.assertIsNone( middle.content[3].sections[1].content[1].src)
        self.assertIsNone( middle.content[3].sections[1].content[1].type) 
        self.assertIsNone( middle.content[3].sections[1].content[1].width) 
        self.assertIsNone( middle.content[3].sections[1].content[1].xmlSpace) 

        # section-03 -- sub-section[1] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[3].sections[1].anchor)
        self.assertTrue(middle.content[3].sections[1].numbered)
        self.assertFalse(middle.content[3].sections[1].removeInRFC)
        self.assertIsNone(middle.content[3].sections[1].title)
        self.assertEqual(middle.content[3].sections[1].toc, "default" )

        # section-03 -- sub-section[0] content[2--5] <T> 
        self.assertIsInstance(middle.content[3].sections[1].content[2], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[3], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[4], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[5], rfc.T)

        # section-03 -- sub-section[1] content[6] <Artwork> 
        self.assertIsInstance(middle.content[3].sections[1].content[6], rfc.Artwork)
        if not isinstance(middle.content[3].sections[1].content[6], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[3].sections[1].content[6].content, rfc.Text)
        if not isinstance( middle.content[3].sections[1].content[6].content, rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[1].content[6].content.content, 
"""0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| V |P|X|  CC   |M|     PT      |       Sequence Number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Timestamp                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                Synchronization Source identifier              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                [Contributing Source identifiers]              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Header Extension                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Payload                           :
:                                                               :
:                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Padding             | Padding Count |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
""")
        # section-03 -- sub-section[1] content[6] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[3].sections[1].content[6].align, "left")
        self.assertIsNone( middle.content[3].sections[1].content[6].alt)
        self.assertIsNone( middle.content[3].sections[1].content[6].anchor)
        self.assertIsNone( middle.content[3].sections[1].content[6].height) 
        self.assertIsNone( middle.content[3].sections[1].content[6].name)
        self.assertIsNone( middle.content[3].sections[1].content[6].src)
        self.assertIsNone( middle.content[3].sections[1].content[6].type) 
        self.assertIsNone( middle.content[3].sections[1].content[6].width) 
        self.assertIsNone( middle.content[3].sections[1].content[6].xmlSpace) 


        # section-03 -- sub-section[0] content[7--23] <T> 
        self.assertIsInstance(middle.content[3].sections[1].content[7], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[8], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[9], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[10], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[11], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[12], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[13], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[14], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[15], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[16], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[17], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[18], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[19], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[20], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[21], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[22], rfc.T)
        self.assertIsInstance(middle.content[3].sections[1].content[23], rfc.T)

        # section-03 -- sub-section[1] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[3].sections[1].anchor)
        self.assertTrue(middle.content[3].sections[1].numbered)
        self.assertFalse(middle.content[3].sections[1].removeInRFC)
        self.assertIsNone(middle.content[3].sections[1].title)
        self.assertEqual(middle.content[3].sections[1].toc, "default" )


        # section-03 -- sub-section[2]
        self.assertIsInstance(middle.content[3].sections[2], rfc.Section)
        self.assertIsInstance(middle.content[3].sections[2].name, rfc.Name)
        if not isinstance(middle.content[3].sections[2].name, rfc.Name): # type-check
            return
        self.assertIsInstance(middle.content[3].sections[2].name.content, list)
        self.assertEqual(len(middle.content[3].sections[2].name.content), 1)
        self.assertIsInstance(middle.content[3].sections[2].name.content[0], rfc.Text)
        self.assertEqual(middle.content[3].sections[2].name.content[0].content, "PDUs with Non-Contiguous Fields")

        # section-03 -- sub-section[2] content 
        self.assertIsInstance(middle.content[3].sections[2].content, list)
        self.assertEqual(len(middle.content[3].sections[2].content), 6)

        # section-03 -- sub-section[2] content[0--1] <T> 
        self.assertIsInstance(middle.content[3].sections[2].content[0], rfc.T)
        self.assertIsInstance(middle.content[3].sections[2].content[1], rfc.T)

        # section-03 -- sub-section[1] content[2] <Artwork>
        self.assertIsInstance(middle.content[3].sections[2].content[2], rfc.Artwork)
        if not isinstance(middle.content[3].sections[2].content[2], rfc.Artwork):
            return
        self.assertIsInstance( middle.content[3].sections[2].content[2].content, rfc.Text)
        if not isinstance( middle.content[3].sections[2].content[2].content, rfc.Text):
            return
        self.assertEqual( middle.content[3].sections[2].content[2].content.content, 
"""0                   1
0 1 2 3 4 5 6 7 8 9 0 1 2 3
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|M|M|M|M|M|C|M|M|M|C|M|M|M|M|
|B|A|9|8|7|1|6|5|4|0|3|2|1|0|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
""")
        # section-03 -- sub-section[2] content[2] <Artwork> align, alt, anchor, height, name, src, type, width, xmlSpace
        self.assertEqual ( middle.content[3].sections[2].content[2].align, "left")
        self.assertIsNone( middle.content[3].sections[2].content[2].alt)
        self.assertIsNone( middle.content[3].sections[2].content[2].anchor)
        self.assertIsNone( middle.content[3].sections[2].content[2].height) 
        self.assertIsNone( middle.content[3].sections[2].content[2].name)
        self.assertIsNone( middle.content[3].sections[2].content[2].src)
        self.assertIsNone( middle.content[3].sections[2].content[2].type) 
        self.assertIsNone( middle.content[3].sections[2].content[2].width) 
        self.assertIsNone( middle.content[3].sections[2].content[2].xmlSpace) 



        # section-03 -- sub-section[2] content[3--5] <T> 
        self.assertIsInstance(middle.content[3].sections[2].content[3], rfc.T)
        self.assertIsInstance(middle.content[3].sections[2].content[4], rfc.T)
        self.assertIsInstance(middle.content[3].sections[2].content[5], rfc.T)

        # section-03 -- sub-section[2] sections 
        self.assertIsInstance(middle.content[3].sections[2].sections, list)
        if not isinstance(middle.content[3].sections[2].sections, list):
            return
        self.assertEqual(len(middle.content[3].sections[2].sections), 0)

        # section-03 -- sub-section[2] anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[3].sections[2].anchor)
        self.assertTrue(middle.content[3].sections[2].numbered)
        self.assertFalse(middle.content[3].sections[2].removeInRFC)
        self.assertIsNone(middle.content[3].sections[2].title)
        self.assertEqual(middle.content[3].sections[2].toc, "default" )

        # section-03 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[3].anchor)
        self.assertTrue(middle.content[3].numbered)
        self.assertFalse(middle.content[3].removeInRFC)
        self.assertIsNone(middle.content[3].title)
        self.assertEqual(middle.content[3].toc, "default" )

        # sec-04
        self.assertIsInstance(middle.content[4], rfc.Section)
        # section-04 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[4].anchor)
        self.assertTrue(middle.content[4].numbered)
        self.assertFalse(middle.content[4].removeInRFC)
        self.assertIsNone(middle.content[4].title)
        self.assertEqual(middle.content[4].toc, "default" )

        # sec-05
        self.assertIsInstance(middle.content[5], rfc.Section)
        # section-05 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[5].anchor)
        self.assertTrue(middle.content[5].numbered)
        self.assertFalse(middle.content[5].removeInRFC)
        self.assertIsNone(middle.content[5].title)
        self.assertEqual(middle.content[5].toc, "default" )

        # sec-06
        self.assertIsInstance(middle.content[6], rfc.Section)
        # section-06 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[6].anchor)
        self.assertTrue(middle.content[6].numbered)
        self.assertFalse(middle.content[6].removeInRFC)
        self.assertIsNone(middle.content[6].title)
        self.assertEqual(middle.content[6].toc, "default" )

        # sec-07
        self.assertIsInstance(middle.content[7], rfc.Section)
        # section-07 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[7].anchor)
        self.assertTrue(middle.content[7].numbered)
        self.assertFalse(middle.content[7].removeInRFC)
        self.assertIsNone(middle.content[7].title)
        self.assertEqual(middle.content[7].toc, "default" )

        # sec-08
        self.assertIsInstance(middle.content[8], rfc.Section)
        # section-08 -- anchor, numbered, removeInRFC, title, toc
        self.assertIsNone(middle.content[8].anchor)
        self.assertTrue(middle.content[8].numbered)
        self.assertFalse(middle.content[8].removeInRFC)
        self.assertIsNone(middle.content[8].title)
        self.assertEqual(middle.content[8].toc, "default" )
