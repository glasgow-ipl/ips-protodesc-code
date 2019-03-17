import parsley
import os
import string
import itertools
from typing import Callable
from .elements import Field, Art, ArtField
from .rel_loc import RelLoc
from .names import Names
from protocol import *


class Parse:
    """
    Wrapper class for handling parsing
    """

    parser: Callable = None
    protocol: Protocol

    def __init__(self, protocol: Protocol):
        self.load_parser_file(os.path.dirname(os.path.realpath(__file__)) + "/grammar.txt", protocol)
        self.protocol = protocol

    def load_parser(self, grammar: str, protocol: Protocol) -> None:
        """
        Load the parser using the given grammar
        :param grammar: The parser grammar
        :param protocol: The protocol
        :return: None
        """
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
        """
        Load the parser using grammar from the given file
        :param filename: File containing grammar
        :param protocol: The protocol
        :return:
        """
        with open(filename) as fp:
            grammar = fp.read()
        self.load_parser(grammar, protocol)

