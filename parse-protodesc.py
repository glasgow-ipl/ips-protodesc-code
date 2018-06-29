import argparse
import importlib
import input_parsers
import formatters

def load_input_parser(name):
	return importlib.import_module("." + name, "input_parsers")

def load_output_formatter(name):
	return importlib.import_module("." + name, "formatters")

def main():
	parser = argparse.ArgumentParser(description='Parse a packet description into a specified output format')
	parser.add_argument('--input-format', type=str, help='Input format name')
	parser.add_argument('--input-file', type=str, help='Input filename')
	parser.add_argument('--output-format', type=str, help='Output format name')
	parser.add_argument('--output-file', type=str, help='Output filename')
	args = parser.parse_args()

	try:
		input_parser = load_input_parser(args.input_format)
	except ModuleNotFoundError:
		print("Could not load input parser (%s)" % args.input_format)
	
	try:
		proto = input_parser.parse_file(args.input_file)
	except:
		print("Could not parse input file (%s) with specified parser (%s)" % (args.input_file, args.input_format))

	try:
		output_formatter = load_output_formatter(args.output_format)
	except ModuleNotFoundError:
		print("Could not load output formatter: %s" % args.output_format)

	try:
		output = output_formatter.protostr(proto)
	except:
		print("Could not format output with specified formatter (%s)" % args.output_format)

	try:
		with open(args.output_file, "w+") as outputFile:
			outputFile.write(output)
	except:
		print("Could not write output to file (%s)" % args.output_file)
	
if __name__ == "__main__":
	main()
