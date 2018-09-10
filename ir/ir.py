# =============================================================================
# Copyright (C) 2018 University of Glasgow
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
# =============================================================================

import json
import re

# Type names begin with an upper case letter, function names do not:
TYPE_NAME_REGEX = "^[A-Z][A-Za-z0-9$]+$"
FUNC_NAME_REGEX = "^[a-z][A-Za-z0-9$]+$"

class IRError(Exception):
    def __init__(self, reason):
        self.reason = reason

class IR:
    def _define_type(self, kind, name, attributes, components):
        """
        Define a new type.

        Arguments:
          kind       -- The kind of type being defined
          name       -- The name of the type being defined
          attributes -- The public attributes of the new type
          components -- The hidden components of the new type

        Returns:
          Nothing

        The "kind" specifies what sort of type is being constructed. Examples
        of kinds include "BitString", "Array", Struct", "Enum", and "Function".

        The "attributes" are visible in the intermediate representation, and
        include things such as the size of a bit string, or the length of an
        array. The "components" are not directly visible in the intermediate
        representation, and are used in the implementation of the type.
        """

        if re.search(TYPE_NAME_REGEX, name) == None:
            raise IRError("Invalid type name: " + name)
        if name in self.types:
            raise IRError("Redefinition of type " + name)
        if name in self.traits:
            raise IRError("Type redefines trait " + name)
        self.types[name] = {
                "kind" : kind,
                "name" : name,
                "attributes" : attributes,
                "components" : components,
                "implements" : [],
                "methods"    : {}
            }



    def _define_trait(self, t_name, methods):
        """
        Define a new trait.

        Arguments:
          t_name  -- The name of the trait being defined
          methods -- A list of methods implemented by the trait

        Returns:
          Nothing

        The "methods" argument is a list of tuples, one for each method, where
        the elements of each tuple are "(method name, parameters, return type)".
        The "parameters" element is itself a list of tuples, representing the
        parameters of the method, of the form "(parameter name, parameter type)".

        For example, calling:
          _define_trait(self, "foo", [("set", [("self", None), ("value", Boolean)], "Nothing")])
        defines a new trait named "foo" with a single method named "set". That
        method takes two parameters: "self" with unspecified type, and "value"
        with type Boolean, and returns Nothing.
        """

        # Check validity of trait:
        if re.search(TYPE_NAME_REGEX, t_name) == None:
            raise IRError("Cannot define trait {}: invalid name".format(t_name))
        if t_name in self.traits:
            raise IRError("Cannot define trait {}: already defined".format(t_name))
        if t_name in self.types:
            raise IRError("Cannot define trait {}: already defined as type".format(t_name))

        # Create the trait:
        self.traits[t_name] = {
            "name"    : t_name,
            "methods" : {}
        }

        for (m_name, m_params, m_returns) in methods:
            # Check validity of the method name:
            if re.search(FUNC_NAME_REGEX, m_name) == None:
                raise IRError("Method {} of trait {} has invalid name".format(m_name, t_name))

            # Check validity of the method parameters:
            if m_params[0] != ("self", None):
                raise IRError("Method {} of trait {} is missing self parameter".format(m_name, t_name))
            for (p_name, p_type) in m_params:
                if re.search(FUNC_NAME_REGEX, p_name) == None:
                    raise IRError("Method {} of trait {} has invalid parameter name {}".format(m_name, t_name, p_name))
                if p_type != None and not p_type in self.types:
                    raise IRError("Method {} of trait {} references undefined type {}".format(m_name, t_name, p_type))

            # Check validity of the method return type:
            if m_returns != None and not m_returns in self.types:
                raise IRError("Method {} of trait {} return unknown type {}".format(m_name, t_name, m_returns))

            # Record the method:
            self.traits[t_name]["methods"][m_name] = {}
            self.traits[t_name]["methods"][m_name]["name"]        = m_name
            self.traits[t_name]["methods"][m_name]["params"]      = m_params
            self.traits[t_name]["methods"][m_name]["return_type"] = m_returns



    def _implements(self, type_name, implements):
        """
        Record the traits implemented by a type, and add the definitions
        of the methods provided by that trait to the type.

        Arguments:
          type_name  -- The type being extended
          implements -- The traits to be implemented

        Returns:
          Nothing
        """

        if not type_name in self.types:
            raise IRError("Undefined type " + type_name)

        type_ = self.types[type_name]

        for trait in implements:
            if not trait in self.traits:
                raise IRError("Type {} cannot implement undefined trait {}".format(type_name, trait))
            if trait in type_["implements"]:
                raise IRError("Type {} already implements trait {}".format(type_name, trait))

            type_["implements"].append(trait)
            type_["implements"].sort()

            for method_name in self.traits[trait]["methods"]:
                if method_name in type_["methods"]:
                    raise IRError("Type {} already implements method {}".format(type_name, method_name))

                type_["methods"][method_name] = {}
                type_["methods"][method_name]["name"]   = method_name
                type_["methods"][method_name]["params"] = []

                for (p_name, p_type) in self.traits[trait]["methods"][method_name]["params"]:
                    if p_type == None:
                        p_type = type_name
                    type_["methods"][method_name]["params"].append((p_name, p_type))

                rt = self.traits[trait]["methods"][method_name]["return_type"]
                if rt == None:
                    type_["methods"][method_name]["return_type"] = type_name
                else:
                    type_["methods"][method_name]["return_type"] = rt



    def __init__(self):
        # Create the context, type, trait, and PDU stores:
        self.context = {}
        self.types   = {}
        self.traits  = {}
        self.pdus    = []

        self.protocol_name = ""

        # Define the internal types and standard traits:
        self._define_type("Nothing", "Nothing", {}, {})
        self._define_type("Boolean", "Boolean", {}, {})
        self._define_type("Size",    "Size",    {}, {})

        self._define_trait("Value",
                         [("get",      [("self", None)                                    ],  None),
                          ("set",      [("self", None), ("value",   None)                 ], "Nothing")])
        self._define_trait("IndexCollection",
                         [("get",      [("self", None), ("index", "Size")                 ],  None),
                          ("set",      [("self", None), ("index", "Size"), ("value", None)], "Nothing")])
        self._define_trait("NamedCollection",
                         [("get",      [("self", None), ("key",   "Size")                 ],  None),
                          ("set",      [("self", None), ("key",   "Size"), ("value", None)], "Nothing")])
        self._define_trait("Equality",
                         [("eq",       [("self", None), ("other",  None)                  ], "Boolean"),
                          ("ne",       [("self", None), ("other",  None)                  ], "Boolean")])
        self._define_trait("Ordinal",
                         [("lt",       [("self", None), ("other",  None)                  ], "Boolean"),
                          ("le",       [("self", None), ("other",  None)                  ], "Boolean"),
                          ("gt",       [("self", None), ("other",  None)                  ], "Boolean"),
                          ("ge",       [("self", None), ("other",  None)                  ], "Boolean")])
        self._define_trait("BooleanOps",
                         [("and",      [("self", None), ("other",  None)                  ], "Boolean"),
                          ("or",       [("self", None), ("other",  None)                  ], "Boolean"),
                          ("not",      [("self", None)                                    ], "Boolean")])
        self._define_trait("ArithmeticOps",
                         [("plus",     [("self", None), ("other",  None)                  ],  None),
                          ("minus",    [("self", None), ("other",  None)                  ],  None),
                          ("multiply", [("self", None), ("other",  None)                  ],  None),
                          ("divide",   [("self", None), ("other",  None)                  ],  None)])

        self._implements("Boolean", ["Value", "Equality", "BooleanOps"])
        self._implements(   "Size", ["Value", "Equality", "Ordinal", "ArithmeticOps"])



    def _construct_bitstring(self, defn):
        """
        The type constructor for a Bit String type.
        """
        attributes = {}
        components = {}
        attributes["size"] = defn["size"]
        self._define_type("BitString", defn["name"], attributes, components)
        self._implements(defn["name"], ["Value", "Equality"])



    def _construct_array(self, defn):
        """
        The type constructor for an array type.
        """
        if not defn["element_type"] in self.types:
            raise IRError("Unknown element type")

        components = {}

        attributes = {}
        attributes["element_type"] = defn["element_type"]
        attributes["length"] = defn["length"]
        if attributes["length"] != None:
            attributes["size"] = self.types[attributes["element_type"]]["attributes"]["size"] * attributes["length"]
        else:
            attributes["size"] = None

        self._define_type("Array", defn["name"], attributes, components)
        self._implements(defn["name"], ["Equality", "IndexCollection"])



    def _check_expression(self, expression, this):
        """
        Check that an expression is valid.

        Arguments:
          expression -- The expression to check
          this       -- This type in which the expression is evaluated

        Returns:
          The type of the expression
        """
        if   expression["expression"] == "MethodInvocation":
            # Check the target:
            target_type = self._check_expression(expression["target"], this)
            if not target_type in self.types:
                raise IRError("Expression has unknown target type {}".format(target_type))
            # Check the method is valid:
            if not expression["method"] in self.types[target_type]["methods"]:
                raise IRError("Expression calls unknown method {} on type {}".format(expression["method"], target_type))
            # Check the arguments to the method:
            for arg in expression["arguments"]:
                self._check_expression(arg["value"], this)
            # FIXME: need to check argument names and types match
            # FIXME: what should this return?
        elif expression["expression"] == "FunctionInvocation":
            # FIXME: check the FunctionInvocation expression
            # FIXME: what should this return?
            pass
        elif expression["expression"] == "IfElse":
            # FIXME: check the IfElse expression
            # FIXME: what should this return?
            pass
        elif expression["expression"] == "This":
            if not this in self.types:
                raise IRError("Expression has unknown This type: {}".format(this))
            return this
        elif expression["expression"] == "Context":
            # FIXME: check the Context expression
            # FIXME: what should this return?
            pass
        elif expression["expression"] == "Constant":
            if not expression["type"] in self.types:
                raise IRError("Expression has unknown Constant type: {}".format(expression["type"]))
            return expression["type"]
        else:
            raise IRError("Unknown expression: {}".format(expression["expression"]))



    def _construct_struct(self, defn):
        """
        The type constructor for a structure type.
        """
        attributes = {}
        attributes["size"] = 0

        components = {}
        components["fields"] = []
        field_names = {}
        for field in defn["fields"]:
            # Check that the field name is valid and its type exists, then record the field:
            if re.search(FUNC_NAME_REGEX, field["name"]) == None:
                raise IRError("Invalid field name: " + field["name"])
            if field["name"] in field_names:
                raise IRError("Duplicate field name: " + field["name"])
            field_names[field["name"]] = True
            if not field["type"] in self.types:
                raise IRError("Unknown field type: " + field["type"])
            components["fields"].append((field["name"], field["type"], field["is_present"]))
            attributes["size"] += self.types[field["type"]]["attributes"]["size"]

        self._define_type("Struct", defn["name"], attributes, components)
        self._implements(defn["name"], ["NamedCollection"])

        components["constraints"] = []
        for constraint in defn["constraints"]:
            self._check_expression(constraint, defn["name"])
            components["constraints"].append(constraint)



    def _construct_enum(self, defn):
        """
        The type constructor for an enumerated type.
        """
        attributes = {}
        # The size of an enum is not known until it is parsed, since it
        # depends on the instantiated variant
        attributes["size"] = None

        components = {}
        components["variants"] = []
        for v in defn["variants"]:
            if not v["type"] in self.types:
                raise IRError("Unknown variant: " + v["type"])
            components["variants"].append(v["type"])
            components["variants"].sort()

        self._define_type("Enum", defn["name"], attributes, components)



    def _construct_newtype(self, defn):
        """
        The type constructor for a derived type.
        """
        base_type = defn["derived_from"]
        if not base_type in self.types:
            raise IRError("Derived from unknown type: " + base_type)

        base_kind = self.types[base_type]["kind"]
        base_attr = self.types[base_type]["attributes"]
        base_comp = self.types[base_type]["components"]
        base_impl = self.types[base_type]["implements"]

        self._define_type(base_kind, defn["name"], base_attr, base_comp)
        self._implements(defn["name"], base_impl + defn["implements"])



    def _construct_function(self, defn):
        """
        The type constructor for a function type.
        """
        components = {}

        attributes = {}
        attributes["parameters"] = []
        param_names = {}
        for param in defn["parameters"]:
            # Check that the parameter name is valid and its type exists, then record the field:
            if re.search(FUNC_NAME_REGEX, param["name"]) == None:
                raise IRError("Invalid parameter name: " + param["name"])
            if param["name"] in param_names:
                raise IRError("Duplicate parameter name: " + param["name"])
            param_names[param["name"]] = True
            if not param["type"] in self.types:
                raise IRError("Unknown parameter type: " + param["type"])
            attributes["parameters"].append((param["name"], param["type"]))

        if re.search(TYPE_NAME_REGEX, defn["return_type"]) == None:
            raise IRError("Unknown return type: " + defn["return_type"])
        attributes["return_type"] = defn["return_type"]

        self._define_type("Function", defn["name"], attributes, components)
        



    def _construct_context(self, defn):
        """
        The constructor for the protocol context.
        """
        field_names = {}

        for field in defn["fields"]:
            # Check that the field name is valid and its type exists, then record the field:
            if re.search(FUNC_NAME_REGEX, field["name"]) == None:
                raise IRError("Invalid field name in context: " + field["name"])
            if field["name"] in field_names:
                raise IRError("Duplicate field name in context: " + field["name"])
            field_names[field["name"]] = True
            if not field["type"] in self.types:
                raise IRError("Unknown field type in context: " + field["type"])

            self.context[field["name"]] = {}
            self.context[field["name"]]["name"]  = field["name"]
            self.context[field["name"]]["type"]  = field["type"]
            self.context[field["name"]]["value"] = None



    def load(self, protocol_json):
        """
        Load the JSON-formatted representation of a protocol object.

        Arguments:
          protocol_json -- A string containing the JSON form of a protocol object

        Returns:
          Nothing (but updates self to contain the loaded and type-checked IR)
        """
        protocol = json.loads(protocol_json)
        if protocol["construct"] != "Protocol":
            raise IRError("Not a protocol object")

        if re.search(TYPE_NAME_REGEX, protocol["name"]) == None:
            raise IRError("Invalid protocol name: {}".format(name))
        self.protocol_name = protocol["name"]

        for defn in protocol["definitions"]:
            if   defn["construct"] == "BitString":
                self._construct_bitstring(defn)
            elif defn["construct"] == "Array":
                self._construct_array(defn)
            elif defn["construct"] == "Struct":
                self._construct_struct(defn)
            elif defn["construct"] == "Enum":
                self._construct_enum(defn)
            elif defn["construct"] == "NewType":
                self._construct_newtype(defn)
            elif defn["construct"] == "Function":
                self._construct_function(defn)
            elif defn["construct"] == "Context":
                self._construct_context(defn)
            else:
                raise IRError("Unknown type constructor in definition: {}".format(defn["construct"]))

        for pdu in protocol["pdus"]:
            if not pdu["type"] in self.types:
                raise IRError("Unknown PDU type: {}".format(pdu["type"]))
            self.pdus.append(pdu["type"])
            self.pdus.sort()

