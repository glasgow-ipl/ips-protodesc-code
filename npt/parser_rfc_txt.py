# =================================================================================================
# Copyright (C) 2018-2020 University of Glasgow
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

import sys
import parsley
import string

import npt.rfc as rfc
import npt.parser_rfc_postprocess as domProcess

from typing import Dict, List

def depaginate(lines : List[str]) -> List[str]:
    depaginated_lines = []
    for i in range(len(lines)):
        line_no = i - (56 * int(i/56))
        if line_no not in [53, 54, 55, 0, 1, 2]:
            if line_no == 52 and i+8 < len(lines):
                indent_prev = len(lines[i-1]) - len(lines[i-1].lstrip())
                indent_next = len(lines[i+8]) - len(lines[i+8].lstrip())
                if (indent_prev == indent_next):
                    continue
            depaginated_lines.append(lines[i])
    return depaginated_lines

def trim_blank_lines(lines):
    trimmed_lines = []
    started = False
    for i in range(len(lines)):
        if not started and lines[i] == "\n":
            continue
        if i > 0 and lines[i] == "\n" and lines[i-1] == "\n":
            continue
        else:
            trimmed_lines.append(lines[i])
            started = True
    return trimmed_lines

def structure_subsections(sections):
    section_depths : Dict[int, List[rfc.Section]] = {}
    for depth, section in sections:
        if depth not in section_depths:
            section_depths[depth] = []
        section_depths[depth].append(section)
        if depth > 1:
            sections = section_depths[depth-1][-1]
            if sections.sections is not None:
                sections.sections.append(section)
    return section_depths[1]

def get_doc_series(text):
    return "Internet-Draft"

def get_ipr_code(text):
    return "trust200902"

def infer_toc(alpha:str, num:str):
    return 3

def generate_parser(grammarFilename):
    with open(grammarFilename) as grammarFile:
        return parsley.makeGrammar(grammarFile.read(),
                                   {
                                     "ascii_uppercase"       : string.ascii_uppercase,
                                     "ascii_lowercase"       : string.ascii_lowercase,
                                     "ascii_letters"         : string.ascii_letters,
                                     "punctuation"           : string.punctuation,
                                     "rfc"                   : rfc,
                                     "get_doc_series"        : get_doc_series,
                                     "get_ipr_code"          : get_ipr_code,
                                     "structure_subsections" : structure_subsections,
                                     "infer_toc"             : infer_toc,
                                   })

def parse_rfc(rfcTxt: List[str]):
    rfcTxt = depaginate(rfcTxt)
    rfcTxt = trim_blank_lines(rfcTxt)
    parser = generate_parser("npt/grammar_rfc.txt")
    rfc = parser("".join(rfcTxt)).rfc()
    rfc = domProcess.text_to_dl(rfc, {'tab': ''.join( parser('   ').tab())})
    return rfc

if __name__ == "__main__":
    with open(sys.argv[1], "r") as rfcFile:
        rfcTxt = rfcFile.readlines()
        print(parse_rfc(rfcTxt))
