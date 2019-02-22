import parsley
import os
import string
import itertools
from rfc2xml import Rfc2Xml
from typing import Callable
from .elements import Field, Art, ArtField
from .rel_loc import RelLoc
from .names import Names
from protocol import *


class Parse:
    parser: Callable = None
    protocol: Protocol

    def __init__(self, protocol: Protocol):
        self.load_parser_file(os.path.dirname(os.path.realpath(__file__)) + "/grammar.txt", protocol)
        self.protocol = protocol

    @staticmethod
    def get_generic_int(size: int, protocol: Protocol):
        type_name = "BitString$" + str(4)

        if protocol.is_type(type_name):
            return protocol.get_type(type_name)

        else:
            return protocol.derive_type(
                name=type_name,
                derived_from=BitString(
                    name="BitString$" + str(size),
                    size=size
                ),
                also_implements=[
                    protocol.get_trait("Sized"),
                    protocol.get_trait("Value"),
                    protocol.get_trait("Equality"),
                    protocol.get_trait("Ordinal"),
                    protocol.get_trait("ArithmeticOps"),
                ]
            )

    def load_parser(self, grammar: str, protocol: Protocol):

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

            'protocol': protocol,
            'get_generic_int': Parse.get_generic_int,
            'Boolean': Boolean,
            'ArgumentExpression': ArgumentExpression,
            'MethodInvocationExpression': MethodInvocationExpression,
            'ConstantExpression': ConstantExpression,
            'FieldAccessExpression': FieldAccessExpression,
            'ThisExpression': ThisExpression,
            'IfElseExpression': IfElseExpression,
        })

    def load_parser_file(self, filename: str, protocol: Protocol):
        with open(filename) as fp:
            grammar = fp.read()
        return self.load_parser(grammar, protocol)





    @staticmethod
    def parse_file(filename):
        with open(filename) as fp:
            contents = fp.read()
        return Parse.parse(contents)

    @staticmethod
    def parse(s):
        return Rfc2Xml.parse(s)
