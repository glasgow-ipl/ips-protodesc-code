class Typedef:
	"""
	A class for modelling C-style typedefs
	"""
	
	def __init__(self, name, type_val):
		self.name = name
		self.type_val = type_val
		self.width = type_val.width

class Field:
	def __init__(self, name, type):
		self.name = name
		self.type = type
		
	def add_constraint(self, op, value):
		if op == "=":
			self.value = value
	
class Choice:
	"""
	A class for modelling C-style enums
	"""
	
	def __init__(self):
		self.alternative = []
		
	def add_alternative(self, alternative):
		if alternative not in self.alternative:
			self.alternative.append(alternative)
			
class Array:
	"""
	A class for modelling arrays
	"""
	
	def __init__(self, typedef, width):
		self.typedef = typedef
		self.width = width
		
class Bit:
	"""
	A class for modelling an array of bits (potentially of length 1)
	"""
	
	def __init__(self):
		self.width = 1

class Protocol:
	"""
	A class for modelling a protocol's header description
	"""
	
	def __init__(self):
		self.context = {}
		self.typedefs = {}
		self.structs = []
		self.choices = {}
	
	def add_typedef(self, name, type_val):
		self.typedefs[name] = type_val
		
	def add_struct(self, name, struct):
		self.structs.append(struct)
		
	def add_choice(self, name, choice):
		self.choices[name] = choice
			
	
class Structure:
	"""
	A class for modelling C-style structs
	"""
	
	def __init__(self, name):
		self.fields = []
		self.name = name
		self.width = 0
		
	def add_field(self, field):
		self.fields.append(field)
		if (field.type.width != "undefined"):
			if (field.type.width == "undefined"):
				self.width = "undefined"
			else:
				self.width += field.type.width
	
	def add_constraint(self, field_name, value):
		for field in self.fields:
			if field.name == field_name:
				field.add_constraint("=", value)