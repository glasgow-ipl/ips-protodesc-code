# =================================================================================================
# Copyright (C) 2018-19 University of Glasgow
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
import importlib
import json
import re    

from protocol import *
from protocoltypes import *

# Input parsers
import input_parsers.inputparser
import input_parsers.packetlang.packetlang

# Output formatters
import output_formatters.outputformatter
import output_formatters.simpleprinter

# Protocol DFS

def dfs_struct(struct: Struct, type_names:List[str]):
    for field in struct.fields:
        dfs_protocoltype(field.field_type, type_names)
        if field.transform is not None:
            dfs_protocoltype(field.transform.into_type, type_names)
            dfs_protocoltype(field.transform.using, type_names)
            
def dfs_array(array: Array, type_names:List[str]):
    dfs_protocoltype(array.element_type)
    
def dfs_enum(enum: Enum, type_names:List[str]):
    for variant in enum.variants:
        dfs_protocoltype(variant)
        
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
 
def filename_to_protocol_name(filename):
    split = re.split('[\./\\\]+', filename)
    return split[len(split)-2].title()

def main():
    ######################################################################################
    # Argument parsing
    ######################################################################################
    argparser = argparse.ArgumentParser(description='Parse a packet description into a specified output format')
    argparser.add_argument('--input-format', type=str, required=True, help='Input format name')
    argparser.add_argument('--input-file', type=str, required=True, help='Input filename')
    argparser.add_argument('--output-format', type=str, required=True, help='Output format name')
    argparser.add_argument('--output-file', type=str, required=True, help='Output filename')
    args = argparser.parse_args()

    ######################################################################################
    # Input parsing
    ######################################################################################
    construct_input_parser = {"packetlang" : input_parsers.packetlang.packetlang.PacketLangParser()}
    input_parser = construct_input_parser[args.input_format]
    
    # Load the input file into a string
    with open(args.input_file, "r+") as inputFile:
        inputString = inputFile.read()
    
    # Parse input string using input parser
    try:
        protocol = input_parser.build_protocol(inputString, name=filename_to_protocol_name(args.input_file))
    except Exception as e:
        raise e
        print("Could not parse input file (%s) with specified parser (%s)" % (args.input_file, args.input_format))

    ######################################################################################
    # Depth-first search processing
    ######################################################################################
    type_names = dfs_protocol(protocol)
    print(type_names)

#    ######################################################################################
#    # Output formatting
#    ######################################################################################
#    construct_output_formatter = {"simpleprinter" : output_formatters.simpleprinter.SimplePrinter()}
#    output_formatter = construct_output_formatter[args.output_format]
#    
#    # Format the protocol using output formatter
#    try:
#        #output_formatter.format_protocol(protocol)
#    except:
#        print("Could not format protocol with specified formatter (%s)" % (args.output_format))
#
#    #output_formatter.generate_output()
#
#    # Output to file
#    with open(args.output_file, "w+") as outputFile:
#        #outputFile.write(output_formatter.generate_output())

if __name__ == "__main__":
    main()
