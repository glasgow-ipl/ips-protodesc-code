from ...inputparser import InputParser
import rfc
import protocol
import parsley 
import string

def process_section(section : rfc.Section, parser, structs):
    for content in section.content:
        if type(content) is rfc.T:
            try:
                preamble = parser(content.content).preamble()
                structs.append(preamble)
            except:
                continue
    for subsection in section.sections:
        process_section(subsection, parser, structs)

class AsciiDiagrams(InputParser):
    def __init__(self) -> None:
        super().__init__()

    def build_parser(self):
        with open("input_parsers/rfcdom/asciidiagrams/asciidiagrams-grammar.txt") as grammarFile:
            return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"       : string.ascii_uppercase,
                                     "ascii_lowercase"       : string.ascii_lowercase,
                                     "ascii_letters"         : string.ascii_letters,
                                     "punctuation"           : string.punctuation,
                                     "protocol"              : self.proto
                                   })

    def build_protocol(self, proto: protocol.Protocol, input: rfc.RFC, name: str=None) -> protocol.Protocol:
        # if a Protocol hasn't been passed in, then instantiate one
        if proto is None:
            self.proto = protocol.Protocol()
        else:
            self.proto = proto

        # set the Protocol's name from the RFC's title
        self.proto.set_protocol_name(input.front.title.content)
        
        # make parser
        parser = self.build_parser()
        
        # find matching preambles
        structs = []

        for section in input.middle.content:
            process_section(section, parser, structs)
        
        for struct in structs:
            self.proto.define_pdu(struct.name)

        return self.proto