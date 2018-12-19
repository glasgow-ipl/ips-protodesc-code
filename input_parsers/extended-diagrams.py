# =================================================================================================
# Copyright (C) 2018 University of Glasgow
# All rights reserved.
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
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

import parsley
import string
import sys
import json
import re
from shared import *


def ascii_data_processor(d):
    output = []
    for x in d:
        if type(x) is list:
            output += x

    return output


def data_processor(asciiData, textData):

    # Ensure textData is a list of dicts. Any list of list of dicts should be eliminated
    temp = []
    for td in textData:
        if type(td) is list:
            temp += td
        else:
            temp.append(td)
    textData = temp

    # Inherit properties from Text into the Ascii Data
    for td in textData[:]:
        for ad in asciiData:
            if ad["name"] == td["name"]:
                if td["width"] >= 0:
                    ad["width"] = td["width"]
                if td["width"] == -2:
                    ad["width"] = None
                if "where" in td:
                    ad["where"] = td["where"]
                textData.remove(td)

    # Match items between textData and asciiData
    for td in textData[:]:
        for ad in asciiData:
            if ad["name"] == td["name"][:len(ad["name"])] and ad["width"] == td["width"]:
                ad["name"] = td["name"]
                textData.remove(td)

    return asciiData

def text_title_processor(name, data):
    name = "".join(name)
    width = -1

    if type(data) is dict:
        width = data["width"]

        if "where" in data:
            return {
                "name": name,
                "width": width,
                "where": data["where"]
            }

        else:
            return {
                "name": name,
                "width": width,
            }

    return {
        "name": name,
        "width": width,
    }


def text_bits_processor(d):
    s = "".join(d)

    if s.isdigit():
        return {
            "width": int(s)
        }

    else:
        return {
            "width": -2,
            "where": ["width="+s]
        }


def text_control_bits_processor(d):
    output = []

    for x in d:
        output.append({
            "name": x,
            "width": 1,
        })

    return output


def generate_type_name(str):
    return re.sub(r'[^A-Za-z]', '', str.title())

def generate_field_name(str):
    str = str.lower()
    str = str.replace(' ', '_')
    str = re.sub(r'[^a-z_]', '', str)
    str = re.sub('_+', '_', str)
    return str

def test(data):
    return {'name': "".join(data).strip(), 'width': int((len(data)+1)/2)}

def parse_extended_diagram(str):
    grammar = r"""
                letter = anything:x ?(x in ascii_letters) -> x
                digit = anything:x ?(x in '0123456789') -> x
                letterdigit = anything:x ?(x in ascii_letters or x in '0123456789') -> x
                paragraph = anything:x ?(x in ascii_letters or x in "0123456789 ,.()-'+") -> x
                formula = anything:x ?(x in ascii_letters or x in "0123456789-+*/().%") -> x
            
                crlf = '\n'
                ws = ' '*
            
                header1a = '0                   1                   2                   3'
                header1b = '0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1'
                separator = '+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'
            
                rowStart = '|'
                field = (((' ' | letter)*:d1 '|' crlf ws '+' (' ' | letter)*:d2 '+' crlf ws '|' (' ' | letter)*:d3 -> d1 + d2 + d3)|(' ' | letter)*):data '|' -> test(data) 
            
                header = ws header1a ws crlf ws header1b ws crlf 
                row = ws rowStart field*:data crlf -> data
                separatorRow = ws separator crlf -> ''
            
                ascii = crlf header separatorRow (row:data separatorRow -> data)*:data -> ascii_data_processor(data)
            
                textBits = formula*:data ' ' ('bits'|'bit') -> text_bits_processor(data)
                textTitle = '  ' (' ' | letter)*:name (':  ' textBits:data crlf | crlf:data) -> text_title_processor(name, data)
                textBody = '    ' paragraph* crlf
            
                textTitleControlBits = '  ' (' ' | letter)*:name (':  ' textBits:data ' (from left to right):' crlf | crlf:data) -> text_title_processor(name, data)
                textBodyControlBits = '    ' (letter | ':' | ' ')*:data crlf -> "".join(data)
            
                textTitleVariable = '  ' (' ' | letter)*:name ':  variable' crlf -> {"name":"".join(name), "width": -2}
            
                textRegular = crlf textTitle:data crlf textBody* -> data
                textControlBits = crlf textTitleControlBits crlf textBodyControlBits*:data -> text_control_bits_processor(data)
                textVariable = crlf textTitleVariable:data crlf textBody* -> data
            
                text = (textRegular|textControlBits|textVariable)
            
                expr = ascii:asciiData text*:textData -> data_processor(asciiData, textData)
                """

    parser = parsley.makeGrammar(grammar, {
        "ascii_letters": string.ascii_letters,
        "ascii_data_processor": ascii_data_processor,
        "data_processor": data_processor,
        "text_title_processor": text_title_processor,
        "text_bits_processor": text_bits_processor,
        "text_control_bits_processor": text_control_bits_processor,
        "test": test
    })

    return parser(str).expr()

def parse_convert(packet, protocol_name):

    type_namespace = {}

    fields = []
    bitstrings = []

    for p in packet:
        typeName = "BitString$" + str(p["width"])
        fieldName = generate_field_name(p["name"])

        # If a bitstring of this width hasn't been added yet, add it
        if p["width"] not in bitstrings:
            if p["width"] is None:
                bits = None
            else:
                bits = ('Bits', p["width"])
            new_bitstring(typeName, bits, type_namespace)
            bitstrings.append(p["width"])

        fields.append(new_field(fieldName, (typeName, None), None, type_namespace))

    new_struct("Packet", fields, None, type_namespace, [], [])

    new_enum("PDUs", [("Packet", None)], type_namespace)

    return new_protocol(protocol_name, type_namespace)

def parse_file(filename):
    protocol_name = filename_to_protocol_name(filename)

    with open(filename, 'r') as f:
        packet = parse_extended_diagram(f.read())
    return parse_convert(packet, protocol_name)

if __name__ == "__main__":
    print(json.dumps(parse_file(sys.argv[1]), indent=4))
