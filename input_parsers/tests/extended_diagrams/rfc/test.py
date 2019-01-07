#!/usr/bin/env python3
import os
import sys
base = os.path.dirname(os.path.realpath(__file__)) + "/../../../"
sys.path.insert(0, base)
sys.path.insert(0, base + "tests/extended_diagrams/")
from tests import *
from shared import *


def parse(parser, contents):
    return parser(contents).rfc()


def packet(output, type_namespace):
    return output


if __name__ == "__main__":
    main(parse, packet=packet)