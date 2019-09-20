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
import rfc
import requests
import parse_rfc_xml #TODO tidy up the directory structure for these
import parse_rfc_txt # ^^
import xml.etree.ElementTree as ET
import parse_protodesc #TODO pull the DFS code out of this file
import os.path

from protocol import *

# RFC DOM input parsers
import input_parsers.inputparser
import input_parsers.rfcdom.asciidiagrams.asciidiagrams

# Output formatters
import output_formatters.outputformatter
import output_formatters.simpleprinter
import output_formatters.rust_writer

ACTIVE_ID_URL = "https://www.ietf.org/id/"

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
        # TODO: lookup docname in DT
        return

    if xml is not None:
        rfcXml = ET.fromstring(xml)
        parsed_rfc = parse_rfc_xml.parse_rfc(rfcXml)
    elif txt is not None:
        parsed_rfc = parse_rfc_txt.parse_rfc(txt)

    # ============================================================================================
    # RFC DOM -> Protocol
    # ============================================================================================

    dom_parsers = ["asciidiagrams"]

    construct_dom_parser = {
                            "asciidiagrams"     : input_parsers.rfcdom.asciidiagrams.asciidiagrams.AsciiDiagrams(),
                           }

    protocol = None

    for dom_parser_name in dom_parsers:
        dom_parser = construct_dom_parser[dom_parser_name]
        protocol = dom_parser.build_protocol(protocol, parsed_rfc)

    # ============================================================================================
    # Protocol -> output
    # ============================================================================================

    type_names = parse_protodesc.dfs_protocol(protocol)

    output_file_ext = args.output_file.split(".")[-1]

    file_exts = {
        "rs"  : "rustprinter",
        "txt" : "simpleprinter"
    }

    if args.output_format is None:
        output_file_ext = args.output_file.split(".")[-1]
        args.output_format = file_exts.get(output_file_ext, "simpleprinter")

    construct_output_formatter = {
                                  "simpleprinter" : output_formatters.simpleprinter.SimplePrinter(),
                                  "rustprinter" : output_formatters.rust_writer.RustWriter()
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
        print("Could not format protocol with specified formatter (%s)" % (args.output_format))

    # Output to file
    with open(args.output_file, "w+") as outputFile:
        outputFile.write(output_formatter.generate_output())

if __name__ == "__main__":
    main()
