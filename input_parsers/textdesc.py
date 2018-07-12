import parsley
import string
import sys
import json
import itertools

typedefs = {}

def new_proto(protocol, version, elements):
	protocol = {"name": protocol, "version": version, "typedefs": [], "structs": []}
	for element in elements:
		if type(element) is dict and "kind" in element and element["kind"] == "struct":
			protocol["structs"].append(element)
		if type(element) is dict and "kind" in element and element["kind"] == "typedef":
			protocol["typedefs"].append(element)
	return protocol
	
def new_typedef(name, type, width):
	if type == "bit":
		return {"kind": "typedef", "alias": name, "type": type, "width": width}

def new_struct(name, fields, where):
	s = {"kind": "struct", "name": name, "fields": []}
	for field in fields:
		s["fields"].append(field)
	return s
	
def new_field_array(name, type, width):
	if width is None:
		width = "undefined"
	return {"kind": "array", "name": name, "type": type, "width": width}

def new_field(name, type):
	return {"kind": "field", "name": name, "type": type}

def parse_file(filename):
	filename_head = filename.split(".")[0]
	protocol, version = [x[1] for x in itertools.zip_longest([0,1], filename_head.split("-"))]
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				name = <letter+>:letters -> "".join(letters)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)
				type = name
				typedef = name:n ':=' type:t '[' number:width '];' -> new_typedef(n, t, width)
				field_array = name:n ':' type:t '[' (number)?:width '];' -> new_field_array(n,t,width)
				field = name:n ':' type:t ';' -> new_field(n,t)
				constraint = name:n '=' number:v ';' -> (n, v)
				where_block = '}where{' (constraint)+:c -> c
				struct = name:n ':={' (field|field_array)+:f (where_block)?:where '};' -> new_struct(n, f, where)
				protodef = (typedef|struct)+:elements -> new_proto(protocol, version, elements)
				"""
	parser = parsley.makeGrammar(grammar, {"ascii_letters": string.ascii_letters + "_",
								      "new_typedef": new_typedef,
								      "new_field": new_field,
								      "new_field_array": new_field_array,
								      "new_struct": new_struct,
								      "new_proto": new_proto,
								      "protocol": protocol,
								      "version": version})
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protodef()
	
if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1])))