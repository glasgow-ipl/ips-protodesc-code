import sys
import json

FULL_LINE = "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
HEADER = (" 0                   1                   2                   3  \n"
		  " 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1\n"
		  "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
		  "|")

def fitted_name(field, width):
	if width == -1:
		formatted_name = formatted_name = field["name"].title() + " (?)"
		width = 31
	elif width < 5:
		formatted_name = field["name"].upper()[0]
	else:
		width_str = "(%d)" % (width)
		if (len(field["name"]) + len(width_str) + 3) >= 2*width:
			formatted_name = field["name"].upper()[1]
		else:
			formatted_name = field["name"].title() + " " + width_str
	return formatted_name.center(width*2-1)
	
def print_field(f, output):
	if "width" in f:
		width = f["width"]
	else:
		width = 1
	if width == "undefined":
		n = fitted_name(f, -1)
		output.append(n + "...")
		return 32
	else:
		n = fitted_name(f, width)
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
		if width == "undefined" or width+running_tally >= 32:
			output.append("\n")
			output.append(FULL_LINE)
			output.append("|")
			running_tally = 0
		field_width = print_field(field, output)
		tally += field_width
		running_tally += field_width
	return tally

def protostr(p):
	output = []
	for struct in p["structs"]:
		output.append(HEADER)
		print_struct(struct, output)
		output.append("\n")
		output.append(FULL_LINE + "\n")
	return "".join(output)
	
if __name__ == "__main__":
	with open(sys.argv[1], "r+") as protoFile:
		proto = json.loads(protoFile.read())
	print(protostrAdd (proto))