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

def new_field(name, type_name, transform, type_namespace):
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
	
	# process transform
	if transform is not None:
		to_typename = transform[1][0]
		to_length = transform[1][1]

		if type(to_typename) is tuple or to_typename == "Bits":
			to_typename = new_bitstring(None, to_typename, type_namespace)
		if to_length is not None:
			if to_length == -1:
				to_length = None
			to_typename = new_array(None, (to_typename, to_length), type_namespace)
		
		check_typename(to_typename, type_namespace, True)
		transform = {"into_name": transform[0], "into_type": to_typename, "using": None}
	
	field = {"name": name, "type": type_name, "transform": transform}
	return field
	
def new_struct(name, fields, where_block, type_namespace, context, actions):
	check_typename(name, type_namespace, False)
	
	field_dict = {}
	transform_dict = {}
	# field processing
	for field in fields:
		assert field["name"] not in field_dict
		assert field["name"] not in context
		field_dict[field["name"]] = field
		if field["transform"] is not None:
			transform_dict[field["transform"]["into_name"]] = field["transform"]

	if name == "Context":
		assert where_block is None
		for field in fields:
			field.pop("is_present", None)
		context = {"construct": "Context", "fields": fields}
		type_namespace[name] = context
		return name

	# action processing
	if actions is None:
		actions = []
	
	for i in range(len(actions)):
		action = actions[i]
		# is the action transforming a field?
		if action["expression"] == "MethodInvocation" and action["method"] == "set" and action["self"]["expression"] == "FieldAccess":
			transform_dict[action["self"]["field_name"]]["using"] = action["arguments"]["value"]
			actions.pop(i)

	# construct Struct
	struct = {"construct": "Struct", "name": name, "fields": fields, "constraints": where_block, "actions": actions}
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

def new_func_call(name, args, type_namespace):
	if args[0] is None:
		args = []
	check_typename(name, type_namespace, True)
	def_args = type_namespace[name]["parameters"]
	def_args_names = [x["name"] for x in def_args]
	def_args_types = [x["type"] for x in def_args]
	named_args = [{"name": x[0], "value": x[1]} for x in zip(def_args_names, args)]
	return {"expression": "FunctionInvocation", "name": name, "arguments": named_args}

def build_integer_expression(num, type_namespace):
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
	return {"expression": "Constant", "type": int_typename, "value": num}

def build_accessor_chain(type, refs):
	if refs[-1] == "length" or refs[-1] == "size":
		return {"expression": "MethodInvocation",
			"method": refs[-1],
			"self":  build_accessor_chain(type, refs[:-1]) if len(refs) > 1 else type,
			"arguments": None}
	else:
		return {"expression": "FieldAccess",
			    "target": build_accessor_chain(type, refs[:-1]) if len(refs) > 1 else type,
			    "field_name": refs[-1]}

def build_tree(start, pairs, expression_type):
	ops = {"+": ("plus", "arith") , "-": ("minus", "arith"), "*": ("multiple", "arith"), "/": ("divide", "arith"),
	       ">=": ("ge", "ord"), ">": ("gt","ord"), "<": ("lt", "ord"), "<=": ("le","ord"),
	       "&&": ("and", "bool"), "||": ("or", "bool"), "!": ("not", "bool"),
	       "==": ("eq", "equality"), "!=": ("ne", "equality")}
	for pair in pairs:
		if expression_type == "IfElse":
			start = {"expression": expression_type, "condition": start, "if_true": pair[1], "if_false": pair[2]}
		else:
			start = {"expression": "MethodInvocation", "method": ops[pair[0]][0], "self": pair[1], "arguments": {"name": "other", "value": start}}
	return start

