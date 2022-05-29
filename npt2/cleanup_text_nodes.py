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

from npt2.document import Document, Node

def cleanup_text_nodes(doc: Document, verbose:bool=False) -> None:
    # In the RFC 7991 format, a number of elements have a content model that
    # contains either text or child elements. Find such elements that only
    # contain text, and replace that text with an equivalent <text> element.
    # This ensures that all such elements contain a list of child elements,
    # rather than having some with text and some with child elements.
    cleanup_tags = [
            "annotation",
            "blockquote",
            "xref",
            "dd",
            "dt",
            "em",
            "li",
            "name",
            "refcontent",
            "strong",
            "sub",
            "sup",
            "t",
            "td",
            "th",
            "tt"
        ]

    for tag in cleanup_tags:
        if verbose:
            print(f"Cleaning up <{tag}> nodes")
        for node in doc.root().children(recursive=True, with_tag=tag):
            if node.has_text():
                text = Node("text")
                text.add_text(node.text().replace("\n", " ").strip())
                node.remove_text()
                node.add_child(text)

    # Find the <text> nodes, and collapse unnecessary white space
    if verbose:
        print(f"Cleaning up <text> nodes")
    for tag in cleanup_tags:
        for node in doc.root().children(recursive=True, with_tag=tag):
            first = True
            for child in node.children():
                if child.tag() == "text":
                    if child.text()[0].isspace() and not first:
                        head = " "
                    else:
                        head = ""
                    main = " ".join(child.text().split())
                    if child.text()[-1].isspace():
                        tail = " "
                    else:
                        tail = ""
                    child.replace_text(head + main + tail)
                first = False


