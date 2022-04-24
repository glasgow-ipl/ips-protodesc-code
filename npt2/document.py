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
    _depth      : int
    _parent     : Optional[Node]
    _tag        : str
    _attributes : Dict[str,str]
    _text       : Optional[str]    # It is guaranteed that a node will either
    _children   : List[Node]       # have _text or _children, but never both.


    def __init__(self, parent: Optional[Node], tag: str) -> None:
        self._parent     = parent
        self._tag        = tag
        self._attributes = {}
        self._text       = None
        self._children   = []
        if parent is None:
            self._depth = 0
        else:
            self._depth = parent._depth + 1


    def add_attribute(self, attribute: str, value: str) -> None:
        assert attribute not in self._attributes
        self._attributes[attribute] = value


    def add_text(self, text: str) -> None:
        assert self._children == []
        assert self._text is None
        self._text = text


    def add_child(self, child: Node) -> None:
        assert self._text is None
        self._children.append(child)


    def add_child_after(self, new_child: Node, after: Node) -> None:
        children = []
        for child in self._children:
            children.append(child)
            if child.id() == after.id():
                children.append(new_child)
        self._children = children


    def remove_attribute(self, attribute: str) -> None:
        assert attribute in self._attributes
        del self._attributes[attribute]


    def remove_text(self) -> None:
        assert self._text is not None
        self._text = None


    def remove_child(self, remove: Node) -> None:
        children = []
        for child in self._children:
            if child.id() != remove.id():
                children.append(new_child)
        self._children = children


    def replace_child(self, old_child: Node, new_child: Node) -> None:
        children = []
        for child in self._children:
            if child.id() == new_child.id():
                children.append(new_child)
            else:
                children.append(child)
        self._children = children


    def atttribute(self, attribute:str) -> Optional[str]:
        return self._attributes[attribute]


    def tag(self) -> str:
        assert self._tag is not None
        return self._tag


    def text(self) -> str:
        assert self._text is not None
        return self._text


    def children(self) -> Iterator[Node]:
        for child in self._children:
            yield child


    def nodes(self) -> Iterator[Nodes]:
        yield self
        for child in self._children:
            for node in child.nodes():
                yield node


    def find_nodes(self, tag: str) -> Iterator[Node]:
        for node in self.nodes():
            if node.tag() == tag:
                yield node


    def __str__(self) -> str:
        s = ""
        for d in range(self._depth):
            s = f"{s}  "
        s = f"{s}<{self._tag}"
        for k,v in self._attributes.items():
            s = f'{s} {k}="{v}"'
        s = f"{s}>\n"
        if self._text is None:
            for child in self._children:
                s = f"{s}{child}\n"
        else:
            for line in self._text.splitlines():
                for d in range(self._depth + 1):
                    s = f"{s}  "
                s = f"{s}{line}\n"
        for d in range(self._depth):
            s = f"{s}  "
        s = f"{s}</{self._tag}>"
        return s



class Document:
    _root : Node

    def __init__(self, root: Node) -> None:
        self._root = root


    def root(self) -> Node:
        return self._root


    def nodes(self) -> Iterator[Node]:
        for node in self._root.nodes():
            yield node


    def find_nodes(self, tag: str) -> Iterator[Node]:
        for node in self.nodes():
            if node.tag() == tag:
                yield node


