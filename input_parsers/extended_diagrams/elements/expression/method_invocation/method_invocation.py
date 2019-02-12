from lxml import etree
from ..empty import *
from typing import List
from typing import Dict
from ..empty import Empty


class MethodInvocation(Expression):
    tag_name: str = "expression_method_invocation"
    method: str = None
    self: 'Expression'
    arguments: List['Expression']

    def __init__(self, _self: 'Expression' = None, arguments: List['Expression'] = None):
        super().__init__()
        if _self is None:
            _self = Empty()
        if arguments is None:
            arguments = []

        if not arguments:
            arguments = [Empty()]
        self.self = _self
        self.arguments = arguments

    def children_to_xml(self, element):
        element.append(self.self.to_xml())
        arguments = etree.Element("arguments")
        for arg in self.arguments:
            if not isinstance(arg, Empty):
                arguments.append(arg.to_xml())
        if len(arguments) > 0:
            element.append(arguments)

    def get_attributes(self) -> Dict[str, str]:
        attributes = super().get_attributes()
        if self.method is not None:
            attributes["method"] = self.method
        return attributes
