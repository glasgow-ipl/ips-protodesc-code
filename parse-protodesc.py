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

import argparse
import importlib
import json
import re    

# Input parsers
import input_parsers.inputparser
import input_parsers.packetlang.packetlang

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
        print("Could not parse input file (%s) with specified parser (%s)" % (args.input_file, args.input_format))

    ######################################################################################
    # Output formatting
    ######################################################################################
    #TODO

if __name__ == "__main__":
    main()