# =============================================================================
# Unit tests:

import unittest

class TestIR(unittest.TestCase):
    def test_builtin_types(self):
        ir = IR()
        # Check the number of built-in types:
        self.assertEqual(len(ir.types), 3)
        # Check the built-in Nothing type:
        self.assertEqual(ir.types["Nothing"]["kind"],       "Nothing")
        self.assertEqual(ir.types["Nothing"]["name"],       "Nothing")
        self.assertEqual(ir.types["Nothing"]["attributes"], {})
        self.assertEqual(ir.types["Nothing"]["implements"], [])
        # Check the built-in Boolean type:
        self.assertEqual(ir.types["Boolean"]["kind"],       "Boolean")
        self.assertEqual(ir.types["Boolean"]["name"],       "Boolean")
        self.assertEqual(ir.types["Boolean"]["attributes"], {})
        self.assertEqual(ir.types["Boolean"]["implements"], ["BooleanOps", "Equality", "Value"])
        # Check the built-in Size type:
        self.assertEqual(ir.types["Size"]["kind"],       "Size")
        self.assertEqual(ir.types["Size"]["name"],       "Size")
        self.assertEqual(ir.types["Size"]["attributes"], {})
        self.assertEqual(ir.types["Size"]["implements"], ["ArithmeticOps", "Equality", "Ordinal", "Value"])
        # Check the number of built-in traits:
        self.assertEqual(len(ir.traits), 7)
        # Check the built-in Arithmetic trait:
        self.assertEqual(ir.traits["ArithmeticOps"]["name"], "ArithmeticOps")
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["plus"    ]["name"],   "plus")
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["plus"    ]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["plus"    ]["return_type"], None)
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["minus"   ]["name"],   "minus")
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["minus"   ]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["minus"   ]["return_type"], None)
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["multiply"]["name"],   "multiply")
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["multiply"]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["multiply"]["return_type"], None)
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["divide"  ]["name"],   "divide")
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["divide"  ]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["ArithmeticOps"]["methods"]["divide"  ]["return_type"], None)
        self.assertEqual(len(ir.traits["ArithmeticOps"]["methods"]), 4)
        # Check the built-in Boolean trait:
        self.assertEqual(ir.traits["BooleanOps"]["name"], "BooleanOps")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["and"]["name"],        "and")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["and"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["and"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["or" ]["name"],        "or")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["or" ]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["or" ]["return_type"], "Boolean")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["not"]["name"],        "not")
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["not"]["params"],      [("self", None)])
        self.assertEqual(ir.traits["BooleanOps"]["methods"]["not"]["return_type"], "Boolean")
        self.assertEqual(len(ir.traits["BooleanOps"]["methods"]), 3)
        # Check the built-in Equality trait:
        self.assertEqual(ir.traits["Equality"]["name"], "Equality")
        self.assertEqual(ir.traits["Equality"]["methods"]["eq"]["name"],        "eq")
        self.assertEqual(ir.traits["Equality"]["methods"]["eq"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Equality"]["methods"]["eq"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Equality"]["methods"]["ne"]["name"],        "ne")
        self.assertEqual(ir.traits["Equality"]["methods"]["ne"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Equality"]["methods"]["ne"]["return_type"], "Boolean")
        self.assertEqual(len(ir.traits["Equality"]["methods"]), 2)
        # Check the built-in Ordinal trait:
        self.assertEqual(ir.traits["Ordinal"]["name"], "Ordinal")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["lt"]["name"],        "lt")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["lt"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Ordinal"]["methods"]["lt"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["le"]["name"],        "le")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["le"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Ordinal"]["methods"]["le"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["gt"]["name"],        "gt")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["gt"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Ordinal"]["methods"]["gt"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["ge"]["name"],        "ge")
        self.assertEqual(ir.traits["Ordinal"]["methods"]["ge"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Ordinal"]["methods"]["ge"]["return_type"], "Boolean")
        self.assertEqual(len(ir.traits["Ordinal"]["methods"]), 4)
        # Check the built-in Value trait:
        self.assertEqual(ir.traits["Value"]["name"], "Value")
        self.assertEqual(ir.traits["Value"]["methods"]["get"]["name"],        "get")
        self.assertEqual(ir.traits["Value"]["methods"]["get"]["params"],      [("self", None)])
        self.assertEqual(ir.traits["Value"]["methods"]["get"]["return_type"], None)
        self.assertEqual(ir.traits["Value"]["methods"]["set"]["name"],        "set")
        self.assertEqual(ir.traits["Value"]["methods"]["set"]["params"],      [("self", None), ("value", None)])
        self.assertEqual(ir.traits["Value"]["methods"]["set"]["return_type"], "Nothing")
        self.assertEqual(len(ir.traits["Value"]["methods"]), 2)
        # Check the built-in IndexCollection trait:
        self.assertEqual(ir.traits["IndexCollection"]["name"], "IndexCollection")
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["get"]["name"],        "get")
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["get"]["params"], [("self", None), ("index", "Size")])
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["get"]["return_type"], None)
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["set"]["name"],        "set")
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["set"]["params"], [("self", None), ("index", "Size"), ("value", None)])
        self.assertEqual(ir.traits["IndexCollection"]["methods"]["set"]["return_type"], "Nothing")
        self.assertEqual(len(ir.traits["IndexCollection"]["methods"]), 2)
        # Check the built-in NamedCollection trait:
        self.assertEqual(ir.traits["NamedCollection"]["name"], "NamedCollection")
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["get"]["name"],        "get")
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["get"]["params"], [("self", None), ("key", "Size")])
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["get"]["return_type"], None)
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["set"]["name"],        "set")
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["set"]["params"], [("self", None), ("key", "Size"), ("value", None)])
        self.assertEqual(ir.traits["NamedCollection"]["methods"]["set"]["return_type"], "Nothing")
        self.assertEqual(len(ir.traits["NamedCollection"]["methods"]), 2)



    def test_implements_methods(self):
        ir = IR()
        # Check the built-in Size type:
        self.assertEqual(ir.types["Size"]["kind"],       "Size")
        self.assertEqual(ir.types["Size"]["name"],       "Size")
        self.assertEqual(ir.types["Size"]["attributes"], {})
        self.assertEqual(ir.types["Size"]["implements"], ["ArithmeticOps", "Equality", "Ordinal", "Value"])
        # Should implement the methods of ArithmeticOps:
        self.assertEqual(ir.types["Size"]["methods"]["plus"    ]["name"],   "plus")
        self.assertEqual(ir.types["Size"]["methods"]["plus"    ]["params"], [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["plus"    ]["return_type"], "Size")
        self.assertEqual(ir.types["Size"]["methods"]["minus"   ]["name"],   "minus")
        self.assertEqual(ir.types["Size"]["methods"]["minus"   ]["params"], [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["minus"   ]["return_type"], "Size")
        self.assertEqual(ir.types["Size"]["methods"]["multiply"]["name"],   "multiply")
        self.assertEqual(ir.types["Size"]["methods"]["multiply"]["params"], [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["multiply"]["return_type"], "Size")
        self.assertEqual(ir.types["Size"]["methods"]["divide"  ]["name"],   "divide")
        self.assertEqual(ir.types["Size"]["methods"]["divide"  ]["params"], [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["divide"  ]["return_type"], "Size")
        # Should implement the methods of Equality:
        self.assertEqual(ir.types["Size"]["methods"]["eq"]["name"],        "eq")
        self.assertEqual(ir.types["Size"]["methods"]["eq"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["eq"]["return_type"], "Boolean")
        self.assertEqual(ir.types["Size"]["methods"]["ne"]["name"],        "ne")
        self.assertEqual(ir.types["Size"]["methods"]["ne"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["ne"]["return_type"], "Boolean")
        # Should implement the methods of Ordinal:
        self.assertEqual(ir.types["Size"]["methods"]["lt"]["name"],        "lt")
        self.assertEqual(ir.types["Size"]["methods"]["lt"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["lt"]["return_type"], "Boolean")
        self.assertEqual(ir.types["Size"]["methods"]["le"]["name"],        "le")
        self.assertEqual(ir.types["Size"]["methods"]["le"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["le"]["return_type"], "Boolean")
        self.assertEqual(ir.types["Size"]["methods"]["gt"]["name"],        "gt")
        self.assertEqual(ir.types["Size"]["methods"]["gt"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["gt"]["return_type"], "Boolean")
        self.assertEqual(ir.types["Size"]["methods"]["ge"]["name"],        "ge")
        self.assertEqual(ir.types["Size"]["methods"]["ge"]["params"],      [("self", "Size"), ("other", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["ge"]["return_type"], "Boolean")
        # Should implement the methods of Value:
        self.assertEqual(ir.types["Size"]["methods"]["get"]["name"],        "get")
        self.assertEqual(ir.types["Size"]["methods"]["get"]["params"],      [("self", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["get"]["return_type"], "Size")
        self.assertEqual(ir.types["Size"]["methods"]["set"]["name"],        "set")
        self.assertEqual(ir.types["Size"]["methods"]["set"]["params"],      [("self", "Size"), ("value", "Size")])
        self.assertEqual(ir.types["Size"]["methods"]["set"]["return_type"], "Nothing")
        # Check the number of methods:
        self.assertEqual(len(ir.types["Size"]["methods"]), 12)



    def test_load_empty(self):
        """Test loading an empty protocol object"""
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "EmptyProtocol",
                "definitions" : [],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        # Check that we just have the built-in types and traits, and that
        # no PDUs were defined:
        self.assertEqual(len(ir.types),  3)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "EmptyProtocol")



    def test_load_bitstring(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadBitString",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "TestBitString",
                    "size"      : 16
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 1)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadBitString")
        self.assertEqual(ir.types["TestBitString"]["kind"], "BitString")
        self.assertEqual(ir.types["TestBitString"]["name"], "TestBitString")
        self.assertEqual(ir.types["TestBitString"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["TestBitString"]["components"], {})
        self.assertEqual(ir.types["TestBitString"]["implements"], ["Equality", "Value"])



    def test_load_array(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadArray",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "SSRC",
                    "size"      : 32
                },
                {
                    "construct" : "Array",
                    "name"      : "CsrcList",
                    "element_type" : "SSRC",
                    "length"       : 4
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 2)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadArray")
        self.assertEqual(ir.types["SSRC"]["kind"], "BitString")
        self.assertEqual(ir.types["SSRC"]["name"], "SSRC")
        self.assertEqual(ir.types["SSRC"]["attributes"], {"size" : 32})
        self.assertEqual(ir.types["SSRC"]["components"], {})
        self.assertEqual(ir.types["SSRC"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["CsrcList"]["kind"], "Array")
        self.assertEqual(ir.types["CsrcList"]["name"], "CsrcList")
        self.assertEqual(ir.types["CsrcList"]["attributes"], {"length" : 4, "size" : 128, "element_type" : "SSRC"})
        self.assertEqual(ir.types["CsrcList"]["components"], {})
        self.assertEqual(ir.types["CsrcList"]["implements"], ["Equality", "IndexCollection"])



    def test_load_struct(self):
        ir = IR()
        # FIXME: this doesn't test is_present
        # FIXME: this doesn't test transform
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadStruct",
                "definitions" : [
                    {
                        "construct" : "BitString",
                        "name"      : "SeqNum",
                        "size"      : 16
                    },
                    {
                        "construct" : "BitString",
                        "name"      : "Timestamp",
                        "size"      : 32
                    },
                    {
                        "construct"   : "Struct",
                        "name"        : "TestStruct",
                        "fields"      : [
                            {
                                "name"       : "seq",
                                "type"       : "SeqNum",
                                "is_present" : ""
                            },
                            {
                                "name"       : "ts",
                                "type"       : "Timestamp",
                                "is_present" : ""
                            }
                        ],
                        "constraints" : [
                          {
                             "expression" : "MethodInvocation",
                             "target"     : {
                               "expression" : "MethodInvocation",
                               "target" : {
                                 "expression" : "This"
                               },
                               "method"    : "get",
                               "arguments" : [
                                 {
                                     "name"  : "index",
                                     "value" : {
                                       "expression" : "Constant",
                                       "type"       : "FieldName",
                                       "value"      : "seq"
                                     }
                                  }
                               ]
                             },
                             "method"     : "lt",
                             "arguments"  : [
                               {
                                   "name"  : "other",
                                   "value" : {
                                     "expression" : "Constant",
                                     "type"       : "SeqNum",
                                     "value"      : "47"
                                   }
                               }
                             ]
                          }
                        ]
                    }
                ],
                "pdus" : [
                    {"type" : "TestStruct"}
                ]
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 3)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   1)
        self.assertEqual(ir.protocol_name, "LoadStruct")
        self.assertEqual(ir.types["SeqNum"]["kind"], "BitString")
        self.assertEqual(ir.types["SeqNum"]["name"], "SeqNum")
        self.assertEqual(ir.types["SeqNum"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["SeqNum"]["components"], {})
        self.assertEqual(ir.types["SeqNum"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["Timestamp"]["kind"], "BitString")
        self.assertEqual(ir.types["Timestamp"]["name"], "Timestamp")
        self.assertEqual(ir.types["Timestamp"]["attributes"], {"size" : 32})
        self.assertEqual(ir.types["Timestamp"]["components"], {})
        self.assertEqual(ir.types["Timestamp"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TestStruct"]["kind"], "Struct")
        self.assertEqual(ir.types["TestStruct"]["name"], "TestStruct")
        self.assertEqual(ir.types["TestStruct"]["attributes"], {
            "size"        : 48
        })
        # FIXME: this is not a very useful test of the constraints, since it just 
        # checks that the JSON is unloaded unchanged.
        self.assertEqual(ir.types["TestStruct"]["components"], {
            "fields"      : [("seq", "SeqNum", ""), ("ts",  "Timestamp", "")],
            "constraints" : [
              {
                 "expression" : "MethodInvocation",
                 "target"     : {
                   "expression" : "MethodInvocation",
                   "target" : {
                     "expression" : "This"
                   },
                   "method"    : "get",
                   "arguments" : [
                     {
                         "name"  : "index",
                         "value" : {
                           "expression" : "Constant",
                           "type"       : "FieldName",
                           "value"      : "seq"
                         }
                      }
                   ]
                 },
                 "method"     : "lt",
                 "arguments"  : [
                   {
                       "name"  : "other",
                       "value" : {
                         "expression" : "Constant",
                         "type"       : "SeqNum",
                         "value"      : "47"
                       }
                   }
                 ]
              }
            ]
        })
        self.assertEqual(ir.types["TestStruct"]["implements"], ["NamedCollection"])
        self.assertEqual(ir.pdus, ["TestStruct"])



    def test_load_enum(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadEnum",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "TypeA",
                    "size"      : 32
                },
                {
                    "construct" : "BitString",
                    "name"      : "TypeB",
                    "size"      : 32
                },
                {
                    "construct"   : "Enum",
                    "name"        : "TestEnum",
                    "variants"    : [
                        {"type" : "TypeA"},
                        {"type" : "TypeB"}
                    ]
                }],
                "pdus" : [
                    {"type" : "TestEnum"}
                ]
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 3)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   1)
        self.assertEqual(ir.protocol_name, "LoadEnum")
        self.assertEqual(ir.types["TypeA"]["kind"], "BitString")
        self.assertEqual(ir.types["TypeA"]["name"], "TypeA")
        self.assertEqual(ir.types["TypeA"]["attributes"], {"size" : 32})
        self.assertEqual(ir.types["TypeA"]["components"], {})
        self.assertEqual(ir.types["TypeA"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TypeB"]["kind"], "BitString")
        self.assertEqual(ir.types["TypeB"]["name"], "TypeB")
        self.assertEqual(ir.types["TypeB"]["attributes"], {"size" : 32})
        self.assertEqual(ir.types["TypeB"]["components"], {})
        self.assertEqual(ir.types["TypeB"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TestEnum"]["kind"], "Enum")
        self.assertEqual(ir.types["TestEnum"]["name"], "TestEnum")
        self.assertEqual(ir.types["TestEnum"]["attributes"], {
            "size"     : None
        })
        self.assertEqual(ir.types["TestEnum"]["components"], {
            "variants" : ["TypeA", "TypeB"]
        })
        self.assertEqual(ir.types["TestEnum"]["implements"], [])
        self.assertEqual(ir.pdus, ["TestEnum"])



    def test_load_newtype(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadNewType",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "Bits16",
                    "size"      : 16
                },
                {
                    "construct"    : "NewType",
                    "name"         : "SeqNum",
                    "derived_from" : "Bits16",
                    "implements"   : ["Ordinal"]
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 2)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadNewType")
        self.assertEqual(ir.types["Bits16"]["kind"], "BitString")
        self.assertEqual(ir.types["Bits16"]["name"], "Bits16")
        self.assertEqual(ir.types["Bits16"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["Bits16"]["components"], {})
        self.assertEqual(ir.types["Bits16"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["SeqNum"]["kind"], "BitString")
        self.assertEqual(ir.types["SeqNum"]["name"], "SeqNum")
        self.assertEqual(ir.types["SeqNum"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["SeqNum"]["components"], {})
        self.assertEqual(ir.types["SeqNum"]["implements"], ["Equality", "Ordinal", "Value"])



    def test_load_function(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadFunction",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "Bits16",
                    "size"      : 16
                },
                {
                    "construct"   : "Function",
                    "name"        : "TestFunction",
                    "parameters"  : [
                    {
                        "name" : "foo",
                        "type" : "Bits16"
                    },
                    {
                        "name" : "bar",
                        "type" : "Boolean"
                    }],
                    "return_type" : "Boolean"
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 2)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadFunction")
        self.assertEqual(ir.types["Bits16"]["kind"], "BitString")
        self.assertEqual(ir.types["Bits16"]["name"], "Bits16")
        self.assertEqual(ir.types["Bits16"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["Bits16"]["components"], {})
        self.assertEqual(ir.types["Bits16"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TestFunction"]["kind"], "Function")
        self.assertEqual(ir.types["TestFunction"]["name"], "TestFunction")
        self.assertEqual(ir.types["TestFunction"]["attributes"], {
            "parameters"  : [("foo", "Bits16"), ("bar", "Boolean")],
            "return_type" : "Boolean"
        })
        self.assertEqual(ir.types["TestFunction"]["components"], {})
        self.assertEqual(ir.types["TestFunction"]["implements"], [])



    def test_load_context(self):
        ir = IR()
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadContext",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "Bits16",
                    "size"      : 16
                },
                {
                    "construct"   : "Context",
                    "fields"  : [
                    {
                        "name" : "foo",
                        "type" : "Bits16"
                    },
                    {
                        "name" : "bar",
                        "type" : "Boolean"
                    }]
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 1)
        self.assertEqual(len(ir.traits), 7)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadContext")
        self.assertEqual(ir.types["Bits16"]["kind"], "BitString")
        self.assertEqual(ir.types["Bits16"]["name"], "Bits16")
        self.assertEqual(ir.types["Bits16"]["attributes"], {"size" : 16})
        self.assertEqual(ir.types["Bits16"]["components"], {})
        self.assertEqual(ir.types["Bits16"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.context["foo"]["name"], "foo")
        self.assertEqual(ir.context["foo"]["type"], "Bits16")
        self.assertEqual(ir.context["foo"]["value"], None)
        self.assertEqual(ir.context["bar"]["name"], "bar")
        self.assertEqual(ir.context["bar"]["type"], "Boolean")
        self.assertEqual(ir.context["bar"]["value"], None)



# =============================================================================
if __name__ == "__main__":
    unittest.main()


