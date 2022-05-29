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


# =================================================================================================
# The Lark grammar for a textual format RFC or Internet-draft:

grammar = r"""
_BOM                  : "\uFFFE" | "\uFEFF"

_WS                   : "\t" | " "

_NEWLINE              : "\n" | "\r\n"

_BLANKLINE            : _WS+ _NEWLINE
                      | _NEWLINE

ALPHANUM               : /\w/+

NUMBER                : ("0".."9")+

PUNCTUATION           : ( "." | "," | ":" | ";" | "+" | "-" | "(" | ")" | "{" | "}" | "^" 
                        | "/" | "*" | "?" | "@" | "|" | ">" | "<" | "'" | "\"" | "_" 
                        | "[" | "]" | "=" | "!" | "~" | "&" )+

TEXT                  : (ALPHANUM | PUNCTUATION | " ")+ 

AUTHOR_OR_AFFILIATION : ALPHANUM (ALPHANUM | "." | "," | "-" | " ")+

ORGANISATION          : "Internet Engineering Task Force (IETF)"

CATEGORY              : "Standards Track"

DAY                   : "1"

MONTH                 : "January"
                      | "February"
                      | "March"
                      | "April"
                      | "May"
                      | "June"
                      | "July"
                      | "August"
                      | "September"
                      | "October"
                      | "November"
                      | "December"

YEAR                  : ("0".."9")+

author_or_affiliation : AUTHOR_OR_AFFILIATION

organisation          : ORGANISATION 

header_group          : organisation _WS+ author_or_affiliation _NEWLINE

rfc_num               : "Request for Comments:" _WS INT

header_rfc_num        : rfc_num  _WS+ author_or_affiliation _NEWLINE

category              : "Category:" _WS CATEGORY

header_category       : category _WS+ author_or_affiliation _NEWLINE

header_issn           : "ISSN: 2070-1721" _WS+ author_or_affiliation _NEWLINE

header_author         : _WS+ author_or_affiliation _NEWLINE

header_day            : DAY

header_month          : MONTH

header_year           : YEAR 

header_date           : _WS+ (header_day _WS)? header_month _WS header_year _NEWLINE

header_date_author    : header_date
                      | header_author header_date_author

header_rfc            : header_group header_rfc_num header_category header_issn header_date_author

header_block          : header_rfc _BLANKLINE+

TITLE                 : ("a".."z" | "A".."Z" | ":" | "-" | " ")+

title                 : _WS+ TITLE _NEWLINE _BLANKLINE+

TEXTLINE              : "   " TEXT _NEWLINE

t                     : TEXTLINE+ _BLANKLINE+

abstract              : "Abstract"            _NEWLINE _BLANKLINE t+

status_of_this_memo   : "Status of This Memo" _NEWLINE _BLANKLINE t+

copyright             : "Copyright Notice"    _NEWLINE _BLANKLINE t+

table_of_contents     : "Table of Contents"   _NEWLINE _BLANKLINE t+

front                 : _BOM? _BLANKLINE+ header_block title abstract status_of_this_memo copyright table_of_contents



li_head               : "   *" _WS+ TEXT _NEWLINE

li_cont               : TEXTLINE+ 

li                    : li_head li_cont* _BLANKLINE+

ul                    : li+

section_header        : (NUMBER ".")+ _WS+ TEXT _NEWLINE _BLANKLINE

section_body          : (t | ul)+

section               : section_header section_body

middle                : section+



ref_header            : NUMBER "." _WS+ "References" _NEWLINE _BLANKLINE

REF_ID                : (ALPHANUM | "-")+

ref_label             : "[" REF_ID "]" _NEWLINE?

REF_TEXT              : /[^[]/ (ALPHANUM | PUNCTUATION | " ")+ 

ref_line              : _WS+ REF_TEXT _NEWLINE 

ref_text              : ref_line+ (_BLANKLINE ref_line)? _BLANKLINE

ref                   : _WS+ ref_label ref_text

nref_header           : (NUMBER ".")+ _WS+ "Normative References" _NEWLINE _BLANKLINE

nrefs                 : nref_header ref+

iref_header           : (NUMBER ".")+ _WS+ "Informative References" _NEWLINE _BLANKLINE

irefs                 : iref_header ref+

references            : ref_header nrefs* irefs*



appendix_header_top   : "Appendix " "A".."Z" "." _WS+ TEXT _NEWLINE

appendix_header_sub   : "A".."Z" "." (NUMBER ".")+  _WS+ TEXT _NEWLINE

appendix_header       : appendix_header_top _BLANKLINE
                      | appendix_header_sub _BLANKLINE

appendix              : appendix_header section_body



contributors_header   : "Contributors" _NEWLINE _BLANKLINE

contributors          : contributors_header section_body


_AUTHORS_HEADER       : "Authors' Addresses" _NEWLINE _BLANKLINE

author_name           : _WS+ AUTHOR_OR_AFFILIATION

author_role           : "(" ALPHANUM ")"

author_affiliation    : _WS+ AUTHOR_OR_AFFILIATION _NEWLINE

author_email          : _WS+ "Email: " TEXT _NEWLINE

author                : author_name author_role? _NEWLINE author_affiliation _BLANKLINE? author_email _BLANKLINE*

authors               : _AUTHORS_HEADER author+


back                  : references appendix* contributors? authors


ANYTHING              : (/./ | _NEWLINE)+ 

rfc                   : front middle back

%import common.INT
"""

# =================================================================================================

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


def load_txt(content: str) -> Document:
    parser = Lark(grammar, start = "rfc")

    tree  = parser.parse(content)
    nodes = _load_tree(tree)
    assert len(nodes) == 1
    doc = Document(nodes[0])
    _rewrite_front(doc)
    return doc


