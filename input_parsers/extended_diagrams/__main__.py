import sys
from . import ExtendedDiagrams, Parse
from output_formatters.json import Json
from protocol import *

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

    extended_diagrams = ExtendedDiagrams(filename)

    print(extended_diagrams.dom.to_xml_string(pretty=True))

    extended_diagrams.traverse_dom()

    print(extended_diagrams.dom.to_xml_string(pretty=True))

    protocol = extended_diagrams.protocol_setup()

    if not suppress_result:
        output_formatter = Json()
        output_formatter.format_protocol(protocol)
        print(output_formatter.generate_output())


def usage():
    print("Usage: python -m input_parsers.extended_diagrams [--suppress-result]", file=sys.stderr)


if __name__ == "__main__":
    main()
