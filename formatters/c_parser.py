import sys
import json

class Formatter:
	def __init__(self):
		self.definitions = []

	def output(self):
		definitions = "\n\n".join(self.definitions)
		return definitions

	def bitstring(self, name, width):
		if width is None:
			return
		typedef = """typedef struct %s {
	unsigned int value:%d;
} %s;""" % (name, width, name)
		self.definitions.append(typedef)
		
	def array(self, name, type, length):
		#TODO
		self.definitions.append("array %s %s %d" % (name, type, length))
	
	def struct(self, name, fields):
		#TODO
		self.definitions.append("struct %s %s" % (name, str(fields)))
		
	def enum(self, name, variants):
		#TODO
		self.definitions.append("enum %s %s" % (name, str(variants)))
		
	def protocol(self, pdus):
		#TODO
		self.definitions.append( """int main(int argc, char *argv[]) {
	// TODO %s
}""" % (str(pdus)))