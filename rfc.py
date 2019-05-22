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
    parent  : Union["Annotation", "BlockQuote", "DD", "DT", "EM", "LI", "Preamble", "RefContent", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT"]
    content : Text  

# =================================================================================================
# EM element
# =================================================================================================

@dataclass
class EM(Elem):
    """
    RFC 7991 Section 2.22
    """
    parent  : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "LI", "Preamble", "RefContent", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT"]
    content : ListType[Union[Text, BCP14, "CRef", "IRef", "RelRef", "Strong", "Sub", "Sup", "TT", "XRef"]]

# =================================================================================================
# {C, X, I, E, Rel}Ref elements
# =================================================================================================

@dataclass
class RelRef(Elem):
    """
    RFC 7991 Section 2.44
    """
    parent        : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "EM", "LI", "Name", "Preamble", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT"]
    content       : Text
    displayFormat : str
    relative      : str
    section       : str
    target        : str

@dataclass
class ERef(Elem):
    """
    RFC 7991 Section 2.24
    """
    parent  : Union["Annotation", "BlockQuote", "C", "CRef", "DD", "DT", "EM", "LI", "Name", "Postamble", "Preamble", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT", "TTCol"]
    content : Text
    target  : str

@dataclass
class IRef(Elem):
    """
    RFC 7991 Section 2.27
    """
    parent  : Union["Annotation", "Aside", "BlockQuote", "C", "DD", "DT", "EM", "Figure", "LI", "Postamble", "Preamble", "Section", "Strong", "Sub", "Sup", "T", "Table", "TD", "TH", "TT", "TTCol"]
    item    : str
    primary : bool
    subitem : str

@dataclass
class XRef(Elem):
    """
    RFC 7991 Section 2.66
    """
    parent  : Union["Annotation", "BlockQuote", "C", "CRef", "DD", "DT", "EM", "LI", "Name", "Postamble", "Preamble", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT", "TTCol"]
    content : Text
    format  : str
    pageno  : bool
    target  : str

@dataclass
class CRef(Elem):
    """
    RFC 7991 Section 2.16
    """
    parent  : Union["Annotation", "BlockQuote", "C", "DD", "DT", "EM", "LI", "Name", "Postamble", "Preamble", "Strong", "Sub", "Sup", "T", "TD", "TH", "TT", "TTCol"]
    content : ListType[Union[Text, EM, ERef, RelRef, "Strong", "Sub", "Sup", "TT", XRef]]
    anchor  : str
    display : bool
    source  : str

# =================================================================================================
# Sub and Sup elements
# =================================================================================================

@dataclass
class Strong(Elem):
    """
    RFC 7991 Section 2.50
    """
    parent  : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "EM", "LI", "Preamble", "RefContent", "Sub", "Sup", "T", "TD", "TH", "TT"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, "Sub", "Sup", "TT", XRef]]

@dataclass
class TT(Elem):
    """
    RFC 7991 Section 2.62
    """
    parent  : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "EM", "LI", "Name", "Preamble", "RefContent", "Strong", "Sub", "Sup", "T", "TD", "TH"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, "Sub", "Sup", XRef]]

@dataclass
class Sub(Elem):
    """
    RFC 7991 Section 2.51
    """
    parent  : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "EM", "LI", "Preamble", "RefContent", "Strong", "T", "TD", "TH", "TT"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, TT, XRef]]

@dataclass
class Sup(Elem):
    """
    RFC 7991 Section 2.52
    """
    parent  : Union["Annotation", "BlockQuote", "CRef", "DD", "DT", "EM", "LI", "Preamble", "RefContent", "Strong", "T", "TD", "TH", "TT"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, TT, XRef]]

# =================================================================================================
# SpanX element
# =================================================================================================
    
@dataclass
class SpanX(Elem):
    """
    RFC 7991 Section 3.7
    """
    parent   : Union["Annotation", "C", "Postamble", "Preamble", "T"]
    content  : Text
    style    : str
    xmlSpace : str


# =================================================================================================
# T elements
# =================================================================================================

@dataclass
class List(Elem):
    """
    RFC 7991 Section 3.4
    """
    parent     : "T"
    content    : ListType["T"]
    counter    : str 
    hangIndent : str
    style      : str

@dataclass
class VSpace(Elem):
    """
    RFC 7991 Section 3.10
    """
    parent     : "T"
    blankLines : str

@dataclass
class T(Elem):
    """
    RFC 7991 Section 2.53
    """
    parent           : Union["Abstract", "Aside", "BlockQuote", "DD", "LI", List, "Note", "Section", "TD", "TH"]
    content          : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, List, RelRef, SpanX, Strong, Sub, Sup, TT, VSpace, XRef]]
    anchor           : str
    hangText         : str
    keepWithNext     : bool
    keepWithPrevious : bool

