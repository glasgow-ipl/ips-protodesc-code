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

from __future__ import annotations
from typing     import Dict, List, Iterator, Optional

class Node:
    _parent     : Optional[Node]
    _tag        : str
    _attributes : Dict[str,str]
    _text       : str              # If self._text != "", len(self._children) == 0
    _children   : List[Node]       # if len(self._children) > 0, self._text == ""

    # ---------------------------------------------------------------------------------------------
    # Methods to initialise and modify a Node:

    def __init__(self, tag) -> None:
        self._tag        = tag
        self._parent     = None
        self._attributes = {}
        self._text       = ""
        self._children   = []


    def add_attribute(self, attribute: str, value: str) -> None:
        assert attribute not in self._attributes
        self._attributes[attribute] = value


    def add_text(self, text: str) -> None:
        assert self._children == []
        assert self._text == ""
        self._text = text


    def add_child(self, child: Node) -> None:
        assert self._text == ""
        assert child._parent is None
        child._parent = self
        self._children.append(child)


    def add_child_after(self, new_child: Node, after: Node) -> None:
        assert self._text == ""
        assert new_child._parent is None
        children = []
        for child in self._children:
            children.append(child)
            if id(child) == id(after):
                new_child._parent = self
                children.append(new_child)
        self._children = children


    def remove_attribute(self, attribute: str) -> None:
        assert attribute in self._attributes
        del self._attributes[attribute]


    def remove_text(self) -> None:
        assert self._text != ""
        self._text = ""


    def replace_text(self, text:str) -> None:
        assert self._text != ""
        self._text = text


    def remove_child(self, remove: Node) -> Node:
        removed  = None
        children = []
        for child in self._children:
            if id(child) != id(remove):
                children.append(child)
            else:
                removed = child
                removed._parent = None
        self._children = children
        assert removed is not None
        return removed


    def replace_child(self, old_child: Node, new_child: Node) -> Node:
        removed  = None
        children = []
        for child in self._children:
            if id(child) == id(old_child):
                new_child._parent = self
                children.append(new_child)
                removed = child
                removed._parent = None
            else:
                children.append(child)
        self._children = children
        assert removed is not None
        return removed

    # ---------------------------------------------------------------------------------------------
    # Methods to query the contents of a Node:

    def has_attribute(self, attribute:str) -> bool:
        return attribute in self._attributes


    def attribute(self, attribute:str) -> str:
        return self._attributes[attribute]


    def attributes(self) -> Dict[str,str]:
        return self._attributes


    def tag(self) -> str:
        assert self._tag is not None
        return self._tag


    def has_text(self) -> bool:
        return self._text != ""


    def text(self, recursive:bool=False) -> str:
        text = self._text
        if recursive:
            for child in self.children(recursive=True):
                text += child.text(recursive=True)
        return text


    def children(self, recursive:bool = False, with_tag:Optional[str] = None) -> List[Node]:
        children = []
        for child in self._children:
            if with_tag is None or child.tag() == with_tag:
                assert child.parent() == self
                children.append(child)
            if recursive:
                for node in child.children(recursive = True, with_tag = with_tag):
                    if with_tag is None or node.tag() == with_tag:
                        children.append(node)
        return children


    def child(self, tag: str) -> Node:
        nlist = self.children(recursive=False, with_tag=tag)
        assert len(nlist) == 1
        return nlist[0]


    def parent(self) -> Optional[Node]:
        return self._parent


# =================================================================================================

class Document:
    _root : Node

    def __init__(self, root: Node) -> None:
        self._root = root


    def root(self) -> Node:
        return self._root


