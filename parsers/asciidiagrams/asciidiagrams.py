from ..parser import Parser
import parsers.rfc.rfc as rfc
import protocol
import parsley
import string

def generate_bitstring_type(proto, name, size, units):
    if units == "bytes" or units == "byte":
        size = size * 8
    if name not in proto.get_type_names():
        return proto.define_bitstring(name, size)
    else:
        return proto.get_type(name)

class AsciiDiagrams(Parser):
    def __init__(self) -> None:
        super().__init__()

    def build_parser(self):
        with open("parsers/asciidiagrams/asciidiagrams-grammar.txt") as grammarFile:
            return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"         : string.ascii_uppercase,
                                     "ascii_lowercase"         : string.ascii_lowercase,
                                     "ascii_letters"           : string.ascii_letters,
                                     "punctuation"             : string.punctuation,
                                     "generate_bitstring_type" : generate_bitstring_type,
                                     "protocol"                : self.proto
                                   })

    def process_section(self, section : rfc.Section, parser, structs):
        for i in range(len(section.content)):
            if type(section.content[i]) is rfc.T:
                try:
                    pdu_name = parser(section.content[i].content).preamble()
                    artwork = section.content[i+1]
                    where = section.content[i+2]
                    desc_list = section.content[i+3]
                    fields = []
                    for i in range(len(desc_list.content)):
                        title, desc = desc_list.content[i]
                        field_type = parser(title.content[0]).field_title()
                        field = protocol.StructField(field_type.name.lower(),
                              field_type,
                              protocol.ConstantExpression(self.proto.get_type("Boolean"), "True"))
                        fields.append(field)
                    structs.append(self.proto.define_struct(pdu_name, fields, [], []))
                except Exception as e:
                    continue
        for subsection in section.sections:
            self.process_section(subsection, parser, structs)

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
            self.process_section(section, parser, structs)

        for struct in structs:
            self.proto.define_pdu(struct.name)

        return self.proto
