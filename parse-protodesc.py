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
import input_parsers
import formatters
import json
import input_parsers.inputparser
from protocoljson import *
import re

def load_input_parser(name):
    return importlib.import_module("." + name, "input_parsers")

def load_output_formatter(name):
    return importlib.import_module("." + name, "formatters")        

def filename_to_protocol_name(filename):
    split = re.split('[\./\\\]+', filename)
    return split[len(split)-2].title()
   
def main():
    parser = argparse.ArgumentParser(description='Parse a packet description into a specified output format')
    parser.add_argument('--input-format', type=str, required=True, help='Input format name')
    parser.add_argument('--input-file', type=str, required=True, help='Input filename')
    parser.add_argument('--output-format', type=str, required=True, help='Output format name')
    parser.add_argument('--output-file', type=str, required=True, help='Output filename')
    parser.add_argument('--json-output-file', type=str, required=False, help="Intermediate JSON representation output filename")
    args = parser.parse_args()

    # Import the specified input parser
    try:
        input_parser = importlib.import_module("." + args.input_format, "input_parsers.{}".format(args.input_format)).get_parser()
    except ModuleNotFoundError as e:
        print("Could not load input parser (%s)" % args.input_format)
    
    # Load the input file into a string
    with open(args.input_file, "r+") as inputFile:
        inputString = inputFile.read()
    
    # Parse input string using input parser
    try:
        protocol = input_parser.build_protocol(inputString, name=filename_to_protocol_name(args.input_file))
    except Exception as e:
        print("Could not parse input file (%s) with specified parser (%s)" % (args.input_file, args.input_format))
    
    # Write JSON protocol constructors to file
    try:
        with open(args.json_output_file, "w+") as outputFile:
            outputFile.write(input_parser.get_json_constructors())
    except:
        print("Could not JSON constructors to file (%s)" % args.json_output_file)
    
if __name__ == "__main__":
    main()
