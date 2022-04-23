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
from typing     import Dict, List, Optional

class Node:
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


    def add_attribute(self, key: str, value: str) -> None:
        assert key not in self._attributes
        self._attributes[key] = value


    def add_child(self, child: Node) -> None:
        assert self._text is None
        self._children.append(child)


    def add_text(self, text: str) -> None:
        assert self._children == []
        assert self._text is None
        self._text = text


    def __str__(self) -> str:
        s = f"<{self._tag}"
        for k,v in self._attributes.items():
            s = f"{s} {k}={v}"
        s = f"{s}>"
        if self._text is None:
            for child in self._children:
                s = f"{s}\n{child}"
        else:
            s = f"{s}{self._text}"
        s = f"{s}\n</{self._tag}>"
        return s



class Document:
    root : Node

    def __init__(self, root: Node) -> None:
        self.root = root


