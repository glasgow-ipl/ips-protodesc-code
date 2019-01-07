#!/usr/bin/env python3
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

import sys
import parsley
import string
import json
import os
import itertools
from extended_diagrams.__bindings__ import bindings


def get_parser_file(filename="extended_diagrams.txt"):
    with open(filename) as fp:
        grammar = fp.read()
    return get_parser(grammar)


def get_parser(grammar):
    return parsley.makeGrammar(grammar, {
        'punctuation': string.punctuation,
        'itertools': itertools,
        **bindings()
    })


def parse_file(filename):
    with open(filename) as fp:
        contents = fp.read()

    parser = get_parser_file(
        filename=os.path.dirname(os.path.realpath(__file__)) + "/extended_diagrams.txt"
    )
    return parser(contents).rfc()


def main():
    o = parse_file(sys.argv[1])
    print(json.dumps(o, indent=4))


if __name__ == "__main__":
    main()
