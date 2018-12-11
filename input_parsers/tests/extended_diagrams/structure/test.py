#!/usr/bin/env python3
import os
import sys
base = os.path.dirname(os.path.realpath(__file__)) + "/../../../"
sys.path.insert(0, base)
sys.path.insert(0, base + "tests/extended_diagrams/")
from tests import *
from shared import *


def parse(parser, contents):
    return parser(contents).structure()


def packet(output, type_namespace):
    fields, where, types = output

    new_struct("Packet", fields, where, type_namespace, [], [])
    new_enum("PDUs", [("Packet", None)], type_namespace)

    protocol = new_protocol("Protocol", type_namespace)

    return protocol


if __name__ == "__main__":
    main(parse, packet=packet)