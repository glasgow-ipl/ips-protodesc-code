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

from typing import List as ListType, Union, Optional, Tuple

import sys
import xml.etree.ElementTree as ET

import npt.rfc as rfc


def parse_bcp14(xmlElement: ET.Element) -> rfc.BCP14:
    assert xmlElement.text is not None
    return rfc.BCP14(rfc.Text(xmlElement.text))


def parse_em(xmlElement: ET.Element) -> rfc.EM:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for emChild in xmlElement:
        if emChild.tag == "bcp14":
            content.append(parse_bcp14(emChild))
        elif emChild.tag == "cref":
            content.append(parse_cref(emChild))
        elif emChild.tag == "iref":
            content.append(parse_iref(emChild))
        elif emChild.tag == "relref":
            content.append(parse_relref(emChild))
        elif emChild.tag == "strong":
            content.append(parse_strong(emChild))
        elif emChild.tag == "sub":
            content.append(parse_sub(emChild))
        elif emChild.tag == "sup":
            content.append(parse_sup(emChild))
        elif emChild.tag == "tt":
            content.append(parse_tt(emChild))
        elif emChild.tag == "xref":
            content.append(parse_xref(emChild))
    return rfc.EM(content)


def parse_relref(xmlElement: ET.Element) -> rfc.RelRef:
    assert xmlElement.text is not None
    return rfc.RelRef(rfc.Text(xmlElement.text),
                      xmlElement.attrib.get("displayFormat"),
                      xmlElement.attrib.get("relative"),
                      xmlElement.attrib["section"],
                      xmlElement.attrib["target"])


def parse_eref(xmlElement: ET.Element) -> rfc.ERef:
    if xmlElement.text is not None:
        return rfc.ERef(rfc.Text(xmlElement.text), xmlElement.attrib["target"])
    else:
        return rfc.ERef(None, xmlElement.attrib["target"])


def parse_iref(xmlElement: ET.Element) -> rfc.IRef:
    assert xmlElement.text is not None
    return rfc.IRef(xmlElement.attrib["item"],
                    xmlElement.attrib.get("primary") == "true",
                    xmlElement.attrib.get("subitem"))

def parse_xref(xmlElement: ET.Element) -> rfc.XRef:
    text : Optional[rfc.Text] = None
    if xmlElement.text is not None:
        text = rfc.Text(xmlElement.text)
    return rfc.XRef(text,
                    xmlElement.attrib.get("format"),
                    xmlElement.attrib.get("pageno") == "true",
                    xmlElement.attrib["target"])


