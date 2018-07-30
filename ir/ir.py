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

class IRParseError(Exception):
    def __init__(self, reason):
        self.reason = reason

class IR:
    def _parse_newtype(self, item):
        # Extract the required fields:
        name        = item["name"]
        derivedFrom = item["derivedFrom"]

        # Check that the new type is derived from an existing type, and
        # not from itself:
        if derivedFrom == name:
            raise IRParseError("cannot deriveFrom self")
        if not derivedFrom in self.types:
            raise IRParseError("derivedFrom unknown type")

        # Record the new type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRParseError("type already exists")



    def _parse_array(self, item):
        # Extract the required fields:
        name        = item["name"]
        elementType = item["elementType"]
        length      = item["length"]

        # Check that the length is valid:
        if length is not None:
            if length < 0:
                raise IRParseError("negative array length")

        # Check that the element type has been defined and is distinct
        # from the array type being defined:
        if elementType == name:
            raise IRParseError("elementType equals array type")
        if not elementType in self.types:
            raise IRParseError("elementType unknown")

        # Record the array type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRParseError("type already exists")



    def _parse_struct(self, item):
        # Extract the required fields:
        name        = item["name"]
        fields      = item["fields"]
        constraints = item["constraints"]

        # Check the field types have been defined, and that fields names and
        # types are distinct within this struct:
        field_types = {}
        field_names  = {}
        for field in fields:
            if not field["type"] in self.types:
                raise IRParseError("field type unknwon")
            if field["type"] in field_types:
                raise IRParseError("duplicate field type")
            if field["name"] in field_names:
                raise IRParseError("duplicate field name");
            field_types[field["type"]] = True
            field_names[field["name"]] = True

        # Check the constraints:
        # FIXME

        # Record the structure type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRParseError("type already exists")



    def _parse_enum(self, item):
        # Extract the required fields:
        name        = item["name"]
        variants    = item["variants"]

        # Check the variants exist and are distinct:
        variant_types = {}
        for variant in variants:
            if not variant["type"] in self.types:
                raise IRParseError("variant type unknown")
            if variant["type"] in variant_types:
                raise IRParseError("duplicate variant")
            variant_types[variant["type"]] = True

        # Record the structure type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRParseError("type already exists")



    def __init__(self, rawIR):
        # Create the type store and populate with the primitive Bit type:
        self.types = {}
        self.types["Bit"] = {"irobject" : "bit"}

        # Load the IR:
        parsedIR = json.loads(rawIR)
        if not isinstance(parsedIR, list):
            raise IRParseError("Must be a JSON array")

        # Parse the IR:
        for item in parsedIR:
            if   item["irobject"] == "bit":
                raise IRParseError("cannot redefine bit")
            elif item["irobject"] == "newtype":
                self._parse_newtype(item)
            elif item["irobject"] == "array":
                self._parse_array(item)
            elif item["irobject"] == "struct":
                self._parse_struct(item)
            elif item["irobject"] == "enum":
                self._parse_enum(item)
            else:
                raise IRParseError("unknown irobject")

# =============================================================================
# Unit tests:

import unittest

class TestIR(unittest.TestCase):
    def test_array(self):
        rawIR = """
                [
                    {
                      "irobject"    : "array",
                      "name"        : "SeqNum",
                      "elementType" : "Bit",
                      "length"      : 16
                    }
                ]
                """
        ir = IR(rawIR)
        #self.assertEqual(ir['irobject'],    'array')
        #self.assertEqual(ir['name'],        'SeqNum')
        #self.assertEqual(ir['elementType'], 'Bit')
        #self.assertEqual(ir['length'],      16)

    # Test the failure case, where the elementType is equal to the array type
    def test_array_elementType_equals_type(self):
        rawIR = """
                [
                    {
                      "irobject"    : "array",
                      "name"        : "SeqNum",
                      "elementType" : "SeqNum",
                      "length"      : 16
                    }
                ]
                """
        self.assertRaises(IRParseError, IR, rawIR)

    # Test the failure case, where the array length is negative
    def test_array_negative_length(self):
        rawIR = """
                [
                    {
                      "irobject"    : "array",
                      "name"        : "SeqNum",
                      "elementType" : "Bit",
                      "length"      : -1
                    }
                ]
                """
        self.assertRaises(IRParseError, IR, rawIR)

    def test_compound(self):
        rawIR = """
                [
                    {
                     "irobject"    : "array",
                     "name"        : "PacketNumber",
                     "elementType" : "Bit",
                     "length"      : 7
                    },
                    {
                     "irobject"    : "struct",
                     "name"        : "test",
                     "fields"      : [
                       {
                         "name" : "length",
                         "type" : "PacketNumber"
                       },
                       {
                         "name" : "length",
                         "type" : "Bit"
                       }
                     ],
                     "constraints" : [
                     ]
                    }
                ]
                """
        ir = IR(rawIR)

# =============================================================================
if __name__ == "__main__":
    unittest.main()

