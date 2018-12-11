#!/usr/bin/env python3
import os
import sys
import time
base = os.path.dirname(os.path.realpath(__file__)) + "/"
suite = None
sys.path.insert(0, base)
from extended_diagrams import *
from ometa.runtime import ParseError


def read_file(filename):
    with open(filename) as fp:
        contents = fp.read()
    return contents


def test_suite(parse):
    i = 0
    success = 0
    fail = 0

    start_time = time.time()
    print("Running test suite")

    for filename in os.listdir("."):
        pos = filename.rfind(".")
        extension = filename[pos + 1:]
        name = filename[:pos]

        if extension == "txt":
            contents = read_file(filename)
            result = test(name, contents, parse)

            if result:
                success = success + 1
            else:
                if fail == 0:
                    print("----------------------------------------------------------------------")

                print("Failed test " + name)
                fail = fail + 1

            i = i + 1

    elapsed_time = time.time() - start_time

    print("----------------------------------------------------------------------")

    print("Ran " + str(i) + " tests in " + str(round(elapsed_time, 2)) + "s")
    print()

    if fail == 0:
        print("OK")
    else:
        print("Failed " + str(fail) + " tests")


def test(name, contents, parse):
    parser = get_parser_file({}, filename=base+"../../extended_diagrams.txt")

    try:
        data_actual = parse(parser, contents)
    except ParseError:
        return False

    try:
        json_data = open(name + ".json").read()
    except FileNotFoundError:
        return False

    data_expected = json.loads(json_data)

    if json.dumps(data_actual) == json.dumps(data_expected):
        return True

    else:
        return False


def run(filename, parse, check=False, packet=None):
    type_namespace = {}

    parser = get_parser_file(type_namespace, filename=base+"../../extended_diagrams.txt")
    contents = read_file(filename)
    data_actual = parse(parser, contents)

    if packet is None:
        data_json = json.dumps(data_actual, indent=4)
    else:
        data_json = json.dumps(packet(data_actual, type_namespace), indent=4)

    print(data_json)

    if check:
        name = filename[:filename.rfind(".")]
        json_data = open(name + ".json").read()
        data_expected = json.loads(json_data)

        if data_json == json.dumps(data_expected):
            print("Pass")
        else:
            print("Fail")


def main(parse, packet=None):
    if len(sys.argv) == 1:
        test_suite(parse)
    elif len(sys.argv) == 2:
        run(sys.argv[1], parse, packet=packet)
    elif len(sys.argv) == 3:
        check = str(sys.argv[2]).lower()

        if check == "true":
            run(sys.argv[1], parse, True, packet=packet)
        elif check == "false":
            run(sys.argv[1], parse, False, packet=packet)
        else:
            print("Error: Expecting second argument to be 'true' or 'false'")
            exit(2)
    else:
        print("Error: Too many arguments")
        exit(1)