def parse_cref(xmlElement: ET.Element) -> rfc.CRef:
    content : ListType[Union[rfc.Text, rfc.EM, rfc.ERef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for crefChild in xmlElement:
        if crefChild.tag == "em":
            content.append(parse_em(crefChild))
        elif crefChild.tag == "eref":
            content.append(parse_eref(crefChild))
        elif crefChild.tag == "relref":
            content.append(parse_relref(crefChild))
        elif crefChild.tag == "strong":
            content.append(parse_strong(crefChild))
        elif crefChild.tag == "sub":
            content.append(parse_sub(crefChild))
        elif crefChild.tag == "sup":
            content.append(parse_sup(crefChild))
        elif crefChild.tag == "tt":
            content.append(parse_tt(crefChild))
        elif crefChild.tag == "xref":
            content.append(parse_xref(crefChild))
    return rfc.CRef(content,
                    xmlElement.attrib.get("anchor", None),
                    xmlElement.attrib.get("display", True) == "true",
                    xmlElement.attrib.get("source", None))


def parse_strong(xmlElement: ET.Element) -> rfc.Strong:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for strongChild in xmlElement:
        if strongChild.tag == "bcp14":
            content.append(parse_bcp14(strongChild))
        elif strongChild.tag == "cref":
            content.append(parse_cref(strongChild))
        elif strongChild.tag == "em":
            content.append(parse_em(strongChild))
        elif strongChild.tag == "eref":
            content.append(parse_eref(strongChild))
        elif strongChild.tag == "iref":
            content.append(parse_iref(strongChild))
        elif strongChild.tag == "relref":
            content.append(parse_relref(strongChild))
        elif strongChild.tag == "sub":
            content.append(parse_sub(strongChild))
        elif strongChild.tag == "sup":
            content.append(parse_sup(strongChild))
        elif strongChild.tag == "tt":
            content.append(parse_tt(strongChild))
        elif strongChild.tag == "xref":
            content.append(parse_xref(strongChild))
    return rfc.Strong(content)


def parse_tt(xmlElement: ET.Element) -> rfc.TT:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for ttChild in xmlElement:
        if ttChild.tag == "bcp14":
            content.append(parse_bcp14(ttChild))
        elif ttChild.tag == "cref":
            content.append(parse_cref(ttChild))
        elif ttChild.tag == "em":
            content.append(parse_em(ttChild))
        elif ttChild.tag == "eref":
            content.append(parse_eref(ttChild))
        elif ttChild.tag == "iref":
            content.append(parse_iref(ttChild))
        elif ttChild.tag == "relref":
            content.append(parse_relref(ttChild))
        elif ttChild.tag == "sub":
            content.append(parse_sub(ttChild))
        elif ttChild.tag == "sup":
            content.append(parse_sup(ttChild))
        elif ttChild.tag == "strong":
            content.append(parse_strong(ttChild))
        elif ttChild.tag == "xref":
            content.append(parse_xref(ttChild))
    return rfc.TT(content)


def parse_sub(xmlElement: ET.Element) -> rfc.Sub:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for subChild in xmlElement:
        if subChild.tag == "bcp14":
            content.append(parse_bcp14(subChild))
        elif subChild.tag == "cref":
            content.append(parse_cref(subChild))
        elif subChild.tag == "em":
            content.append(parse_em(subChild))
        elif subChild.tag == "eref":
            content.append(parse_eref(subChild))
        elif subChild.tag == "iref":
            content.append(parse_iref(subChild))
        elif subChild.tag == "relref":
            content.append(parse_relref(subChild))
        elif subChild.tag == "strong":
            content.append(parse_strong(subChild))
        elif subChild.tag == "tt":
            content.append(parse_tt(subChild))
        elif subChild.tag == "xref":
            content.append(parse_xref(subChild))
    return rfc.Sub(content)


def parse_sup(xmlElement: ET.Element) -> rfc.Sup:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for supChild in xmlElement:
        if supChild.tag == "bcp14":
            content.append(parse_bcp14(supChild))
        elif supChild.tag == "cref":
            content.append(parse_cref(supChild))
        elif supChild.tag == "em":
            content.append(parse_em(supChild))
        elif supChild.tag == "eref":
            content.append(parse_eref(supChild))
        elif supChild.tag == "iref":
            content.append(parse_iref(supChild))
        elif supChild.tag == "relref":
            content.append(parse_relref(supChild))
        elif supChild.tag == "strong":
            content.append(parse_strong(supChild))
        elif supChild.tag == "tt":
            content.append(parse_tt(supChild))
        elif supChild.tag == "xref":
            content.append(parse_xref(supChild))
    return rfc.Sup(content)


def parse_spanx(xmlElement: ET.Element) -> rfc.SpanX:
    assert xmlElement.text is not None
    return rfc.SpanX(rfc.Text(xmlElement.text),
                     xmlElement.attrib.get("style", None),
                     xmlElement.attrib.get("xml:space", None))


def parse_list(xmlElement: ET.Element) -> rfc.List:
    content : ListType[rfc.T] = []
    for listChild in xmlElement:
        if listChild.tag == "t":
            content.append(parse_t(xmlElement))
    return rfc.List(content,
                    xmlElement.attrib.get("counter", None),
                    xmlElement.attrib.get("hangIndent", None),
                    xmlElement.attrib.get("style", None))


def parse_vspace(xmlElement: ET.Element) -> rfc.VSpace:
    return rfc.VSpace(xmlElement.attrib.get("blankLines", None))


def parse_t(xmlElement: ET.Element) -> rfc.T:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.List, rfc.RelRef, rfc.SpanX, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.VSpace, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for child in xmlElement:
        if child.tag == "bcp14":
            content.append(parse_bcp14(child))
        elif child.tag == "cref":
            content.append(parse_cref(child))
        elif child.tag == "em":
            content.append(parse_em(child))
        elif child.tag == "eref":
            content.append(parse_eref(child))
        elif child.tag == "iref":
            content.append(parse_iref(child))
        elif child.tag == "relref":
            content.append(parse_relref(child))
        elif child.tag == "spanx":
            content.append(parse_spanx(child))
        elif child.tag == "strong":
            content.append(parse_strong(child))
        elif child.tag == "sub":
            content.append(parse_sub(child))
        elif child.tag == "sup":
            content.append(parse_sup(child))
        elif child.tag == "tt":
            content.append(parse_tt(child))
        elif child.tag == "vspace":
            content.append(parse_vspace(child))
        elif child.tag == "xref":
            content.append(parse_xref(child))
        if child.tail is not None:
            content.append(rfc.Text(child.tail))
    if xmlElement.tail is not None:
        content.append(rfc.Text(xmlElement.tail))
    return rfc.T(content,
                 xmlElement.attrib.get("anchor"),
                 xmlElement.attrib.get("hangText"),
                 xmlElement.attrib.get("keepWithNext") == "true",
                 xmlElement.attrib.get("keepWithPrevious") == "true")


def parse_artwork(xmlElement: ET.Element) -> rfc.Artwork:
    content : Union[rfc.Text, ListType[rfc.SVG]]
    if xmlElement.text is not None:
        content = rfc.Text(xmlElement.text)
    else:
        content = []
        for artworkChild in xmlElement:
            if artworkChild.tag == "svg":
                content.append(rfc.SVG())
    return rfc.Artwork(content,
                       xmlElement.attrib.get("align", "left"),
                       xmlElement.attrib.get("alt"),
                       xmlElement.attrib.get("anchor"),
                       xmlElement.attrib.get("height"),
                       xmlElement.attrib.get("name"),
                       xmlElement.attrib.get("src"),
                       xmlElement.attrib.get("type"),
                       xmlElement.attrib.get("width"),
                       xmlElement.attrib.get("xml:space"))


def parse_postamble(xmlElement: ET.Element) -> rfc.Postamble:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.SpanX, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for postambleChild in xmlElement:
        if postambleChild.tag == "bcp14":
            content.append(parse_bcp14(postambleChild))
        elif postambleChild.tag == "cref":
            content.append(parse_cref(postambleChild))
        elif postambleChild.tag == "em":
            content.append(parse_em(postambleChild))
        elif postambleChild.tag == "eref":
            content.append(parse_eref(postambleChild))
        elif postambleChild.tag == "iref":
            content.append(parse_iref(postambleChild))
        elif postambleChild.tag == "spanx":
            content.append(parse_spanx(postambleChild))
        elif postambleChild.tag == "strong":
            content.append(parse_strong(postambleChild))
        elif postambleChild.tag == "sub":
            content.append(parse_sub(postambleChild))
        elif postambleChild.tag == "sup":
            content.append(parse_sup(postambleChild))
        elif postambleChild.tag == "tt":
            content.append(parse_tt(postambleChild))
        elif postambleChild.tag == "xref":
            content.append(parse_xref(postambleChild))
    return rfc.Postamble(content)


def parse_preamble(xmlElement: ET.Element) -> rfc.Preamble:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.SpanX, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for preambleChild in xmlElement:
        if preambleChild.tag == "bcp14":
            content.append(parse_bcp14(preambleChild))
        elif preambleChild.tag == "cref":
            content.append(parse_cref(preambleChild))
        elif preambleChild.tag == "em":
            content.append(parse_em(preambleChild))
        elif preambleChild.tag == "eref":
            content.append(parse_eref(preambleChild))
        elif preambleChild.tag == "iref":
            content.append(parse_iref(preambleChild))
        elif preambleChild.tag == "spanx":
            content.append(parse_spanx(preambleChild))
        elif preambleChild.tag == "strong":
            content.append(parse_strong(preambleChild))
        elif preambleChild.tag == "sub":
            content.append(parse_sub(preambleChild))
        elif preambleChild.tag == "sup":
            content.append(parse_sup(preambleChild))
        elif preambleChild.tag == "tt":
            content.append(parse_tt(preambleChild))
        elif preambleChild.tag == "xref":
            content.append(parse_xref(preambleChild))
    return rfc.Preamble(content)


def parse_name(xmlElement: ET.Element) -> rfc.Name:
    content : ListType[Union[rfc.Text, rfc.CRef, rfc.ERef, rfc.RelRef, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for nameChild in xmlElement:
        if nameChild.tag == "cref":
            content.append(parse_cref(nameChild))
        elif nameChild.tag == "eref":
            content.append(parse_eref(nameChild))
        elif nameChild.tag == "relref":
            content.append(parse_relref(nameChild))
        elif nameChild.tag == "tt":
            content.append(parse_tt(nameChild))
        elif nameChild.tag == "xref":
            content.append(parse_xref(nameChild))
    return rfc.Name(content)


def parse_sourcecode(xmlElement: ET.Element) -> rfc.SourceCode:
    assert xmlElement.text is not None
    return rfc.SourceCode(rfc.Text(xmlElement.text),
                          xmlElement.attrib.get("anchor", None),
                          xmlElement.attrib.get("name",   None),
                          xmlElement.attrib.get("src",    None),
                          xmlElement.attrib.get("type",   None))


def parse_figure(xmlElement: ET.Element) -> rfc.Figure:
    name = None
    irefs = []
    preamble = None
    content : ListType[Union[rfc.Artwork, rfc.SourceCode]] = []
    postamble = None
    for figureChild in xmlElement:
        if figureChild.tag == "name":
            name = parse_name(figureChild)
        elif figureChild.tag == "iref":
            irefs.append(parse_iref(figureChild))
        elif figureChild.tag == "preamble":
            preamble = parse_preamble(figureChild)
        elif figureChild.tag == "artwork":
            content.append(parse_artwork(figureChild))
        elif figureChild.tag == "sourcecode":
            content.append(parse_sourcecode(figureChild))
        elif figureChild.tag == "postamble":
            postamble = parse_postamble(figureChild)
    return rfc.Figure(name,
                      irefs,
                      preamble,
                      content,
                      postamble,
                      xmlElement.attrib.get("align", "left"),
                      xmlElement.attrib.get("alt"),
                      xmlElement.attrib.get("anchor"),
                      xmlElement.attrib.get("height"),
                      xmlElement.attrib.get("src"),
                      xmlElement.attrib.get("suppress-title") == "true",
                      xmlElement.attrib.get("title"),
                      xmlElement.attrib.get("width"))


def parse_li(xmlElement: ET.Element) -> rfc.LI:
    contentA : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]] = []
    contentB : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for liChild in xmlElement:
        # Variant one in RFC 7991 section 2.29:
        if liChild.tag == "artwork":
            contentA.append(parse_artwork(liChild))
        elif liChild.tag == "dl":
            contentA.append(parse_dl(liChild))
        elif liChild.tag == "figure":
            contentA.append(parse_figure(liChild))
        elif liChild.tag == "ol":
            contentA.append(parse_ol(liChild))
        elif liChild.tag == "sourcecode":
            contentA.append(parse_sourcecode(liChild))
        elif liChild.tag == "t":
            contentA.append(parse_t(liChild))
        elif liChild.tag == "ul":
            contentA.append(parse_ul(liChild))
        # Variant two in RFC 7991 section 2.29:
        elif liChild.tag == "bcp14":
            contentB.append(parse_bcp14(liChild))
        elif liChild.tag == "cref":
            contentB.append(parse_cref(liChild))
        elif liChild.tag == "em":
            contentB.append(parse_em(liChild))
        elif liChild.tag == "eref":
            contentB.append(parse_eref(liChild))
        elif liChild.tag == "iref":
            contentB.append(parse_iref(liChild))
        elif liChild.tag == "relref":
            contentB.append(parse_relref(liChild))
        elif liChild.tag == "strong":
            contentB.append(parse_strong(liChild))
        elif liChild.tag == "sub":
            contentB.append(parse_sub(liChild))
        elif liChild.tag == "sup":
            contentB.append(parse_sup(liChild))
        elif liChild.tag == "tt":
            contentB.append(parse_tt(liChild))
        elif liChild.tag == "xref":
            contentB.append(parse_xref(liChild))
    if xmlElement.text is not None:
        contentB.append(rfc.Text(xmlElement.text))
    if len(contentB) == 0:
        # Variant one:
        assert len(contentA) > 0
        return rfc.LI(contentA, xmlElement.attrib.get("anchor", None))
    else:
        # Variant two:
        assert len(contentB) > 0
        return rfc.LI(contentB, xmlElement.attrib.get("anchor", None))


def parse_ul(xmlElement: ET.Element) -> rfc.UL:
    content = []
    for ulChild in xmlElement:
        if ulChild.tag == "li":
            content.append(parse_li(ulChild))
    return rfc.UL(content,
                  xmlElement.attrib.get("anchor"),
                  xmlElement.attrib.get("empty") == "true",
                  xmlElement.attrib.get("spacing", "normal"))


def parse_ol(xmlElement: ET.Element) -> rfc.OL:
    content = []
    for olChild in xmlElement:
        if olChild.tag == "li":
            content.append(parse_li(olChild))
    return rfc.OL(content,
                  xmlElement.attrib.get("anchor"),
                  xmlElement.attrib.get("group"),
                  xmlElement.attrib.get("spacing", "normal"),
                  xmlElement.attrib.get("start"),
                  xmlElement.attrib.get("type"))


def parse_dd(xmlElement: ET.Element) -> rfc.DD:
    contentA : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]] = []
    contentB : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []

    if xmlElement.text is not None and len(xmlElement.text.strip()) != 0:
        contentB.append(rfc.Text(xmlElement.text))

    for ddChild in xmlElement:
        # Variant one in RFC 7991 section 2.18:
        if ddChild.tag == "artwork":
            contentA.append(parse_artwork(ddChild))
        elif ddChild.tag == "dl":
            contentA.append(parse_dl(ddChild))
        elif ddChild.tag == "figure":
            contentA.append(parse_figure(ddChild))
        elif ddChild.tag == "ol":
            contentA.append(parse_ol(ddChild))
        elif ddChild.tag == "sourcecode":
            contentA.append(parse_sourcecode(ddChild))
        elif ddChild.tag == "t":
            contentA.append(parse_t(ddChild))
        elif ddChild.tag == "ul":
            contentA.append(parse_ul(ddChild))
        # Variant two in RFC 7991 section 2.18:
        elif ddChild.tag == "bcp14":
            contentB.append(parse_bcp14(ddChild))
        elif ddChild.tag == "cref":
            contentB.append(parse_cref(ddChild))
        elif ddChild.tag == "em":
            contentB.append(parse_em(ddChild))
        elif ddChild.tag == "eref":
            contentB.append(parse_eref(ddChild))
        elif ddChild.tag == "iref":
            contentB.append(parse_iref(ddChild))
        elif ddChild.tag == "relref":
            contentB.append(parse_relref(ddChild))
        elif ddChild.tag == "strong":
            contentB.append(parse_strong(ddChild))
        elif ddChild.tag == "sub":
            contentB.append(parse_sub(ddChild))
        elif ddChild.tag == "sup":
            contentB.append(parse_sup(ddChild))
        elif ddChild.tag == "tt":
            contentB.append(parse_tt(ddChild))
        elif ddChild.tag == "xref":
            contentB.append(parse_xref(ddChild))
        if ddChild.tail is not None and len(ddChild.tail.strip()) != 0:
            contentB.append(rfc.Text(ddChild.tail))

    if len(contentB) == 0:
        assert len(contentA) > 0
        return rfc.DD(contentA, xmlElement.attrib.get("anchor"))
    else:
        assert len(contentA) == 0
        return rfc.DD(contentB, xmlElement.attrib.get("anchor"))


