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

from typing import Optional, List, Any, cast

import xml.etree.ElementTree as ET

import npt.parser
import npt.parser_rfc_txt
import npt.parser_rfc_xml
import npt.rfc
import npt.util

from npt.formatter            import Formatter
from npt.formatter_rust       import RustFormatter
from npt.formatter_simple     import SimpleFormatter
from npt.parser_asciidiagrams import AsciiDiagramsParser
from npt.protocol             import *

# Expression DFS

def dfs_expression(formatter: Formatter, expr: Expression) -> Any:
    if isinstance(expr, ArgumentExpression):
        return dfs_argumentexpression(formatter, expr)
    elif isinstance(expr, MethodInvocationExpression):
        return dfs_methodinvocationexpr(formatter, expr)
    elif isinstance(expr, FunctionInvocationExpression):
        return dfs_functioninvocationexpr(formatter, expr)
    elif isinstance(expr, FieldAccessExpression):
        return dfs_fieldaccessexpr(formatter, expr)
    elif isinstance(expr, ContextAccessExpression):
        return dfs_contextaccessexpr(formatter, expr)
    elif isinstance(expr, IfElseExpression):
        return dfs_ifelseexpr(formatter, expr)
    elif isinstance(expr, SelfExpression):
        return dfs_selfexpr(formatter, expr)
    elif isinstance(expr, ConstantExpression):
        return dfs_constantexpr(formatter, expr)

def dfs_argumentexpression(formatter: Formatter, expr: ArgumentExpression) -> Any:
    arg_value = dfs_expression(formatter, expr.arg_value)
    return formatter.format_argumentexpression(expr.arg_name, arg_value)

def dfs_methodinvocationexpr(formatter: Formatter, expr: MethodInvocationExpression) -> Any:
    target = dfs_expression(formatter, expr.target)
    arg_exprs = [dfs_expression(formatter, args_expr) for args_expr in expr.arg_exprs]
    return formatter.format_methodinvocationexpr(target, expr.method_name, arg_exprs)

def dfs_functioninvocationexpr(formatter: Formatter, expr: FunctionInvocationExpression) -> Any:
    args_exprs = [dfs_expression(formatter, arg_expr) for arg_expr in expr.arg_exprs]
    return formatter.format_functioninvocationexpr(expr.func.name, args_exprs)

def dfs_fieldaccessexpr(formatter: Formatter, expr: FieldAccessExpression) -> Any:
    target = dfs_expression(formatter, expr.target)
    return formatter.format_fieldaccessexpr(target, expr.field_name)

def dfs_contextaccessexpr(formatter: Formatter, expr: ContextAccessExpression) -> Any:
    return formatter.format_contextaccessexpr(expr.field_name)

def dfs_ifelseexpr(formatter: Formatter, expr: IfElseExpression) -> Any:
    condition = dfs_expression(formatter, expr.condition)
    if_true = dfs_expression(formatter, expr.if_true)
    if_false = dfs_expression(formatter, expr.if_false)
    return formatter.format_ifelseexpr(condition, if_true, if_false)

def dfs_selfexpr(formatter: Formatter, expr: SelfExpression) -> Any:
    return formatter.format_selfexpr()

def dfs_constantexpr(formatter: Formatter, expr: ConstantExpression) -> Any:
    return formatter.format_constantexpr(expr.constant_type, expr.constant_value)

# Protocol DFS

def dfs_struct(struct: Struct, type_names:List[str]):
    for field in struct.get_fields():
        dfs_protocoltype(field.field_type, type_names)
        
def dfs_array(array: Array, type_names:List[str]):
    dfs_protocoltype(array.element_type, type_names)
    dfs_protocoltype(array.parse_from, type_names)
    dfs_protocoltype(array.serialise_to, type_names)

def dfs_enum(enum: Enum, type_names:List[str]):
    for variant in enum.variants:
        dfs_protocoltype(variant, type_names)
    dfs_protocoltype(enum.parse_from, type_names)
    dfs_protocoltype(enum.serialise_to, type_names)

def dfs_function(function: Function, type_names:List[str]):
    for parameter in function.parameters:
        if not isinstance(parameter.param_type, TypeVariable) and isinstance(parameter.param_type, ConstructableType) and parameter.param_type.name not in type_names:
            dfs_protocoltype(parameter.param_type, type_names)
    if not isinstance(function.return_type, TypeVariable) and isinstance(function.return_type, ConstructableType) and function.return_type.name not in type_names:
        dfs_protocoltype(function.return_type, type_names)
        
