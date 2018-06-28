import parsley
import string
import sys
sys.path.append('../')
import intermediate.base_types as bt

typedefs = {}

def new_proto(elements):
	p = bt.Protocol()
	for element in elements:
		if type(element) is bt.Structure:
			p.add_struct(element.name, element)
	return p
	
def new_typedef(name, type, width):
	if type == "bit":
		typedefs[name] = bt.Typedef(name, bt.Array(bt.Bit(), width))
		return typedefs[name]

def new_struct(name, fields):
	s = bt.Structure(name)
	for field in fields:
		s.add_field(field)
	typedefs[name] = s
	return s
	
def new_field_array(name, type, width):
	if width is None:
		width = "undefined"
	return bt.Field(name, bt.Array(bt.Bit(), width))

def new_field(name, type):
	if type == "bit":
		t = bt.Bit()
	else:
		t = typedefs[type]
	return bt.Field(name,t)

def parse_file(filename):
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				name = <letter+>:letters -> "".join(letters)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)
				type = name
				typedef = name:n ':=' type:t '[' number:width '];' -> new_typedef(n, t, width)
				field_array = name:n ':' type:t '[' (number)?:width '];' -> new_field_array(n,t,width)
				field = name:n ':' type:t ';' -> new_field(n,t)
				struct = name:n ':={' (field|field_array)+:f '};' -> new_struct(n, f)
				protodef = (typedef|struct)+:elements -> new_proto(elements)
				"""
	parser = parsley.makeGrammar(grammar, {"ascii_letters": string.ascii_letters + "_",
								      "new_typedef": new_typedef,
								      "new_field": new_field,
								      "new_field_array": new_field_array,
								      "new_struct": new_struct,
								      "new_proto": new_proto})
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protodef()