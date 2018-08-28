import parsley
import string
import sys
import json

def new_protocol(protocol_name, type_namespace):
	return {"construct": "Protocol", 
	        "name": protocol_name, 
	        "definitions": [element for element in type_namespace.values()]}

def check_typename(name, type_namespace, should_be_defined):
	if name in type_namespace and not should_be_defined:
		raise Exception("Name '%s' has already been defined" % name)
	elif name not in type_namespace and should_be_defined:
		raise Exception("Name '%s' has not been defined" % name)
	return True

def new_bitstring(name, type_name, type_namespace):
	# if name is None, we'll generate one: don't want to check
	if name is not None:
		check_typename(name, type_namespace, False)
		
	# need to determine the width
	if type(type_name) is tuple:
		if type_name[1] is not None:
			width = type_name[1]
		else:
			width = 1
	else:
		width = None
		
	# generate a name if necessary
	if name is None:
		name = "BitString$" + str(width)
		
	# construct BitString
	bitstring = {"construct": "BitString", "name": name, "width": width}
	type_namespace[name] = bitstring
	return name

def new_array(name, type_name, type_namespace):
	length = type_name[1]
	type_name = type_name[0]
		
	# if name is None, we'll generate one: don't want to check
	if name is not None:
		check_typename(name, type_namespace, False)
		
	# check if built-in type, and create if needed
	if type(type_name) is tuple or type_name == "Bits":
		type_name = new_bitstring(None, type_name, type_namespace)
	
	# check if type has been defined
	check_typename(type_name, type_namespace, True)
	
	# generate a name if necessary
	if name is None:
		name = type_name + "$" + str(length)
	
	if length == -1:
		length = None
		# construct Array
		array = {"construct": "Array", "name": name, "element_type": type_name, "length": length}
		type_namespace[name] = array
	elif length is not None:
		# construct Array
		array = {"construct": "Array", "name": name, "element_type": type_name, "length": length}
		type_namespace[name] = array
	else:
		derived_type = {"construct": "NewType", "name": name, "derived_from": type_name, "implements": []}
		type_namespace[name] = derived_type
	return name

def new_field(name, type_name, type_namespace):
	length = type_name[1]
	type_name = type_name[0]

	check_typename(name, type_namespace, False)
	if type(type_name) is tuple or type_name == "Bits":
		type_name = new_bitstring(None, type_name, type_namespace)
	if length is not None:
		if length == -1:
			length = None
		type_name = new_array(None, (type_name, length), type_namespace)
	
	# check if type has been defined
	check_typename(type_name, type_namespace, True)
	
	field = {"name": name, "type": type_name, "is_present": True}
	return field
	
def new_struct(name, fields, where_block, type_namespace, context):
	check_typename(name, type_namespace, False)
	
	field_names = []
	
	# field processing
	for field in fields:
		assert field["name"] not in field_names
		assert field["name"] not in context
		field_names.append(field["name"])
	
	if name == "Context":
		assert where_block is None
		for field in fields:
			field.pop("is_present", None)
		context = {"construct": "Context", "fields": fields}
		type_namespace[name] = context
		return name


	# constraint processing
	if where_block is not None:
		for constraint in where_block:
			assert constraint["constraint"] == "Ordinal" \
		       	or constraint["constraint"] == "Boolean" \
		       	or constraint["constraint"] == "BooleanConst" \
		       	or constraint["constraint"] == "Equality"
		       
	# construct Struct
	struct = {"construct": "Struct", "name": name, "fields": fields, "constraints": where_block}
	type_namespace[name] = struct
	return name
	
def new_enum(name, variants, type_namespace):
	check_typename(name, type_namespace, False)
	
	checked_variants = []
	
	for variant in variants:
		type_name = variant[0]
		length = variant[1]
		if type(type_name) is tuple or type_name == "Bits":
			type_name = new_bitstring(None, type_name, type_namespace)
		if length is not None:
			if length == -1:
				length = None
			type_name = new_array(None, (type_name, length), type_namespace)
		if check_typename(type_name, type_namespace, True):
			checked_variants.append(type_name)
	
	# construct Enum
	enum = {"construct": "Enum", "name": name, "variants": checked_variants}
	type_namespace[name] = enum
	return name

def new_func(name, params, ret_type, type_namespace):
	if len(params) > 1 and params[0] is None:
		raise Exception("Syntax error")
	check_typename(name, type_namespace, False)
	
	ret_type_name = ret_type[0]
	ret_length = ret_type[1]
	if type(ret_type_name) is tuple or ret_type_name == "Bits":
		ret_type_name = new_bitstring(None, ret_type_name, type_namespace)
	if ret_length is not None:
		if ret_length == -1:
			ret_length = None
		ret_type_name = new_array(None, (ret_type_name, ret_length), type_namespace)

	# construct Function
	function = {"construct": "Function", "name": name, "parameters": [param for param in params if param.pop('is_present', None)], "return_type": ret_type_name}
	type_namespace[name] = function
	return name

def build_integer_constraint(num, type_namespace):
	#TODO: widths
	width = "32"
	int_typename = "Int$" + width
	if int_typename not in type_namespace: 
		if "BitString$" + width not in type_namespace:
			new_bitstring(None, ("Bit", int(width)), type_namespace)
		type_namespace[int_typename] = {"construct": "NewType",
									    "name": int_typename,
									    "derived_from": "BitString$" + width,
									    "implements": [{"trait": "Ordinal"}, 
									                   {"trait": "ArithmeticOps"}]}
	return {"constraint": "Constant", "type": int_typename, "value": num}

