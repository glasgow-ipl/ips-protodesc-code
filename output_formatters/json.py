import json
from .outputformatter import OutputFormatter
from protocol import *
from typing import Dict


class Json(OutputFormatter):
    output: Dict = None
    definitions: List = None

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

        self.definitions.append({
            "construct": "Struct",
            "name": struct.name,
            "fields": fields,
            "constraints": []
        })

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

        import sys

        print()

        sys.exit()

        self.output = {
            "construct": "Protocol",
            "name": protocol.get_protocol_name(),
            "definitions": self.definitions,
            "pdus": pdus
        }

