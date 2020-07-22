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

from npt.formatter     import Formatter
from npt.protocol     import *

# Expression DFS

class ExpressionTraversal:
    formatter: Formatter

    def __init__(self, formatter: Formatter):
        self.formatter = formatter
    
    def dfs_expression(self, expr: Optional[Expression]) -> Any:
        if expr is None:
            return None
        if isinstance(expr, ArgumentExpression):
            return self.dfs_argumentexpression(expr)
        elif isinstance(expr, MethodInvocationExpression):
            return self.dfs_methodinvocationexpr(expr)
        elif isinstance(expr, FunctionInvocationExpression):
            return self.dfs_functioninvocationexpr(expr)
        elif isinstance(expr, FieldAccessExpression):
            return self.dfs_fieldaccessexpr(expr)
        elif isinstance(expr, ContextAccessExpression):
            return self.dfs_contextaccessexpr(expr)
        elif isinstance(expr, IfElseExpression):
            return self.dfs_ifelseexpr(expr)
        elif isinstance(expr, SelfExpression):
            return self.dfs_selfexpr(expr)
        elif isinstance(expr, ConstantExpression):
            return self.dfs_constantexpr(expr)
    
    def dfs_argumentexpression(self, expr: ArgumentExpression) -> Any:
        arg_value = self.dfs_expression(expr.arg_value)
        return self.formatter.format_argumentexpression(expr.arg_name, arg_value)
    
    def dfs_methodinvocationexpr(self, expr: MethodInvocationExpression) -> Any:
        target = self.dfs_expression(expr.target)
        arg_exprs = [self.dfs_expression(args_expr) for args_expr in expr.arg_exprs]
        return self.formatter.format_methodinvocationexpr(target, expr.method_name, arg_exprs)
    
    def dfs_functioninvocationexpr(self, expr: FunctionInvocationExpression) -> Any:
        args_exprs = [self.dfs_expression(arg_expr) for arg_expr in expr.arg_exprs]
        return self.formatter.format_functioninvocationexpr(expr.func.name, args_exprs)
    
    def dfs_fieldaccessexpr(self, expr: FieldAccessExpression) -> Any:
        target = self.dfs_expression(expr.target)
        return self.formatter.format_fieldaccessexpr(target, expr.field_name)
    
    def dfs_contextaccessexpr(self, expr: ContextAccessExpression) -> Any:
        return self.formatter.format_contextaccessexpr(expr.field_name)
    
    def dfs_ifelseexpr(self, expr: IfElseExpression) -> Any:
        condition = self.dfs_expression(expr.condition)
        if_true = self.dfs_expression(expr.if_true)
        if_false = self.dfs_expression(expr.if_false)
        return self.formatter.format_ifelseexpr(condition, if_true, if_false)
    
    def dfs_selfexpr(self,expr: SelfExpression) -> Any:
        return self.formatter.format_selfexpr()
    
    def dfs_constantexpr(self, expr: ConstantExpression) -> Any:
        return self.formatter.format_constantexpr(expr.constant_type, expr.constant_value)
