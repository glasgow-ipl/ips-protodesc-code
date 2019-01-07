from ..empty import *
from typing import List
from ...construct import Construct


class MethodInvocation(Expression):
    method: str = None
    self: 'Expression'
    arguments: List['Expression']

    def __init__(self, _self: 'Expression' = None, arguments: List['Expression'] = None):
        if _self is None:
            _self = Empty()
        if arguments is None:
            arguments = []

        if not arguments:
            arguments = [Empty()]
        self.self = _self
        self.arguments = arguments

    def to_dict(self):

        arguments = []
        for argument in self.arguments:
            arguments.append(argument.to_dict())
        if arguments == [None]:
            arguments = None

        return {
            "expression": "MethodInvocation",
            "method": self.method,
            "self": self.self.to_dict(),
            "arguments": arguments
        }

    def get_field_names(self):
        arguments_definitions = []
        for argument in self.arguments:
            arguments_definitions.append(argument.get_field_names())

        return self.self.get_field_names() + arguments_definitions

    def get_definitions(self) -> List[Construct]:
        arguments_definitions = []
        for argument in self.arguments:
            arguments_definitions += argument.get_definitions()

        return self.self.get_definitions() + arguments_definitions
