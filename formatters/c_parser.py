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
import math

class Formatter:
	def __init__(self):
		self.type_defs = []
		self.parse_funcs = []
		self.type_lengths = {}
		self.field_lengths = {}
		
	def output(self):
		libs = """#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
"""
		bitreader = """
typedef struct BitBuffer {
	/* buffers */
	uint8_t byte_buffer;
	uint8_t *buffer;

	/* lengths */
	size_t bytes_read;
	size_t bits_read;
	size_t buffer_length; /* in bytes */
} BitBuffer;

BitBuffer *new_bbuf(uint8_t *buffer, size_t length) {
	BitBuffer *bbuf;
	if ((bbuf = (BitBuffer *) malloc(sizeof(BitBuffer))) == NULL) {
		return (BitBuffer *) -1;
	}
	
	bbuf->buffer = buffer;
	bbuf->bytes_read = 0;
	bbuf->bits_read = 0;
	bbuf->buffer_length = length;

	return bbuf;
}

void destroy_bbuf(BitBuffer *bbuf) {
	return free(bbuf);
}

void bytewise_bitshift_right(uint8_t *buf, size_t buf_len, size_t shift) {
	for (int i = buf_len; i >= 0; i--) {
		buf[i] = buf[i] >> shift;
		if (i-1 >= 0) {
			buf[i] = (buf[i-1] << (8-shift)) | buf[i];
		}
	}
}

size_t read_bits(BitBuffer *bbuf, uint8_t *dest, size_t num_bits) {
	/* want bytes, no bits read */
	if (bbuf->bits_read == 0 && num_bits % 8 == 0) {
		memcpy(dest, bbuf->buffer+bbuf->bytes_read, num_bits / 8);
		bbuf->bytes_read += num_bits / 8;
	}
	/* need to read bits, but <= number of bits remaining in first byte */
	else if (num_bits <= (8-bbuf->bits_read)) {
		memcpy(&bbuf->byte_buffer, bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->byte_buffer = bbuf->byte_buffer << bbuf->bits_read;
		bbuf->byte_buffer = bbuf->byte_buffer >> (8-num_bits);
		memcpy(dest, &bbuf->byte_buffer, 1);
		bbuf->bits_read += num_bits;
		if (bbuf->bits_read > 8) {
			bbuf->bytes_read++;
			bbuf->bits_read -= 8;
		}
	}
	/* need to read bits, but <= 8, and need to read into next byte */
	else if (num_bits <= 8) {
		memcpy(&bbuf->byte_buffer, bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->byte_buffer = bbuf->byte_buffer << bbuf->bits_read;
		uint8_t next_byte = *(bbuf->buffer+bbuf->bytes_read+1);
		next_byte = next_byte >> (8-bbuf->bits_read);
		bbuf->byte_buffer = bbuf->byte_buffer | next_byte;
		bbuf->byte_buffer = bbuf->byte_buffer >> (8-num_bits);
		memcpy(dest, &bbuf->byte_buffer, 1);
		bbuf->bytes_read++;
		bbuf->bits_read = num_bits-(8-bbuf->bits_read);
	} 
	else if (bbuf->bits_read == 0 && num_bits > 8) {
		read_bits(bbuf, dest, num_bits - (num_bits % 8));
		memcpy(dest + ((num_bits - (num_bits % 8))/8), bbuf->buffer+bbuf->bytes_read, 1);
		bbuf->bits_read = num_bits % 8;
		bytewise_bitshift_right(dest, num_bits / 8, 8 - (num_bits % 8));
	}
	else if (bbuf->bits_read != 0 && num_bits % 8 != 0) {
		size_t bits_read_prev = bbuf->bits_read;
		read_bits(bbuf, dest, num_bits - (num_bits % 8));
		memcpy(dest + ((num_bits - (num_bits % 8))/8), bbuf->buffer+bbuf->bytes_read, 1);
		dest[((num_bits - (num_bits % 8))/8)] = dest[((num_bits - (num_bits % 8))/8)] << bits_read_prev;
		bytewise_bitshift_right(dest, num_bits / 8, bits_read_prev);
	}
	else if (bbuf->bits_read != 0 && num_bits % 8 == 0) {
		for (int i = 0; i < num_bits / 8; i++) {
			read_bits(bbuf, dest+i, 8);
		}
	}
	return num_bits;
}
"""

		type_defs = "\n\n".join(self.type_defs)
		parse_funcs = "\n\n".join(self.parse_funcs)
		return libs + "\n" + type_defs + "\n" + bitreader + "\n" + parse_funcs

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
		typedef = """typedef struct %s {
	uint8_t *value;
	int width = %d;
} %s;""" % (name, width, name)
		self.type_lengths[name] = width
		self.type_defs.append(typedef)
		
	def array(self, name, type, length):
		if length is None:
			length = ""
		typedef = """typedef struct %s {
	%s value[%s];
} %s;""" % (name, type, str(length), name)
		self.type_defs.append(typedef)

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
		self.type_defs.append(struct_def)
		
		# construct parser function
		field_memcpys = []
		cumulative_len = 0
		for field in fields:
			if field["type"] in self.type_lengths:
				length = self.type_lengths[field["type"]]
				cumulative_len += length
			else:
				length = "len-%d" % (cumulative_len)
			field_memcpys.append("read_bits(bbuf, %s->%s.value, %s);" % (name.lower(), field["name"], length))
			self.field_lengths[name.lower() + "->" + field["name"].lower()] = length
		
		# constraints
		constraint_checks = []
		
		for constraint in constraints:
			constraint_checks.append("if (!(%s)) {" % (self.expression(name.lower(), constraint)))
			constraint_checks.append("    free(%s);" % (name.lower()))
			constraint_checks.append("    return -1;")
			constraint_checks.append("}")

		parser_func = """int parse_%s(BitBuffer *bbuf, size_t len, %s **parsed_%s) {
	/* malloc struct */
    %s *%s = (%s *) malloc(sizeof(%s));
    
    /* parse input buffer */
    %s
    
    /* check constraints */
    %s
    
    *parsed_%s = %s;
    return 0;
}""" % (name.lower(), name, name.lower(), name, name.lower(), name, name, "\n\t".join(field_memcpys), "\n\t".join(constraint_checks), name.lower(), name.lower())

		self.parse_funcs.append(parser_func)
		
	def enum(self, name, variants):
		typedef = """typedef enum %s {%s} %s;""" % (name, ", ".join("%s_%s" % (name.upper(), variant["type"].upper()) for variant in variants), name)
		
		funcs = []
		for variant in variants:
			func = """if (parse_%s(bbuf, len, parsed_%s)) {
		return %s_%s;
	}""" % (variant["type"].lower(), name.lower(), name.upper(), variant["type"].upper())
			funcs.append(func)

		parser_func = """int parse_%s(BitBuffer *bbuf, size_t len, %s **parsed_%s) {
	%s
	return -1;
}""" % (name.lower(), name, name.lower(), "\n\telse ".join(funcs))

		self.type_defs.append(typedef)
		self.parse_funcs.append(parser_func)
		
	def protocol(self, name, pdus):
		pdu_parsers = []
		for pdu in pdus:
			pdu_parsers.append("/* try to parse as %s */" % pdu["type"])
			pdu_parsers.append("if (parse_%s(bbuf, filesize, (%s**) pdu) == 0) {" % (pdu["type"].lower(), pdu["type"]))
			pdu_parsers.append("    printf(\"Parsed: %s\\n\");" % (pdu["type"]))
			pdu_parsers.append("}")

		self.parse_funcs.append( """int main(int argc, char *argv[]) {
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
	
	/* create BitBuffer */
	BitBuffer *bbuf = new_bbuf((uint8_t *) buffer, filesize);
	
	/* parse buffer using PDU parsing functions */
	void **pdu;
	%s
	
	/* clean-up */
	free(*pdu);
	destroy_bbuf(bbuf);
	free(buffer);
}""" % ("\n\t".join(pdu_parsers)))
