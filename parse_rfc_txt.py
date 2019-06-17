import sys
import parsley
import string
import rfc

def depaginate(lines):
    depaginated_lines = []
    for i in range(len(lines)):
        line_no = i - (56 * int(i/56))
        if line_no not in [53, 54, 55, 0, 1, 2, 3]:
            if line_no == 52 and i+8 < len(lines):
                indent_prev = len(lines[i-1]) - len(lines[i-1].lstrip())
                indent_next = len(lines[i+8]) - len(lines[i+8].lstrip())
                if (indent_prev == indent_next):
                    continue
            depaginated_lines.append(lines[i])
    return depaginated_lines

def trim_blank_lines(lines):
    trimmed_lines = []
    for i in range(len(lines)):
        if i > 0 and lines[i] == "\n" and lines[i-1] == "\n":
            continue
        else:
            trimmed_lines.append(lines[i])
    return trimmed_lines

def get_doc_series(text):
    return "Internet-Draft"

def get_ipr_code(text):
    return "trust200902"

def generate_parser(grammarFilename):
    with open(grammarFilename) as grammarFile:
        return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase" : string.ascii_uppercase,
                                     "ascii_lowercase" : string.ascii_lowercase,
                                     "ascii_letters"   : string.ascii_letters,
                                     "punctuation"     : string.punctuation,
                                     "rfc"             : rfc,
                                     "get_doc_series"  : get_doc_series,
                                     "get_ipr_code"    : get_ipr_code,
                                   })

def parse_rfc(rfcTxt):
    rfcTxt = depaginate(rfcTxt)
    rfcTxt = trim_blank_lines(rfcTxt)
    parser = generate_parser("rfc-grammar.txt")
    rfc = parser("".join(rfcTxt)).rfc()
    return rfc

if __name__ == "__main__":
    with open(sys.argv[1], "r") as rfcFile:
        rfcTxt = rfcFile.readlines()
        print(parse_rfc(rfcTxt))