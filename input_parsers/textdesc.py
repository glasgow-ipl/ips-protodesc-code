import parsley
import string
import sys
import json
import itertools

typedefs = {}

def new_proto(protocol, version, elements):
	protocol = {"irobject": "protocol", "name": protocol, "version": version, "types": elements}
	protocol["types"] = elements
	return protocol
	
def new_array(name, type, length):
        return {"irobject": "array", "name": name, "elementType": type, "length": length}

def new_struct(name, fields, where):
	s = {"irobject": "struct", "name": name, "fields": []}
	for field in fields:
		s["fields"].append(field)
	if where is not None:
		s["constraints"] = where
	return s
	
def new_field_array(name, type, width):
	if name[0] == "0" or name[0] == "1":
		return {"irobject": "anonarray", "value": name, "type": type, "width": width}
	else:
		return {"irobject": "array", "name": name, "type": type, "width": width}

def new_field(name, type):
	if name[0] == "0" or name[0] == "1":
		return {"irobject": "anonfield", "value": name, "type": type}
	else:
		return {"irobject": "field", "name": name, "type": type}

def new_enum(n, n1, n2):
	return {"irobject": "enum", "name": n, "variants": [n1] + n2}

def add_node(stack, value):
	right_node = stack.pop()
	left_node = stack.pop()
	stack.append({"irobject": "constraint_ast_node", "left": left_node, "value": value, "right": right_node})

def new_anonstruct(bitstring, field):
	return {"irobject": "anonstruct", "fields": [new_field_array(bitstring, "bit", len(bitstring)), field]}

def new_prototype(name, field, fields, return_type):
	if return_type[1] == -1:
		return_width = None
	elif return_type[1] is not None:
		return_width = return_type[1]
	else:
		return {"irobject": "prototype", "name": name, "parameters": [field] + fields, "return_type": return_type[0]}
	return {"irobject": "prototype", "name": name, "parameters": [field] + fields, "return_type": return_type[0], "return_width": return_width}

def width_check(width):
	if width is None:
		return -1
	else:
		return width

def build_expr_tree(start, pairs):
	for pair in pairs:
		start = {"irobject": "constraint_binary", "value": pair[0], "left": start, "right": pair[1]}
	return start

def build_rel_tree(start, pairs):
	for pair in pairs:
		start = {"irobject": "constraint_relational", "value": pair[0], "left": start, "right": pair[1]}
	return start

def parse_file(filename):
	filename_head = filename.split(".")[0]
	protocol, version = [x[1] for x in itertools.zip_longest([0,1], filename_head.split("-"))]
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				name = <letter+>:letters -> "".join(letters)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)
				
				# Binary expressions
				cb_number = <digit+>:ds -> {"irobject": "constraint_binary", "value": int(ds), "left": None, "right": None}
				cb_name = <letter+>:letters -> {"irobject": "constraint_binary", "value": "".join(letters), "left": None, "right": None}
				parens = '(' expr:e ')' -> e
				value = cb_name | cb_number | parens
				add = '+' expr2:n -> ('+', n)
				sub = '-' expr2:n -> ('-', n)
				mul = '*' expr3:n -> ('*', n)
				div = '/' expr3:n -> ('/', n)
				pow = '^' value:n -> ('^', n)
				expr = expr2:left (add | sub)*:right -> build_expr_tree(left, right)
				expr2 = expr3:left (mul | div)*:right -> build_expr_tree(left, right)
				expr3 = value:left pow*:right -> build_expr_tree(left, right)
				
				# Relational expressions
				eq = '==' expr:n -> ('==', n)
				neq = '!=' expr:n -> ('!=', n)
				lt = '<' expr:n -> ('<', n)
				gt = '>' expr:n -> ('>', n)
				lte = '<=' expr:n -> ('<=', n)
				gte = '>=' expr:n -> ('>=', n)
				cr_expr = expr:left (eq|neq|lt|gt|lte|gte)*:right -> build_rel_tree(left, right)

				bindigit = anything:x ?(x in '01')
				type = name
				bitstring = '"'  <bindigit+>:bds '"' -> "".join(bds)
				array = name:n ':=' type:t '[' number:width '];' -> new_array(n, t, width)
				field_array_s = name:n ':' type:t '[' (number)?:width ']' -> new_field_array(n,t,width)
				field_s = (name|bitstring):n ':' type:t -> new_field(n,t)
				field_array = name:n ':' type:t '[' (number)?:width '];' -> new_field_array(n,t,width)
				field = (name|bitstring):n ':' type:t ';' -> new_field(n,t)
				anonstruct = bitstring:b 'followedby' (field|field_array):f -> new_anonstruct(b, f)
				enum = name:n ':={' (anonstruct|name):n1 ('|' (anonstruct|name))+:n2 '};' -> new_enum(n, n1, n2)
				constraint = cr_expr:c ';' -> c
				where_block = '}where{' (constraint)+:c -> c
				struct = name:n ':={' (field|field_array)+:f (where_block)?:where '};' -> new_struct(n, f, where)
				type_array = type:t (('[' (number)?:n ']')->width_check(n))?:width -> (t, width)
				prototype = name:n '::(' (field_s|field_array_s):f (',' (field_s|field_array_s))*:fs ')->' type_array:ta ';' -> new_prototype(n, f, fs, ta)
				protodef = (array|struct|enum|prototype)+:elements -> new_proto(protocol, version, elements)
				"""
	parser = parsley.makeGrammar(grammar, {"ascii_letters": string.ascii_letters + "_",
								      "new_array": new_array,
								      "new_field": new_field,
								      "new_field_array": new_field_array,
								      "new_struct": new_struct,
								      "new_proto": new_proto,
								      "new_enum": new_enum,
								      "new_anonstruct": new_anonstruct,
								      "new_prototype": new_prototype,
								      "build_expr_tree": build_expr_tree,
								      "build_rel_tree": build_rel_tree,
								      "width_check":width_check,
								      "protocol": protocol,
								      "version": version})
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protodef()
	
if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1])))
