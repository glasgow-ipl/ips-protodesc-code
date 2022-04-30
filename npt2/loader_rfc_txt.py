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

from typing        import List, Union, Optional, Tuple, Dict, Iterator
from pathlib       import Path
from lark          import Lark, Tree, Token

from npt2.document import Node, Document


def _load_tree(tree: Tree) -> List[Node]:
    node = Node(tree.data)

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
                for child in _load_tree(elem):
                    node.add_child(child)
            if isinstance(elem, Token):
                text = Node("text")
                text.add_text(elem)
                node.add_child(text)
    return [node]


def _extract_authors(doc: Document) -> Iterator[Node]:
    # Are these useful?
    aa_list = []
    for aa in doc.root().children(tag="author_or_affiliation", recursive=True):
        aa_list.append(aa.text)

    for a in doc.root().children(tag="author", recursive=True):
        name        = a.child("author_name").text()
        affiliation = a.child("author_affiliation").text()
        email_addr  = a.child("author_email").text()

        organisation = Node("organization")
        organisation.add_attribute("showOnFrontPage", "true")
        if affiliation is not None:
            organisation.add_text(affiliation)

        email = Node("email")
        assert email_addr is not None
        email.add_text(email_addr)

        address = Node("address")
        address.add_child(email)

        author = Node("author")
        if name is not None:
            author.add_attribute("fullname", name.strip())
        author.add_child(organisation)
        author.add_child(address)

        role = a.children(tag="author_role", recursive=False)
        if len(role) > 0:
            role_text = role[0].text()
            if role_text is not None:
                author.add_attribute("role", role_text)

        yield author


def _rewrite_front(doc: Document) -> None:
    front = Node("front")
    for author in _extract_authors(doc):
        front.add_child(author)
    # FIXME: remove old front element from the document
    # FIXME: add new front element to the document


def load_rfc_txt(rfc_txt_file : Path) -> Document:
    with open("npt2/loader_rfc_txt.lark") as grammar:
        parser = Lark(grammar, start = "rfc")

        with open(rfc_txt_file, "r") as inf:
            lines = inf.read()
            tree  = parser.parse(lines)
            nodes = _load_tree(tree)
    assert len(nodes) == 1
    doc = Document(nodes[0])
    _rewrite_front(doc)
    return doc


