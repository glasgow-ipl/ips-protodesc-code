#!/usr/bin/env python3
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
