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
import npt.parser_rfc_txt
import npt.parser_rfc_xml

from npt.parser               import Parser
from npt.parser_asciidiagrams import AsciiDiagramsParser

from typing import Union, Optional, List, Tuple

def iter_child(node):
    if getattr(node, "__annotations__", None) == None :
        return

    for field in  node.__annotations__ :
        try :
            yield field, getattr(node, field)
        except AttributeError :
            pass

def isiterable(node):
    if isinstance(node , str):
        return False

    try :
        k = iter(node)
    except TypeError as expt :
        return False
    else :
        return True

class NodeTypeVisitor:
    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        #print(f"calling  {method} ---> {visitor}")
        return visitor(node)

    def generic_visit(self, node):
        for name, field in iter_child( node ):
            #print(f"key [{name}]  -> field {type(field)}")
            if field is None :
                #print(f"1. ####### key {name}  is Optional\n")
                pass
            elif isiterable(field):
                #print(f"2. ####### key {name}  is iterable\n")
                for item in field :
                    #print(f">>>>>>>>> key {name} visiting {type(item)} \n")
                    self.visit(item)
            else :
                #print(f"3. ####### key {name}  is {type(field)} \n")
                self.visit(field)
            # check if optional
            # check if iterable
            # check object type which needs to be recursed



class TraverseRFCType(NodeTypeVisitor):
    def __init__(self, root):
        self.root = root
        self.stack = []

    def generic_visit(self, node):
        self.stack.append(node)
        super().generic_visit(node)
        self.stack.pop()

    def visit_RFC(self, node ):
        #print(f"RFC --> type =  {type(node)}\n")
        self.generic_visit(node)


    def visit_Front(self, node):
        print(f"front material -> {node}")
        self.generic_visit(node)

    def visit_Text(self,node):
        #print(f"type text ->  {node.content}")
        self.generic_visit(node)



