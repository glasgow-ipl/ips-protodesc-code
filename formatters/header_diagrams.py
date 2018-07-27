import sys
import json

FULL_LINE = "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
HEADER = (" 0                   1                   2                   3  \n"
		  " 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1\n"
		  "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
		  "|")

def fitted_name(field, width, struct):
	if "constraints" in struct:
		found = False
		for constraint in struct["constraints"]:
			if constraint["field"] == field["name"]:
				if(constraint["property"] == "value" and constraint["relational_op"] == '=' and constraint["ast"]["left"] is None and constraint["ast"]["right"] is None):
					display = constraint["ast"]["value"]
					found = True
		if not found:
			display = field["name"]
	elif field["irobject"] == "anonfield":
		display = field["value"]
	else:
		display = field["name"]
	if width == -1:
		formatted_name = formatted_name = display.title() + " (?)"
		width = 31
	elif width < 5:
		formatted_name = display.upper()[0]
	else:
		width_str = "(%d)" % (width)
		if (len(field["name"]) + len(width_str) + 3) >= 2*width:
			formatted_name = display.upper()[0]
		else:
			formatted_name = display.title() + " " + width_str
	return formatted_name.center(width*2-1)
	
def print_field(f, output, s):
	if "width" in f:
		width = f["width"]
	else:
		width = 1
	if width is None:
		n = fitted_name(f, -1, s)
		output.append(n + "...")
		return 32
	else:
		n = fitted_name(f, width, s)
		output.append(n + "|")
		return width
		   
def print_struct(s, output):
	tally = 0
	running_tally = 0
	for field in s["fields"]:
		if "width" in field:
			width = field["width"]
		else:
			width = 1
		if width is None or width+running_tally >= 32:
			output.append("\n")
			output.append(FULL_LINE)
			output.append("|")
			running_tally = 0
		field_width = print_field(field, output, s)
		tally += field_width
		running_tally += field_width
	return tally

def protostr(p):
	output = []
	for type in p["types"]:
		if type["irobject"] == "struct":
			output.append(HEADER)
			print_struct(type, output)
			output.append("\n")
			output.append(FULL_LINE + "\n")
	return "".join(output)
	
if __name__ == "__main__":
	with open(sys.argv[1], "r+") as protoFile:
		proto = json.loads(protoFile.read())
	print(protostrAdd (proto))
