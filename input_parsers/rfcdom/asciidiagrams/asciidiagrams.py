from ...inputparser import InputParser
import rfc
import protocol

class AsciiDiagrams(InputParser):
    def __init__(self) -> None:
        super().__init__()

    def build_protocol(self, input: rfc.RFC, name: str=None) -> protocol.Protocol:
        return protocol.Protocol()

