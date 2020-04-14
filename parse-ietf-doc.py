#!/usr/bin/env python3.7
# =================================================================================================
# Copyright (C) 2019 University of Glasgow
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

import argparse
import requests
import xml.etree.ElementTree as ET
import os.path
import urllib

import ietfdata.datatracker as DT

from protocol import *

# RFC DOM input parsers
import parsers.parser
import parsers.rfc.rfc as rfc
import parsers.rfc.rfc_txt_parser
import parsers.rfc.rfc_xml_parser
import parsers.asciidiagrams.asciidiagrams_parser

# Output formatters
import formatters.formatter
import formatters.simple_formatter
import formatters.rust_formatter

ACTIVE_ID_URL = "https://www.ietf.org/id/"

# Protocol DFS

def dfs_struct(struct: Struct, type_names:List[str]):
    for field in struct.fields:
        dfs_protocoltype(field.field_type, type_names)

def dfs_array(array: Array, type_names:List[str]):
    dfs_protocoltype(array.element_type, type_names)

def dfs_enum(enum: Enum, type_names:List[str]):
    for variant in enum.variants:
        dfs_protocoltype(variant, type_names)

def dfs_function(function: Function, type_names:List[str]):
    for parameter in function.parameters:
        dfs_protocoltype(parameter.param_type)
    dfs_protocoltype(function.return_type)

def dfs_context(context: Context, type_names:List[str]):
    for field in context.fields:
        dfs_protocoltype(field.field_type)

def dfs_protocoltype(pt: ProtocolType, type_names:List[str]):
    if type(pt) is Struct:
        dfs_struct(pt, type_names)
    elif type(pt) is Array:
        dfs_array(pt, type_names)
    elif type(pt) is Enum:
        dfs_enum(pt, type_names)
    elif type(pt) is Function:
        dfs_function(pt, type_names)
    elif type(pt) is Context:
        dfs_context(pt, type_names)
    elif pt is None:
        return
    type_names.append(pt.name)

def dfs_protocol(protocol: Protocol):
    type_names = []

    for pdu_name in protocol.get_pdu_names():
        dfs_protocoltype(protocol.get_pdu(pdu_name), type_names)

    type_names_dedupe = []

    for type_name in type_names:
        if type_name not in type_names_dedupe:
            type_names_dedupe.append(type_name)

    return type_names_dedupe

def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument("--docname",       type=str, required=True)
    argparser.add_argument("--output-format", type=str, required=False, help="If not specified, the output format will be inferred from the output filename's extension")
    argparser.add_argument("--output-file",   type=str, required=True)

    args = argparser.parse_args()

    xml = None
    txt = None
    parsed_rfc = None

    # ============================================================================================
    # RFC -> RFC DOM
    # ============================================================================================

    if os.path.exists(args.docname):
        with open(args.docname) as inputFile:
            if args.docname[-3:] == "xml":
                xml = inputFile.read()
            else:
                txt = inputFile.readlines()
    else:
        # TODO: this could be much smarter about document names; doesn't handle errors/XML not being available
        dt = DT.DataTracker()
        doc = dt.document_from_draft(args.docname)
        if doc is not None:
            with urllib.request.urlopen(ACTIVE_ID_URL + doc.name + "-" + doc.rev + ".xml") as response:
                xml = response.read()
        else:
            return

    if xml is not None:
        rfcXml = ET.fromstring(xml)
        parsed_rfc = parsers.rfc.rfc_xml_parser.parse_rfc(rfcXml)
    elif txt is not None:
        parsed_rfc = parsers.rfc.rfc_txt_parser.parse_rfc(txt)

    # ============================================================================================
    # RFC DOM -> Protocol
    # ============================================================================================

    dom_parsers = ["asciidiagrams"]

    construct_dom_parser = {
                            "asciidiagrams"     : parsers.asciidiagrams.asciidiagrams_parser.AsciiDiagramsParser(),
                           }

    protocol = None

    for dom_parser_name in dom_parsers:
        dom_parser = construct_dom_parser[dom_parser_name]
        protocol = dom_parser.build_protocol(protocol, parsed_rfc)

    # ============================================================================================
    # Protocol -> output
    # ============================================================================================

    type_names = dfs_protocol(protocol)

    output_file_ext = args.output_file.split(".")[-1]

    file_exts = {
        "rs"  : "rust_formatter",
        "txt" : "simple_formatter"
    }

    if args.output_format is None:
        output_file_ext = args.output_file.split(".")[-1]
        args.output_format = file_exts.get(output_file_ext, "simpleprinter")

    construct_output_formatter = {
                                  "simple_formatter" : formatters.simple_formatter.SimpleFormatter(),
                                  "rust_formatter"   : formatters.rust_formatter.RustFormatter()
                                 }

    output_formatter = construct_output_formatter[args.output_format]

    # Format the protocol using output formatter
    try:
        for type_name in type_names:
            pt = protocol.get_type(type_name)
            if type(pt) is BitString:
                output_formatter.format_bitstring(pt)
            elif type(pt) is Struct:
                output_formatter.format_struct(pt)
            elif type(pt) is Array:
                output_formatter.format_array(pt)
            elif type(pt) is Enum:
                output_formatter.format_enum(pt)
            elif type(pt) is Function:
                output_formatter.format_function(pt)
            elif type(pt) is Context:
                output_formatter.format_context(pt)
        output_formatter.format_protocol(protocol)
    except Exception as e:
        print("*** Error *** Could not format protocol with specified formatter (%s)" % (args.output_format))

    # Output to file
    with open(args.output_file, "w+") as outputFile:
        outputFile.write(output_formatter.generate_output())

if __name__ == "__main__":
    main()
