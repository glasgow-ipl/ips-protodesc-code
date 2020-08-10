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

        # category -- deprecated in rfc7991 (v3)
        # backwards compatibility
        category = xml_tree.attrib.get("category", None)
        if category is None :
            self.assertIsNone( node.category )
        else :
            self.assertIsNotNone( node.category )
            self.assertIsInstance( node.category, str)
            self.assertIn( node.category, [ "std", "bcp", "info", "exp", "historic" ])
        
        # consensus
        consensus = xml_tree.attrib.get("consensus", None)
        self.assertIsInstance( node.consensus , bool)
        if consensus in [ None, "no" , "false" ]:
            self.assertFalse( node.consensus )
        elif consensus in ["yes", "true"] :
            self.assertTrue( node.consensus )
        else :
            self.assertIn( consensus, ["no", "yes", "false", "true"], f"unexpected consensus -- {consensus}")

        # docName,number -- deprecated in rfc7991 (v3)
        # backwards compatibility
        # docName and number cannot be simultaneously provided
        docName = xml_tree.attrib.get("docName", None)
        if docName is not None :
            self.assertIsNotNone(node.docName)
            self.assertIsNone(node.number) # if docName is provided number should be None
            self.assertIsInstance(node.docName, str)
            self.assertEqual(docName,node.docName)

        number = xml_tree.attrib.get("number", None)
        if number is not None :
            self.assertIsNotNone(node.number)
            self.assertIsNone(node.docName) # if number is provided docName should be None
            self.assertIsInstance(node.number, str)
            self.assertEqual(docName,node.docName)


        # indexInclude
        indexInclude = xml_tree.attrib.get("indexInclude", None)
        if indexInclude is None :
            self.assertTrue(node.indexInclude)
        else :
            self.assertIn( indexInclude, ["true", "false"], msg=f"RFC indexInclude not a boolean. Input file error" )
            if indexInclude == "true" :
                self.assertTrue( node.indexInclude )
            else :
                self.assertFalse( node.indexInclude )

        # ipr
        ipr = xml_tree.attrib.get("ipr", None)
        if ipr is None :
            self.assertIsNone(node.ipr)
        else :
            self.assertIsInstance(node.ipr, str)
            self.assertEqual(ipr, node.ipr)

        # iprExract
        iprExtract = xml_tree.attrib.get("iprExtract", None)
        if iprExtract is None :
            self.assertIsNone(node.iprExtract)
        else :
            self.assertIsInstance(node.iprExtract, str)
            self.assertEqual(iprExtract, node.iprExtract)

        # obsoletes
        obsoletes = xml_tree.attrib.get("obsoletes", None)
        if obsoletes is None :
            self.assertIsNone(node.obsoletes)
        else :
            self.assertIsInstance(node.obsoletes, str)
            self.assertEqual(obsoletes, node.obsoletes)


        # prepTime
        prepTime = xml_tree.attrib.get("prepTime", None)
        if prepTime is None :
            self.assertIsNone(node.prepTime)
        else :
            self.assertIsInstance(node.prepTime, str)
            self.assertEqual(prepTime, node.prepTime)
            # TO DO : add time formatting check - format is ISO format rfc3339

        # seriesNo
        seriesNo = xml_tree.attrib.get("seriesNo", None)
        if seriesNo is None :
            self.assertIsNone(node.seriesNo)
        else :
            self.assertIsInstance(node.seriesNo, str)
            self.assertEqual(seriesNo, node.seriesNo)


        # sortRefs
        sortRefs = xml_tree.attrib.get("sortRefs", None)
        self.assertIsInstance( node.sortRefs , bool)
        if sortRefs in [ None, "false" ]:
            self.assertFalse( node.sortRefs )
        elif consensus == "true" :
            self.assertTrue( node.sortRefs )
        else :
            self.assertIn( consensus, ["false", "true"], f"unexpected sortRefs -- {sortRefs}")

        # submissionType
        submissionType = xml_tree.attrib.get("submissionType", None)
        self.assertIsNotNone( node.submissionType )
        self.assertIsInstance( node.submissionType , str)
        if submissionType is None :
            self.assertEqual( node.submissionType , "IETF")
        else :
            self.assertEqual( submissionType, node.submissionType )
            self.assertIn( node.submissionType, [ "IETF", "IAB", "IRTF", "independent"] )

        # symRefs
        symRefs = xml_tree.attrib.get("symRefs", None)
        self.assertIsInstance( node.symRefs , bool)
        if symRefs in [ None, "true" ]:
            self.assertTrue( node.symRefs )
        elif symRefs == "false" :
            self.assertFalse( node.symRefs )
        else :
            self.assertIn( symRefs, ["false", "true"], f"unexpected symRefs -- {symRefs}")


        ## tocDepth
        #tocDepth = xml_tree.attrib.get("tocDepth", None)
        #self.assertIsInstance(node.tocDepth, str)
        #if tocDepth is None :
        #   self.assertEqual(node.tocDepth, "3" )
        #else :
        #    self.assertEqual(tocDepth, node.tocDepth)

        # DJ - bypass tocDepth
        tocDepth = xml_tree.attrib.get("tocDepth", None)
        self.assertIsNone(node.tocDepth)
        if tocDepth is None :
           self.assertIsNone(node.tocDepth)
        else :
            self.assertEqual(tocDepth, node.tocDepth)

        # tocInclude
        tocInclude = xml_tree.attrib.get("tocInclude", None)
        self.assertIsInstance( node.tocInclude , bool)
        if tocInclude in [ None, "true" ]:
            self.assertTrue( node.tocInclude )
        elif symRefs == "false" :
            self.assertFalse( node.tocInclude )
        else :
            self.assertIn( symRefs, ["false", "true"], f"unexpected tocInclude -- {tocInclude}")


        # updates
        updates = xml_tree.attrib.get("updates", None)
        if updates is None :
            self.assertIsNone( node.updates )
        else :
            self.assertIsNotNone( node.updates )
            self.assertIsInstance( node.updates , str)
            self.assertEqual( updates, node.updates )

        # version
        version = xml_tree.attrib.get("version", None)
        if version is None :
            self.assertIsNone( node.version )
        else :
            self.assertIsNotNone( node.version )
            self.assertIsInstance( node.version , str)
            self.assertEqual( version, node.version )

    def test_rfc_front(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as fd:
            raw_content = fd.read()
            xml_tree = ET.fromstring(raw_content)
            content = npt.parser_rfc_xml.parse_rfc(xml_tree)
            node = content.front
            self.assertEqual( len( [ _front for _front in xml_tree.findall("front") ]), 1 )
            xml_front = xml_tree.find("front") 

        # Test whether the title has been parsed correctly
        self.assertIsInstance( node.title , rfc.Title )
        self.assertIsInstance( node.title.content, rfc.Text )
        self.assertIsInstance( node.title.content.content, str )
        self.assertEqual( node.title.content.content.lstrip().rstrip() , 
                "Describing Protocol Data Units with Augmented Packet Header Diagrams")


        # Test seriesInfo elements
        self.assertIsInstance( node.seriesInfo , list )
        xml_seriesInfo = [ _sinfo for _sinfo in xml_front.findall("seriesInfo") ]

        # uniquely named seriesInfo elements
        self.assertEqual(len({ si.attrib.get("name") for si in xml_seriesInfo }), len(xml_seriesInfo))
        self.assertEqual( len(xml_seriesInfo), len(node.seriesInfo))


        for idx, (sinfo, xml_sinfo) in enumerate(zip(node.seriesInfo, xml_seriesInfo)):
            self.assertIsInstance(sinfo, rfc.SeriesInfo, msg=f"rfc-front seriesInfo item-{idx} type -> {type(sinfo)}")
            self._check_seriesInfo(sinfo, xml_sinfo)

        # seriesInfo Cross-check
        xml_drafts = [ d for d in filter( lambda x: x.attrib.get("name") == "Internet-Draft" , xml_seriesInfo ) ] 
        xml_rfc = [ rfc for rfc in filter( lambda x: x.attrib.get("name") == "RFC" , xml_seriesInfo ) ] 
        if len(xml_drafts) > 0 : 
            self.assertEqual(len(xml_rfc),0)  # RFC 7991  2.47.3 (c) 


        # author 
        self.assertIsInstance(node.authors, list)
        xml_author_list = [ author for author in xml_front.findall("author") ]
        self.assertEqual(len(node.authors), len(xml_author_list))

        # Hard-coded author checks 
        authors = [ 
           rfc.Author( org = rfc.Organization(content=rfc.Text("University of Glasgow"), abbrev=None, ascii=None),
                       address = rfc.Address( postal=rfc.Postal([ rfc.Street(content=rfc.Text("School of Computing Science"), 
                                                                             ascii=None),
                                                                  rfc.City(content=rfc.Text("Glasgow"), ascii=None),
                                                                  rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None),
                                                                  rfc.Country(content=rfc.Text("UK"), ascii=None)
                                                                ]),
                                              phone = None, 
                                              facsimile = None, 
                                              email = rfc.Email(content=rfc.Text("sm@smcquistin.uk"), ascii=None),
                                              uri = None), 
                       asciiFullname = None, 
                       asciiInitials = None, 
                       asciiSurname  = None, 
                       fullname      = "Stephen McQuistin", 
                       initials      = "S.",
                       role          = None,
                       surname       = "McQuistin" ), 
           rfc.Author( org = rfc.Organization(content=rfc.Text("University of Glasgow"), abbrev=None, ascii=None),
                       address = rfc.Address( postal=rfc.Postal([ rfc.Street(content=rfc.Text("School of Computing Science"),
                                                                             ascii=None),
                                                                  rfc.City(content=rfc.Text("Glasgow"), ascii=None),
                                                                  rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None),
                                                                  rfc.Country(content=rfc.Text("UK"), ascii=None)
                                                                 ]),
                                              phone = None, 
                                              facsimile = None, 
                                              email = rfc.Email(content=rfc.Text("vivianband0@gmail.com"), ascii=None),
                                              uri = None), 
                        asciiFullname = None, 
                        asciiInitials = None, 
                        asciiSurname  = None, 
                        fullname      = "Vivian Band", 
                        initials      = "V.",
                        role          = None,
                        surname       = "Band" ), 
           rfc.Author( org = rfc.Organization(content=rfc.Text("University of Glasgow"), abbrev=None, ascii=None),
                       address = rfc.Address( postal=rfc.Postal([ rfc.Street(content=rfc.Text("School of Computing Science"), 
                                                                             ascii=None),
                                                                  rfc.City(content=rfc.Text("Glasgow"), ascii=None),
                                                                  rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None),
                                                                  rfc.Country(content=rfc.Text("UK"), ascii=None)
                                                                 ]),
                                              phone = None, 
                                              facsimile = None, 
                                              email = rfc.Email(content=rfc.Text("d.jacob.1@research.gla.ac.uk"), ascii=None),
                                              uri = None), 
                        asciiFullname = None, 
                        asciiInitials = None, 
                        asciiSurname  = None, 
                        fullname      = "Dejice Jacob", 
                        initials      = "D.",
                        role          = None,
                        surname       = "Jacob" ), 
           rfc.Author( org = rfc.Organization(content=rfc.Text("University of Glasgow"), abbrev=None, ascii=None),
                       address = rfc.Address( postal=rfc.Postal([ rfc.Street(content=rfc.Text("School of Computing Science"),
                                                                             ascii=None),
                                                                  rfc.City(content=rfc.Text("Glasgow"), ascii=None),
                                                                  rfc.Code(content=rfc.Text("G12 8QQ"), ascii=None),
                                                                  rfc.Country(content=rfc.Text("UK"), ascii=None)
                                                                ]),
                                              phone = None, 
                                              facsimile = None, 
                                              email = rfc.Email(content=rfc.Text("csp@csperkins.org"), ascii=None),
                                              uri = None), 
                       asciiFullname = None, 
                       asciiInitials = None, 
                       asciiSurname  = None, 
                       fullname      = "Colin Perkins", 
                       initials      = "C. S.",
                       role          = None,
                       surname       = "Perkins" ) ]

        self.assertEqual( authors, node.authors )

        # Check each author individually against xml document 
        for author, xml_node in  zip(node.authors, xml_author_list ): 
            self._check_author( author, xml_node )


        # abstract 

    def _check_seriesInfo(self, node , xml_node ):
        self.assertIsNone(xml_node.text)

        # name - mandatory attribute
        name = xml_node.attrib.get("name", None)
        self.assertIsNotNone( name )
        self.assertEqual(name, node.name)
        self.assertEqual(node.name, node.asciiName)
        self.assertIn(node.name, ["RFC", "Internet-Draft", "DOI"])

        # value - mandatory attribute
        value = xml_node.attrib.get("value", None)
        self.assertIsNotNone( value )
        self.assertEqual(value, node.value)
        self.assertEqual(node.value, node.asciiValue)

        # status - optional attribute
        status = xml_node.attrib.get("status", None)
        if status is not None : 
            self.assertIsNotNone( node.status ) 
            self.assertEqual(status, node.status)
            self.assertIn(node.status, ["standard", "informational", "experimental", "bcp", "fyi", "full-standard" ])
        else :
            self.assertIsNone( node.status )


        ## stream - optional attribute
        #stream = xml_node.attrib.get("stream", None)
        #self.assertIsNotNone( node.stream ) 
        #if stream is not None : 
        #    self.assertEqual(stream, node.stream)
        #    self.assertIn(node.stream, ["IETF", "IAB", "IRTF", "independent"])
        #else :
        #    self.assertEqual( node.stream, "IETF")

        # DJ-bypass stream - optional attribute
        stream = xml_node.attrib.get("stream", None)
        if stream is not None : 
            self.assertIsNotNone( node.stream ) 
            self.assertEqual(stream, node.stream)
            self.assertIn(node.stream, ["IETF", "IAB", "IRTF", "independent"])
        else :
            self.assertIsNone( node.stream )


    def _check_organization(self, node, xml_node):
        # abbrev
        abbrev = xml_node.attrib.get("abbrev",None)
        if abbrev == None :
            self.assertIsNone(node.abbrev)
        else :
            self.assertIsInstance(node.abbrev,str)
            self.assertEqual(node.abbrev, abbrev)
        
        # ascii
        ascii = xml_node.attrib.get("ascii",None)
        if ascii == None :
            self.assertIsNone(node.ascii)
        else :
            self.assertIsInstance(node.ascii,str)
            self.assertEqual(node.ascii, ascii)

        # check text
        self.assertEqual( xml_node.text, node.content.content )



    def _check_author(self, node, xml_node):
        # organization 
        organizations = xml_node.findall("organization") 
        self.assertLessEqual(len(organizations), 1) 
        if len(organizations) > 0 : 
            self._check_organization(node.org , organizations[0])


        # address
        addr = xml_node.findall("address") 
        self.assertLessEqual(len(addr), 1) 
        if len(addr) > 0 : 
            self._check_address(node.address , addr[0])

        # asciiFullname
        asciiFullname = xml_node.attrib.get("asciiFullname", None)
        if asciiFullname is None :
            self.assertIsNone( node.asciiFullname )
        else : 
            self.assertIsNotNone( node.asciiFullname )
            self.assertIsInstance( node.asciiFullname, str )
            self.assertEqual( asciiFullname, node.asciiFullname )

        # asciiInitials
        asciiInitials = xml_node.attrib.get("asciiInitials", None)
        if asciiInitials is None :
            self.assertIsNone( node.asciiInitials )
        else : 
            self.assertIsNotNone( node.asciiInitials )
            self.assertIsInstance( node.asciiInitials, str )
            self.assertEqual( asciiFullname, node.asciiInitials )

        # asciiSurname
        asciiSurname = xml_node.attrib.get("asciiSurname", None)
        if asciiSurname is None :
            self.assertIsNone( node.asciiSurname )
        else : 
            self.assertIsNotNone( node.asciiSurname )
            self.assertIsInstance( node.asciiSurname, str )
            self.assertEqual( asciiSurname, node.asciiSurname )

        # fullname 
        fullname = xml_node.attrib.get("fullname", None)


        if asciiFullname is not None or asciiInitials is not None or asciiSurname is not None : 
               self.assertIsNotNone(fullname)

        # initials 
        initials = xml_node.attrib.get("initials", None)
        if initials is not None :
            self.assertEqual(node.initials, initials)
        else : 
            self.assertIsNone(node.initials)

        # role 
        role = xml_node.attrib.get("role", None)
        if role is not None :
            self.assertEqual(node.role, "editor")
        else : 
            self.assertIsNone(node.role)

        # surname 
        surname = xml_node.attrib.get("surname", None)
        if surname is not None :
            self.assertEqual(node.surname, surname)
        else : 
            self.assertIsNone(node.surname)



    def _check_address(self, node, xml_node):
        #postal 

        #phone 
        phones = xml_node.findall("phone")
        self.assertLessEqual(len(phones), 1) 
        if len(phones) > 0 :
            self.assertIsInstance(node.phone, rfc.Phone)
            self.assertEqual(node.phone.content.content, phones[0].text)
        else :
            self.assertIsNone(node.phone)

        #facsimile
        fax = xml_node.findall("facsimile")
        self.assertLessEqual(len(fax), 1) 
        if len(fax) > 0 :
            self.assertIsInstance(node.facsimile, rfc.Facsimile)
            self.assertEqual(node.facsimile.content.content, fax[0].text)
        else :
            self.assertIsNone(node.facsimile)

        #email
        emails = xml_node.findall("email")
        self.assertLessEqual(len(emails), 1) 
        if len(emails) > 0 :
            self.assertIsInstance(node.email, rfc.Email)
            self.assertEqual(node.email.content.content, emails[0].text)

            ascii = emails[0].attrib.get("ascii",None)
            if ascii == None :
                self.assertIsNone(node.email.ascii)
            else:
                self.assertIsInstance(node.email.ascii, str)
                self.assertEqual(node.email.ascii, ascii)
        else :
            self.assertIsNone(node.email)


        #uri
        uris = xml_node.findall("uri")
        self.assertLessEqual(len(uris), 1) 
        if len(uris) > 0 :
            self.assertIsInstance(node.uri, rfc.Email)
            self.assertEqual(node.uri.content.content, uris[0].text)
        else :
            self.assertIsNone(node.uri)