def build_accessor_chain(refs):
	if refs[0] in ["value", "length", "is_present"]:
		accessor_type = "Attribute"
	elif type(refs[0]) is str:
		accessor_type = "NamedCollection"
	else:
		accessor_type = "IndexedCollection"
	return {"access": accessor_type,
			"key": refs[0],
			"next":  build_accessor_chain(refs[1:]) if len(refs) > 1 else None}

def build_tree(start, pairs, constraint_type):
	ops = {"+": ("plus", "arith") , "-": ("minus", "arith"), "*": ("multiple", "arith"), "/": ("divide", "arith"),
	       ">=": ("ge", "ord"), ">": ("gt","ord"), "<": ("lt", "ord"), "<=": ("le","ord"),
	       "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"),
	       "==": ("eq", "equality"), "!=": ("ne", "equality")}
	for pair in pairs:
		if constraint_type == "IfElse":
			start = {"constraint": constraint_type, "condition": start, "if_true": pair[1], "if_false": pair[2]}
		else:
			start = {"constraint": constraint_type, "method": ops[pair[0]][0], "left": start, "right": pair[1]}
	return start

def parse_file(filename):
	protocol_name = filename.split(".")[0]
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				uppercase_letter = anything:x ?(x in ascii_uppercase)
				lowercase_letter = anything:x ?(x in ascii_lowercase)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)

				comment = '#' (anything:x ?(x != '#'))* '#'

				type_name = <uppercase_letter>:x <letter+>:xs -> x + "".join(xs)
				field_name = <lowercase_letter>:x <(letter|'_')+>:xs -> x + "".join(xs)
				
				type_def = (('Bits':t -> t)|('Bit':t number?:n -> (t, n))|type_name:t -> t):type (('[' number?:length ']') -> length if length is not None else -1)?:length -> (type, length)
				
				field_def = field_name:name ':' type_def:type -> new_field(name, type, type_namespace)
				
				# constraint grammar
				primary_expr = number:n -> build_integer_constraint(n, type_namespace)
							 | ('True'|'False'):bool -> {"constraint": "Constant", "type": "Boolean", "value": bool}
				             | field_name:x (('.' ('value' | 'length' | 'is_present'):attribute -> attribute)|('[' (number|'"' field_name:n '"' -> n):key ']' -> key))*:xs -> {"constraint": "Field", "accessor": build_accessor_chain([x]+xs)}
							 | '(' cond_expr:expr ')' -> expr
				multiplicative_expr = primary_expr:left (('*'|'/'):operator primary_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "Arithmetic")
				additive_expr = multiplicative_expr:left (('+'|'-'):operator multiplicative_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "Arithmetic")
			
				ordinal_expr = additive_expr:left (('<='|'<'|'>='|'>'):operator additive_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "Ordinal")
				boolean_expr = ordinal_expr:left (('&&'|'||'|'!'):operator ordinal_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "Boolean")
				equality_expr = boolean_expr:left (('=='|'!='):operator boolean_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "Equality")
				cond_expr = equality_expr:left ('?' cond_expr:operand1 ':' equality_expr:operand2 -> ('?:', operand1, operand2))*:rights -> build_tree(left, rights, "IfElse")

				where_block = '}where{' (equality_expr:constraint ';' -> constraint)+:constraints -> constraints
				bitstring_def = type_name:name ':=' (('Bits':t -> t)|('Bit':t number?:n -> (t, n))):type ';' -> new_bitstring(name, type, type_namespace)
				array_def = type_name:name ':=' type_def:type ';' -> new_array(name, type, type_namespace)
				struct_def = type_name:name ':={' (field_def:f ';' -> f)+:fields where_block?:where '};' -> new_struct(name, fields, where, type_namespace, context)
				enum_def = type_name:name ':={' type_def:t ('|' type_def:n -> n)*:ts '};' -> new_enum(name, [t] + ts, type_namespace)
				func_def = field_name:name '::(' (field_def:f -> f)?:param (',' field_def:f -> f)*:params ')->' type_def:ret_type ';' -> new_func(name, [param] + params, ret_type, type_namespace)
				protocol = (bitstring_def|array_def|struct_def|enum_def|func_def|comment)+:elements -> new_protocol(protocol_name, type_namespace)
				
				"""
	parser = parsley.makeGrammar(grammar, {"protocol_name": protocol_name,
	                                       "ascii_letters": string.ascii_letters,
									       "ascii_uppercase": string.ascii_uppercase,
									       "ascii_lowercase": string.ascii_lowercase,
									       "type_namespace": {},
									       "new_bitstring": new_bitstring,
									       "new_array": new_array,
									       "new_field": new_field,
									       "new_struct": new_struct,
									       "new_enum": new_enum,
									       "new_func": new_func,
									       "new_protocol": new_protocol,
									       "build_tree": build_tree,
									       "build_integer_constraint": build_integer_constraint,
									       "build_accessor_chain": build_accessor_chain,
									       "context": {},
									      })
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protocol()

if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1]), indent=4))
