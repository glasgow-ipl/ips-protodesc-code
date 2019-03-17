import sys
from . import ExtendedDiagrams
from output_formatters.json import Json


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

    extended_diagrams = ExtendedDiagrams()
    extended_diagrams.load_dom(filename)
    extended_diagrams.traverse_dom()
    protocol = extended_diagrams.setup_protocol()

    if not suppress_result:
        output_formatter = Json()
        output_formatter.format_protocol(protocol)
        print(output_formatter.generate_output())


def usage():
    print("Usage: python -m input_parsers.extended_diagrams [--suppress-result]", file=sys.stderr)


if __name__ == "__main__":
    main()
