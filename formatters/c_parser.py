import sys
import json

class Formatter:
	def __init__(self):
		self.definitions = []

	def output(self):
		return "\n\n".join(self.definitions)

	def bitstring(self, name, width):
		bitfield_typedef = """typedef struct %s {
	unsigned int value:%d;
} %s;""" % (name, width, name)
		self.definitions.append(bitfield_typedef)