def parse_dt(xmlElement: ET.Element) -> rfc.DT:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for dtChild in xmlElement:
        if dtChild.tag == "bcp14":
            content.append(parse_bcp14(dtChild))
        elif dtChild.tag == "cref":
            content.append(parse_cref(dtChild))
        elif dtChild.tag == "em":
            content.append(parse_em(dtChild))
        elif dtChild.tag == "eref":
            content.append(parse_eref(dtChild))
        elif dtChild.tag == "iref":
            content.append(parse_iref(dtChild))
        elif dtChild.tag == "relref":
            content.append(parse_relref(dtChild))
        elif dtChild.tag == "strong":
            content.append(parse_strong(dtChild))
        elif dtChild.tag == "sub":
            content.append(parse_sub(dtChild))
        elif dtChild.tag == "sup":
            content.append(parse_sup(dtChild))
        elif dtChild.tag == "tt":
            content.append(parse_tt(dtChild))
        elif dtChild.tag == "xref":
            content.append(parse_xref(dtChild))
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    return rfc.DT(content, xmlElement.attrib.get("anchor"))


def parse_dl(xmlElement) -> rfc.DL:
    content : ListType[Tuple[rfc.DT, rfc.DD]] = []
    dt = None
    dd = None
    for dlChild in xmlElement:
        if dlChild.tag == "dt":
            assert dd == None
            dt = parse_dt(dlChild)
        elif dlChild.tag == "dd":
            assert dt is not None
            dd = parse_dd(dlChild)
            content.append((dt, dd))
            dt = None
            dd = None
    return rfc.DL(content,
                  xmlElement.attrib.get("anchor"),
                  not xmlElement.attrib.get("hanging") == "false",
                  xmlElement.attrib.get("spacing", "normal"))


