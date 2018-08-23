import argparse
import importlib
import input_parsers
import formatters
import json

def load_input_parser(name):
	return importlib.import_module("." + name, "input_parsers")

def load_output_formatter(name):
	return importlib.import_module("." + name, "formatters")

def main():
	parser = argparse.ArgumentParser(description='Parse a packet description into a specified output format')
	parser.add_argument('--input-format', type=str, required=True, help='Input format name')
	parser.add_argument('--input-file', type=str, required=True, help='Input filename')
	parser.add_argument('--output-format', type=str, required=True, help='Output format name')
	parser.add_argument('--output-file', type=str, required=True, help='Output filename')
	parser.add_argument('--json-output-file', type=str, required=False, help="Intermediate JSON representation output filename")
	args = parser.parse_args()

	try:
		input_parser = load_input_parser(args.input_format)
	except ModuleNotFoundError as e:
		print(e)
		print("Could not load input parser (%s)" % args.input_format)
	
	try:
		proto = input_parser.parse_file(args.input_file)
	except Exception as e:
		print(e)
		print("Could not parse input file (%s) with specified parser (%s)" % (args.input_file, args.input_format))

	if args.json_output_file is not None:
		try:
			with open(args.json_output_file, "w+") as jsonOutputFile:
				jsonOutputFile.write(json.dumps(proto, indent=4))
		except:
			print("Could not write intermediate JSON representation output to file (%s)" % args.json_output_file)

	try:
		output_formatter = load_output_formatter(args.output_format)
	except ModuleNotFoundError:
		print("Could not load output formatter: %s" % args.output_format)

	try:
		formatter = output_formatter.Formatter()
		for definition in proto["definitions"]:
			if "construct" in definition:
				if definition["construct"] == "BitString":
					formatter.bitstring(definition["name"], definition["width"])
		output = formatter.output()
	except Exception as e:
		print(e)
		print("Could not format output with specified formatter (%s)" % args.output_format)

	try:
		with open(args.output_file, "w+") as outputFile:
			outputFile.write(output)
	except:
		print("Could not write output to file (%s)" % args.output_file)
	
if __name__ == "__main__":
	main()