class Test_XML_Input(unittest.TestCase, NodeTypeVisitor):
    def setUp(self):
        self.stack = []
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as example_file:
            raw_content = example_file.read()
            xml_tree = ET.fromstring(raw_content)
            self.content = npt.parser_rfc_xml.parse_rfc(xml_tree)
            self.xml_tree = xml_tree

    def generic_visit(self,node):
        self.stack.append(node)
        super().generic_visit(node)
        self.stack.pop()

    def visit_RFC(self, node ):
        # Test URLs and links have been extracted correctly
        links = [ npt.rfc.Link(child.attrib["href"], child.attrib.get("rel", None))
                        for child in self.xml_tree.findall("link")]
        href_sort = lambda x : x.href
        links.sort(key = href_sort)

        rfc_links = node.links.copy()
        rfc_links.sort(key=href_sort)

        self.assertEqual(len(links), len(rfc_links))
        self.assertEqual(links, rfc_links)

        # Test all optional attributes

        # category -- deprecated in rfc7991 (v3)
        # backwards compatibility
        category = self.xml_tree.attrib.get("category", None)
        if category is None :
            self.assertIsNone( node.category )
        else :
            self.assertIsNotNone( node.category )
            self.assertIsInstance( category, str)
            self.assertIn( category, [ "std", "bcp", "info", "exp", "historic" ])

        # consensus
        consensus = self.xml_tree.attrib.get("consensus", None)
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
        docName = self.xml_tree.attrib.get("docName", None)
        if docName is not None :
            self.assertIsNotNone(node.docName)
            self.assertIsNone(node.number) # if docName is provided number should be None
            self.assertIsInstance(node.docName, str)
            self.assertEqual(docName,node.docName)

        number = self.xml_tree.attrib.get("number", None)
        if number is not None :
            self.assertIsNotNone(node.number)
            self.assertIsNone(node.docName) # if number is provided docName should be None
            self.assertIsInstance(node.number, str)
            self.assertEqual(docName,node.docName)


        # indexInclude
        indexInclude = self.xml_tree.attrib.get("indexInclude", None)
        if indexInclude is None :
            self.assertTrue(node.indexInclude)
        else :
            self.assertIn( indexInclude, ["true", "false"], msg=f"RFC indexInclude not a boolean. Input file error" )
            if indexInclude == "true" :
                self.assertTrue( node.indexInclude )
            else :
                self.assertFalse( node.indexInclude )

        # ipr
        ipr = self.xml_tree.attrib.get("ipr", None)
        if ipr is None :
            self.assertIsNone(node.ipr)
        else :
            self.assertIsInstance(node.ipr, str)
            self.assertEqual(ipr, node.ipr)

        # iprExract
        iprExtract = self.xml_tree.attrib.get("iprExtract", None)
        if iprExtract is None :
            self.assertIsNone(node.iprExtract)
        else :
            self.assertIsInstance(node.iprExtract, str)
            self.assertEqual(iprExtract, node.iprExtract)

        # obsoletes
        obsoletes = self.xml_tree.attrib.get("obsoletes", None)
        if obsoletes is None :
            self.assertIsNone(node.obsoletes)
        else :
            self.assertIsInstance(node.obsoletes, str)
            self.assertEqual(obsoletes, node.obsoletes)

        # prepTime
        prepTime = self.xml_tree.attrib.get("prepTime", None)
        if prepTime is None :
            self.assertIsNone(node.prepTime)
        else :
            self.assertIsInstance(node.prepTime, str)
            self.assertEqual(prepTime, node.prepTime)
            # TO DO : add time formatting check - format is ISO format rfc3339

        # seriesNo
        seriesNo = self.xml_tree.attrib.get("seriesNo", None)
        if seriesNo is None :
            self.assertIsNone(node.seriesNo)
        else :
            self.assertIsInstance(node.seriesNo, str)
            self.assertEqual(seriesNo, node.seriesNo)


        # sortRefs
        sortRefs = self.xml_tree.attrib.get("sortRefs", None)
        self.assertIsInstance( node.sortRefs , bool)
        if sortRefs in [ None, "false" ]:
            self.assertFalse( node.sortRefs )
        elif consensus == "true" :
            self.assertTrue( node.sortRefs )
        else :
            self.assertIn( consensus, ["false", "true"], f"unexpected sortRefs -- {sortRefs}")

        # submissionType
        submissionType = self.xml_tree.attrib.get("submissionType", None)
        self.assertIsNotNone( node.submissionType )
        self.assertIsInstance( node.submissionType , str)
        if submissionType is None :
            self.assertEqual( node.submissionType , "IETF")
        else :
            self.assertEqual( submissionType, node.submissionType )
            self.assertIn( node.submissionType, [ "IETF", "IAB", "IRTF", "independent"] )

        # symRefs
        symRefs = self.xml_tree.attrib.get("symRefs", None)
        self.assertIsInstance( node.symRefs , bool)
        if symRefs in [ None, "true" ]:
            self.assertTrue( node.symRefs )
        elif symRefs == "false" :
            self.assertFalse( node.symRefs )
        else :
            self.assertIn( symRefs, ["false", "true"], f"unexpected symRefs -- {symRefs}")


        # tocDepth
        tocDepth = self.xml_tree.attrib.get("tocDepth", None)
        #self.assertIsInstance(node.tocDepth, str)
        if tocDepth is None :
            #self.assertEqual(node.tocDepth, "3" )
            pass
        else :
            #self.assertEqual(tocDepth, node.tocDepth)
            pass

        # tocInclude
        tocInclude = self.xml_tree.attrib.get("tocInclude", None)
        self.assertIsInstance( node.tocInclude , bool)
        if tocInclude in [ None, "true" ]:
            self.assertTrue( node.tocInclude )
        elif symRefs == "false" :
            self.assertFalse( node.tocInclude )
        else :
            self.assertIn( symRefs, ["false", "true"], f"unexpected tocInclude -- {tocInclude}")


        # updates
        updates = self.xml_tree.attrib.get("updates", None)
        if updates is None :
            self.assertIsNone( node.updates )
        else :
            self.assertIsNotNone( node.updates )
            self.assertIsInstance( node.updates , str)
            self.assertEqual( updates, node.updates )

        # version
        version = self.xml_tree.attrib.get("version", None)
        if version is None :
            self.assertIsNone( node.version )
        else :
            self.assertIsNotNone( node.version )
            self.assertIsInstance( node.version , str)
            self.assertEqual( version, node.version )

        self.generic_visit(node)




    def visit_Front(self, node):
        if len(self.stack) == 1 and isinstance(self.stack[0], npt.rfc.RFC) :
            # Test only immediate leaf nodes
            front = self.xml_tree.tag
            #print(f"parent rfc type is  -> {type(self.stack[0])}")
        self.generic_visit(node)

    #def test_links(self):
        #for k in self.content.__annotations__ :
        #    print(f" key {k} ->  {self.content.__annotations__.get(k , None)}   ---> {type(self.content.__annotations__.get(k , None))}")
        #print(f"links = {links}")

        #k = TraverseRFCField(self.content, self.xml_tree)
        #k = TraverseRFCType(self.content)

    def test_rfc(self):
        self.visit(self.content)

    def tearDown(self):
        del(self.stack)