def parse_ttcol(xmlElement: ET.Element) -> rfc.TTCol:
    content : ListType[Union[rfc.Text, rfc.CRef, rfc.ERef, rfc.IRef, rfc.XRef]] = []
    for ttcolChild in xmlElement:
        if ttcolChild.tag == "cref":
            content.append(parse_cref(ttcolChild))
        elif ttcolChild.tag == "eref":
            content.append(parse_eref(ttcolChild))
        elif ttcolChild.tag == "iref":
            content.append(parse_iref(ttcolChild))
        elif ttcolChild.tag == "xref":
            content.append(parse_xref(ttcolChild))
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    return rfc.TTCol(content,
                     xmlElement.attrib.get("align", "left"),
                     xmlElement.attrib.get("width"))


def parse_c(xmlElement: ET.Element) -> rfc.C:
    content :  ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.SpanX, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for cChild in xmlElement:
        if cChild.tag == "bcp14":
            content.append(parse_bcp14(cChild))
        elif cChild.tag == "cref":
            content.append(parse_cref(cChild))
        elif cChild.tag == "em":
            content.append(parse_em(cChild))
        elif cChild.tag == "eref":
            content.append(parse_eref(cChild))
        elif cChild.tag == "iref":
            content.append(parse_iref(cChild))
        elif cChild.tag == "spanx":
            content.append(parse_spanx(cChild))
        elif cChild.tag == "strong":
            content.append(parse_strong(cChild))
        elif cChild.tag == "sub":
            content.append(parse_sub(cChild))
        elif cChild.tag == "sup":
            content.append(parse_sup(cChild))
        elif cChild.tag == "tt":
            content.append(parse_tt(cChild))
        elif cChild.tag == "xref":
            content.append(parse_xref(cChild))
        if cChild.text is not None:
            content.append(rfc.Text(cChild.text))
    return rfc.C(content)


def parse_texttable(xmlElement: ET.Element) -> rfc.TextTable:
    name = None
    preamble = None
    ttcols = []
    cs = []
    postamble = None
    for texttableChild in xmlElement:
        if texttableChild.tag == "name":
            name = parse_name(texttableChild)
        elif texttableChild.tag == "preamble":
            preamble = parse_preamble(texttableChild)
        elif texttableChild.tag == "ttcol":
            ttcols.append(parse_ttcol(texttableChild))
        elif texttableChild.tag == "c":
            cs.append(parse_c(texttableChild))
        elif texttableChild.tag == "postamble":
            postamble = parse_postamble(texttableChild)
    return rfc.TextTable(name,
                         preamble,
                         ttcols,
                         cs,
                         postamble,
                         xmlElement.attrib.get("align", "center"),
                         xmlElement.attrib.get("anchor"),
                         xmlElement.attrib.get("style"),
                         xmlElement.attrib.get("suppress-title") == "true",
                         xmlElement.attrib.get("title"))


def parse_br(xmlElement: ET.Element) -> rfc.BR:
    return rfc.BR()


