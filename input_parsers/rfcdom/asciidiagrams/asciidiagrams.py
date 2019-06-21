from ...inputparser import InputParser
import rfc
import protocol

class AsciiDiagrams(InputParser):
    def __init__(self) -> None:
        super().__init__()

    def build_protocol(self, proto: protocol.Protocol, input: rfc.RFC, name: str=None) -> protocol.Protocol:
        if proto is None:
            proto = protocol.Protocol()
        proto.set_protocol_name(input.front.title.content)
        return proto