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

import sys
import json

class Formatter:
	def __init__(self):
		self.definitions = []
		self.type_lengths = {}
		self.field_lengths = {}
		
	def output(self):
		libs = """#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
"""
		definitions = "\n\n".join(self.definitions)
		return libs + "\n" + definitions

	def expression(self, struct_name, json_expr):
		# Equality trait
		equality_methods = {"eq": "==", "ne": "!="}
		if json_expr["expression"] == "MethodInvocation" and json_expr["method"] in equality_methods:
			left = self.expression(struct_name, json_expr["self"])
			right = self.expression(struct_name, json_expr["arguments"][0]["value"])
			return "%s %s %s" % (left, equality_methods[json_expr["method"]], right)
			
		# ArithmeticOps trait
		arithmeticops_methods = {"plus": "+", "minus": "-", "multiply": "*", "divide": "/", "modulo": "%"}
		if json_expr["expression"] == "MethodInvocation" and json_expr["method"] in arithmeticops_methods:
			left = self.expression(struct_name, json_expr["self"])
			right = self.expression(struct_name, json_expr["arguments"][0]["value"])
			return "%s %s %s" % (left, arithmeticops_methods[json_expr["method"]], right)
			
		# Constant
		if json_expr["expression"] == "Constant":
			return json_expr["value"]

		# FieldAccess
		if json_expr["expression"] == "FieldAccess":
			if json_expr["target"]["expression"] == "This":
				return "%s->%s" % (struct_name, json_expr["field_name"])
		
		# Field width
		if json_expr["expression"] == "MethodInvocation" and json_expr["method"] == "width":
			field = self.expression(struct_name, json_expr["self"])
			return self.field_lengths[field]

		print(json_expr)

	def bitstring(self, name, width):
		if width is None:
			width = 8
			name = "Bits"
		typedef = "typedef uint%d_t %s;" % (width, name)
		self.type_lengths[name] = int(width / 8)
		self.definitions.append(typedef)
		
	def array(self, name, type, length):
		#TODO
		self.definitions.append("array %s %s %d" % (name, type, length))

	def struct(self, name, fields, constraints):
		# get field definitions
		field_defs = []
		for field in fields:
			if field["type"] == "BitString$None":
				field_def = "Bits %s[];" % (field["name"])
			else:
				field_def = "%s %s;" % (field["type"], field["name"])
			field_defs.append("    " + field_def)
			
		# construct struct definition
		struct_def = """typedef struct %s {
%s
} %s;""" % (name, "\n".join(field_defs), name)

		# construct parser function
		field_memcpys = []
		cumulative_len = 0
		for field in fields:
			if field["type"] in self.type_lengths:
				length = self.type_lengths[field["type"]]
				cumulative_len += length
			else:
				length = "len-%d" % (cumulative_len)
			field_memcpys.append("memcpy(&%s->%s, buffer, %s);" % (name.lower(), field["name"], length))
			field_memcpys.append("buffer = buffer + %s;" % (length))
			self.field_lengths[name.lower() + "->" + field["name"].lower()] = length
		
		# constraints
		constraint_checks = []
		
		for constraint in constraints:
			constraint_checks.append("if (!(%s)) {" % (self.expression(name.lower(), constraint)))
			constraint_checks.append("    free(%s);" % (name.lower()))
			constraint_checks.append("    return -1;")
			constraint_checks.append("}")

		parser_func = """int parse_%s(uint8_t *buffer, size_t len, %s **parsed_%s) {
	/* malloc struct, and parse buffer into it */
    %s *%s = (%s *) malloc(sizeof(%s));
    %s
    
    /* check constraints */
    %s
    
    *parsed_%s = %s;
    return 0;
}""" % (name.lower(), name, name.lower(), name, name.lower(), name, name, "\n\t".join(field_memcpys), "\n\t".join(constraint_checks), name.lower(), name.lower())

		self.definitions.append(struct_def + "\n\n" + parser_func)
		
	def enum(self, name, variants):
		#TODO
		self.definitions.append("enum %s %s" % (name, str(variants)))
		
	def protocol(self, name, pdus):
		pdu_parsers = []
		for pdu in pdus:
			pdu_parsers.append("/* try to parse as %s */" % pdu["type"])
			pdu_parsers.append("if (parse_%s(buffer, filesize, (%s**) pdu) == 0) {" % (pdu["type"].lower(), pdu["type"]))
			pdu_parsers.append("    printf(\"Parsed: %s\\n\");" % (pdu["type"]))
			pdu_parsers.append("}")

		self.definitions.append( """int main(int argc, char *argv[]) {
	if (argc != 2) {
		printf("usage: %%s <buffer filename>\\n", argv[0]);
		return -1;
	}
	
	/* open file */
	FILE *fp = fopen(argv[1], "rb");
	
	/* get file size */
	fseek(fp, 0, SEEK_END);
	size_t filesize = ftell(fp);
	fseek(fp, 0, SEEK_SET);
	
	/* malloc buffer */
	uint8_t *buffer = malloc(filesize);
	
	/* read file into buffer */
	if (fread(&buffer, sizeof(int8_t), filesize, fp) != filesize) {
		printf("error: could not read file\\n");
		return -1;
	}
	
	fclose(fp);
	
	/* parse buffer using PDU parsing functions */
	void **pdu;
	%s
	
	/* clean-up */
	free(*pdu);
	free(buffer);
}""" % ("\n\t".join(pdu_parsers)))
