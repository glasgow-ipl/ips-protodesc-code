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

from typing import Union, Optional, List

def iter_child(node): 
    if getattr(node, "__annotations__", None) == None : 
        return 

    for field in  node.__annotations__ : 
        try : 
            yield field, getattr(node, field) 
        except AttributeError : 
            pass


class NodeVisitor:
    def isiterable(self, node):
        try : 
            k = iter(node)
        except TypeError as expt :
            return False 
        else : 
            return True

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
            elif self.isiterable(field):
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





class TraverseRFC(NodeVisitor):
    def __init__(self, root):
        self.root = root 
        self.stack = [] 

    def _field_name(self,node):
        pass

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
        print(f"type text ->  {node.content}")
        self.generic_visit(node)


class Test_xml_input(unittest.TestCase):
    def setUp(self):
        with open("examples/draft-mcquistin-augmented-ascii-diagrams.xml" , 'r') as example_file:
            raw_content = example_file.read()
            xml_tree = ET.fromstring(raw_content)
            self.content = npt.parser_rfc_xml.parse_rfc(xml_tree)
            self.xml_tree = xml_tree


    def test_toplevel(self):
        #for k in self.content.__annotations__ :
        #    print(f" key {k} ->  {self.content.__annotations__.get(k , None)}   ---> {type(self.content.__annotations__.get(k , None))}")

        k = TraverseRFC(self.content)
        k.visit(self.content)
        #TODO
