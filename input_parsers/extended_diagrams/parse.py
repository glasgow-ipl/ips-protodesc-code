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
            'Boolean': Boolean,
            'Size': Size,
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

