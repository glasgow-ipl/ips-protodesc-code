import sys
sys.path.append('../')

import intermediate.base_types

FULL_LINE = "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
HEADER = (" 0                   1                   2                   3  \n"
		  " 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1\n"
		  "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
		  "|")

def fitted_name(field, width):
	if hasattr(field, "value"):
		name = str(field.value)
	else:
		name = field.name
	if width == -1:
		formatted_name = formatted_name = name.title() + " (?)"
		width = 31
	elif width < 5:
		formatted_name = name.upper()[0]
	else:
		width_str = "(%d)" % (width)
		if (len(name) + len(width_str) + 3) >= 2*width:
			formatted_name = name.upper()[1]
		else:
			formatted_name = name.title() + " " + width_str
	return formatted_name.center(width*2-1)
	
def print_field(f):
	if f.type.width == "undefined":
		n = fitted_name(f, -1)
		print(n, end='...')
		return 32
	else:
		n = fitted_name(f, f.type.width)
		print(n, end='|')
		return f.type.width
		   
def print_struct(s):
	tally = 0
	running_tally = 0
	for field in s.fields:
		if type(field.type) is intermediate.base_types.Structure or field.type.width == "undefined" or field.type.width+running_tally >= 32:
			print()
			print(FULL_LINE, end='')
			print("|", end='')
			running_tally = 0
		field_width = print_field(field)
		tally += field_width
		running_tally += field_width
	return tally

def print_proto(p):
	for struct in p.structs:
		print(HEADER, end='')
		print_struct(struct)
		print()
		print(FULL_LINE)