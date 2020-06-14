#!/usr/bin/env python3.7
# =================================================================================================
# Copyright (C) 2018-2019 University of Glasgow
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

# =================================================================================================
# The xml2rfc Version 3 Vocabulary, as defined in RFC 7991
# =================================================================================================

from typing      import List as ListType, Union, Optional, Tuple
from dataclasses import dataclass

class Elem:
    pass
    
# =================================================================================================
# SVG element
# =================================================================================================

@dataclass
class SVG(Elem):
    pass

# =================================================================================================
# Text element
# =================================================================================================

@dataclass
class Text(Elem):
    content : str 

# =================================================================================================
# BCP14 element
# =================================================================================================

@dataclass
class BCP14(Elem):
    """
    RFC 7991 Section 2.9
    """
    content : Text  

# =================================================================================================
# EM element
# =================================================================================================

@dataclass
class EM(Elem):
    """
    RFC 7991 Section 2.22
    """
    content : ListType[Union[Text, BCP14, "CRef", "IRef", "RelRef", "Strong", "Sub", "Sup", "TT", "XRef"]]

# =================================================================================================
# {C, X, I, E, Rel}Ref elements
# =================================================================================================

@dataclass
class RelRef(Elem):
    """
    RFC 7991 Section 2.44
    """
    content       : Text
    displayFormat : Optional[str]
    relative      : Optional[str]
    section       : str
    target        : str

@dataclass
class ERef(Elem):
    """
    RFC 7991 Section 2.24
    """
    content : Text
    target  : str

@dataclass
class IRef(Elem):
    """
    RFC 7991 Section 2.27
    """
    item    : str
    primary : Optional[bool]
    subitem : Optional[str]

@dataclass
class XRef(Elem):
    """
    RFC 7991 Section 2.66
    """
    content : Text
    format  : Optional[str]
    pageno  : Optional[bool]
    target  : str

@dataclass
class CRef(Elem):
    """
    RFC 7991 Section 2.16
    """
    content : ListType[Union[Text, EM, ERef, RelRef, "Strong", "Sub", "Sup", "TT", XRef]]
    anchor  : Optional[str]
    display : Optional[bool]
    source  : Optional[str]

# =================================================================================================
# Sub and Sup elements
# =================================================================================================

@dataclass
class Strong(Elem):
    """
    RFC 7991 Section 2.50
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, "Sub", "Sup", "TT", XRef]]

@dataclass
class TT(Elem):
    """
    RFC 7991 Section 2.62
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, "Sub", "Sup", XRef]]

@dataclass
class Sub(Elem):
    """
    RFC 7991 Section 2.51
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, TT, XRef]]

@dataclass
class Sup(Elem):
    """
    RFC 7991 Section 2.52
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, TT, XRef]]

# =================================================================================================
# SpanX element
# =================================================================================================
    
@dataclass
class SpanX(Elem):
    """
    RFC 7991 Section 3.7
    """
    content  : Text
    style    : Optional[str]
    xmlSpace : Optional[str]


# =================================================================================================
# T elements
# =================================================================================================

@dataclass
class List(Elem):
    """
    RFC 7991 Section 3.4
    """
    content    : ListType["T"]
    counter    : Optional[str] 
    hangIndent : Optional[str]
    style      : Optional[str]

@dataclass
class VSpace(Elem):
    """
    RFC 7991 Section 3.10
    """
    blankLines : Optional[str]

@dataclass
class T(Elem):
    """
    RFC 7991 Section 2.53
    """
    content          : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, List, RelRef, SpanX, Strong, Sub, Sup, TT, VSpace, XRef]]
    anchor           : Optional[str]
    hangText         : Optional[str]
    keepWithNext     : Optional[bool]
    keepWithPrevious : Optional[bool]

# =================================================================================================
# Artwork element
# =================================================================================================

@dataclass
class Artwork(Elem):
    """
    RFC 7991 Section 2.5
    """
    content  : Union[Text, ListType[SVG]]
    align    : Optional[str]
    alt      : Optional[str]
    anchor   : Optional[str]
    height   : Optional[str]
    name     : Optional[str]
    src      : Optional[str]
    type     : Optional[str]
    width    : Optional[str]
    xmlSpace : Optional[str]

# =================================================================================================
# Pre and Postamble elements
# =================================================================================================

@dataclass
class Postamble(Elem):
    """
    RFC 7991 Section 3.5
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class Preamble(Elem):
    """
    RFC 7991 Section 3.6
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

