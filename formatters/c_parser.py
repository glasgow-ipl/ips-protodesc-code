import sys
import json

class Formatter:
	def __init__(self):
		self.definitions = []
		self.type_lengths = {}
		
	def output(self):
		libs = """#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
"""
		definitions = "\n\n".join(self.definitions)
		return libs + "\n" + definitions

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

	def struct(self, name, fields):
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
		parser_func = """%s *parse_%s(uint8_t *buffer, size_t len) {
    %s *%s = (%s *) malloc(sizeof(%s));
    %s
    return %s;
}""" % (name, name.lower(), name, name.lower(), name, name, "\n\t".join(field_memcpys), name.lower())

		self.definitions.append(struct_def + "\n\n" + parser_func)
		
	def enum(self, name, variants):
		#TODO
		self.definitions.append("enum %s %s" % (name, str(variants)))
		
	def protocol(self, pdus):
		#TODO
		self.definitions.append( """int main(int argc, char *argv[]) {
	// TODO %s
}""" % (str(pdus)))