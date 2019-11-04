from ..parser import Parser
import parsers.rfc.rfc as rfc
import protocol
import parsley
import string

def valid_field_name_convertor(name):
    return name.lower()

def valid_type_name_convertor(name):
    return name.capitalize().replace(" ", "_")

def generate_bitstring_type(proto, name, size, units):
    name = valid_type_name_convertor(name)
    #if units == "bytes" or units == "byte":
    #    size = size * 8
    if name not in proto.get_type_names():
        return proto.define_bitstring(name, size)
    else:
        return proto.get_type(name)

class AsciiDiagramsParser(Parser):
    def __init__(self) -> None:
        super().__init__()

    def new_this(self):
        return protocol.SelfExpression()

    def new_methodinvocation(self, target, method, arguments):
        if type(target) is protocol.MethodInvocationExpression and target.method_name == "to_integer":
            target = target.target
        arguments = [] if arguments == None else arguments
        return protocol.MethodInvocationExpression(target, method, arguments)

    def new_fieldaccess(self, target, field_name):
        return self.new_methodinvocation(protocol.FieldAccessExpression(target, field_name), "to_integer", [])

    def new_constant(self, type_name, value):
        return protocol.ConstantExpression(self.proto.get_type(type_name), value)

    def build_tree(self, start, pairs, expression_type):
        ops = {"+": ("plus", "arith"), "-": ("minus", "arith"), "*": ("multiply", "arith"), "/": ("divide", "arith"), "%": ("modulo", "arith"),
               ">=": ("ge", "ord"), ">": ("gt", "ord"), "<": ("lt", "ord"), "<=": ("le", "ord"),
               "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"), "and": ("and", "bool"), "or": ("or", "bool"), "not": ("not", "bool"),
               "==": ("eq", "equality"), "!=": ("ne", "equality")}
        for pair in pairs:
            if expression_type == "IfElse":
                start = protocol.IfElseExpression(start, pair[1], pair[2])
            else:
                start = protocol.MethodInvocationExpression(pair[1], ops[pair[0]][0], [protocol.ArgumentExpression("other", start)])
        return start

    def build_parser(self):
        with open("parsers/asciidiagrams/asciidiagrams-grammar.txt") as grammarFile:
            return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"         : string.ascii_uppercase,
                                     "ascii_lowercase"         : string.ascii_lowercase,
                                     "ascii_letters"           : string.ascii_letters,
                                     "punctuation"             : string.punctuation,
                                     "new_constant"            : self.new_constant,
                                     "build_tree"              : self.build_tree,
                                     "new_fieldaccess"         : self.new_fieldaccess,
                                     "new_this"                : self.new_this,
                                     "generate_bitstring_type" : generate_bitstring_type,
                                     "protocol"                : self.proto
                                   })

    def process_section(self, section : rfc.Section, parser, structs):
        for i in range(len(section.content)):
            if type(section.content[i]) is rfc.T:
                is_pdu = False
                try:
                    pdu_name = parser(section.content[i].content[-1]).preamble()
                    is_pdu = True
                    artwork = section.content[i+1]
                    where = section.content[i+2]
                    desc_list = section.content[i+3]
                    fields = []
                    for i in range(len(desc_list.content)):
                        title, desc = desc_list.content[i]
                        field_type = parser(title.content[0]).field_title()
                        field = protocol.StructField(valid_field_name_convertor(field_type.name),
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
