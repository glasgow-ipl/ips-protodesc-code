import parsley
import string
import sys
import json
import itertools

typedefs_lookup = {}
typedefs_order = []

def new_proto(protocol, elements):
	if "pdus" not in typedefs_lookup or typedefs_lookup["pdus"]["irobject"] != "enum":
		raise Exception("`pdus` enum must be defined")
	else:
		typedefs_order.remove("pdus")
	return {"irobject": "protocol", "name": protocol, "definitions": [typedefs_lookup[name] for name in typedefs_order], "pdus": typedefs_lookup["pdus"]["variants"]}
	
def new_array(name, type, length):
	if type == "bit":
		type = "Bit"
	if length is None:
		new_def = {"irobject": "newtype", "name": name, "derivedFrom": type}
	else:
		new_def = {"irobject": "array", "name": name, "elementType": type, "length": length}
	typedefs_lookup[name] = new_def
	typedefs_order.append(name)
	return new_def

def new_struct(name, fields, where):
	s = {"irobject": "struct", "name": name, "fields": []}
	fields_lookup = {}
	for field in fields:
		fields_lookup[field["name"]] = field
		s["fields"].append(field)
	if where is not None:
		for expression in where.copy():
			if expression["constraint"] == "assignment":
				field_name = expression["left"]["value"]
				constraint = expression["right"]
				fields_lookup[field_name]["isPresent"] = expression["right"]
				where.remove(expression)
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
		return {"irobject": "field", "name": None, "value": name, "type": generated_name, "isPresent": {"constraint": "constant", "value": 1}}
	else:
		generated_name = "$" + type + str(width)
		if generated_name not in typedefs_order:
			typedefs_lookup[generated_name] = {"irobject": "array", "name": generated_name, "elementType": type, "length": width}
			typedefs_order.append(generated_name)
		return {"irobject": "field", "name": name, "type": generated_name, "isPresent": {"constraint": "constant", "value": 1}}

def new_field(name, type):
	if type == "bit":
		type = "Bit"
	return {"irobject": "field", "name": name, "type": type, "isPresent": {"constraint": "constant", "value": 1}}

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
				var = {"constraint": "field_name", "property": "value", "value": constraint[0]}
				val = {"constraint": "constant", "value": constraint[1]}
				new_constraint = {"constraint": "binary", "value": "==", "left": var, "right": val}
				variant["constraints"].append(new_constraint)
			count += 1
		else:
			generated_name = variant
		variants.append({"type": generated_name})
	enum = {"irobject": "enum", "name": name, "variants": variants}
	typedefs_lookup[name] = enum
	typedefs_order.append(name)
	return enum

def new_anonstruct(bitstring, field):
	return {"irobject": "struct", "name": None, "fields": [new_field_array(bitstring, "bit", len(bitstring)), field]}

def new_prototype(name, field, fields, return_type):
	parameters = [field] + fields
	for parameter in parameters:
		parameter.pop("irobject", None)
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

def build_tree(start, pairs):
	for pair in pairs:
		if len(pair) == 2:
			start = {"constraint": "binary", "value": pair[0], "left": start, "right": pair[1]}
		elif len(pair) == 3:
			start = {"constraint": "ternary", "value": pair[0], "cond": start, "true": pair[1], "else": pair[2]}
	return start

def parse_file(filename):
	protocol = filename.split(".")[0]
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				name = <letter+>:letters -> "".join(letters)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)
				
				# expression grammar
				primary_expr = number:n -> {"constraint": "constant", "value": n}
				             | name:n ('.' ('length' | 'value' | 'is_present'):p -> p)?:prop -> {"constraint": "field_name", "property": prop if prop else "value", "value": n}
							 | '(' cond_expr:expr ')' -> expr
				multiplicative_expr = primary_expr:left (('*' | '/' | '%'):operator primary_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				additive_expr = multiplicative_expr:left (('+' | '-'):operator multiplicative_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				shift_expr = additive_expr:left (('<<' | '>>'):operator additive_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				relational_expr = shift_expr:left (('<=' | '>=' | '<' | '>'):operator shift_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				equality_expr = relational_expr:left (('==' | '!='):operator relational_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				and_expr = equality_expr:left ('&':operator equality_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				xor_expr = and_expr:left ('^':operator and_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				or_expr = xor_expr:left ('|':operator xor_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				land_expr = or_expr:left ('&&':operator or_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				lor_expr = land_expr:left ('||':operator land_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights)
				cond_expr = lor_expr:left ('?' cond_expr:operand1 ':' lor_expr:operand2 -> ('?:', operand1, operand2))*:rights -> build_tree(left, rights)
				assignment_expr = (name:n '.is_present' -> {"constraint": "field_name", "property": "is_present", "value": n}):left '=' primary_expr:c -> {"constraint": "assignment", "left": left, "right": c}

				bindigit = anything:x ?(x in '01')
				type = name
				bitstring = '"'  <bindigit+>:bds '"' -> "".join(bds)
				array = name:n ':=' type:t ('[' number:w ']' -> w)?:width ';' -> new_array(n, t, width)
				field_array_s = name:n ':' type:t '[' (number)?:width ']' -> new_field_array(n,t,width)
				field_s = (name|bitstring):n ':' type:t -> new_field(n,t)
				field_array = name:n ':' type:t '[' (number)?:width '];' -> new_field_array(n,t,width)
				field = (name|bitstring):n ':' type:t ';' -> new_field(n,t)
				anonstruct = bitstring:b 'followedby' (field|field_array):f -> new_anonstruct(b, f)
				enum = name:n ':={' (anonstruct|name):n1 ('|' (anonstruct|name))*:n2 '};' -> new_enum(n, n1, n2)
				constraint = (assignment_expr|cond_expr):c ';' -> c
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
								      "build_tree": build_tree,
								      "width_check":width_check,
								      "protocol": protocol})
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protodef()
	
if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1])))