# =================================================================================================
# Artwork element
# =================================================================================================

@dataclass
class Artwork(Elem):
    """
    RFC 7991 Section 2.5
    """
    parent   : Union["Aside", "BlockQuote", "DD", "Figure", "LI", "Section", "TD", "TH"]
    content  : Union[Text, ListType[SVG]]
    align    : str
    alt      : str
    anchor   : str
    height   : str
    name     : str
    src      : str
    type     : str
    width    : str
    xmlSpace : str

# =================================================================================================
# Pre and Postamble elements
# =================================================================================================

@dataclass
class Postamble(Elem):
    """
    RFC 7991 Section 3.5
    """
    parent  : Union["Figure", "TextTable"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class Preamble(Elem):
    """
    RFC 7991 Section 3.6
    """
    parent  : Union["Figure", "TextTable"]
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

# =================================================================================================
# Name element
# =================================================================================================

@dataclass
class Name(Elem):
    """
    RFC 7991 Section 2.32
    """
    parent  : Union["Figure", "Note", "References", "Section", "Table", "TextTable"]
    content : ListType[Union[Text, CRef, ERef, RelRef, TT, XRef]]

# =================================================================================================
# SourceCode element
# =================================================================================================

@dataclass
class SourceCode(Elem):
    """
    RFC 7991 Section 2.48
    """
    parent  : Union["BlockQuote", "DD", "Figure", "LI", "Section", "TD", "TH"]
    content : Text
    anchor  : str
    name    : str
    src     : str
    type    : str

# =================================================================================================
# Figure element
# =================================================================================================

@dataclass
class Figure(Elem):
    """
    RFC 7991 Section 2.25
    """
    parent        : Union["Aside", "BlockQuote", "DD", "LI", "Section", "TD", "TH"]
    name          : Optional[Name]
    irefs         : Optional[ListType[IRef]]
    preamble      : Optional[Preamble]
    content       : ListType[Union[Artwork, SourceCode]]
    postamble     : Optional[Postamble]
    align         : str
    alt           : str
    anchor        : str
    height        : str
    src           : str
    suppressTitle : bool
    title         : str
    width         : str

# =================================================================================================
# OL elements
# =================================================================================================

@dataclass
class LI(Elem):
    """
    RFC 7991 Section 2.29
    """
    parent  : Union["OL", "UL"]
    content : Union[ListType[Union[Artwork, "DL", Figure, "OL", SourceCode, T, "UL"]],
                    ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor  : str

@dataclass
class UL(Elem):
    """
    RFC 7991 Section 2.63
    """
    parent  : Union["Abstract", "Aside", "BlockQuote", "DD", LI, "Note", "Section", "TD", "TH"]
    content : ListType[LI]
    anchor  : str
    empty   : bool
    spacing : str

@dataclass
class OL(Elem):
    """
    RFC 7991 Section 2.34
    """
    parent  : Union["Abstract", "Aside", "BlockQuote", "DD", LI, "Note", "Section", "TD", "TH"]
    content : ListType[LI]
    anchor  : str
    group   : str
    spacing : str
    start   : str
    type    : str

# =================================================================================================
# DL elements
# =================================================================================================

@dataclass
class DD(Elem):
    """
    RFC 7991 Section 2.18
    """
    parent  : "DL"
    content : Union[ListType[Union[Artwork, "DL", Figure, OL, SourceCode, T, UL]],
                    ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor  : str

@dataclass
class DT(Elem):
    """
    RFC 7991 Section 2.21
    """
    parent  : "DL" 
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]
    anchor  : str

@dataclass
class DL(Elem):
    """
    RFC 7991 Section 2.20
    """
    parent  : Union["Abstract", "Aside", "BlockQuote", DD, LI, "Note", "Section", "TD", "TH"]
    content : ListType[Tuple[DT, DD]]
    anchor  : str
    hanging : bool
    spacing : str

# =================================================================================================
# TextTable elements
# =================================================================================================

@dataclass
class TTCol(Elem):
    """
    RFC 7991 Section 3.9
    """
    parent  : "TextTable"
    content : ListType[Union[Text, CRef, ERef, IRef, XRef]]
    align   : str
    width   : str

@dataclass
class C(Elem):
    """
    RFC 7991 Section 3.1
    """
    parent  : "TextTable"
    content : ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class TextTable(Elem):
    """
    RFC 7991 Section 3.8
    """
    parent        : Union["Aside", "Section"]
    name          : Optional[Name]
    preamble      : Optional[Preamble]
    ttcols        : ListType[TTCol]
    cs            : Optional[ListType[C]]
    postamble     : Optional[Postamble]
    align         : str
    anchor        : str
    style         : str
    suppressTitle : bool
    title         : str 

# =================================================================================================
# TR elements
# =================================================================================================

@dataclass
class BR(Elem):
    """
    RFC 7991 Section 2.12
    """
    parent : Union["TD", "TR"]

@dataclass
class TH(Elem):
    """
    RFC 7991 Section 2.58
    """
    parent  : "TR"
    content : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]], 
                    ListType[Union[Text, BCP14, BR, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    align   : str
    anchor  : str
    colspan : str
    rowspan : str

@dataclass
class TD(Elem):
    """
    RFC 7991 Section 2.56
    """
    parent  : "TR"
    content : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]],
                    ListType[Union[Text, BCP14, BR, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    align   : str
    anchor  : str
    colspan : str
    rowspan : str

@dataclass
class TR(Elem):
    """
    RFC 7991 Section 2.61
    """
    parent  : Union["TBody", "TFoot", "THead"]
    content : ListType[Union[TD, TH]]
    anchor  : str 

# =================================================================================================
# Table elements
# =================================================================================================

@dataclass
class TBody(Elem):
    """
    RFC 7991 Section 2.55
    """
    parent  : "Table"
    content : ListType[TR]
    anchor  : str

@dataclass
class TFoot(Elem):
    """
    RFC 7991 Section 2.57
    """
    parent  : "Table"
    content : ListType[TR]
    anchor  : str

@dataclass
class THead(Elem):
    """
    RFC 7991 Section 2.59
    """
    parent  : "Table"
    content : ListType[TR]
    anchor  : str

@dataclass
class Table(Elem):
    """
    RFC 7991 Section 2.54
    """
    parent  : Union["Aside", "Section"]
    name    : Optional[Name]
    irefs   : Optional[ListType[IRef]]
    thead   : Optional[THead]
    tbodies : ListType[TBody]
    tfoot   : Optional[TFoot]
    anchor  : str

# =================================================================================================
# Section elements
# =================================================================================================

@dataclass
class Aside(Elem):
    """
    RFC 7991 Section 2.6
    """
    parent  : "Section"
    content : ListType[Union[Artwork, DL, Figure, IRef, List, OL, T, Table, UL]]
    anchor  : str

@dataclass
class BlockQuote(Elem):
    """
    RFC 7991 Section 2.10
    """
    parent     : "Section"
    content    : Union[ListType[Union[Artwork, DL, Figure, OL, SourceCode, T, UL]],
                       ListType[Union[Text, BCP14, CRef, EM, ERef, IRef, RelRef, Strong, Sub, Sup, TT, XRef]]]
    anchor     : str
    cite       : str
    quotedFrom : str

@dataclass
class Section(Elem):
    """
    RFC 7991 Section 2.46
    """
    parent      : Union["Back", "Boilerplate", "Middle", "Section"]
    name        : Optional[Name]
    content     : ListType[Union[Artwork, Aside, BlockQuote, DL, Figure, IRef, OL, SourceCode, T, Table, TextTable, UL]]
    sections    : Optional[ListType["Section"]]
    anchor      : str
    numbered    : bool
    removeInRFC : bool
    title       : str
    toc         : str

# =================================================================================================
# Middle element
# =================================================================================================
   
@dataclass
class Middle(Elem):
    """
    RFC 7991 Section 2.31
    """
    parent  : "RFC"
    content : ListType[Section]

# =================================================================================================
# Postal elements
# =================================================================================================

@dataclass
class Street(Elem):
    """
    RFC 7991 Section 2.49
    """
    parent  : "Postal" 
    content : Text
    ascii   : str

@dataclass
class Region(Elem):
    """
    RFC 7991 Section 2.43
    """
    parent  : "Postal"
    content : Text
    ascii   : str

@dataclass
class PostalLine(Elem):
    """
    RFC 7991 Section 2.38
    """
    parent  : "Postal"
    content : Text
    ascii   : str

@dataclass
class City(Elem):
    """
    RFC 7991 Section 2.13
    """
    parent  : "Postal"
    content : Text
    ascii   : str

@dataclass
class Code(Elem):
    """
    RFC 7991 Section 2.14
    """
    parent  : "Postal"
    content : Text
    ascii   : str
    
@dataclass
class Country(Elem):
    """
    RFC 7991 Section 2.15
    """
    parent  : "Postal"
    content : Text
    ascii   : str

@dataclass
class Postal(Elem):
    """
    RFC 7991 Section 2.37
    """
    parent  : "Address"
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
    parent  : "Address"
    content : Text
    ascii   : str

@dataclass
class Phone(Elem):
    """
    RFC 7991 Section 2.36
    """
    parent  : "Address"
    content : Text

@dataclass
class URI(Elem):
    """
    RFC 7991 Section 2.64
    """
    parent  : "Address"
    content : Text

@dataclass
class Facsimile(Elem):
    """
    RFC 7991 Section 3.2
    """
    parent  : "Address"
    content : str

@dataclass
class Address(Elem):
    """
    RFC 7991 Section 2.2
    """
    parent     : "Author"
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
    parent  : Optional["Author"]
    content : Text
    abbrev  : Optional[str]
    ascii   : Optional[str]

@dataclass
class Author(Elem):
    """
    RFC 7991 Section 2.7
    """
    parent        : Optional["Front"]
    org           : Optional[Organization]
    address       : Optional[Address]
    asciiFullname : str
    asciiInitials : str
    asciiSurname  : str
    fullname      : str
    initials      : str
    role          : str
    surname       : str

# =================================================================================================
# Front elements
# =================================================================================================

@dataclass
class SeriesInfo(Elem):
    """
    RFC 7991 Section 2.47
    """
    parent     : Optional[Union["Front", "Reference"]]
    asciiName  : str
    asciiValue : str
    name       : str
    status     : str # TODO: optional?
    stream     : str # TODO: optional?
    value      : str

@dataclass
class Title(Elem):
    """
    RFC 7991 Section 2.60
    """
    parent  : Optional["Front"]
    content : Text
    abbrev  : str
    ascii   : str

@dataclass
class Date(Elem):
    """
    RFC 7991 Section 2.17
    """
    parent : "Front"
    day    : str
    month  : str
    year   : str

@dataclass
class Area(Elem):
    """
    RFC 7991 Section 2.4
    """
    parent  : "Front"
    content : Text

@dataclass
class Workgroup(Elem):
    """
    RFC 7991 Section 2.65
    """
    parent  : "Front"
    content : str

@dataclass
class Keyword(Elem):
    """
    RFC 7991 Section 2.28
    """
    parent  : "Front"
    content : Text

@dataclass
class Abstract(Elem):
    """
    RFC 7991 Section 2.1
    """
    parent  : "Front"
    content : ListType[Union[DL, OL, T, UL]]
    anchor  : str

@dataclass
class Note(Elem):
    """
    RFC 7991 Section 2.33
    """
    parent      : "Front"
    name        : Optional[Name]
    content     : ListType[Union[DL, OL, T, UL]]
    removeInRFC : bool 
    title       : str

@dataclass
class Boilerplate(Elem):
    """
    RFC 7991 Section 2.11
    """
    parent  : "Front"
    content : ListType[Section]

@dataclass
class Front(Elem):
    """
    RFC 7991 Section 2.26
    """
    parent      : Union["Reference", "RFC"]
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
    parent : "Reference" 
    octets : str
    target : str
    type   : str

@dataclass
class Annotation(Elem):
    """
    RFC 7991 Section 2.3
    """
    parent  : "Reference"
    content : ListType[Union[BCP14, CRef, EM, ERef, IRef, RelRef, SpanX, Strong, Sub, Sup, TT, XRef]]

@dataclass
class RefContent(Elem):
    """
    RFC 7991 Section 2.39
    """
    parent  : "Reference"
    content : ListType[Union[Text, BCP14, EM, Strong, Sub, Sup, TT]]

@dataclass
class Reference(Elem):
    """
    RFC 7991 Section 2.40
    """
    parent     : Union["ReferenceGroup", "References"]
    front      : Front
    content    : ListType[Union[Annotation, Format, RefContent, SeriesInfo]]
    anchor     : str
    quoteTitle : bool 
    target     : str

@dataclass
class ReferenceGroup(Elem):
    """
    RFC 7991 Section 2.41
    """
    parent  : "References"
    content : ListType[Reference]
    anchor  : str

@dataclass
class References(Elem):
    """
    RFC 7991 Section 2.42
    """
    parent  : "Back"
    name    : Optional[Name]
    content : ListType[Union[Reference, ReferenceGroup]]
    anchor  : str
    title   : str

# =================================================================================================
# Back elements
# =================================================================================================

@dataclass
class DisplayReference(Elem):
    """
    RFC 7991 Section 2.19
    """
    parent : "Back"
    target : str
    to     : str

@dataclass
class Back(Elem):
    """
    RFC 7991 Section 2.8
    """
    parent      : "RFC"
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
    parent : "RFC"
    href   : str
    rel    : str

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
    category       : str
    consensus      : str
    docName        : str
    indexInclude   : bool 
    ipr            : str
    iprExtract     : str
    number         : str
    obsoletes      : str
    prepTime       : str
    seriesNo       : str
    sortRefs       : bool 
    submissionType : str
    symRefs        : bool 
    tocDepth       : str
    tocInclude     : bool 
    updates        : str
    version        : str