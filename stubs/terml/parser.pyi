from terml.nodes import Tag as Tag, Term as Term, termMaker as termMaker
from typing import Any, Optional

integer_types: Any

def concat(*bits: Any): ...

Character: Any

def makeFloat(sign: Any, ds: Any, tail: Any): ...
def signedInt(sign: Any, x: Any, base: int = ...): ...
def join(x: Any): ...
def makeHex(sign: Any, hs: Any): ...
def makeOctal(sign: Any, ds: Any): ...
def isDigit(x: Any): ...
def isOctDigit(x: Any): ...
def isHexDigit(x: Any): ...
def contains(container: Any, value: Any): ...
def cons(first: Any, rest: Any): ...
def makeTag(nameSegs: Any): ...
def prefixedTag(tagnameSegs: Any): ...
def tagString(string: Any): ...
def numberType(n: Any): ...
def leafInternal(tag: Any, data: Any, span: Optional[Any] = ...): ...
def makeTerm(t: Any, args: Optional[Any] = ..., span: Optional[Any] = ...): ...
def Tuple(args: Any, span: Optional[Any] = ...): ...
def Bag(args: Any, span: Optional[Any] = ...): ...
def LabelledBag(f: Any, arg: Any, span: Optional[Any] = ...): ...
def Attr(k: Any, v: Any, span: Optional[Any] = ...): ...

TermLParser: Any

def parseTerm(termString: Any): ...