def parse_th(xmlElement: ET.Element) -> rfc.TH:
    contentA : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]] = []
    contentB : ListType[Union[rfc.Text, rfc.BCP14, rfc.BR, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for thChild in xmlElement:
        # Variant one in RFC 7991 section 2.58:
        if thChild.tag == "artwork":
            contentA.append(parse_artwork(thChild))
        elif thChild.tag == "dl":
            contentA.append(parse_dl(thChild))
        elif thChild.tag == "figure":
            contentA.append(parse_figure(thChild))
        elif thChild.tag == "ol":
            contentA.append(parse_ol(thChild))
        elif thChild.tag == "sourcecode":
            contentA.append(parse_sourcecode(thChild))
        elif thChild.tag == "t":
            contentA.append(parse_t(thChild))
        elif thChild.tag == "ul":
            contentA.append(parse_ul(thChild))
        # Variant two in RFC 7991 section 2.58:
        elif thChild.tag == "bcp14":
            contentB.append(parse_bcp14(thChild))
        elif thChild.tag == "br":
            contentB.append(parse_br(thChild))
        elif thChild.tag == "cref":
            contentB.append(parse_cref(thChild))
        elif thChild.tag == "em":
            contentB.append(parse_em(thChild))
        elif thChild.tag == "eref":
            contentB.append(parse_eref(thChild))
        elif thChild.tag == "iref":
            contentB.append(parse_iref(thChild))
        elif thChild.tag == "relref":
            contentB.append(parse_relref(thChild))
        elif thChild.tag == "strong":
            contentB.append(parse_strong(thChild))
        elif thChild.tag == "sub":
            contentB.append(parse_sub(thChild))
        elif thChild.tag == "sup":
            contentB.append(parse_sup(thChild))
        elif thChild.tag == "tt":
            contentB.append(parse_tt(thChild))
        elif thChild.tag == "xref":
            contentB.append(parse_xref(thChild))
    if xmlElement.text is not None:
        contentB.append(rfc.Text(xmlElement.text))
    if len(contentB) == 0:
        assert len(contentA) > 0
        return rfc.TH(contentA,
                      xmlElement.attrib.get("align", "left"),
                      xmlElement.attrib.get("anchor", None),
                      xmlElement.attrib.get("colspan", None),
                      xmlElement.attrib.get("rowspan", None))
    else:
        assert len(contentB) > 0
        return rfc.TH(contentB,
                      xmlElement.attrib.get("align", "left"),
                      xmlElement.attrib.get("anchor", None),
                      xmlElement.attrib.get("colspan", None),
                      xmlElement.attrib.get("rowspan", None))


def parse_td(xmlElement: ET.Element) -> rfc.TD:
    contentA : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]] = []
    contentB : ListType[Union[rfc.Text, rfc.BCP14, rfc.BR, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for tdChild in xmlElement:
        # Variant one in RFC 7991 section 2.56:
        if tdChild.tag == "artwork":
            contentA.append(parse_artwork(tdChild))
        elif tdChild.tag == "dl":
            contentA.append(parse_dl(tdChild))
        elif tdChild.tag == "figure":
            contentA.append(parse_figure(tdChild))
        elif tdChild.tag == "ol":
            contentA.append(parse_ol(tdChild))
        elif tdChild.tag == "sourcecode":
            contentA.append(parse_sourcecode(tdChild))
        elif tdChild.tag == "t":
            contentA.append(parse_t(tdChild))
        elif tdChild.tag == "ul":
            contentA.append(parse_ul(tdChild))
        # Variant two in RFC 7991 section 2.56:
        elif tdChild.tag == "bcp14":
            contentB.append(parse_bcp14(tdChild))
        elif tdChild.tag == "br":
            contentB.append(parse_br(tdChild))
        elif tdChild.tag == "cref":
            contentB.append(parse_cref(tdChild))
        elif tdChild.tag == "em":
            contentB.append(parse_em(tdChild))
        elif tdChild.tag == "eref":
            contentB.append(parse_eref(tdChild))
        elif tdChild.tag == "iref":
            contentB.append(parse_iref(tdChild))
        elif tdChild.tag == "relref":
            contentB.append(parse_relref(tdChild))
        elif tdChild.tag == "strong":
            contentB.append(parse_strong(tdChild))
        elif tdChild.tag == "sub":
            contentB.append(parse_sub(tdChild))
        elif tdChild.tag == "sup":
            contentB.append(parse_sup(tdChild))
        elif tdChild.tag == "tt":
            contentB.append(parse_tt(tdChild))
        elif tdChild.tag == "xref":
            contentB.append(parse_xref(tdChild))
    if xmlElement.text is not None:
        contentB.append(rfc.Text(xmlElement.text))
    if len(contentB) == 0:
        assert len(contentA) > 0
        return rfc.TD(contentA,
                      xmlElement.attrib.get("align", "left"),
                      xmlElement.attrib.get("anchor", None),
                      xmlElement.attrib.get("colspan", None),
                      xmlElement.attrib.get("rowspan", None))
    else:
        assert len(contentB) > 0
        return rfc.TD(contentB,
                      xmlElement.attrib.get("align", "left"),
                      xmlElement.attrib.get("anchor", None),
                      xmlElement.attrib.get("colspan", None),
                      xmlElement.attrib.get("rowspan", None))


def parse_tr(xmlElement: ET.Element) -> rfc.TR:
    content : ListType[Union[rfc.TD, rfc.TH]] = []
    for trChild in xmlElement:
        if trChild.tag == "td":
            content.append(parse_td(trChild))
        elif trChild.tag == "th":
            content.append(parse_th(trChild))
    return rfc.TR(content,
                  xmlElement.attrib.get("anchor", None))


def parse_tbody(xmlElement: ET.Element) -> rfc.TBody:
    content = []
    for tbodyChild in xmlElement:
        if tbodyChild.tag == "tr":
            content.append(parse_tr(tbodyChild))
    return rfc.TBody(content,
                     xmlElement.attrib.get("anchor", None))


def parse_tfoot(xmlElement: ET.Element) -> rfc.TFoot:
    content = []
    for tfootChild in xmlElement:
        if tfootChild.tag == "tr":
            content.append(parse_tr(tfootChild))
    return rfc.TFoot(content,
                     xmlElement.attrib.get("anchor", None))


def parse_thead(xmlElement: ET.Element) -> rfc.THead:
    content = []
    for theadChild in xmlElement:
        if theadChild.tag == "tr":
            content.append(parse_tr(theadChild))
    return rfc.THead(content,
                     xmlElement.attrib.get("anchor", None))


def parse_table(xmlElement: ET.Element) -> rfc.Table:
    name = None
    irefs = []
    thead = None
    tbody = []
    tfoot = None
    for tableChild in xmlElement:
        if tableChild.tag == "name":
            name = parse_name(tableChild)
        elif tableChild.tag == "iref":
            irefs.append(parse_iref(tableChild))
        elif tableChild.tag == "thead":
            thead = parse_thead(tableChild)
        elif tableChild.tag == "tbody":
            tbody.append(parse_tbody(tableChild))
        elif tableChild.tag == "tfoot":
            tfoot = parse_tfoot(tableChild)
    return rfc.Table(name,
                     irefs,
                     thead,
                     tbody,
                     tfoot,
                     xmlElement.attrib.get("anchor"))


def parse_aside(xmlElement: ET.Element) -> rfc.Aside:
    content : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.IRef, rfc.List, rfc.OL, rfc.T, rfc.Table, rfc.UL]] = []
    for asideChild in xmlElement:
        if asideChild.tag == "artwork":
            content.append(parse_artwork(asideChild))
        elif asideChild.tag == "dl":
            content.append(parse_dl(asideChild))
        elif asideChild.tag == "figure":
            content.append(parse_figure(asideChild))
        elif asideChild.tag == "iref":
            content.append(parse_iref(asideChild))
        elif asideChild.tag == "list":
            content.append(parse_list(asideChild))
        elif asideChild.tag == "ol":
            content.append(parse_ol(asideChild))
        elif asideChild.tag == "t":
            content.append(parse_t(asideChild))
        elif asideChild.tag == "table":
            content.append(parse_table(asideChild))
        elif asideChild.tag == "ul":
            content.append(parse_ul(asideChild))
    return rfc.Aside(content,
                     xmlElement.attrib.get("anchor", None))


