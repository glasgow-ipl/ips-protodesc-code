# =================================================================================================
# Copyright (C) 2018 University of Glasgow
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

import argparse
import importlib
import input_parsers
import formatters
import json

def load_input_parser(name):
	return importlib.import_module("." + name, "input_parsers")

def load_output_formatter(name):
	return importlib.import_module("." + name, "formatters")

def dfs_array(formatter, type_constructors, defined, array_name):
	array = type_constructors[array_name]
	print("dfs array %s" % array_name)
	dfs(formatter, type_constructors, defined, array["type"])
	if array_name not in defined:
		formatter.array(array_name, array["type"], array["length"])
		defined.append(array_name)
		
def dfs_struct(formatter, type_constructors, defined, struct_name):
	struct = type_constructors[struct_name]
	print("dfs struct %s" % struct_name)
	for field in struct["fields"]:
		print("proc field %s" % field["name"])
		dfs(formatter, type_constructors, defined, field["type"])
	if struct_name not in defined:
		formatter.struct(struct_name, struct["fields"], struct["constraints"])
		defined.append(struct_name)

def dfs_enum(formatter, type_constructors, defined, enum_name):
	enum = type_constructors[enum_name]
	print("dfs enum %s" % enum_name)
	for variant in enum["variants"]:
	
		dfs(formatter, type_constructors, defined, variant["type"])
	if enum_name not in defined:
		formatter.enum(enum_name, enum["variants"])
		defined.append(enum_name)
	
def dfs(formatter, type_constructors, defined, type_name):
	print("dfs %s" % type_constructors[type_name]["construct"])
	type_constructor = type_constructors[type_name]
	if type_constructor["construct"] == "BitString":
		if type_constructor["name"] not in defined:
			formatter.bitstring(type_constructor["name"], type_constructor["width"])
			defined.append(type_constructor["name"])
	if type_constructors[type_name]["construct"] == "Struct":
		dfs_struct(formatter, type_constructors, defined, type_name)
	if type_constructors[type_name]["construct"] == "Array":
		dfs_array(formatter, type_constructors, defined, type_name)
	if type_constructors[type_name]["construct"] == "Enum":
		dfs_enum(formatter, type_constructors, defined, type_name)
		
	
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
		
		# construct dictionary of type constructors
		defined = []
		type_constructors = {}
		for constructor in proto["definitions"]:
			type_constructors[constructor["name"]] = constructor
		for variant in proto["pdus"]:
			name = variant["type"]
			dfs(formatter, type_constructors, defined, name)
		formatter.protocol(proto["name"], proto["pdus"])
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
