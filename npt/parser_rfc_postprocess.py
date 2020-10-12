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

#import abc
#from typing       import Dict, List, Tuple, Optional, Any, Union
#from npt.protocol import Protocol

from typing       import Dict
import npt.rfc as rfc
import npt.protocol
import npt.parser_asciidiagrams as ascii_parser


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
            if field is None :   # check if optional 
                #print(f"1. ####### key {name}  is Optional\n") 
                pass
            elif self.isiterable(field): # check if iterable 
                #print(f"2. ####### key {name}  is iterable\n") 
                for item in field :
                    #print(f">>>>>>>>> key {name} visiting {type(item)} \n") 
                    self.visit(item)
            else : # check object type which needs to be recursed 
                #print(f"3. ####### key {name}  is {type(field)} \n") 
                self.visit(field)

class TraverseRFC(NodeVisitor):
    def __init__(self, root, symbols):
        self.root = root 
        self.sym = symbols

        asciiParser = ascii_parser.AsciiDiagramsParser()
        asciiParser.proto = npt.protocol.Protocol()
        self.parser = asciiParser.build_parser()

    def visit_RFC(self, node ):
        self.generic_visit(node)

    def visit_Middle(self, node):
        self.generic_visit(node)

    def visit_Section(self,node):
        self.generic_visit(node)
        xform_dl: List[Tuple[int,rfc.DL]] = [] 

        flag = False
        for pdu_grp in reversed(self._group_pdu(node)):
            self._convert_to_pdu(node, pdu_grp)
            flag = True

        if flag : 
            print(f"\n\n-----------AFTER CONVERSION BEGIN :--------------") 
            for idx,child in enumerate(node.content): 
                if not isinstance(child,rfc.DL): 
                    print(f"[{idx}] ******\n{child}") 
                else: 
                    for i,dl in enumerate(child.content):
                        print(f"  [{idx}.{i}] -> dt = {dl[0]}") 
                        print(f"  [{idx}.{i}] -> dd = {dl[1]}") 
            print(f"-----------AFTER CONVERSION END :-------------\n\n")

    def _group_pdu(self, section):
        start = anchor = None
        rawPDU = [] # start-idx, end-idx+1 , art-work node

        for idx, child in enumerate(section.content): 
            if isinstance(child, rfc.Artwork):
                if anchor != None : # more than one artwork 
                    rawPDU.append((start, idx, anchor))
                start, anchor = (idx, child)
        else :
            if anchor != None : 
                rawPDU.append((start, idx+1, anchor))
        return rawPDU


    def _convert_to_pdu(self, section, action):
        start, end, artWork = action
        # assert guard conditions 
        if not isinstance(section.content[start], rfc.Artwork) \
           or not isinstance(section.content[start].content, rfc.Text):
            return
        artwork = section.content[start].content.content

        if start == (end-1) \
           or not isinstance(section.content[start+1], rfc.T) \
           or len(section.content[start+1].content) != 1 : 
            return 

        where = section.content[start+1].content[0].content.strip().split() 
        if len(where) != 1 or where[0] != "where:" :
            return

        # Parse out all field names
        try: 
            artwork_fields = self.parser(artwork.strip()).diagram() 
            #print(f"Diagram ->\n{artwork}\n-----------------\nArt Fields -> {artwork_fields}")
        except Exception as e:
            return

        # verify  number of field descriptions match list of fields
        if (end - start) < (len(artwork_fields) + 2):
            #print(f"ASSERT--ASSERT --> ({end}-{start}) < {len(artwork_fields)}+2")
            return

        # parse each <t> element and convert to (<dt>, <dd>) pairs
        field_desc, consumed = [], 0
        try: 
            for elem_t in section.content[start+2:end]:
                if len(field_desc) == len(artwork_fields): 
                    break 

                # check paragraph description is a <t> element
                if not isinstance(elem_t, rfc.T) \
                   or len(elem_t.content) != 1 \
                   or not isinstance(elem_t.content[0], rfc.Text):
                    raise Exception(f"Expected rfc.T element. Found {type(elem_t)} -->  {elem_t}")

                text = elem_t.content[0].content
                try : 
                    delim = text.index(". ")
                except ValueError as vexcpt: 
                    delim = text.index(".")

                # check if current <t> section is a new field description or 
                if (len(text) - len(text.lstrip())) == len( self.sym['tab']): 
                    field_desc.append( (rfc.DT([rfc.Text( text[:delim+1])], None), 
                                        rfc.DD([rfc.Text( text[delim+1:])], None)) ) 
                elif len(field_desc) > 0 :
                    if isinstance(field_desc[-1][1].content[0], rfc.Text): 
                        # convert to list of <t> elements
                        field_desc[-1][1].content[0] = rfc.T( [field_desc[-1][1].content[0]], None, None, False, False)
                        #assert False, f"1. Are we here yet? text = {text}\n<T> = {field_desc[-1][1].content[0]}\n</T>\ntype = {type(field_desc[-1][1].content[0])}"
                    # generate <t> element and append to previous PDU desc <dd> 
                    field_desc[-1][1].content.append( rfc.T( [rfc.Text(text)], None, None, False, False))
                else :
                    raise Exception(f"Formatting error in PDU description."
                                    f"Field name description does not start with correct indentation. Text = \n"
                                    f"{text}")
                consumed+=1
        except Exception as e:
            #print(f"\n\n<><><><><><><><><>\n<><><><><><><><><>\n<><><><><><><><><>\n<><><><><><><><><>\n{e}")
            #print(f"<><><><><><><><><>\n<><><><><><><><><>\n<><><><><><><><><>\n<><><><><><><><><>\n")
            return

        section.content.insert(start+2, rfc.DL( field_desc, None , True , "normal")) 
        section.content = section.content[:start+3] + section.content[start+3+consumed:]
        return


# Convert relevant <t> elements to <dl> 
def text_to_dl( root_node: rfc , symbols: Dict[str,str]) -> rfc : 
    postProcess = TraverseRFC(root_node.middle, symbols )
    postProcess.visit(root_node.middle)
    #assert False, "We are here"
    return root_node 