# =================================================================================================
# Name element
# =================================================================================================

@dataclass
class Name(Elem):
    """
    RFC 7991 Section 2.32
    """
    content : ListType[Union[Text, CRef, ERef, RelRef, TT, XRef]]

# =================================================================================================
# SourceCode element
# =================================================================================================

@dataclass
class SourceCode(Elem):
    """
    RFC 7991 Section 2.48
    """
    content : Text
    anchor  : Optional[str]
    name    : Optional[str]
    src     : Optional[str]
    type    : Optional[str]

# =================================================================================================
# Figure element
# =================================================================================================

@dataclass
class Figure(Elem):
    """
    RFC 7991 Section 2.25
    """
    name          : Optional[Name]
    irefs         : Optional[ListType[IRef]]
    preamble      : Optional[Preamble]
    content       : ListType[Union[Artwork, SourceCode]]
    postamble     : Optional[Postamble]
    align         : Optional[str]
    alt           : Optional[str]
    anchor        : Optional[str]
    height        : Optional[str]
    src           : Optional[str]
    suppressTitle : Optional[bool]
    title         : Optional[str]
    width         : Optional[str]

# =================================================================================================
# OL elements
# =================================================================================================

@dataclass
class LI(Elem):
    """
    RFC 7991 Section 2.29
    """
    content : Union[ListType[Union[Artwork, "DL", Figure, "OL", SourceCode, T, "UL"]],
                    ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor  : Optional[str]

@dataclass
class UL(Elem):
    """
    RFC 7991 Section 2.63
    """
    content : ListType[LI]
    anchor  : Optional[str]
    empty   : Optional[bool]
    spacing : Optional[str]

@dataclass
class OL(Elem):
    """
    RFC 7991 Section 2.34
    """
    content : ListType[LI]
    anchor  : Optional[str]
    group   : Optional[str]
    spacing : Optional[str]
    start   : Optional[str]
    type    : Optional[str]

# =================================================================================================
# DL elements
# =================================================================================================

@dataclass
class DD(Elem):
    """
    RFC 7991 Section 2.18
    """
    content : Union[ListType[Union[Artwork, "DL", Figure, OL, SourceCode, T, UL]],
                    ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor  : Optional[str]

@dataclass
class DT(Elem):
    """
    RFC 7991 Section 2.21
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]
    anchor  : Optional[str]

@dataclass
class DL(Elem):
    """
    RFC 7991 Section 2.20
    """
    content : ListType[Tuple[DT, DD]]
    anchor  : Optional[str]
    hanging : Optional[bool]
    spacing : Optional[str]

# =================================================================================================
# TextTable elements
# =================================================================================================

@dataclass
class TTCol(Elem):
    """
    RFC 7991 Section 3.9
    """
    content : ListType[Union[Text, CRef, ERef, IRef, XRef]]
    align   : Optional[str]
    width   : Optional[str]

@dataclass
class C(Elem):
    """
    RFC 7991 Section 3.1
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class TextTable(Elem):
    """
    RFC 7991 Section 3.8
    """
    name          : Optional[Name]
    preamble      : Optional[Preamble]
    ttcols        : ListType[TTCol]
    cs            : Optional[ListType[C]]
    postamble     : Optional[Postamble]
    align         : Optional[str]
    anchor        : Optional[str]
    style         : Optional[str]
    suppressTitle : Optional[bool]
    title         : Optional[str]

# =================================================================================================
# TR elements
# =================================================================================================

@dataclass
class BR(Elem):
    """
    RFC 7991 Section 2.12
    """

@dataclass
class TH(Elem):
    """
    RFC 7991 Section 2.58
    """
    content : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]], 
                    ListType[Union[Text, BCP14, BR, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    align   : Optional[str]
    anchor  : Optional[str]
    colspan : Optional[str]
    rowspan : Optional[str]

@dataclass
class TD(Elem):
    """
    RFC 7991 Section 2.56
    """
    content : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]],
                    ListType[Union[Text, BCP14, BR, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    align   : Optional[str]
    anchor  : Optional[str]
    colspan : Optional[str]
    rowspan : Optional[str]

@dataclass
class TR(Elem):
    """
    RFC 7991 Section 2.61
    """
    content : ListType[Union[TD, TH]]
    anchor  : Optional[str] 

# =================================================================================================
# Table elements
# =================================================================================================

@dataclass
class TBody(Elem):
    """
    RFC 7991 Section 2.55
    """
    content : ListType[TR]
    anchor  : Optional[str]

@dataclass
class TFoot(Elem):
    """
    RFC 7991 Section 2.57
    """
    content : ListType[TR]
    anchor  : Optional[str]

@dataclass
class THead(Elem):
    """
    RFC 7991 Section 2.59
    """
    content : ListType[TR]
    anchor  : Optional[str]

@dataclass
class Table(Elem):
    """
    RFC 7991 Section 2.54
    """
    name    : Optional[Name]
    irefs   : Optional[ListType[IRef]]
    thead   : Optional[THead]
    tbodies : ListType[TBody]
    tfoot   : Optional[TFoot]
    anchor  : Optional[str]

# =================================================================================================
# Section elements
# =================================================================================================

@dataclass
class Aside(Elem):
    """
    RFC 7991 Section 2.6
    """
    content : ListType[Union[Artwork, DL, Figure, IRef, List, OL, T, Table, UL]]
    anchor  : Optional[str]

@dataclass
class BlockQuote(Elem):
    """
    RFC 7991 Section 2.10
    """
    content    : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]],
                       ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor     : Optional[str]
    cite       : Optional[str]
    quotedFrom : Optional[str]

