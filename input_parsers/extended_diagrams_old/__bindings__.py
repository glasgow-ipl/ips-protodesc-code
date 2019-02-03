from .dom import *
from .dom import __all__ as dom_all
from .dom.element import *
from .dom.element import __all__ as element_all
from .dom.section import *
from .dom.section import __all__ as section_all

from .ir.expression import *
from .ir.expression import __all__ as expression_all
from .ir.expression.method_invocation import *
from .ir.expression.method_invocation import __all__ as method_invocation_all

def bindings_sub(b):
    o = {}
    for a in b:
        o[a] = eval(a)
    return o


def bindings():
    return {
        **bindings_sub(dom_all),
        **bindings_sub(element_all),
        **bindings_sub(section_all),

        **bindings_sub(expression_all),
        **bindings_sub(method_invocation_all),
    }