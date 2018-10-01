import sys
import json

class Formatter:
	def __init__(self):
		self.definitions = []

	def output(self):
		definitions = "\n\n".join(self.definitions)
		return definitions + """

int main(int argc, char *argv[]) {
	// TODO
}"""

	def bitstring(self, name, width):
		if width is None:
			return
		typedef = """typedef struct %s {
	unsigned int value:%d;
} %s;""" % (name, width, name)
		self.definitions.append(typedef)