from rfc2xml.elements import Element
from protocol import Expression as ProtocolExpression
from lxml import etree
from output_formatters.json import Json
import json
from protocol import *


class Expression(Element):
    tag_name: str = "expression"
    expression: ProtocolExpression

    xxx = {
        "eq": "==",
        "ne": "!=",
        "and": "&&",
        "or": "||",
        "le": "<=",
        "lt": "<",
        "ge": ">=",
        "gt": ">",
        "multiply": "*",
        "divide": "/",
        "modulo": "%",
        "plus": "+",
        "minus": "-",
    }

    def __init__(self, expression: ProtocolExpression):
        super().__init__()
        self.expression = expression

    def get_expression_text(self) -> str:
        return self.expression_to_string(self.expression)
        #return json.dumps(Json.constraint_to_dict(self.expression), indent=4)

    def expression_to_string(self, expression: ProtocolExpression):
        if isinstance(expression, ArgumentExpression):
            return self.expression_to_string(expression.arg_value)
        elif isinstance(expression, MethodInvocationExpression):
            if expression.method_name in self.xxx:
                operator = " " + self.xxx[expression.method_name] + " "
            else:
                operator = "." + expression.method_name + "()"
            output = self.expression_to_string(expression.target) + operator
            if len(expression.arg_exprs) == 1:
                output += self.expression_to_string(expression.arg_exprs[0])
            elif len(expression.arg_exprs) > 1:
                output += "["
                for arg in expression.arg_exprs:
                    output += self.expression_to_string(arg) + ", "
                output += "]"
            return output
        elif isinstance(expression, IfElseExpression):
            return self.expression_to_string(expression.condition) + " ? " + self.expression_to_string(expression.if_true) + " : " + self.expression_to_string(expression.if_false)
        elif isinstance(expression, ConstantExpression):
            return str(expression.value)   # Type?
        elif isinstance(expression, FieldAccessExpression):
            return self.expression_to_string(expression.target) + "." + expression.field_name
        elif isinstance(expression, ThisExpression):
            return "this"
        else:
            return "NotImplemented<" + str(expression.__class__) + ">"

    def to_xml(self):
        element = etree.Element(str(self.tag_name), self.get_attributes())
        #element.text = etree.CDATA("\n" + self.get_expression_text() + "\n")
        element.text = self.get_expression_text()
        return element
