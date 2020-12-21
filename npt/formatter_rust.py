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

import itertools

from string  import ascii_letters
from pathlib import Path

from npt.protocol  import *
from npt.formatter import Formatter
from npt.helpers   import ExpressionTraversal

import re

def camelcase(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title().replace(" ", "")

class RustFormatter(Formatter):
    """
    Class to generate Rust code from parsed ASCII diagrams
    """

    output: List[str]
    expr_traversal: ExpressionTraversal

    #add necessary imports at the start of every generated rust file
    def __init__(self):
        self.output = []
        self.structs = {}
        self.struct_field_signatures = {}
        self.expr_traversal = ExpressionTraversal(self)

    def generate_output(self, output_name: str) -> Dict[Path, str]:
        manifest = f"[package]\nname = \"{output_name.replace('-', '_')}\"\nversion = \"0.1.0\"\n\n[dependencies]\nnom = \"5.1.2\"\n\n"
        self.output = ["extern crate nom;\n\nuse nom::bits::complete::take;\nuse nom::IResult;\nuse nom::Err;\nuse nom::error::ErrorKind;\n"] + self.output
        output_files = {Path(f"src/lib.rs"): "".join(self.output),
                        Path(f"Cargo.toml"): manifest}
        return output_files

    def format_argumentexpression(self, arg_name: str, arg_value: Any) -> Any:
        return arg_value

    def format_methodinvocationexpr(self, target: Any, method_name: str, arg_exprs: List[Any]) -> Any:
        if method_name == "pow":
            return f"({target}.pow({arg_exprs[0]}))"
        elif method_name == "multiply":
            return f"({target}*{arg_exprs[0]})"
        elif method_name == "minus":
            return f"({target}-{arg_exprs[0]})"
        elif method_name == "ge":
            return f"({target} >= {arg_exprs[0]})"
        elif method_name == "gt":
            return f"({target} > {arg_exprs[0]})"
        elif method_name == "eq":
            return f"({target} == {arg_exprs[0]})"
        elif method_name == "plus":
            return f"({target} + {arg_exprs[0]})"
        elif method_name == "and":
            return f"({target} && {arg_exprs[0]}"
        if method_name == "to_number":
            return f"{target}"
        return ""

    def format_functioninvocationexpr(self, func_name: str, args_exprs: List[Any]) -> Any:
        return ""

    def format_fieldaccessexpr(self, target: Any, field_name: str) -> Any:
        if target == "self":
            return f"self({field_name})"
        else:
            return None

    def format_contextaccessexpr(self, field_name: str) -> Any:
        return f"context.{field_name} as usize"

    def format_ifelseexpr(self, condition: Any, if_true: Any, if_false: Any) -> Any:
        return ""

    def format_selfexpr(self) -> Any:
        return "self"

    def format_constantexpr(self, constant_type: ProtocolType, constant_value: Any) -> Any:
        if constant_type == Number():
            return int(constant_value)
        else:
            return str(constant_value)

    def format_expression(self, expr:Expression):
        return ""

    def format_bitstring(self, bitstring:BitString, size: Any):
        required_vars = []
        if type(size) is not str:
            data_type = f"u{self.assign_int_size(size)}"
        else:
            data_type = "Vec<u8>"
            self_vars = re.findall(r"self\(([\w]*)\)", size)
            size = re.sub(r"self\(([\w]*)\)", r"\1", size)
            self.struct_field_signatures[f"parse_{bitstring.name.lower()}"] = self_vars
            required_vars = [f"{var_name}: usize" for var_name in self_vars]
        assert bitstring.name not in self.output
        self.output.append(f"\n// Structure and parser for {bitstring.name} (bitstring type)\n")
        self.output.append("\n#[derive(Debug, PartialEq, Eq)]\n")
        self.output.extend(["pub struct ", camelcase(bitstring.name), "(pub %s);\n" % (data_type)])
        if len(required_vars) > 0:
            self.output.append("\npub fn parse_{fname}<'a>(input: (&'a [u8], usize), context: &'a mut Context, {required_vars_signatures}) -> (IResult<(&'a [u8], usize), {typename}>, &'a mut Context) {{\n".format(fname=bitstring.name.lower(), typename=camelcase(bitstring.name), required_vars_signatures=", ".join(required_vars)))
        else:
            self.output.append("\npub fn parse_{fname}<'a>(input: (&'a [u8], usize), context: &'a mut Context) -> (IResult<(&'a [u8], usize), {typename}>, &'a mut Context) {{\n".format(fname=bitstring.name.lower(), typename=camelcase(bitstring.name)))
        if data_type == "Vec<u8>":
            if size[0] == "(" and size[-1] == ")":
                size = size[1:-1]
            self.output.append(f"    let mut {bitstring.name.lower()}_size = {size};\n")
            self.output.append(f"    let mut {bitstring.name.lower()} = {camelcase(bitstring.name)}(Vec::new());\n")
            self.output.append(f"    let mut input = input;\n")
            self.output.append(f"    while {bitstring.name.lower()}_size > 0 {{\n")
            self.output.append(f"        let bits_consumed = if {bitstring.name.lower()}_size > 8 {{ 8 }} else {{ {bitstring.name.lower()}_size }};\n")
            self.output.append(f"        match take(bits_consumed as usize)(input) {{\n")
            self.output.append(f"            IResult::Ok((i, o)) => {{\n")
            self.output.append(f"                input = i;\n")
            self.output.append(f"                {bitstring.name.lower()}.0.push(o);\n")
            self.output.append(f"            }},\n")
            self.output.append(f"            IResult::Err(e) => return (IResult::Err(e), context)\n")
            self.output.append(f"        }}\n")
            self.output.append(f"        {bitstring.name.lower()}_size -= bits_consumed;\n")
            self.output.append(f"    }}\n")
            self.output.append(f"    (IResult::Ok((input, {bitstring.name.lower()})), context)\n")
        else:
            self.output.append(f"    (take({size} as usize)(input).map(|(i, o)| (i, {camelcase(bitstring.name)}(o))), context)\n")
        self.output.append("}\n")


    def assign_int_size(self, bitstring_size: Optional[int]):
        if bitstring_size is None:
            return 8
        elif bitstring_size <= 8:
            return 8
        elif bitstring_size <= 16:
            return 16
        elif bitstring_size <= 32:
            return 32
        elif bitstring_size <= 64:
            return 64
        else:
            return 128

    def format_struct_field(self, index: int, struct_name: str, field_names: List[str], parser_func_names: List[str], constraints, presence_constraints):
        args = []
        if parser_func_names[index] in self.struct_field_signatures:
            args = [f"{arg}.0 as usize" for arg in self.struct_field_signatures[parser_func_names[index]]]
        indentation = "    "*(index+1) + "    "*(index)
        generated_code = []

        # process constraints: find those that can be expressed here
        handled_constraints = []
        unhandled_constraints = []
        for constraint in constraints:
            if all(field in field_names[:index+1] for field in constraint[1]):
                constraint_expr = constraint[0]
                for field in constraint[1]:
                    if field == field_names[index]:
                        constraint_expr = constraint_expr.replace(field, "o.0")
                handled_constraints.append((constraint_expr, constraint[0]))
            else:
                unhandled_constraints.append(constraint)


        if presence_constraints == None or presence_constraints[index] != "True":
            presence_constraints[index] = re.sub(r"self\(([\w]*)\)", r"\1.0", presence_constraints[index])
            if presence_constraints[index][0] == "(" and presence_constraints[index][-1] == ")":
                presence_constraints[index] = presence_constraints[index][1:-1]
            presence_constraint = f"if {presence_constraints[index]} {{ Some("
            presence_else = "}) } else { None ";
        else:
            presence_constraint = ""
            presence_else = ""
        constraint_code = "\n" + "\n".join([f"            // check constraint: {constraint[1]}\n            if !({constraint[0]}) {{\n                return (IResult::Err(Err::Error((input, ErrorKind::NonEmpty))), c);\n            }};" for constraint in handled_constraints]) + "\n"
        if len(args) > 0:
            generated_code.append(f"    let {field_names[index]} = {presence_constraint}match {parser_func_names[index]}(input, context, {', '.join(args)}) {{\n")
        else:
            generated_code.append(f"    let {field_names[index]} = {presence_constraint}match {parser_func_names[index]}(input, context) {{\n")
        if len(handled_constraints) > 0:
            generated_code.append(f"        (IResult::Ok((i, o)), c) => {{{constraint_code}            input = i;\n")
            generated_code.append(f"            context = c;\n")
            generated_code.append(f"            o\n")
            generated_code.append(f"        }},\n")
        else:
            generated_code.append("        (IResult::Ok((i, o)), c) => {\n");
            generated_code.append("            input = i;\n");
            generated_code.append("            context = c;\n");
            generated_code.append("            o\n")
            generated_code.append("        }\n")
        generated_code.append("        (IResult::Err(e), c) => return (IResult::Err(e), c),\n")
        generated_code.append(f"    {presence_else}}};\n\n")
        if index+1 < len(field_names):
            generated_code = generated_code + self.format_struct_field(index+1, struct_name, field_names, parser_func_names, unhandled_constraints, presence_constraints)
        return generated_code

    def format_struct(self, struct: Struct, constraints: List[str]):
        assert struct.name not in self.output
        # process constraints - pick out field names and build structure
        processed_constraints = []
        for constraint in constraints:
            processed_constraints.append((re.sub(r"self\(([\w]*)\)", r"\1", constraint), re.findall(r"self\(([\w]*)\)", constraint)))
        self.output.append(f"\n// Structure and parser for {struct.name}\n")
        self.output.append("\n#[derive(Debug")
        for trait in struct.traits:
            if trait == "Equality":
                self.output.append(", PartialEq, Eq")
            elif trait == "Ordinal":
                self.output.append(", Ord")
        self.output.append(")]\n")
        self.output.extend(["pub struct ", camelcase(struct.name), " {\n"])
        parser_functions = []
        field_names = []
        presence_constraints = []
        for field in struct.get_fields():
            type_name = field.field_type.name if isinstance(field.field_type, ConstructableType) else "nothing"
            if not(isinstance(field.is_present, ConstantExpression) and type(field.is_present.constant_type) is Boolean and field.is_present.constant_value is True):
                self.output.append("    pub %s: Option<%s>,\n" % (field.field_name, camelcase(type_name)))
            else:
                self.output.append("    pub %s: %s,\n" % (field.field_name, camelcase(type_name)))
            presence_constraints.append(self.expr_traversal.dfs_expression(field.is_present))
            parser_functions.append("parse_{name}".format(name=type_name.lower()))
            field_names.append(f"{field.field_name}")
        self.output.append("}\n")
        self.output.append("\npub fn parse_{fname}<'a>(mut input: (&'a [u8], usize), mut context: &'a mut Context) -> (IResult<(&'a [u8], usize), {typename}>, &'a mut Context) {{\n".format(fname=struct.name.replace(" ", "_").replace("-", "_").lower(),typename=camelcase(struct.name)))
        self.output += self.format_struct_field(0, camelcase(struct.name), field_names, parser_functions, processed_constraints, presence_constraints)
        self.output.append(f"    (IResult::Ok((\n")
        self.output.append(f"        input,\n")
        self.output.append(f"        {camelcase(struct.name)} {{\n")
        for field_name in field_names:
            self.output.append(f"            {field_name},\n")
        self.output.append(f"        }},\n")
        self.output.append(f"    )),\n")
        self.output.append(f"    context)\n")
        self.output.append("}\n")
        self.struct_field_signatures = {}

    def format_array(self, array: Array):
        assert array.name not in self.output
        fname = array.name.replace(" ", "_").replace("-", "_").lower()
        element_type_name = array.element_type.name if isinstance(array.element_type, ConstructableType) else "nothing"
        self.output.append(f"\n// Structure and parser for {array.name}\n")
        self.output.append("\n#[derive(Debug)]")
        self.output.append("\npub struct %s(pub Vec<%s>);\n" % (camelcase(array.name), camelcase(element_type_name)))
        if (array.length is not None):
            self.output.append(f"\npub fn parse_{fname}<'a>(mut input: (&'a [u8], usize), mut context: &'a mut Context) -> (IResult<(&'a [u8], usize), {camelcase(array.name)}>, &'a mut Context) {{")
            self.output.append(f"\n    let mut {fname} = {camelcase(array.name)}(Vec::new());")
            self.output.append(f"\n    for _n in 1..={self.expr_traversal.dfs_expression(array.length)} {{")
            self.output.append(f"\n        match parse_{element_type_name.replace(' ', '_').replace('-', '_').lower()}(input, context) {{")
            self.output.append(f"\n            (IResult::Ok((i, o)), c) => {{ input = i; context = c; {fname}.0.push(o); }},")
            self.output.append(f"\n            (IResult::Err(e), c) => return (IResult::Err(e), c),")
            self.output.append(f"\n        }}")
            self.output.append(f"\n    }}")
            self.output.append(f"\n    (IResult::Ok((input, {fname})), context)")
        elif array.size is not None:
            size_expr = self.expr_traversal.dfs_expression(array.size)
            self_vars = re.findall(r"self\(([\w]*)\)", size_expr)
            size_expr = re.sub(r"self\(([\w]*)\)", r"\1", size_expr)[1:-1]
            self.struct_field_signatures[f"parse_{fname}"] = self_vars
            required_vars = [f"{var_name}: usize" for var_name in self_vars]
            required_vars_signatures=", ".join(required_vars)
            self.output.append(f"\npub fn parse_{fname}<'a>(mut input: (&'a [u8], usize), mut context: &'a mut Context, {required_vars_signatures}) -> (IResult<(&'a [u8], usize), {camelcase(array.name)}>, &'a mut Context) {{")
            self.output.append(f"\n    let mut {fname} = {camelcase(array.name)}(Vec::new());")
            self.output.append(f"\n    let mut bits_read = 0;")
            self.output.append(f"\n    let bits_to_read = {size_expr};")
            self.output.append(f"\n    while bits_to_read > bits_read {{")
            self.output.append(f"\n        match parse_{element_type_name.replace(' ', '_').replace('-', '_').lower()}(input, context) {{")
            self.output.append(f"\n            (IResult::Ok((i, o)), c) => {{")
            self.output.append(f"\n                bits_read += (input.1 - i.1) + (input.0.len() - i.0.len())*8;")
            self.output.append(f"\n                input = i;")
            self.output.append(f"\n                context = c;")
            self.output.append(f"\n                {fname}.0.push(o);")
            self.output.append(f"\n            }},")
            self.output.append(f"\n            (IResult::Err(_e), c) => {{")
            self.output.append(f"\n                context = c;")
            self.output.append(f"\n                break")
            self.output.append(f"\n            }}")
            self.output.append(f"\n        }}")
            self.output.append(f"\n    }}")
            self.output.append(f"\n")
            self.output.append(f"\n    if bits_read != bits_to_read {{")
            self.output.append(f"\n        (IResult::Err(Err::Error((input, ErrorKind::NonEmpty))), context)")
            self.output.append(f"\n    }} else {{")
            self.output.append(f"\n        (IResult::Ok((input, {fname})), context)")
            self.output.append(f"\n    }}")
        self.output.append(f"\n}}\n")

    def format_enum(self, enum:Enum):
        func_name = enum.name.replace(" ", "_").replace("-", "_").lower()
        self.output.append(f"\n// Parse enum `{enum.name}`\n")
        self.output.append("\n#[derive(Debug)]")
        self.output.append(f"\npub enum {camelcase(enum.name)} {{\n")
        self.output.append("\n".join([f"    {camelcase(variant.name)}({camelcase(variant.name)})," for variant in enum.variants if isinstance(variant, ConstructableType)]))
        self.output.append("\n}\n\n")
        parse_funcs = []
        type_names = []
        for variant in enum.variants:
            if isinstance(variant, ConstructableType):
                type_names.append(camelcase(variant.name))
                parse_func_name = variant.name.replace(" ", "_").replace("-", "_").lower()
                parse_funcs.append(f"parse_{parse_func_name}")
        self.output.append(f"pub fn parse_{func_name}<'a>(input: (&'a [u8], usize), mut context: &'a mut Context) -> (IResult<(&'a [u8], usize), {camelcase(enum.name)}>, &'a mut Context) {{\n")
        self.output += self.format_enum_variants(camelcase(enum.name), 0, parse_funcs, type_names)
        self.output.append("    (IResult::Err(Err::Error((input, ErrorKind::NonEmpty))), context)\n")
        self.output.append("}\n")

    def format_function(self, function:Function):
        assert function.name not in self.output
        self.output.append("\nfn {function_name}(".format(function_name=function.name))
        for param in function.parameters:
            #TODO: handle parameters which aren't just structs
            assert not isinstance(param.param_type, TypeVariable)
            param_type_name = param.param_type.name if isinstance(param.param_type, ConstructableType) else "nothing"
            self.output.append("{param_name}: {param_type}".format(param_name=param.param_name, param_type=param_type_name))
            if param not in function.parameters[-1:]:
                self.output.append(", ")
            else:
                self.output.append(") ")
        if not isinstance(function.return_type, Nothing) and function.return_type is not None:
            return_type_name = function.return_type.name if isinstance(function.return_type, ConstructableType) else "nothing"
            self.output.append("-> {return_type}".format(return_type=camelcase(return_type_name)))
        self.output.append(" {\n    //function body required\n    unimplemented!();\n}\n\n")

    def format_context(self, context: Context):
        context_output = "\n// Context\n\npub struct Context {\n"
        fields_output = []
        for field in context.get_fields():
            if isinstance(field.field_type, BitString):
                size = self.assign_int_size(self.expr_traversal.dfs_expression(field.field_type.size))
                fields_output.append(f"    pub {field.field_name}: {size},")
            if isinstance(field.field_type, Number):
                fields_output.append(f"    pub {field.field_name}: u32,")
        context_output += ",\n".join(fields_output) + "\n}\n"
        self.output = [context_output] + self.output

    def format_pdu_variants(self, container_name: str, index: int, parser_func_names: List[str], type_names: List[str]):
        generated_code = []
        generated_code.append(f"    match {parser_func_names[index]}(input, context) {{\n")
        generated_code.append(f"        (IResult::Ok((([], 0), o)), c) => return (IResult::Ok(((&[], 0), {container_name}::{type_names[index]}(o))), c),\n")
        generated_code.append(f"        (IResult::Ok(_), c) | (IResult::Err(_), c) => {{ context = c; }}\n    }}\n\n")

        if index+1 < len(parser_func_names):
            generated_code = generated_code + self.format_pdu_variants(container_name, index+1, parser_func_names, type_names)
        return generated_code

    def format_enum_variants(self, container_name: str, index: int, parser_func_names: List[str], type_names: List[str]):
        generated_code = []
        generated_code.append(f"    match {parser_func_names[index]}(input, context) {{\n")
        generated_code.append(f"        (IResult::Ok((i, o)), c) => return (IResult::Ok((i, {container_name}::{type_names[index]}(o))), c),\n")
        generated_code.append(f"        (IResult::Err(_), c) =>  {{ context = c; }}\n    }}\n\n")

        if index+1 < len(parser_func_names):
            generated_code = generated_code + self.format_enum_variants(container_name, index+1, parser_func_names, type_names)
        return generated_code

    def format_protocol(self, protocol: Protocol):
        self.output.append("\n// Parse incoming PDUs\n")
        self.output.append("\n#[derive(Debug)]")
        self.output.append("\npub enum PDU {\n")
        self.output.append("\n".join([f"    {camelcase(pdu_name)}({camelcase(pdu_name)})," for pdu_name in protocol.get_pdu_names()]))
        self.output.append("\n}\n\n")
        parse_funcs = []
        type_names = []
        for pdu_name in protocol.get_pdu_names():
            type_names.append(camelcase(pdu_name))
            parse_funcs.append(f"parse_{pdu_name.replace(' ', '_').replace('-', '_').lower()}")
        self.output.append("pub fn parse_pdu<'a>(input: (&'a [u8], usize), mut context: &'a mut Context) -> (IResult<(&'a [u8], usize), PDU>, &'a mut Context) {\n")
        self.output += self.format_pdu_variants("PDU", 0, parse_funcs, type_names)
        self.output.append("    (IResult::Err(Err::Error((input, ErrorKind::NonEmpty))), context)")
        self.output.append("\n}")