def parse_blockquote(xmlElement: ET.Element) -> rfc.BlockQuote:
    contentA : ListType[Union[rfc.Artwork, rfc.DL, rfc.Figure, rfc.OL, rfc.SourceCode, rfc.T, rfc.UL]] = []
    contentB : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    for blockquoteChild in xmlElement:
        # Variant one in RFC 7991 section 2.10:
        if blockquoteChild.tag == "artwork":
            contentA.append(parse_artwork(blockquoteChild))
        elif blockquoteChild.tag == "dl":
            contentA.append(parse_dl(blockquoteChild))
        elif blockquoteChild.tag == "figure":
            contentA.append(parse_figure(blockquoteChild))
        elif blockquoteChild.tag == "ol":
            contentA.append(parse_ol(blockquoteChild))
        elif blockquoteChild.tag == "sourcecode":
            contentA.append(parse_sourcecode(blockquoteChild))
        elif blockquoteChild.tag == "t":
            contentA.append(parse_t(blockquoteChild))
        elif blockquoteChild.tag == "ul":
            contentA.append(parse_ul(blockquoteChild))
        # Variant two in RFC 7991 section 2.10:
        elif blockquoteChild.tag == "bcp14":
            contentB.append(parse_bcp14(blockquoteChild))
        elif blockquoteChild.tag == "cref":
            contentB.append(parse_cref(blockquoteChild))
        elif blockquoteChild.tag == "em":
            contentB.append(parse_em(blockquoteChild))
        elif blockquoteChild.tag == "eref":
            contentB.append(parse_eref(blockquoteChild))
        elif blockquoteChild.tag == "iref":
            contentB.append(parse_iref(blockquoteChild))
        elif blockquoteChild.tag == "relref":
            contentB.append(parse_relref(blockquoteChild))
        elif blockquoteChild.tag == "strong":
            contentB.append(parse_strong(blockquoteChild))
        elif blockquoteChild.tag == "sub":
            contentB.append(parse_sub(blockquoteChild))
        elif blockquoteChild.tag == "sup":
            contentB.append(parse_sup(blockquoteChild))
        elif blockquoteChild.tag == "tt":
            contentB.append(parse_tt(blockquoteChild))
        elif blockquoteChild.tag == "xref":
            contentB.append(parse_xref(blockquoteChild))
    if blockquoteChild.text is not None:
        contentB.append(rfc.Text(blockquoteChild.text))
    if len(contentB) == 0:
        assert len(contentA) > 0
        return rfc.BlockQuote(contentA,
                              xmlElement.attrib.get("anchor", None),
                              xmlElement.attrib.get("cite", None),
                              xmlElement.attrib.get("quotedFrom", None))
    else:
        assert len(contentB) > 0
        return rfc.BlockQuote(contentB,
                              xmlElement.attrib.get("anchor", None),
                              xmlElement.attrib.get("cite", None),
                              xmlElement.attrib.get("quotedFrom", None))


def parse_section(xmlElement: ET.Element) -> rfc.Section:
    name = None
    content : ListType[Union[rfc.Artwork, rfc.Aside, rfc.BlockQuote, rfc.DL, rfc.Figure, rfc.IRef, rfc.OL, rfc.SourceCode, rfc.T, rfc.Table, rfc.TextTable, rfc.UL]] = []
    sections = []
    for sectionChild in xmlElement:
        if sectionChild.tag == "artwork":
            content.append(parse_artwork(sectionChild))
        elif sectionChild.tag == "aside":
            content.append(parse_aside(sectionChild))
        elif sectionChild.tag == "blockquote":
            content.append(parse_blockquote(sectionChild))
        elif sectionChild.tag == "dl":
            content.append(parse_dl(sectionChild))
        elif sectionChild.tag == "figure":
            content.append(parse_figure(sectionChild))
        elif sectionChild.tag == "iref":
            content.append(parse_iref(sectionChild))
        elif sectionChild.tag == "ol":
            content.append(parse_ol(sectionChild))
        elif sectionChild.tag == "sourcecode":
            content.append(parse_sourcecode(sectionChild))
        elif sectionChild.tag == "t":
            content.append(parse_t(sectionChild))
        elif sectionChild.tag == "table":
            content.append(parse_table(sectionChild))
        elif sectionChild.tag == "texttable":
            content.append(parse_texttable(sectionChild))
        elif sectionChild.tag == "ul":
            content.append(parse_ul(sectionChild))
        elif sectionChild.tag == "section":
            sections.append(parse_section(sectionChild))
        elif sectionChild.tag == "name":
            name = parse_name(sectionChild)
    return rfc.Section(name,
                       content,
                       sections,
                       xmlElement.attrib.get("anchor"),
                       not xmlElement.attrib.get("numbered") == "false",
                       xmlElement.attrib.get("removeInRFC") == "true",
                       xmlElement.attrib.get("title", None),
                       xmlElement.attrib.get("toc", "default"))


def parse_middle(xmlElement: ET.Element) -> rfc.Middle:
    content = []
    for middleChild in xmlElement:
        if middleChild.tag == "section":
            content.append(parse_section(middleChild))
    return rfc.Middle(content)


