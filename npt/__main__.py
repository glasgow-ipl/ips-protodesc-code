#!/usr/bin/env python3.7
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

import argparse
import lxml.etree # type: ignore
import os
import npt.parser
import npt.parser_rfc_txt
import npt.parser_rfc_xml
import npt.rfc
import npt.protocol
import npt.helpers

from npt.formatter            import Formatter
from npt.formatter_rust       import RustFormatter
from npt.formatter_simple     import SimpleFormatter
from npt.loader               import InputFile, load_file
from npt.parser_asciidiagrams import AsciiDiagramsParser
from pathlib                  import Path
from typing                   import Any, Optional, List, Tuple, Union, cast
from urllib.parse             import urlparse


class DTDResolver(lxml.etree.Resolver):
    def resolve(self, system_url, public_id, context):
        if urlparse(system_url).netloc:
            return self.resolve_filename(system_url, context)
        else:
            return self.resolve_filename(os.path.join("npt/", os.path.basename(system_url)), context)

# Protocol DFS

def dfs_struct(struct: npt.protocol.Struct, type_names:List[str]) -> None:
    for field in struct.get_fields():
        dfs_protocoltype(field.field_type, type_names)

def dfs_array(array: npt.protocol.Array, type_names:List[str]) -> None:
    dfs_protocoltype(array.element_type, type_names)
    #dfs_protocoltype(array.parse_from, type_names)
    #dfs_protocoltype(array.serialise_to, type_names)

def dfs_enum(enum: npt.protocol.Enum, type_names:List[str]) -> None:
    for variant in enum.variants:
        dfs_protocoltype(variant, type_names)
    #dfs_protocoltype(enum.parse_from, type_names)
    #dfs_protocoltype(enum.serialise_to, type_names)

def dfs_function(function: npt.protocol.Function, type_names:List[str]) -> None:
    for parameter in function.parameters:
        if not isinstance(parameter.param_type, npt.protocol.TypeVariable) and isinstance(parameter.param_type, npt.protocol.ConstructableType) and parameter.param_type.name not in type_names:
            dfs_protocoltype(parameter.param_type, type_names)
    if not isinstance(function.return_type, npt.protocol.TypeVariable) and isinstance(function.return_type, npt.protocol.ConstructableType) and function.return_type.name not in type_names:
        dfs_protocoltype(function.return_type, type_names)

def dfs_context(context: npt.protocol.Context, type_names:List[str]) -> None:
    for field in context.get_fields():
        dfs_protocoltype(field.field_type, type_names)

def dfs_protocoltype(pt: Union[None, npt.protocol.Function, npt.protocol.ProtocolType], type_names:List[str]) -> None:
    if isinstance(pt, npt.protocol.BitString):
        type_names.append(pt.name)
    elif isinstance(pt, npt.protocol.Struct):
        dfs_struct(pt, type_names)
        type_names.append(pt.name)
    elif isinstance(pt, npt.protocol.Array):
        dfs_array(pt, type_names)
        type_names.append(pt.name)
    elif isinstance(pt, npt.protocol.Enum):
        dfs_enum(pt, type_names)
        type_names.append(pt.name)
    elif isinstance(pt, npt.protocol.Function):
        dfs_function(pt, type_names)
        type_names.append(pt.name)
    elif isinstance(pt, npt.protocol.Context):
        dfs_context(pt, type_names)
        type_names.append(pt.name)
    elif pt is None:
        return

def dfs_protocol(protocol: npt.protocol.Protocol) -> List[str]:
    type_names : List[str] = []

    for pdu_name in protocol.get_pdu_names():
        dfs_protocoltype(protocol.get_pdu(pdu_name), type_names)

    dfs_protocoltype(protocol.get_context(), type_names)

    type_names_dedupe = []

    for type_name in type_names:
        if type_name not in type_names_dedupe:
            type_names_dedupe.append(type_name)

    return type_names_dedupe



# =================================================================================================================================


def main():
    ap = argparse.ArgumentParser(description=f"Parse IETF drafts and RFCs and generate protocol parsers")
    ap.add_argument("-d",  dest="outdir", help="directory in which to store output files", required=True)
    ap.add_argument("-f", dest="format", help="output format", required=True)
    ap.add_argument("document", help="document to process")
    args = ap.parse_args()

    # Load the output formatter:
    if args.format == "simple":
        formatter : Formatter = SimpleFormatter()
    elif args.format == "rust":
        formatter = RustFormatter()
    else:
        print(f"Error: cannot load output formatter {args.format}")
        return 1

    input_doc = load_file(args.document)
    if input_doc is None:
        print(f"Error: cannot load input document {args.document}")
        return 1

    if input_doc.fmt == ".xml":
        parser = lxml.etree.XMLParser(dtd_validation=False, load_dtd=True, attribute_defaults=True, 
                                      no_network=False, remove_comments=True, remove_pis=False, 
                                      remove_blank_text=False, resolve_entities=False, strip_cdata=True)
        parser.resolvers.add(DTDResolver())
        xml_tree = lxml.etree.fromstring(input_doc.data, parser=parser)
        content = npt.parser_rfc_xml.parse_rfc(xml_tree)
    elif input_doc.fmt == '.txt':
        content = npt.parser_rfc_txt.parse_rfc(input_doc.data.decode('UTF-8').splitlines())
    else:
        print(f"Error: cannot parse format {input_doc.fmt}")
        return 1

    dom_parser = AsciiDiagramsParser()
    protocol = dom_parser.build_protocol(None , content )
    protocol.synthesise()

    expr_traversal = npt.helpers.ExpressionTraversal(formatter)
    for type_name in dfs_protocol(protocol):
        if protocol.has_type(type_name):
            pt = protocol.get_type(type_name)
            if isinstance(pt, npt.protocol.BitString):
                size_expr = expr_traversal.dfs_expression(cast(npt.protocol.Expression, pt.size))
                formatter.format_bitstring(pt, size_expr)
            elif isinstance(pt, npt.protocol.Struct):
                constraints = []
                for constraint in pt.constraints:
                    expr = expr_traversal.dfs_expression(constraint)
                    constraints.append(expr)
                formatter.format_struct(pt, constraints)
            elif isinstance(pt, npt.protocol.Array):
                formatter.format_array(pt)
            elif isinstance(pt, npt.protocol.Enum):
                formatter.format_enum(pt)
            elif isinstance(pt, npt.protocol.Context):
                formatter.format_context(pt)
        elif protocol.has_func(type_name):
            formatter.format_function(protocol.get_func(type_name))

    formatter.format_protocol(protocol)

    output_dir = Path(args.outdir)
    if not output_dir.exists():
        output_dir.mkdir()

    for output_file, output_string in formatter.generate_output(args.document).items():
        output_filepath = output_dir / Path(output_file)
        output_filepath.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        with open(output_filepath, "w") as outf:
            outf.write(output_string)


if __name__ == "__main__":
    main()
