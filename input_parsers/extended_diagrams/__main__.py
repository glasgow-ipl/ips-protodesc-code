import json
import sys
from . import ExtendedDiagrams


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    filename = sys.argv[1]
    suppress_result = False

    for arg in sys.argv[2:]:
        if arg == "--suppress-result":
            suppress_result = True
        else:
            print("Unknown argument", arg)
            usage()
            sys.exit(2)

    result = ExtendedDiagrams.parse_file(filename)

    if not suppress_result:
        print(json.dumps(result, indent=4))


def usage():
    print("Usage: python -m input_parsers.extended_diagrams [--suppress-result]", file=sys.stderr)


if __name__ == "__main__":
    main()
