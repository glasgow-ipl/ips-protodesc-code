import parsley
import os
import string
import itertools
from rfc2xml import Rfc2Xml
from typing import Callable
from .elements import Field, Art, ArtField
from .rel_loc import RelLoc
from .elements.expression import *
from .elements.expression.method_invocation import *
from .names import Names


class Parse:
    parser: Callable = None

    def __init__(self):
        self.load_parser_file(os.path.dirname(os.path.realpath(__file__)) + "/grammar.txt")

    def load_parser(self, grammar: str = None):
        self.parser = parsley.makeGrammar(grammar, {
            'punctuation': string.punctuation,
            'ascii_uppercase': string.ascii_uppercase,
            'ascii_lowercase': string.ascii_lowercase,
            'itertools': itertools,

            'Art': Art,
            'ArtField': ArtField,
            'Field': Field,
            'RelLoc': RelLoc,
            'Names': Names,

            'Constant': Constant,
            'FieldAccess': FieldAccess,
            'IfElse': IfElse,
            'Other': Other,

            'And': And,
            'Not': Not,
            'Or': Or,
            'Divice': Divide,
            'Eq': Eq,
            'Ge': Ge,
            'Gt': Gt,
            'Le': Le,
            'Lt': Lt,
            'Minus': Minus,
            'Modulo': Modulo,
            'Multiply': Multiply,
            'Ne': Ne,
            'Plus': Plus,

        })

    def load_parser_file(self, filename: str):
        with open(filename) as fp:
            grammar = fp.read()
        return self.load_parser(grammar)





    @staticmethod
    def parse_file(filename):
        with open(filename) as fp:
            contents = fp.read()
        return Parse.parse(contents)

    @staticmethod
    def parse(s):
        return Rfc2Xml.parse(s)
