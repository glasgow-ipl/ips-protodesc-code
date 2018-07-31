import parsley
import string
import sys
import json
import itertools

typedefs_lookup = {}
typedefs_order = []

def new_proto(protocol, elements):
	return {"irobject": "protocol", "name": protocol, "definitions": [typedefs_lookup[name] for name in typedefs_order], "pdus": [{"irobject": "pdu", "type": "pdus"}]}
	
def new_array(name, type, length):
	if type == "bit":
		type = "Bit"
	array = {"irobject": "array", "name": name, "elementType": type, "length": length}
	typedefs_lookup[name] = array
	typedefs_order.append(name)
	return array

def new_struct(name, fields, where):
	s = {"irobject": "struct", "name": name, "fields": []}
	for field in fields:
		s["fields"].append(field)
	if where is not None:
		s["constraints"] = where
	typedefs_lookup[name] = s
	typedefs_order.append(name)
	return s
	
def new_field_array(name, type, width):
	if type == "bit":
		type = "Bit"
	if name[0] == "0" or name[0] == "1":
		generated_name = "$" + type + str(width)
		if generated_name not in typedefs_order:
			typedefs_lookup[generated_name] = {"irobject": "array", "name": generated_name, "elementType": type, "length": width}
			typedefs_order.append(generated_name)
		return {"irobject": "field", "name": None, "value": name, "type": generated_name}
	else:
		generated_name = "$" + type + str(width)
		if generated_name not in typedefs_order:
			typedefs_lookup[generated_name] = {"irobject": "array", "name": generated_name, "elementType": type, "length": width}
			typedefs_order.append(generated_name)
		return {"irobject": "field", "name": name, "type": generated_name}

def new_field(name, type):
	if type == "bit":
		type = "Bit"
	return {"irobject": "field", "name": name, "type": type}

def new_enum(name, n1, n2):
	variants = []
	count = 0
	for variant in [n1] + n2:
		if type(variant) is dict and variant["irobject"] == "struct":
			generated_name = "$" + name + "#" + str(count)
			variant["name"] = generated_name
			typedefs_lookup[generated_name] = variant
			typedefs_order.append(generated_name)
			field_count = 0
			constraints = []
			for field in variant["fields"]:
				if "value" in field:
					field["name"] = generated_name + "#" + str(field_count)
					field_count += 1
					constraints.append((field["name"], field["value"]))
					field.pop('value', None)
			variant["constraints"] = []
			for constraint in constraints:
				var = {"irobject": "constraint_binary", "value": constraint[0], "left": None, "right": None}
				val = {"irobject": "constraint_binary", "value": constraint[1], "left": None, "right": None}
				new_constraint = {"irobject": "constraint_relational", "value": "==", "left": var, "right": val}
				variant["constraints"].append(new_constraint)
			count += 1
		else:
			generated_name = variant
		variants.append({"irobject": "variant", "type": generated_name})
	enum = {"irobject": "enum", "name": name, "variants": variants}
	typedefs_lookup[name] = enum
	typedefs_order.append(name)
	return enum

def new_anonstruct(bitstring, field):
	return {"irobject": "struct", "name": None, "fields": [new_field_array(bitstring, "bit", len(bitstring)), field]}

def new_prototype(name, field, fields, return_type):
	parameters = [field] + fields
	for parameter in parameters:
		parameter["irobject"] = "parameter"
	print(name, field, fields, return_type)
	if return_type[1] is None:
		ret = return_type[0]
	else:
		ret_width = return_type[1]
		if ret_width == -1:
			ret_width = None
			ret = new_field_array("return", return_type[0], ret_width)["type"]
	function = {"irobject": "function", "name": name, "parameters": parameters, "returnType": ret}
	typedefs_lookup[name] = function
	typedefs_order.append(name)

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
	protocol = filename.split(".")[0]
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
				protodef = (array|struct|enum|prototype)+:elements -> new_proto(protocol, elements)
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
								      "protocol": protocol})
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protodef()
	
if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1])))