def parse_file(filename):
	protocol_name = filename.split(".")[0]
	grammar = r"""
				letter = anything:x ?(x in ascii_letters)
				letterdigit = anything:x ?(x in ascii_letters or x in '0123456789')
				uppercase_letter = anything:x ?(x in ascii_uppercase)
				lowercase_letter = anything:x ?(x in ascii_lowercase)
				digit = anything:x ?(x in '0123456789')
				number = <digit+>:ds -> int(ds)

				comment = '#' (anything:x ?(x != '#'))* '#'

				type_name = <uppercase_letter>:x <letterdigit+>:xs -> x + "".join(xs)
				field_name = <lowercase_letter>:x <(letter|'_')+>:xs -> x + "".join(xs)
				
				type_def = (('Bits':t -> t)|('Bit':t number?:n -> (t, n))|type_name:t -> t):type (('[' number?:length ']') -> length if length is not None else -1)?:length -> (type, length)
				
				field_def = field_name:name ':' type_def:type ('->' field_name:to_name ':' type_def:to_type -> (to_name, to_type))?:transform -> new_field(name, type, transform, type_namespace)
				
				field_accessor = field_name:x (('.' ('value' | 'length' | 'is_present'):attribute -> attribute)|('[' (number|'"' field_name:n '"' -> n):key ']' -> key))*:xs -> build_accessor_chain({"expression": "This"}, [x]+xs)
					           | 'Context.' field_name:x (('.' ('value' | 'length' | 'is_present'):attribute -> attribute)|('[' (number|'"' field_name:n '"' -> n):key ']' -> key))*:xs -> build_accessor_chain({"expression": "Context"}, [x]+xs)
				# expression grammar
				primary_expr = number:n -> build_integer_expression(n, type_namespace)
							 | ('True'|'False'):bool -> {"expression": "Constant", "type": "Boolean", "value": bool}
							 | field_name:name '(' (cond_expr:e -> e)?:arg (',' cond_expr:e -> e)*:args ')' -> new_func_call(name, [arg] + args, type_namespace)
							 | field_accessor
							 | '(' cond_expr:expr ')' -> expr
				
				multiplicative_expr = primary_expr:left (('*'|'/'):operator primary_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				additive_expr = multiplicative_expr:left (('+'|'-'):operator multiplicative_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
			
				ordinal_expr = additive_expr:left (('<='|'<'|'>='|'>'):operator additive_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				boolean_expr = ordinal_expr:left (('&&'|'||'|'!'):operator ordinal_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				equality_expr = boolean_expr:left (('=='|'!='):operator boolean_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				cond_expr = equality_expr:left ('?' cond_expr:operand1 ':' equality_expr:operand2 -> ('?:', operand1, operand2))*:rights -> build_tree(left, rights, "IfElse")
				assign_expr = field_accessor:left '=' cond_expr:expr -> {"expression": "MethodInvocation", "method": "set", "self": left, "arguments": {"value": expr}}

				onparse_block = '}onparse{' (assign_expr:expression ';' -> expression)+:constraints -> constraints
				where_block = '}where{' (cond_expr:expression ';' -> expression)+:constraints -> constraints
				bitstring_def = type_name:name ':=' (('Bits':t -> t)|('Bit':t number?:n -> (t, n))):type ';' -> new_bitstring(name, type, type_namespace)
				array_def = type_name:name ':=' type_def:type ';' -> new_array(name, type, type_namespace)
				struct_def = type_name:name ':={' (field_def:f ';' -> f)+:fields where_block?:where onparse_block?:actions '};' -> new_struct(name, fields, where, type_namespace, context, actions)
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
									       "new_func_call": new_func_call,
									       "new_protocol": new_protocol,
									       "build_tree": build_tree,
									       "build_integer_expression": build_integer_expression,
									       "build_accessor_chain": build_accessor_chain,
									       "context": {},
									      })
	with open(filename, "r+") as defFile:
		defStr = defFile.read().replace(" ", "").replace("\n", "").replace("\t", "")
	return parser(defStr).protocol()

if __name__ == "__main__":
	print(json.dumps(parse_file(sys.argv[1]), indent=4))
