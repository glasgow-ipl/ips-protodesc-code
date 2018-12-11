import parsley
import string
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from shared import *

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
								
				field_accessor = field_name:x (('.' ('value' | 'length' | 'width'):attribute -> attribute)|('[' (number|'"' field_name:n '"' -> n):key ']' -> key))*:xs -> build_accessor_chain({"expression": "This"}, [x]+xs)
					           | 'Context.' field_name:x (('.' ('value' | 'length'):attribute -> attribute)|('[' (number|'"' field_name:n '"' -> n):key ']' -> key))*:xs -> build_accessor_chain({"expression": "Context"}, [x]+xs)
				# expression grammar
				primary_expr = number:n -> build_integer_expression(n, type_namespace)
							 | ('True'|'False'):bool -> {"expression": "Constant", "type": "Boolean", "value": bool}
							 | field_name:name '(' (cond_expr:e -> e)?:arg (',' cond_expr:e -> e)*:args ')' -> new_func_call(name, [arg] + args, type_namespace)
							 | field_accessor
							 | '(' cond_expr:expr ')' -> expr
				
				multiplicative_expr = primary_expr:left (('*'|'/'|'%'):operator primary_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				additive_expr = multiplicative_expr:left (('+'|'-'):operator multiplicative_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
			
				ordinal_expr = additive_expr:left (('<='|'<'|'>='|'>'):operator additive_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				boolean_expr = ordinal_expr:left (('&&'|'||'|'!'):operator ordinal_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				equality_expr = boolean_expr:left (('=='|'!='):operator boolean_expr:operand -> (operator, operand))*:rights -> build_tree(left, rights, "")
				cond_expr = equality_expr:left ('?' cond_expr:operand1 ':' equality_expr:operand2 -> ('?:', operand1, operand2))*:rights -> build_tree(left, rights, "IfElse")
				assign_expr = field_accessor:left '=' cond_expr:expr -> {"expression": "MethodInvocation", "method": "set", "self": left, "arguments": {"value": expr}}

				field_def = field_name:name ':' type_def:type (('?' cond_expr:exp -> exp)|('->' field_name:to_name ':' type_def:to_type -> (to_name, to_type)))?:transform -> new_field(name, type, transform, type_namespace)

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