@dataclass
class Section(Elem):
    """
    RFC 7991 Section 2.46
    """
    name        : Optional[Name]
    content     : ListType[Union[Artwork, Aside, BlockQuote, DL, Figure, IRef, OL, SourceCode, T, Table, TextTable, UL]]
    sections    : Optional[ListType["Section"]]
    anchor      : Optional[str]
    numbered    : Optional[bool]
    removeInRFC : Optional[bool]
    title       : Optional[str]
    toc         : Optional[str]

# =================================================================================================
# Middle element
# =================================================================================================
   
@dataclass
class Middle(Elem):
    """
    RFC 7991 Section 2.31
    """
    content : ListType[Section]

# =================================================================================================
# Postal elements
# =================================================================================================

@dataclass
class Street(Elem):
    """
    RFC 7991 Section 2.49
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class Region(Elem):
    """
    RFC 7991 Section 2.43
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class PostalLine(Elem):
    """
    RFC 7991 Section 2.38
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class City(Elem):
    """
    RFC 7991 Section 2.13
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class Code(Elem):
    """
    RFC 7991 Section 2.14
    """
    content : Text
    ascii   : Optional[str]
    
@dataclass
class Country(Elem):
    """
    RFC 7991 Section 2.15
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class Postal(Elem):
    """
    RFC 7991 Section 2.37
    """
    content : Union[ListType[Union[City, Code, Country, Region, Street]],
                    ListType[PostalLine]]

# =================================================================================================
# Address elements
# =================================================================================================

@dataclass
class Email(Elem):
    """
    RFC 7991 Section 2.23
    """
    content : Text
    ascii   : Optional[str]

@dataclass
class Phone(Elem):
    """
    RFC 7991 Section 2.36
    """
    content : Text

@dataclass
class URI(Elem):
    """
    RFC 7991 Section 2.64
    """
    content : Text

@dataclass
class Facsimile(Elem):
    """
    RFC 7991 Section 3.2
    """
    content : Text

@dataclass
class Address(Elem):
    """
    RFC 7991 Section 2.2
    """
    postal     : Optional[Postal]
    phone      : Optional[Phone]
    facsimile  : Optional[Facsimile]
    email      : Optional[Email]
    uri        : Optional[URI]

# =================================================================================================
# Author elements
# =================================================================================================

@dataclass
class Organization(Elem):
    """
    RFC 7991 Section 2.35
    """
    content : Text
    abbrev  : Optional[str]
    ascii   : Optional[str]

@dataclass
class Author(Elem):
    """
    RFC 7991 Section 2.7
    """
    org           : Optional[Organization]
    address       : Optional[Address]
    asciiFullname : Optional[str]
    asciiInitials : Optional[str]
    asciiSurname  : Optional[str]
    fullname      : Optional[str]
    initials      : Optional[str]
    role          : Optional[str]
    surname       : Optional[str]

# =================================================================================================
# Front elements
# =================================================================================================

@dataclass
class SeriesInfo(Elem):
    """
    RFC 7991 Section 2.47
    """
    asciiName  : Optional[str]
    asciiValue : Optional[str]
    name       : str
    status     : Optional[str]
    stream     : Optional[str]
    value      : str

@dataclass
class Title(Elem):
    """
    RFC 7991 Section 2.60
    """
    content : Text
    abbrev  : Optional[str]
    ascii   : Optional[str]

@dataclass
class Date(Elem):
    """
    RFC 7991 Section 2.17
    """
    day    : Optional[str]
    month  : Optional[str]
    year   : Optional[str]

@dataclass
class Area(Elem):
    """
    RFC 7991 Section 2.4
    """
    content : Text

@dataclass
class Workgroup(Elem):
    """
    RFC 7991 Section 2.65
    """
    content : Text

@dataclass
class Keyword(Elem):
    """
    RFC 7991 Section 2.28
    """
    content : Text

@dataclass
class Abstract(Elem):
    """
    RFC 7991 Section 2.1
    """
    content : ListType[Union[DL, OL, T, UL]]
    anchor  : Optional[str]

@dataclass
class Note(Elem):
    """
    RFC 7991 Section 2.33
    """
    name        : Optional[Name]
    content     : ListType[Union[DL, OL, T, UL]]
    removeInRFC : Optional[bool] 
    title       : Optional[str]

@dataclass
class Boilerplate(Elem):
    """
    RFC 7991 Section 2.11
    """
    content : ListType[Section]

@dataclass
class Front(Elem):
    """
    RFC 7991 Section 2.26
    """
    title       : Title
    seriesInfo  : Optional[ListType[SeriesInfo]]
    authors     : ListType[Author]
    date        : Optional[Date]
    areas       : Optional[ListType[Area]]
    workgroups  : Optional[ListType[Workgroup]]
    keywords    : Optional[ListType[Keyword]]
    abstract    : Optional[Abstract]
    notes       : Optional[ListType[Note]]
    boilerplate : Optional[Boilerplate]

# =================================================================================================
# References and ReferenceGroup elements
# =================================================================================================

@dataclass
class Format(Elem):
    """
    RFC 7991 Section 3.3
    """
    octets : Optional[str]
    target : Optional[str]
    type   : str

@dataclass
class Annotation(Elem):
    """
    RFC 7991 Section 2.3
    """
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class RefContent(Elem):
    """
    RFC 7991 Section 2.39
    """
    content : ListType[Union[Text, BCP14, EM, Strong, Sub, Sup, TT]]

@dataclass
class Reference(Elem):
    """
    RFC 7991 Section 2.40
    """
    front      : Front
    content    : ListType[Union[Annotation, Format, RefContent, SeriesInfo]]
    anchor     : str
    quoteTitle : Optional[bool] 
    target     : Optional[str]

@dataclass
class ReferenceGroup(Elem):
    """
    RFC 7991 Section 2.41
    """
    content : ListType[Reference]
    anchor  : str

@dataclass
class References(Elem):
    """
    RFC 7991 Section 2.42
    """
    name    : Optional[Name]
    content : ListType[Union[Reference, ReferenceGroup]]
    anchor  : Optional[str]
    title   : Optional[str]

# =================================================================================================
# Back elements
# =================================================================================================

@dataclass
class DisplayReference(Elem):
    """
    RFC 7991 Section 2.19
    """
    target : str
    to     : str

@dataclass
class Back(Elem):
    """
    RFC 7991 Section 2.8
    """
    displayrefs : Optional[ListType[DisplayReference]]
    refs        : Optional[ListType[References]]
    sections    : Optional[ListType[Section]]

# =================================================================================================
# Link element
# =================================================================================================

@dataclass
class Link(Elem):
    """
    RFC 7991 Section 2.30
    """
    href   : str
    rel    : Optional[str]

# =================================================================================================
# RFC
# =================================================================================================
    
@dataclass
class RFC(Elem):
    """
    RFC 7991 Section 2.45
    """
    links          : Optional[ListType[Link]]
    front          : Front
    middle         : Middle
    back           : Optional[Back]
    category       : Optional[str]
    consensus      : Optional[bool]
    docName        : Optional[str]
    indexInclude   : Optional[bool] 
    ipr            : Optional[str]
    iprExtract     : Optional[str]
    number         : Optional[str]
    obsoletes      : Optional[str]
    prepTime       : Optional[str]
    seriesNo       : Optional[str]
    sortRefs       : Optional[bool] 
    submissionType : Optional[str]
    symRefs        : Optional[bool] 
    tocDepth       : Optional[str]
    tocInclude     : Optional[bool] 
    updates        : Optional[str]
    version        : Optional[str]
