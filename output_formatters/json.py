import json
from .outputformatter import OutputFormatter
from protocol import *
from typing import Dict, Union


class Json(OutputFormatter):
    output: Dict
    definitions: List

    def __init__(self):
        self.output = {}
        self.definitions = []

    def generate_output(self):
        return json.dumps(self.output, indent=4)

    def format_bitstring(self, bitstring: BitString):
        self.definitions.append({
            "construct": "BitString",
            "name": bitstring.name,
            "size": bitstring.size  # TODO: Width vs. Size
        })

    def format_struct(self, struct: Struct):
        fields = []

        for field in struct.fields:
            if isinstance(field, BitString):
                self.format_bitstring(field)

            fields.append({
                "name": field.field_name,
                "type": field.field_type.name,
                "transform": field.transform
            })

        constraints = []
        for constraint in struct.constraints:
            constraints.append(self._constraint_to_dict(constraint))

        self.definitions.append({
            "construct": "Struct",
            "name": struct.name,
            "fields": fields,
            "constraints": constraints
        })

    def _constraint_to_dict(self, expression: Union['Expression', 'ArgumentExpression']):
        if isinstance(expression, ArgumentExpression):
            return {
                "name": expression.arg_name,
                "value": self._constraint_to_dict(expression.arg_value)
            }
        elif isinstance(expression, MethodInvocationExpression):
            return {
                "expression": "MethodInvocation",
                "method": expression.method_name,
                "self": self._constraint_to_dict(expression.target),
                "arguments": self._constraint_list_to_dict(expression.arg_exprs),
            }
        elif isinstance(expression, IfElseExpression):
            return {
                "expression": "IfElse",
                "condition": self._constraint_to_dict(expression.condition),
                "if_true": self._constraint_to_dict(expression.if_true),
                "if_false": self._constraint_to_dict(expression.if_false)
            }
        elif isinstance(expression, ConstantExpression):
            return {
                "expression": "ConstantExpression",
                "type": str(expression._result_type),   # TODO: Accessing private field
                "value": str(expression.value)
            }
        elif isinstance(expression, FieldAccessExpression):
            return {
                "expression": "FieldAccessExpression",
                "target": self._constraint_to_dict(expression.target),
                "field_name": expression.field_name
            }
        elif isinstance(expression, ThisExpression):
            return {
                "expression": "This"
            }
        else:
            return {
                "expression": "NotImplemented",
                "class": str(expression.__class__)
            }

    def _constraint_list_to_dict(self, expressions: List[Union['Expression', 'ArgumentExpression']]):
        output = []
        for expression in expressions:
            output.append(self._constraint_to_dict(expression))
        return output

    def format_array(self, array: Array):
        raise Exception("Not Implemented")

    def format_enum(self, enum: Enum):
        raise Exception("Not Implemented")

    def format_function(self, function: Function):
        raise Exception("Not Implemented")

    def format_context(self, context: Context):
        raise Exception("Not Implemented")

    def format_protocol(self, protocol: Protocol):

        for name in protocol.get_type_names():
            type = protocol.get_type(name)
            if isinstance(type, BitString):
                self.format_bitstring(type)
            elif isinstance(type, Struct):
                self.format_struct(type)

        pdus = []
        for name in protocol.get_pdu_names():
            pdus.append({
                "type": name
            })

        self.output = {
            "construct": "Protocol",
            "name": protocol.get_protocol_name(),
            "definitions": self.definitions,
            "pdus": pdus
        }

