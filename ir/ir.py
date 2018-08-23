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
        self.pdus   = []

        self.protocol_name = ""

        # Define the internal types and standard traits:
        self._define_type("Nothing", "Nothing", {})
        self._define_type("Boolean", "Boolean", {})
        self._define_type("Size",    "Size",    {})

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
        self._define_trait("Collection",  [("get", [("self", None), ("index", "Size")], None),
                                           ("set", [("self", None), ("index", "Size"), ("value", None)], "Nothing")])

        self._implements("Boolean", ["Value", "Equality", "Boolean"])
        self._implements(   "Size", ["Value", "Equality", "Ordinal", "Arithmetic"])



    def _construct_bitstring(self, defn):
        attributes = {}
        attributes["width"] = defn["width"]
        self._define_type("BitString", defn["name"], attributes)
        self._implements(defn["name"], ["Value"])
        self._implements(defn["name"], ["Equality"])



    def _construct_array(self, defn):
        if not defn["element_type"] in self.types:
            raise IRError("Unknown element type")
        attributes = {}
        attributes["element_type"] = defn["element_type"]
        attributes["length"]       = defn["length"]
        self._define_type("Array", defn["name"], attributes)
        self._implements(defn["name"], ["Equality"])
        self._implements(defn["name"], ["Collection"])



    def _construct_struct(self, defn):
        attributes = {}

        attributes["fields"] = []
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
            attributes["fields"].append((field["name"], field["type"], field["is_present"]))

        # FIXME: add support for constraints
        attributes["constraints"] = []

        self._define_type("Struct", defn["name"], attributes)
        self._implements(defn["name"], ["Collection"])



    def _construct_enum(self, defn):
        attributes = {}
        attributes["variants"] = []
        for v in defn["variants"]:
            if not v["type"] in self.types:
                raise IRError("Unknown variant: " + v["type"])
            attributes["variants"].append(v["type"])
            attributes["variants"].sort()
        self._define_type("Enum", defn["name"], attributes)



    def _construct_newtype(self, defn):
        base_type = defn["derived_from"]
        if not base_type in self.types:
            raise IRError("Derived from unknown type: " + base_type)

        base_kind = self.types[base_type]["kind"]
        base_attr = self.types[base_type]["attributes"]
        base_impl = self.types[base_type]["implements"]

        self._define_type(base_kind, defn["name"], base_attr)
        self._implements(defn["name"], base_impl + defn["implements"])



    def _construct_function(self, defn):
        raise IRError("unimplemented")



    def _construct_context(self, defn):
        raise IRError("unimplemented")



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

        # Record the PDUs:
        for pdu in protocol["pdus"]:
            if not pdu["type"] in self.types:
                raise IRError("Unknown PDU type: " + pdu["type"])
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
        self.assertEqual(ir.types["Boolean"]["implements"], ["Boolean", "Equality", "Value"])
        # Check the built-in Size type:
        self.assertEqual(ir.types["Size"]["kind"],       "Size")
        self.assertEqual(ir.types["Size"]["name"],       "Size")
        self.assertEqual(ir.types["Size"]["attributes"], {})
        self.assertEqual(ir.types["Size"]["implements"], ["Arithmetic", "Equality", "Ordinal", "Value"])
        # Check the number of built-in traits:
        self.assertEqual(len(ir.traits), 6)
        # Check the built-in Arithmetic trait:
        self.assertEqual(ir.traits["Arithmetic"]["name"], "Arithmetic")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["name"],   "plus")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["plus"    ]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["name"],   "minus")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["minus"   ]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["name"],   "multiply")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["params"], [("self", None), ("other", None)])
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["multiply"]["return_type"], None)
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["divide"  ]["name"],   "divide")
        self.assertEqual(ir.traits["Arithmetic"]["methods"]["divide"  ]["params"], [("self", None), ("other", None)])
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
        # Check the built-in Collection trait:
        self.assertEqual(ir.traits["Collection"]["name"], "Collection")
        self.assertEqual(ir.traits["Collection"]["methods"]["get"]["name"],        "get")
        self.assertEqual(ir.traits["Collection"]["methods"]["get"]["params"], [("self", None), ("index", "Size")])
        self.assertEqual(ir.traits["Collection"]["methods"]["get"]["return_type"], None)
        self.assertEqual(ir.traits["Collection"]["methods"]["set"]["name"],        "set")
        self.assertEqual(ir.traits["Collection"]["methods"]["set"]["params"], [("self", None), ("index", "Size"), ("value", None)])
        self.assertEqual(ir.traits["Collection"]["methods"]["set"]["return_type"], "Nothing")
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
        self.assertEqual(len(ir.traits), 6)
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
                    "width"     : 16
                }],
                "pdus"        : []
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 1)
        self.assertEqual(len(ir.traits), 6)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadBitString")
        self.assertEqual(ir.types["TestBitString"]["kind"], "BitString")
        self.assertEqual(ir.types["TestBitString"]["name"], "TestBitString")
        self.assertEqual(ir.types["TestBitString"]["attributes"], {"width" : 16})
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
                    "width"     : 32
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
        self.assertEqual(len(ir.traits), 6)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadArray")
        self.assertEqual(ir.types["SSRC"]["kind"], "BitString")
        self.assertEqual(ir.types["SSRC"]["name"], "SSRC")
        self.assertEqual(ir.types["SSRC"]["attributes"], {"width" : 32})
        self.assertEqual(ir.types["SSRC"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["CsrcList"]["kind"], "Array")
        self.assertEqual(ir.types["CsrcList"]["name"], "CsrcList")
        self.assertEqual(ir.types["CsrcList"]["attributes"], {"length" : 4, "element_type" : "SSRC"})
        self.assertEqual(ir.types["CsrcList"]["implements"], ["Collection", "Equality"])



    def test_load_struct(self):
        ir = IR()
        # FIXME: this doesn't test is_present
        # FIXME: this doesn't test constraints
        protocol = """
            {
                "construct"   : "Protocol",
                "name"        : "LoadStruct",
                "definitions" : [
                {
                    "construct" : "BitString",
                    "name"      : "SeqNum",
                    "width"     : 16
                },
                {
                    "construct" : "BitString",
                    "name"      : "Timestamp",
                    "width"     : 32
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
                    }],
                    "constraints" : []
                }],
                "pdus" : [
                    {"type" : "TestStruct"}
                ]
            }
        """
        ir.load(protocol)
        self.assertEqual(len(ir.types),  3 + 3)
        self.assertEqual(len(ir.traits), 6)
        self.assertEqual(len(ir.pdus),   1)
        self.assertEqual(ir.protocol_name, "LoadStruct")
        self.assertEqual(ir.types["SeqNum"]["kind"], "BitString")
        self.assertEqual(ir.types["SeqNum"]["name"], "SeqNum")
        self.assertEqual(ir.types["SeqNum"]["attributes"], {"width" : 16})
        self.assertEqual(ir.types["SeqNum"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["Timestamp"]["kind"], "BitString")
        self.assertEqual(ir.types["Timestamp"]["name"], "Timestamp")
        self.assertEqual(ir.types["Timestamp"]["attributes"], {"width" : 32})
        self.assertEqual(ir.types["Timestamp"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TestStruct"]["kind"], "Struct")
        self.assertEqual(ir.types["TestStruct"]["name"], "TestStruct")
        self.assertEqual(ir.types["TestStruct"]["attributes"], {
            "fields"      : [("seq", "SeqNum", ""), ("ts",  "Timestamp", "")],
            "constraints" : []
        })
        self.assertEqual(ir.types["TestStruct"]["implements"], ["Collection"])
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
                    "width"     : 32
                },
                {
                    "construct" : "BitString",
                    "name"      : "TypeB",
                    "width"     : 32
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
        self.assertEqual(len(ir.traits), 6)
        self.assertEqual(len(ir.pdus),   1)
        self.assertEqual(ir.protocol_name, "LoadEnum")
        self.assertEqual(ir.types["TypeA"]["kind"], "BitString")
        self.assertEqual(ir.types["TypeA"]["name"], "TypeA")
        self.assertEqual(ir.types["TypeA"]["attributes"], {"width" : 32})
        self.assertEqual(ir.types["TypeA"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TypeB"]["kind"], "BitString")
        self.assertEqual(ir.types["TypeB"]["name"], "TypeB")
        self.assertEqual(ir.types["TypeB"]["attributes"], {"width" : 32})
        self.assertEqual(ir.types["TypeB"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["TestEnum"]["kind"], "Enum")
        self.assertEqual(ir.types["TestEnum"]["name"], "TestEnum")
        self.assertEqual(ir.types["TestEnum"]["attributes"], {
            "variants" : ["TypeA", "TypeB"],
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
                    "width"     : 16
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
        self.assertEqual(len(ir.traits), 6)
        self.assertEqual(len(ir.pdus),   0)
        self.assertEqual(ir.protocol_name, "LoadNewType")
        self.assertEqual(ir.types["Bits16"]["kind"], "BitString")
        self.assertEqual(ir.types["Bits16"]["name"], "Bits16")
        self.assertEqual(ir.types["Bits16"]["attributes"], {"width" : 16})
        self.assertEqual(ir.types["Bits16"]["implements"], ["Equality", "Value"])
        self.assertEqual(ir.types["SeqNum"]["kind"], "BitString")
        self.assertEqual(ir.types["SeqNum"]["name"], "SeqNum")
        self.assertEqual(ir.types["SeqNum"]["attributes"], {"width" : 16})
        self.assertEqual(ir.types["SeqNum"]["implements"], ["Equality", "Ordinal", "Value"])



# =============================================================================
if __name__ == "__main__":
    unittest.main()


