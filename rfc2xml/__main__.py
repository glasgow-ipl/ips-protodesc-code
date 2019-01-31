from lxml import etree
import sys
from . import Rfc2Xml


def test():
    e1 = etree.Element(str("t"), {})
    e1.text = "This document defines the core of the QUIC transport protocol.  Accompanying documents describe QUIC's loss detection and congestion control "

    e2 = etree.Element(str("xref"), {"target": "QUIC-RECOVERY"})
    e2.tail = " and the use of TLS for key negotiation "
    e1.append(e2)

    e3 = etree.Element(str("xref"), {"target": "QUIC-TLS"})
    e3.tail = "."
    e1.append(e3)

    print(etree.tostring(e1, pretty_print=True).decode())

    sys.exit()


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

    result = Rfc2Xml.parse_file(filename).to_xml()

    if not suppress_result:
        print(etree.tostring(result, pretty_print=True).decode())


def usage():
    print("Usage: python -m rfc2xml <filename> [--suppress-result]", file=sys.stderr)


if __name__ == "__main__":
    main()
