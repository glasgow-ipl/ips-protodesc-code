from ..parser import Parser
import parsers.rfc.rfc as rfc
import protocol
import parsley
import string

def valid_field_name_convertor(name):
    return name.lower().replace(" ", "_")

def valid_type_name_convertor(name):
    return name.capitalize().replace(" ", "_")

def generate_bitstring_type(proto, name, size, units):
    name = valid_type_name_convertor(name)
    if type(size) is protocol.ConstantExpression:
        bitwidth = size.constant_value
        if units == "bytes" or units == "byte":
            bitwidth *= 8
    else:
        bitwidth = None

    if name not in proto.get_type_names():
        if type(size) is protocol.ConstantExpression:
            return (bitwidth, size, proto.define_bitstring(name, size))
        else:
            return (bitwidth, size, proto.define_bitstring(name, None))
    else:
        print(bitwidth, name, size)
        return (bitwidth, size, proto.get_type(name))

class AsciiDiagramsParser(Parser):
    def __init__(self) -> None:
        super().__init__()
        self.field_accesses = []

    def new_this(self):
        return protocol.SelfExpression()

    def new_methodinvocation(self, target, method, arguments):
        if type(target) is protocol.MethodInvocationExpression and target.method_name == "to_number":
            target = target.target
        arguments = [] if arguments == None else arguments
        print(target, method, arguments)
        return protocol.MethodInvocationExpression(target, method, arguments)

    def new_fieldaccess(self, target, field_name):
        field_access = protocol.FieldAccessExpression(target, valid_field_name_convertor(field_name))
        self.field_accesses.append(field_access)
        return self.new_methodinvocation(field_access, "to_number", [])

    def new_constant(self, type_name, value):
        return protocol.ConstantExpression(self.proto.get_type(type_name), value)

    def build_tree(self, start, pairs, expression_type):
        ops = {"^" : ("pow", "arith"), "+": ("plus", "arith"), "-": ("minus", "arith"), "*": ("multiply", "arith"), "/": ("divide", "arith"), "%": ("modulo", "arith"),
               ">=": ("ge", "ord"), ">": ("gt", "ord"), "<": ("lt", "ord"), "<=": ("le", "ord"),
               "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"), "and": ("and", "bool"), "or": ("or", "bool"), "not": ("not", "bool"),
               "==": ("eq", "equality"), "!=": ("ne", "equality")}
        for pair in pairs:
            if expression_type == "IfElse":
                start = protocol.IfElseExpression(start, pair[1], pair[2])
            else:
                start = protocol.MethodInvocationExpression(start, ops[pair[0]][0], [protocol.ArgumentExpression("other", pair[1])])
        return start

    def proc_diagram_fields(self, diagram_fields):
        clean_diagram_fields = []
        bits = 0
        label = None
        for field in diagram_fields:
            if field == None:
                if bits != 0 and label is not None:
                    clean_diagram_fields.append((bits, label))
                continue
            if ':' in field[1]:
                field = ("var", field[1].replace(':', '').strip())
            if field[1] == '':
                bits = bits + field[0]
                continue
            if field[1] == '+                                                               +':
                continue
            if field[1][0] == '+' and field[1][-1] == '+':
                label = field[1][1:-1].strip()
                continue
            clean_diagram_fields.append(field)
        return clean_diagram_fields

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
                                     "new_methodinvocation"    : self.new_methodinvocation,
                                     "new_this"                : self.new_this,
                                     "proc_diagram_fields"     : self.proc_diagram_fields,
                                     "generate_bitstring_type" : generate_bitstring_type,
                                     "protocol"                : self.proto
                                   })

    def process_section(self, section : rfc.Section, parser, structs):
        for i in range(len(section.content)):
            if type(section.content[i]) is rfc.T:
                is_pdu = False
                try:
                    pdu_name = parser(section.content[i].content[-1]).preamble()
                    print(pdu_name)
                    is_pdu = True
                    artwork = section.content[i+1]
                    artwork_fields = parser(artwork.content.strip()).diagram()
                    where = section.content[i+2]
                    desc_list = section.content[i+3]
                    fields = []
                    constraints = []
                    self.field_name_map = {}
                    # Check field counts
                    print(artwork_fields)
                    if len(artwork_fields) != len(desc_list.content):
                        print("** Warning ** [%s] Field count mismatch: description list has %d fields; packet header diagram has %d fields" % (pdu_name, len(desc_list.content), len(artwork_fields)))

                    for i in range(len(desc_list.content)):
                        title, desc = desc_list.content[i]
                        field_long_name, field_short_name, value_constraint, is_present, (field_width, field_size, field_type) = parser(title.content[0]).field_title()

                        if type(field_type.size) is protocol.MethodInvocationExpression:
                            constraints.append(field_size)

                        # check name
                        if field_short_name != artwork_fields[i][1] and field_long_name != artwork_fields[i][1]:
                            if value_constraint is not None:
                                if type(value_constraint) is protocol.MethodInvocationExpression:
                                    if type(value_constraint.target) is protocol.ConstantExpression:
                                        if value_constraint.target.constant_value != int(artwork_fields[i][1]):
                                            print("** Warning ** [%s] Value constraint mismatch: description list has field with constant value %d; packet header diagram has field with constant value %d" % (pdu_name, field_long_name, value_constraint.target.constant_value, int(artwork_fields[i][1])))
                            elif field_short_name is not None:
                                print("** Warning ** [%s] Name mismatch: description list has field '%s' (short label: '%s'); packet header diagram has field '%s'" % (pdu_name, field_short_name, field_long_name, artwork_fields[i][1]))
                            else:
                                print("** Warning ** [%s] Name mismatch: description list has field '%s'; packet header diagram has field '%s'" % (pdu_name, field_long_name, artwork_fields[i][1]))

                        if field_short_name is not None:
                            self.field_name_map[valid_field_name_convertor(field_short_name)] = valid_field_name_convertor(field_type.name)


                        # check width
                        if field_width is None:
                            if artwork_fields[i][0] != "var":
                                print("** Warning ** [%s::%s] Field width mismatch: description list has field as variable width; packet header diagram has field width as %d bits" % (pdu_name, field_long_name, artwork_fields[i][0]))
                        else:
                            if artwork_fields[i][0] == "var":
                                print("** Warning ** [%s::%s] Field width mismatch: description list has field width as %d bits; packet header diagram has field as variable width" % (pdu_name, field_long_name, field_width))
                            elif field_width != artwork_fields[i][0]:
                                print("** Warning ** [%s::%s] Field width mismatch: description list has field width as %d bits; packet header diagram has field width as %d bits" % (pdu_name, field_long_name, field_width, artwork_fields[i][0]))

                        if is_present is None:
                            is_present = protocol.ConstantExpression(self.proto.get_type("Boolean"), "True")

                        if value_constraint is not None:
                            constraints.append(value_constraint)

                        field = protocol.StructField(valid_field_name_convertor(field_type.name),
                              field_type,
                              is_present)
                        fields.append(field)

                    # short field names -> long field names
                    for field_access in self.field_accesses:
                        print(field_access)
                        print(field_access.field_name)
                        field_access.field_name = self.field_name_map.get(field_access.field_name, field_access.field_name)
                        print(field_access)
                    structs.append(self.proto.define_struct(pdu_name, fields, constraints, []))
                except Exception as e:
                    print(e)
                    pass
                try:
                    protocol_name, pdus = parser(section.content[i].content[-1]).protocol_definition()
                    print("Protocol", protocol_name, pdus)
                except Exception as e:
                    #print(e)
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
