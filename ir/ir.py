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
    def _define_type(self, kind, name, attributes):
        if re.search(TYPE_NAME_REGEX, name) == None:
            raise IRError("Invalid type name: " + name)
        if name in self.types:
            raise IRError("Redefinition of type " + name)
        self.types[name] = {
                "kind" : kind,
                "name" : name,
                "attributes" : attributes,
                "implements" : []
            }

    def _define_trait(self, name, methods):
        # Check validity of trait:
        if re.search(TYPE_NAME_REGEX, name) == None:
            raise IRError("Invalid trait name: " + name)
        if name in self.traits:
            raise IRError("Redefinition of trait " + name)

        # Create the trait:
        self.traits[name] = {
                "name"    : name,
                "methods" : {}
            }
        for (m_name, m_params, m_returns) in methods:
            # Check validity of the method name:
            if re.search(FUNC_NAME_REGEX, m_name) == None:
                raise IRError("Invalid method name: " + m_name)

            # Check validity of the method parameters:
            if m_params[0] != ("self", None):
                raise IRError("Method " + m_name + " does not have valid self parameter")
            for (p_name, p_type) in m_params:
                if re.search(FUNC_NAME_REGEX, p_name) == None:
                    raise IRError("Invalid parameter name: " + p_name)
                if p_type != None and not p_type in self.types:
                    raise IRError("Method " + m_name + " in trait " + name + "references undefined type " + p_type)

            # Check validity of the method return type:
            if m_returns != None and not m_returns in self.types:
                raise IRError("Unknown method return type " + m_returns + " in method " + m_name + " of trait " + name)

            # Record the method:
            self.traits[name]["methods"][m_name] = {}
            self.traits[name]["methods"][m_name]["name"]        = m_name
            self.traits[name]["methods"][m_name]["params"]      = m_params
            self.traits[name]["methods"][m_name]["return_type"] = m_returns

    def _implements(self, type_, traits):
        if not type_ in self.types:
            raise IRError("Undefined type " + type_)
        for trait in traits:
            if not trait in self.traits:
                raise IRError("Undefined trait " + trait)
            if trait in self.types[type_]["implements"]:
                raise IRError("Reimplementation of trait " + trait + " for type " + type_)
            self.types[type_]["implements"].append(trait)
            self.types[type_]["implements"].sort()

    def __init__(self):
        # Create the type, trait, and PDU stores:
        self.types  = {}
        self.traits = {}
        self.pdus   = {}

        self.protocol_name = ""

        # Define the internal types and standard traits:
        self._define_type("Nothing", "Nothing", [])
        self._define_type("Boolean", "Boolean", [])
        self._define_type("Size",    "Size",    [])

        self._define_trait("Value",       [("get", [("self", None)], None),
                                           ("set", [("self", None), ("value", None)], "Nothing")])
        self._define_trait("Equality",    [("eq",  [("self", None), ("other", None)], "Boolean"),
                                           ("ne",  [("self", None), ("other", None)], "Boolean")])
        self._define_trait("Boolean",     [("and", [("self", None), ("other", None)], "Boolean"),
                                           ("or",  [("self", None), ("other", None)], "Boolean"),
                                           ("not", [("self", None)                 ], "Boolean")])
        self._define_trait("Ordinal",     [("lt",  [("self", None), ("other", None)], "Boolean"),
                                           ("le",  [("self", None), ("other", None)], "Boolean"),
                                           ("gt",  [("self", None), ("other", None)], "Boolean"),
                                           ("ge",  [("self", None), ("other", None)], "Boolean")])
        self._define_trait("Arithmetic", [("plus", [("self", None), ("other", None)], None),
                                         ("minus", [("self", None), ("other", None)], None),
                                      ("multiply", [("self", None), ("other", None)], None),
                                        ("divide", [("self", None), ("other", None)], None)])

        self._implements("Boolean", ["Value", "Equality", "Boolean"])
        self._implements(   "Size", ["Value", "Equality", "Ordinal", "Arithmetic"])

    # protocol_json is a string holding the JSON form of a protocol object
    def load(self, protocol_json):
        # Load the JSON and check that it represents a Protocol object:
        protocol = json.loads(protocol_json)
        if protocol["construct"] != "Protocol":
            raise IRError("Not a protocol object")

        # Check and record the protocol name:
        if re.search(TYPE_NAME_REGEX, protocol["name"]) == None:
            raise IRError("Invalid protocol name: " + name)
        self.protocol_name = protocol["name"]

        # Load the definitions:
        for defn in protocol["definitions"]:
            if   defn["construct"] == "BitString":
                raise IRError("unimplemented")
            elif defn["construct"] == "Array":
                raise IRError("unimplemented")
            elif defn["construct"] == "Struct":
                raise IRError("unimplemented")
            elif defn["construct"] == "Enum":
                raise IRError("unimplemented")
            elif defn["construct"] == "NewType":
                raise IRError("unimplemented")
            elif defn["construct"] == "Function":
                raise IRError("unimplemented")
            elif defn["construct"] == "Context":
                raise IRError("unimplemented")

        # Record the PDUs:
        for p in protocol["pdus"]:
            raise IRError("unimplemented")

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
        self.assertEqual(ir.types["Nothing"]["attributes"], [])
        self.assertEqual(ir.types["Nothing"]["implements"], [])
        # Check the built-in Boolean type:
        self.assertEqual(ir.types["Boolean"]["kind"],       "Boolean")
        self.assertEqual(ir.types["Boolean"]["name"],       "Boolean")
        self.assertEqual(ir.types["Boolean"]["attributes"], [])
        self.assertEqual(ir.types["Boolean"]["implements"], ["Boolean", "Equality", "Value"])
        # Check the built-in Size type:
        self.assertEqual(ir.types["Size"]["kind"],       "Size")
        self.assertEqual(ir.types["Size"]["name"],       "Size")
        self.assertEqual(ir.types["Size"]["attributes"], [])
        self.assertEqual(ir.types["Size"]["implements"], ["Arithmetic", "Equality", "Ordinal", "Value"])
        # Check the number of built-in traits:
        self.assertEqual(len(ir.traits), 5)
        # Check the built-in Arithmetic trait:
        self.assertEqual(ir.traits["Arithmetic"]["name"], "Arithmetic")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["name"],        "plus")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["name"],        "minus")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["name"],        "multiply")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["divide"  ]["name"],        "divide")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["divide"  ]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["divide"  ]["return_type"], None)
        self.assertEqual(len(ir.traits["Arithmetic"]["methods"]), 4)
        # Check the built-in Boolean trait:
        self.assertEqual(ir.traits["Boolean"]["name"], "Boolean")
        self.assertEqual(ir.traits["Boolean"]["methods"]["and"]["name"],        "and")
        self.assertEqual(ir.traits["Boolean"]["methods"]["and"]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Boolean"]["methods"]["and"]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Boolean"]["methods"]["or" ]["name"],        "or")
        self.assertEqual(ir.traits["Boolean"]["methods"]["or" ]["params"],      [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Boolean"]["methods"]["or" ]["return_type"], "Boolean")
        self.assertEqual(ir.traits["Boolean"]["methods"]["not"]["name"],        "not")
        self.assertEqual(ir.traits["Boolean"]["methods"]["not"]["params"],      [("self", None)])
        self.assertEqual(ir.traits["Boolean"]["methods"]["not"]["return_type"], "Boolean")
        self.assertEqual(len(ir.traits["Boolean"]["methods"]), 3)
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
        self.assertEqual(len(ir.traits), 5)
        self.assertEqual(len(ir.pdus),   0)


# =============================================================================
if __name__ == "__main__":
    unittest.main()


