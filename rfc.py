#!/usr/bin/env python3.7
#
# The xml2rfc Version 3 Vocabulary, as defined in RFC 7991
#

from typing      import List, Union
from dataclasses import dataclass

class Elem:
    pass

class Text(Elem):
    text     : str

@dataclass
class Abstract(Elem):
    """
    RFC 7991 Section 2.1
    """
    parent   : Front
    abstract : List[Union[DL,OL,UL,T]]
    anchor   : str

@dataclass
class Address(Elem):
    """
    RFC 7991 Section 2.2
    """
    parent    : Author
    postal    : Postal
    phone     : Phone
    facsimile : Facsimilie
    email     : Email
    uri       : URI

@dataclass
class Annotation(Elem):
    """
    RFC 7991 Section 2.3
    """
    parent     : Reference
    annotation : List[Union[Text,BCP14,CRef,EM,ERef,IRef,RelRef,SpanX,Strong,Sub,Sup,TT,Xref]]

@dataclass
class Area(Elem):
    """
    RFC 7991 Section 2.4
    """
    parent  : Front
    area    : str

@dataclass
class Artwork(Elem):
    """
    RFC 7991 Section 2.5
    """
    parent       : Union[Aside,BlockQuote,DD,Figure,LI,Section,TD,TH]
    artwork      : Union[Text,SVG]
    align        : str
    alt          : str
    anchor       : str
    name         : str
    src          : str
    artwork_type : str

@dataclass
class Aside(Elem):
    """
    RFC 7991 Section 2.6
    """
    parent : Section
    aside  : List[Union[Artwork,DL,Figure,IRef,List,OL,T,Table,UL]]
    anchor : str

@dataclass
class Author(Elem):
    """
    RFC 7991 Section 2.7
    """
    parent         : Front
    organization   : Organization
    address        : Address
    ascii_fullname : str
    ascii_initials : str
    ascii_surname  : str
    fullname       : str
    initials       : str
    surname        : str
    role           : str

@dataclass
class Back(Elem):
    """
    RFC 7991 Section 2.8
    """
    parent           : RFC
    displayreference : List[DisplayReference]
    references       : List[References]
    sections         : List[Section]

@dataclass
class BCP14(Elem):
    """
    RFC 7991 Section 2.9
    """
    parent : Union[Annotation,Blockquote,DD,DT,EM,LI,Preamble,RefContent,String,Sub,Sup,T,TD,TH,TT]
    phrase : str

@dataclass
class Blockquote(Elem):
    """
    RFC 7991 Section 2.10
    """
    parent      : Section
    blockquote  : Union[List[Union[Artwork,DL,Figure,OL,Sourcecode,T,UL]],
                        List[Union[Text,BCP14,CRef,EM,ERef,IRef,RelRef,Strong,Sub,Sup,TT,XRef]]]
    anchor      : str
    cite        : str
    quoted_from : str

@dataclass
class Boilerplate(Elem):
    """
    RFC 7991 Section 2.11
    """
    parent   : Front
    sections : List[Section]

@dataclass
class Br(Elem):
    """
    RFC 7991 Section 2.12
    """
    parent : Union[TD,TH]

@dataclass
class City(Elem):
    """
    RFC 7991 Section 2.13
    """
    parent     : Postal
    city       : str
    city_ascii : str

@dataclass
class PostCode(Elem):
    """
    RFC 7991 Section 2.14
    """
    parent         : Postal
    postcode       : str
    postcode_ascii : str

@dataclass
class Country(Elem):
    """
    RFC 7991 Section 2.15
    """
    parent         : Postal
    country        : str
    country_ascii  : str

@dataclass
class CRef(Elem):
    """
    RFC 7991 Section 2.16
    """
    parent  : Union[Annotation,Blockquote,C,DD,DT,EM,LI,Name,Postamble,Preamble,Strong,Sub,Sup,T,TD,TH,TT,TTCOL]
    cref    : List[Union[Text,EM,ERef,RelRef,Strong,Sub,Sup,TT,Xref]]
    anchor  : str
    display : bool
    source  : str

@dataclass
class Date(Elem):
    """
    RFC 7991 Section 2.17
    """
    parent : Front
    day    : str
    month  : str
    year   : str

@dataclass
class DD(Elem):
    """
    RFC 7991 section 2.18
    """
    parent  : DL
    content : Union[List[Union[Artwork,DL,Figure,OL,Sourcecode,T,UL]],
                    List[Union[Text,BCP14,CRef,EM,ERef,IRef,RelRef,Strong,Sub,Sup,TT,XRef]]]
    anchor  : str