def dfs_context(context: Context, type_names:List[str]):
    for field in context.get_fields():
        dfs_protocoltype(field.field_type, type_names)

def dfs_protocoltype(pt: Union[None, Function, ProtocolType], type_names:List[str]):
    if isinstance(pt, ConstructableType):
        type_names.append(pt.name)
    if isinstance(pt, Struct):
        dfs_struct(pt, type_names)
    elif isinstance(pt, Array):
        dfs_array(pt, type_names)
    elif isinstance(pt, Enum):
        dfs_enum(pt, type_names)
    elif isinstance(pt, Function):
        dfs_function(pt, type_names)
    elif isinstance(pt, Context):
        dfs_context(pt, type_names)
    elif pt is None:
        return

def dfs_protocol(protocol: Protocol):
    type_names : List[str] = []

    for pdu_name in protocol.get_pdu_names():
        dfs_protocoltype(protocol.get_pdu(pdu_name), type_names)

    type_names_dedupe = []

    for type_name in type_names:
        if type_name not in type_names_dedupe:
            type_names_dedupe.append(type_name)

    return type_names_dedupe



def parse_input_file( doc : npt.util.IETF_URI ) -> Optional[npt.rfc.RFC] :
    content = None
    doc_filepath = doc.get_filepath_in()
    if doc.extn == '.xml' and doc_filepath is not None:
        with open(doc_filepath , 'r') as infile :
            xml_tree = ET.fromstring(infile.read())
            content = npt.parser_rfc_xml.parse_rfc(xml_tree)
    elif doc.extn == '.txt' and doc_filepath is not None:
        with open(doc_filepath, 'r') as infile :
            content = npt.parser_rfc_txt.parse_rfc(infile.readlines())
    return content

def main():
    # Set up optional component parsers
    # TODO : Currently we have only one parser. When multiple parsers
    # for each sub-subcomponent are available, loop through them and initialise
    #dom_parser = { "asciidiagrams" : parsers.asciidiagrams.asciidiagrams_parser.AsciiDiagramsParser() }
    dom_parser = AsciiDiagramsParser()
    output_formatter = {
            "simple" : (".txt", SimpleFormatter()),
            "rust"   : (".rs" , RustFormatter())
            }

    opt = npt.util.parse_cmdline()
    for idx, doc in enumerate(opt.infiles):
        print(f"document [{idx}] --> {doc} --> {doc.get_filepath_in()}")
        parsed_content = parse_input_file( doc )
        if parsed_content is None :
            print(f"Error : Parsing {doc.get_filepath_in()} -> container = {doc}")
            continue

        protocol = dom_parser.build_protocol(  None , parsed_content )

        try:
            protocol.synthesise()
        except Exception as e:
            print(f"Error: could not synthesise protocol ({e})")
            continue
        
        type_names = dfs_protocol(protocol)

        for o_fmt in opt.output_fmt :
            out_extn, formatter = output_formatter[o_fmt]
            try:
                for type_name in type_names:
                    if protocol.has_type(type_name):
                        pt = protocol.get_type(type_name)
                        if isinstance(pt, BitString):
                            size_expr = dfs_expression(formatter, cast(Expression, pt.size))
                            formatter.format_bitstring(pt, size_expr)
                        elif isinstance(pt, Struct):
                            constraints = []
                            for constraint in pt.constraints:
                                expr = dfs_expression(formatter, constraint)
                                constraints.append(formatter.format_expression(expr))
                            formatter.format_struct(pt, constraints)
                        elif isinstance(pt, Array):
                            formatter.format_array(pt)
                        elif isinstance(pt, Enum):
                            formatter.format_enum(pt)
                        elif isinstance(pt, Context):
                            formatter.format_context(pt)
                    elif protocol.has_func(type_name):
                        formatter.format_function(protocol.get_func(type_name))
            except Exception as e:
                print(f"Error : File {doc.get_filepath_in()}: Could not format protocol with '{o_fmt}' formatter (format_{pt} failed)")
                continue
            try:
                formatter.format_protocol(protocol)
            except Exception as e:
                print(f"Error : File {doc.get_filepath_in()}: Could not format protocol with '{o_fmt}' formatter (format_protocol failed)")
                continue

            output_file = doc.gen_filepath_out( opt.root_dir, out_extn)
            assert output_file is not None
            output_file.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            with open(output_file, "w") as out_fp:
                out_fp.write(formatter.generate_output())
                print(f"Generated {o_fmt} output :\ninput doc = {doc.get_filepath_in()},\n--- output file = {output_file}")


if __name__ == "__main__":
    main()
