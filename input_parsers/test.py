#!/usr/bin/env python3
from extended_diagrams.dom.expression import *
from extended_diagrams.dom.expression.method_invocation import *
from extended_diagrams.__bindings__ import bindings
from extended_diagrams import *



if __name__ == "__main__":

    t1 = Eq(
        Constant(2),
        FieldAccess("version")
    )

    t2 = Eq(
        Multiply(
            Constant(2),
            FieldAccess("version")
        ),
        FieldAccess("Length")
    )

    t3 = Eq(
        Multiply(
            Constant(8),
            FieldAccess("Length")
        ),
        FieldAccess("Payload").width()
    )

    get_parser_file()
