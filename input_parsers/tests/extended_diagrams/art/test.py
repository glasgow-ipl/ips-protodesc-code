#!/usr/bin/env python3
import os
import sys
base = os.path.dirname(os.path.realpath(__file__)) + "/../../../"
sys.path.insert(0, base)
sys.path.insert(0, base + "tests/extended_diagrams/")
from tests import *


def parse(parser, contents):
    return parser(contents).art()


if __name__ == "__main__":
    main(parse)