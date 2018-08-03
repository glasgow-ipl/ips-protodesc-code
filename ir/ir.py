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

class IRError(Exception):
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
            raise IRError("cannot deriveFrom self")
        if not derivedFrom in self.types:
            raise IRError("derivedFrom unknown type")

        # Record the new type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRError("type already exists")



    def _parse_array(self, item):
        # Extract the required fields:
        name        = item["name"]
        elementType = item["elementType"]
        length      = item["length"]

        # Check that the length is valid:
        if length is not None:
            if length < 0:
                raise IRError("negative array length")

        # Check that the element type has been defined and is distinct
        # from the array type being defined:
        if elementType == name:
            raise IRError("elementType equals array type")
        if not elementType in self.types:
            raise IRError("elementType unknown")

        # Record the array type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRError("type already exists")



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
                raise IRError("field type unknwon")
            if field["type"] in field_types:
                raise IRError("duplicate field type")
            if field["name"] in field_names:
                raise IRError("duplicate field name");
            field_types[field["type"]] = True
            field_names[field["name"]] = True

        # Check the constraints:
        # FIXME

        # Record the structure type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRError("type already exists")



    def _parse_enum(self, item):
        # Extract the required fields:
        name        = item["name"]
        variants    = item["variants"]

        # Check the variants exist and are distinct:
        variant_types = {}
        for variant in variants:
            if not variant["type"] in self.types:
                raise IRError("variant type unknown")
            if variant["type"] in variant_types:
                raise IRError("duplicate variant")
            variant_types[variant["type"]] = True

        # Record the enum type in the type store:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRError("type already exists")



    def _parse_func(self, item):
        # Extract the required fields:
        name        = item["name"]
        parameters  = item["parameters"]
        returnType  = item["returnType"]

        # Check that the function name doesn't exist:
        if name in self.types:
            raise IRError("function name redefined")

        # Check that the parameter types exist, and that the parameter
        # names are distinct:
        param_names  = {}
        for param in parameters:
            if not param["type"] in self.types:
                raise IRError("unknown parameter type")
            if param["name"] in param_names:
                raise IRError("duplicate parameter name");
            param_names[param["name"]] = True

        # Check that the return type exists:
        if not returnType in self.types:
            raise IRError("unknown returnType")

        # Record the function definition:
        if not name in self.types:
            self.types[name] = item
        else:
            raise IRError("function already exists")



    def __init__(self, ir):
        # Create and type store, and populate with the primitive Bit type:
        self.types = {}
        self.types["Bit"] = {"irobject" : "bit", 
                             "name"     : "Bit"}

        # Check that we have been given a dictionary containing a protocol
        # object:
        if ir["irobject"] != "protocol":
            raise IRError("not a protocol")

        # Check that the protocol has a name:
        if not "name" in ir:
            raise IRError("protocol has no name")

        # Load the definitions:
        for item in ir["definitions"]:
            if   item["irobject"] == "bit":
                raise IRError("cannot redefine bit")
            elif item["irobject"] == "newtype":
                self._parse_newtype(item)
            elif item["irobject"] == "array":
                self._parse_array(item)
            elif item["irobject"] == "struct":
                self._parse_struct(item)
            elif item["irobject"] == "enum":
                self._parse_enum(item)
            elif item["irobject"] == "function":
                self._parse_func(item)
            else:
                raise IRError("protocol definitions contain unknown irobject")

        # Check the PDU types:
        if ir["pdus"] == []:
            raise IRError("protocol has empty PDU array")
        for pdu in ir["pdus"]:
            if not pdu in self.types:
                raise IRError("protocol has unkown PDU type")

# =============================================================================
# Unit tests:

import unittest

class TestIR(unittest.TestCase):
    def test_empty(self):
        ir = IR({
                  "irobject"    : "protocol",
                  "name"        : "Test",
                  "definitions" : [],
                  "pdus"        : ["Bit"]
                })

# =============================================================================
if __name__ == "__main__":
    unittest.main()

