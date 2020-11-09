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

from typing       import Dict, List, Tuple, Optional, Union, cast, Any
import npt.rfc as rfc
import npt.protocol
import npt.parser_asciidiagrams as ascii_parser


def iter_child(node): 
    """
    Iterate over all the child elements in classes
    decorated with @dataclass
    """
    if getattr(node, "__annotations__", None) == None : 
        return 

    for field in  node.__annotations__ : 
        try : 
            yield field, getattr(node, field) 
        except AttributeError : 
            pass


class NodeVisitor:
    """
    Base class that walks the DOM structure and calls a visitor function
    on eah function type. 

    This class should be sub-classed by to over-ride default behaviour. 
    A visitor function may be overridden in the inherited class by defining
    a method with the name `visit_<class-type>'. 
    
    Assumes that all classes in the DOM structure are data-classes 
    i.e. decorated with @dataclass
    """
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
        return visitor(node) 

    def generic_visit(self, node):
        for name, field in iter_child( node ):
            if field is None :   # check if optional 
                pass
            elif self.isiterable(field): # check if iterable 
                for item in field :
                    self.visit(item)
            else : # check object type which needs to be recursed 
                self.visit(field)

class TraverseRFC(NodeVisitor):
    """
    DOM walker class to post-process Sections parsed by the RFC text parser.
    The content in all (sub)-sections are searched for rfc.Artwork elements. 

    If any field names are found when parsing the  rfc.Artwork element, 
    the following rfc.T elements corresponding to these field descriptions 
    are converted to an rfc.DL element to ensure conformity with later 
    parsing stages. 
    """
    def __init__(self, root, symbols):
        self.root = root 
        self.sym = symbols

        self.asciiParser = ascii_parser.AsciiDiagramsParser()
        self.asciiParser.proto = npt.protocol.Protocol()
        self.parser = self.asciiParser.build_parser()

    def visit_Section(self,node: rfc.Section) -> None:
        self.generic_visit(node)

        for pdu_grp in reversed(self._group_pdu(node)):
            self._convert_to_pdu(node, pdu_grp)

    def _group_pdu(self, section: rfc.Section) -> List[Tuple[Optional[int], int, Optional[rfc.Artwork]]]:
        start = anchor = None
        rawPDU : List[Tuple[Optional[int], int, Optional[rfc.Artwork]]] = list()  # start-idx, end-idx+1 , art-work node

        for idx, child in enumerate(section.content): 
            if isinstance(child, rfc.Artwork):
                if anchor !=  None : # more than one artwork 
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
            artwork_fields = self.asciiParser.process_diagram(artwork, self.parser)
        except Exception as e:
            return

        # verify  number of field descriptions match list of fields
        if (end - start) < (len(artwork_fields) + 2):
            return

        # parse each <t> element and convert to (<dt>, <dd>) pairs
        field_desc: List[Tuple[rfc.DT, rfc.DD]] = list() 
        consumed : int  = 0 
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
                # another paragraph within the current field description
                if (len(text) - len(text.lstrip())) == len( self.sym['tab']): 
                    dt_content = cast( List[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]], [rfc.Text( text[:delim+1])])
                    dd_content = cast(Union[List[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]], 
                                            List[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]]] , 
                                            [rfc.Text( text[delim+1:])])
                    field_desc.append( (rfc.DT(dt_content, None), 
                                        rfc.DD(dd_content, None)) ) 
                elif len(field_desc) > 0 :
                    if isinstance(field_desc[-1][1].content[0], rfc.Text): 
                        # convert to list of <t> elements
                        elem_t = cast( Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef], rfc.T( [field_desc[-1][1].content[0]] , None, None, False, False))
                        field_desc[-1][1].content[0] = elem_t
                       
                    # generate <t> element and append to previous PDU desc <dd> 
                    elem_t = cast( Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef], rfc.T( [rfc.Text(text)], None, None, False, False))
                    field_desc[-1][1].content.append( elem_t )
                else :
                    raise Exception(f"Formatting error in PDU description."
                                    f"Field name description does not start with correct indentation. Text = \n"
                                    f"{text}")
                consumed+=1
        except Exception as e:
            return

        section.content.insert(start+2, rfc.DL( field_desc, None , True , "normal")) 
        section.content = section.content[:start+3] + section.content[start+3+consumed:]
        return


# Convert relevant <t> elements to <dl> 
def text_to_dl( root_node , symbols: Dict[str,str]): 
    postProcess = TraverseRFC(root_node.middle, symbols )
    postProcess.visit(root_node.middle)
    return root_node 