def parse_street(xmlElement: ET.Element) -> rfc.Street:
    assert xmlElement.text is not None
    return rfc.Street(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_region(xmlElement: ET.Element) -> rfc.Region:
    assert xmlElement.text is not None
    return rfc.Region(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_postalline(xmlElement: ET.Element) -> rfc.PostalLine:
    assert xmlElement.text is not None
    return rfc.PostalLine(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_city(xmlElement: ET.Element) -> rfc.City:
    assert xmlElement.text is not None
    return rfc.City(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_code(xmlElement: ET.Element) -> rfc.Code:
    assert xmlElement.text is not None
    return rfc.Code(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_country(xmlElement: ET.Element) -> rfc.Country:
    assert xmlElement.text is not None
    return rfc.Country(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_postal(xmlElement: ET.Element) -> rfc.Postal:
    postalElementsA : ListType[Union[rfc.City, rfc.Code, rfc.Country, rfc.Region, rfc.Street]] = []
    postalElementsB : ListType[rfc.PostalLine] = []
    for postalChild in xmlElement:
        # Variant one in RFC 7991 section 2.37:
        if postalChild.tag == "city":
            postalElementsA.append(parse_city(postalChild))
        elif postalChild.tag == "code":
            postalElementsA.append(parse_code(postalChild))
        elif postalChild.tag == "country":
            postalElementsA.append(parse_country(postalChild))
        elif postalChild.tag == "region":
            postalElementsA.append(parse_region(postalChild))
        elif postalChild.tag == "street":
            postalElementsA.append(parse_street(postalChild))
        # Variant two in RFC 7991 section 2.37:
        elif postalChild.tag == "postalLine":
            postalElementsB.append(parse_postalline(postalChild))
    if len(postalElementsB) == 0:
        assert len(postalElementsA) > 0
        return rfc.Postal(postalElementsA)
    else:
        assert len(postalElementsB) > 0
        return rfc.Postal(postalElementsB)


def parse_email(xmlElement: ET.Element) -> rfc.Email:
    assert xmlElement.text is not None
    return rfc.Email(rfc.Text(xmlElement.text), xmlElement.attrib.get("ascii", None))


def parse_phone(xmlElement: ET.Element) -> rfc.Phone:
    assert xmlElement.text is not None
    return rfc.Phone(rfc.Text(xmlElement.text))


def parse_uri(xmlElement: ET.Element) -> rfc.URI:
    assert xmlElement.text is not None
    return rfc.URI(rfc.Text(xmlElement.text))


def parse_facsimile(xmlElement: ET.Element) -> rfc.Facsimile:
    assert xmlElement.text is not None
    return rfc.Facsimile(rfc.Text(xmlElement.text))


def parse_address(xmlElement: ET.Element) -> rfc.Address:
    postal = None
    phone = None
    facsimile = None
    email = None
    uri = None
    for addressChild in xmlElement:
        if addressChild.tag == "postal":
            postal = parse_postal(addressChild)
        elif addressChild.tag == "phone":
            phone = parse_phone(addressChild)
        elif addressChild.tag == "facsimile":
            facsimile = parse_facsimile(addressChild)
        elif addressChild.tag == "email":
            email = parse_email(addressChild)
        elif addressChild.tag == "uri":
            uri = parse_uri(addressChild)
    return rfc.Address(postal, phone, facsimile, email, uri)


def parse_organization(xmlElement: ET.Element) -> rfc.Organization:
    organisation : Optional[rfc.Text] = None
    if xmlElement.text is not None:
        organisation = rfc.Text(xmlElement.text)
    return rfc.Organization(organisation, xmlElement.attrib.get("abbrev", None), xmlElement.attrib.get("ascii", None))


def parse_author(xmlElement: ET.Element) -> rfc.Author:
    org = None
    address = None
    for authorChild in xmlElement:
        if authorChild.tag == "organization":
            org = parse_organization(authorChild)
        elif authorChild.tag == "address":
            address = parse_address(authorChild)
    return rfc.Author(org,
                      address,
                      xmlElement.attrib.get("asciiFullname", None),
                      xmlElement.attrib.get("asciiInitials", None),
                      xmlElement.attrib.get("asciiSurname", None),
                      xmlElement.attrib.get("fullname", None),
                      xmlElement.attrib.get("initials", None),
                      xmlElement.attrib.get("role", None),
                      xmlElement.attrib.get("surname", None))


def parse_seriesinfo(xmlElement: ET.Element) -> rfc.SeriesInfo:
    return rfc.SeriesInfo(xmlElement.attrib["name"],
                          xmlElement.attrib["value"],
                          xmlElement.attrib["name"],
                          xmlElement.attrib.get("status", None),
                          xmlElement.attrib.get("stream", None),
                          xmlElement.attrib["value"])


def parse_title(xmlElement: ET.Element) -> rfc.Title:
    assert xmlElement.text is not None
    return rfc.Title(rfc.Text(xmlElement.text),
                     xmlElement.attrib.get("abbrev", None),
                     xmlElement.attrib.get("ascii", None))


def parse_date(xmlElement: ET.Element) -> rfc.Date:
    return rfc.Date(xmlElement.attrib.get("day", None),
                    xmlElement.attrib.get("month", None),
                    xmlElement.attrib.get("year", None))


def parse_area(xmlElement: ET.Element) -> rfc.Area:
    assert xmlElement.text is not None
    return rfc.Area(rfc.Text(xmlElement.text))


def parse_workgroup(xmlElement: ET.Element) -> rfc.Workgroup:
    assert xmlElement.text is not None
    return rfc.Workgroup(rfc.Text(xmlElement.text))


def parse_keyword(xmlElement: ET.Element) -> rfc.Keyword:
    assert xmlElement.text is not None
    return rfc.Keyword(rfc.Text(xmlElement.text))


def parse_abstract(xmlElement: ET.Element) -> rfc.Abstract:
    content : ListType[Union[rfc.DL, rfc.OL, rfc.T, rfc.UL]] = []
    for abstractChild in xmlElement:
        if abstractChild.tag == "dl":
            content.append(parse_dl(abstractChild))
        elif abstractChild.tag == "ol":
            content.append(parse_ol(abstractChild))
        elif abstractChild.tag == "t":
            content.append(parse_t(abstractChild))
        elif abstractChild.tag == "ul":
            content.append(parse_ul(abstractChild))
    return rfc.Abstract(content, xmlElement.attrib.get("anchor", None))


def parse_note(xmlElement: ET.Element) -> rfc.Note:
    name = None
    content : ListType[Union[rfc.DL, rfc.OL, rfc.T, rfc.UL]] = []
    for noteChild in xmlElement:
        if noteChild.tag == "dl":
            content.append(parse_dl(noteChild))
        elif noteChild.tag == "ol":
            content.append(parse_ol(noteChild))
        elif noteChild.tag == "t":
            content.append(parse_t(noteChild))
        elif noteChild.tag == "ul":
            content.append(parse_ul(noteChild))
        elif noteChild.tag == "name":
            name = parse_name(noteChild)
    return rfc.Note(name, content, xmlElement.attrib.get("removeInRFC") == "true", xmlElement.attrib.get("title"))


def parse_boilerplate(xmlElement: ET.Element) -> rfc.Boilerplate:
    content = []
    for boilerplateChild in xmlElement:
        if boilerplateChild.tag == "section":
            content.append(parse_section(boilerplateChild))
    return rfc.Boilerplate(content)


def parse_front(xmlElement: ET.Element) -> rfc.Front:
    title : rfc.Title
    seriesInfo = []
    authors = []
    date = None
    areas = []
    workgroups = []
    keywords = []
    abstract = None
    notes = []
    boilerplate = None
    for frontChild in xmlElement:
        if frontChild.tag == "title":
            title = parse_title(frontChild)
        elif frontChild.tag == "seriesInfo":
            seriesInfo.append(parse_seriesinfo(frontChild))
        elif frontChild.tag == "author":
            authors.append(parse_author(frontChild))
        elif frontChild.tag == "date":
            date = parse_date(frontChild)
        elif frontChild.tag == "area":
            areas.append(parse_area(frontChild))
        elif frontChild.tag == "workgroup":
            workgroups.append(parse_workgroup(frontChild))
        elif frontChild.tag == "keyword":
            keywords.append(parse_keyword(frontChild))
        elif frontChild.tag == "abstract":
            abstract = parse_abstract(frontChild)
        elif frontChild.tag == "note":
            notes.append(parse_note(frontChild))
        elif frontChild.tag == "boilerplate":
            boilerplate = parse_boilerplate(frontChild)
    return rfc.Front(title, seriesInfo, authors, date, areas, workgroups, keywords, abstract, notes, boilerplate)


def parse_format(xmlElement: ET.Element) -> rfc.Format:
    return rfc.Format(xmlElement.attrib.get("octets", None), xmlElement.attrib.get("target", None), xmlElement.attrib["type"])


def parse_annotation(xmlElement: ET.Element) -> rfc.Annotation:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.CRef, rfc.EM, rfc.ERef, rfc.IRef, rfc.RelRef, rfc.SpanX, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT, rfc.XRef]] = []
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    for annotationChild in xmlElement:
        if annotationChild.tag == "bcp14":
            content.append(parse_bcp14(annotationChild))
        elif annotationChild.tag == "cref":
            content.append(parse_cref(annotationChild))
        elif annotationChild.tag == "em":
            content.append(parse_em(annotationChild))
        elif annotationChild.tag == "eref":
            content.append(parse_eref(annotationChild))
        elif annotationChild.tag == "iref":
            content.append(parse_iref(annotationChild))
        elif annotationChild.tag == "relref":
            content.append(parse_relref(annotationChild))
        elif annotationChild.tag == "spanx":
            content.append(parse_spanx(annotationChild))
        elif annotationChild.tag == "strong":
            content.append(parse_strong(annotationChild))
        elif annotationChild.tag == "sub":
            content.append(parse_sub(annotationChild))
        elif annotationChild.tag == "sup":
            content.append(parse_sup(annotationChild))
        elif annotationChild.tag == "tt":
            content.append(parse_tt(annotationChild))
        elif annotationChild.tag == "xref":
            content.append(parse_xref(annotationChild))
    return rfc.Annotation(content)


def parse_refcontent(xmlElement: ET.Element) -> rfc.RefContent:
    content : ListType[Union[rfc.Text, rfc.BCP14, rfc.EM, rfc.Strong, rfc.Sub, rfc.Sup, rfc.TT]] = []
    for refcontentChild in xmlElement:
        if refcontentChild.tag == "bcp14":
            content.append(parse_bcp14(refcontentChild))
        elif refcontentChild.tag == "em":
            content.append(parse_em(refcontentChild))
        elif refcontentChild.tag == "strong":
            content.append(parse_strong(refcontentChild))
        elif refcontentChild.tag == "sub":
            content.append(parse_sub(refcontentChild))
        elif refcontentChild.tag == "sup":
            content.append(parse_sup(refcontentChild))
        elif refcontentChild.tag == "tt":
            content.append(parse_tt(refcontentChild))
    if xmlElement.text is not None:
        content.append(rfc.Text(xmlElement.text))
    return rfc.RefContent(content)


def parse_reference(xmlElement: ET.Element) -> rfc.Reference:
    front   : rfc.Front
    content : ListType[Union[rfc.Annotation, rfc.Format, rfc.RefContent, rfc.SeriesInfo]] = []
    for referenceChild in xmlElement:
        if referenceChild.tag == "front":
            front = parse_front(referenceChild)
        elif referenceChild.tag == "annotation":
            content.append(parse_annotation(referenceChild))
        elif referenceChild.tag == "format":
            content.append(parse_format(referenceChild))
        elif referenceChild.tag == "refcontent":
            content.append(parse_refcontent(referenceChild))
        elif referenceChild.tag == "seriesInfo":
            content.append(parse_seriesinfo(referenceChild))
    return rfc.Reference(front,
                         content,
                         xmlElement.attrib["anchor"],
                         not xmlElement.attrib.get("quoteTitle") == "false",
                         xmlElement.attrib.get("target"))


def parse_referencegroup(xmlElement: ET.Element) -> rfc.ReferenceGroup:
    content = []
    for referencegroupChild in xmlElement:
        if referencegroupChild.tag == "reference":
            content.append(parse_reference(referencegroupChild))
    return rfc.ReferenceGroup(content, xmlElement.attrib["anchor"])


def parse_references(xmlElement: ET.Element) -> rfc.References:
    name = None
    content : ListType[Union[rfc.Reference, rfc.ReferenceGroup]] = []
    for referencesChild in xmlElement:
        if referencesChild.tag == "name":
            name = parse_name(referencesChild)
        elif referencesChild.tag == "reference":
            content.append(parse_reference(referencesChild))
        elif referencesChild.tag == "referencegroup":
            content.append(parse_referencegroup(referencesChild))
    return rfc.References(name,
                          content,
                          xmlElement.attrib.get("anchor"),
                          xmlElement.attrib.get("title"))


def parse_displayreference(xmlElement: ET.Element) -> rfc.DisplayReference:
    return rfc.DisplayReference(xmlElement.attrib["target"], xmlElement.attrib["to"])


def parse_back(xmlElement: ET.Element) -> rfc.Back:
    displayrefs = []
    refs = []
    sections = []
    for backChild in xmlElement:
        if backChild.tag == "displayreference":
            displayrefs.append(parse_displayreference(backChild))
        elif backChild.tag == "references":
            refs.append(parse_references(backChild))
        elif backChild.tag == "section":
            sections.append(parse_section(backChild))
    return rfc.Back(displayrefs, refs, sections)


def parse_link(xmlElement: ET.Element) -> rfc.Link:
    return rfc.Link(xmlElement.attrib["href"], xmlElement.attrib.get("rel", None))


def parse_rfc(xmlElement: ET.Element) -> rfc.RFC:
    links = []
    front  : rfc.Front
    middle : rfc.Middle
    back   : rfc.Back
    for rfcChild in xmlElement:
        if rfcChild.tag == "link":
            links.append(parse_link(rfcChild))
        elif rfcChild.tag == "front":
            front = parse_front(rfcChild)
        elif rfcChild.tag == "middle":
            middle = parse_middle(rfcChild)
        elif rfcChild.tag == "back":
            back = parse_back(rfcChild)
    return rfc.RFC(links,
                   front,
                   middle,
                   back,
                   xmlElement.attrib.get("category"),
                   xmlElement.attrib.get("consensus") == "true",
                   xmlElement.attrib.get("docName", None),
                   not xmlElement.attrib.get("indexInclude") == "false",
                   xmlElement.attrib.get("ipr"),
                   xmlElement.attrib.get("iprExtract"),
                   xmlElement.attrib.get("number"),
                   xmlElement.attrib.get("obsoletes"),
                   xmlElement.attrib.get("prepTime"),
                   xmlElement.attrib.get("seriesNo"),
                   xmlElement.attrib.get("sortRefs") == "true",
                   xmlElement.attrib.get("submissionType", "IETF"),
                   not xmlElement.attrib.get("symRefs") == "false",
                   xmlElement.attrib.get("tocDepth"),
                   not xmlElement.attrib.get("tocInclude") == "false",
                   xmlElement.attrib.get("updates"),
                   xmlElement.attrib.get("version"))

if __name__ == "__main__":
    rfcXml = ET.parse(sys.argv[1]).getroot()
    parsed_rfc = parse_rfc(rfcXml)
    print(parsed_rfc)
