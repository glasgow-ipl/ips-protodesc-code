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
from pathlib       import Path
from lark          import Lark, Tree, Token

from npt2.document import Node, Document


def _load_tree(tree: Tree, parent: Optional[Node]) -> List[Node]:
    node = Node(tree.data, parent)

    only_has_text = True
    combined_text = ""
    for elem in tree.children:
        if isinstance(elem, Tree):
            only_has_text = False
        else:
            combined_text += elem

    if only_has_text:
        node.add_text(combined_text)
    else:
        for elem in tree.children:
            if isinstance(elem, Tree):
                for child in _load_tree(elem, node):
                    node.add_child(child)
            if isinstance(elem, Token):
                text = Node(node, "text")
                text.add_text(elem)
                node.add_child(text)
    return [node]


def load_rfc_txt(rfc_txt_file : Path) -> Document:
    with open("npt2/loader_rfc_txt.lark") as grammar:
        parser = Lark(grammar, start = "rfc")

        with open(rfc_txt_file, "r") as inf:
            lines = inf.read()
            tree  = parser.parse(lines)
            nodes = _load_tree(tree, None)
    assert len(nodes) == 1
    doc = Document(nodes[0])
    return doc


