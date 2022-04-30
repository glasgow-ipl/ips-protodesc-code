# =================================================================================================
# Copyright (C) 2022 University of Glasgow
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

from typing        import List, Union, Optional, Tuple, Dict
from lxml          import etree as ET # type: ignore
from pathlib       import Path

from npt2.document import Node, Document

def _load_xml(xmlElement:ET.Element, parent:Optional[Node] = None) -> List[Node]:
    node = Node(xmlElement.tag)

    for k, v in xmlElement.attrib.items():
        node.add_attribute(k, v)

    if xmlElement.text is not None and len(xmlElement.text.strip()) > 0:
        if len(xmlElement) == 0:
            node.add_text(xmlElement.text)
        else:
            text = Node("text")
            text.add_text(xmlElement.text)
            node.add_child(text)

    for elem in xmlElement:
        for child in _load_xml(elem, node):
            assert child.parent() == None
            node.add_child(child)

    if xmlElement.tail is not None and len(xmlElement.tail.strip()) > 0:
        tail = Node("text")
        tail.add_text(xmlElement.tail)
        return [node, tail]
    else:
        return [node]



def load_rfc_xml(rfc_xml_file : Path) -> Document:
    xml   = ET.parse(rfc_xml_file).getroot()
    nodes = _load_xml(xml)
    assert len(nodes) == 1
    return Document(nodes[0])


