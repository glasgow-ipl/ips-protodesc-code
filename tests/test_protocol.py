# =================================================================================================
# Copyright (C) 2018-2019 University of Glasgow
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

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from npt.protocol import *


class TestProtocol(unittest.TestCase):
    # =============================================================================================
    # Test cases for traits:

    def test_traits_value(self):
        value_trait = Value()
        
        self.assertEqual(value_trait.name, "Value")
        self.assertEqual(len(value_trait.methods), 2)

        self.assertEqual(value_trait.methods[0].name, "get")
        self.assertEqual(len(value_trait.methods[0].parameters), 1)
        self.assertEqual(value_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(value_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(value_trait.methods[0].return_type, None)         
        
        self.assertEqual(value_trait.methods[1].name, "set")
        self.assertEqual(len(value_trait.methods[1].parameters), 2)
        self.assertEqual(value_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(value_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(value_trait.methods[1].parameters[1].param_name, "value")
        self.assertEqual(value_trait.methods[1].parameters[1].param_type, None)
        self.assertEqual(value_trait.methods[1].return_type, Nothing()) 


    def test_traits_sized(self):
        sized_trait = Sized()
        
        self.assertEqual(sized_trait.name, "Sized")
        self.assertEqual(len(sized_trait.methods), 1)

        self.assertEqual(sized_trait.methods[0].name, "size")
        self.assertEqual(len(sized_trait.methods[0].parameters), 1)
        self.assertEqual(sized_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(sized_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(sized_trait.methods[0].return_type, Number())         


    def test_traits_indexcollection(self):
        indexcollection_trait = IndexCollection()
        
        self.assertEqual(indexcollection_trait.name, "IndexCollection")
        self.assertEqual(len(indexcollection_trait.methods), 3)

        self.assertEqual(indexcollection_trait.methods[0].name, "get")
        self.assertEqual(len(indexcollection_trait.methods[0].parameters), 2)
        self.assertEqual(indexcollection_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(indexcollection_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(indexcollection_trait.methods[0].parameters[1].param_name, "index")
        self.assertEqual(indexcollection_trait.methods[0].parameters[1].param_type, Number())
        self.assertEqual(indexcollection_trait.methods[0].return_type, None)  

        self.assertEqual(indexcollection_trait.methods[1].name, "set")
        self.assertEqual(len(indexcollection_trait.methods[1].parameters), 3)
        self.assertEqual(indexcollection_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(indexcollection_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(indexcollection_trait.methods[1].parameters[1].param_name, "index")
        self.assertEqual(indexcollection_trait.methods[1].parameters[1].param_type, Number())
        self.assertEqual(indexcollection_trait.methods[1].parameters[2].param_name, "value")
        self.assertEqual(indexcollection_trait.methods[1].parameters[2].param_type, None)
        self.assertEqual(indexcollection_trait.methods[1].return_type, None)

        self.assertEqual(indexcollection_trait.methods[2].name, "length")
        self.assertEqual(len(indexcollection_trait.methods[2].parameters), 1)
        self.assertEqual(indexcollection_trait.methods[2].parameters[0].param_name, "self")
        self.assertEqual(indexcollection_trait.methods[2].parameters[0].param_type, None)
        self.assertEqual(indexcollection_trait.methods[2].return_type, Number())


    def test_traits_equality(self):
        equality_trait = Equality()
        
        self.assertEqual(equality_trait.name, "Equality")
        self.assertEqual(len(equality_trait.methods), 2)

        self.assertEqual(equality_trait.methods[0].name, "eq")
        self.assertEqual(len(equality_trait.methods[0].parameters), 2)
        self.assertEqual(equality_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(equality_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(equality_trait.methods[0].parameters[1].param_name, "other")
        self.assertEqual(equality_trait.methods[0].parameters[1].param_type, None)
        self.assertEqual(equality_trait.methods[0].return_type, Boolean())         

        self.assertEqual(equality_trait.methods[1].name, "ne")
        self.assertEqual(len(equality_trait.methods[1].parameters), 2)
        self.assertEqual(equality_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(equality_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(equality_trait.methods[1].parameters[1].param_name, "other")
        self.assertEqual(equality_trait.methods[1].parameters[1].param_type, None)
        self.assertEqual(equality_trait.methods[1].return_type, Boolean())  


    def test_traits_ordinal(self):
        ordinal_trait = Ordinal()
        
        self.assertEqual(ordinal_trait.name, "Ordinal")
        self.assertEqual(len(ordinal_trait.methods), 4)

        self.assertEqual(ordinal_trait.methods[0].name, "lt")
        self.assertEqual(len(ordinal_trait.methods[0].parameters), 2)
        self.assertEqual(ordinal_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(ordinal_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(ordinal_trait.methods[0].parameters[1].param_name, "other")
        self.assertEqual(ordinal_trait.methods[0].parameters[1].param_type, None)
        self.assertEqual(ordinal_trait.methods[0].return_type, Boolean())

        self.assertEqual(ordinal_trait.methods[1].name, "le")
        self.assertEqual(len(ordinal_trait.methods[1].parameters), 2)
        self.assertEqual(ordinal_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(ordinal_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(ordinal_trait.methods[1].parameters[1].param_name, "other")
        self.assertEqual(ordinal_trait.methods[1].parameters[1].param_type, None)
        self.assertEqual(ordinal_trait.methods[1].return_type, Boolean()) 
        
        self.assertEqual(ordinal_trait.methods[2].name, "gt")
        self.assertEqual(len(ordinal_trait.methods[2].parameters), 2)
        self.assertEqual(ordinal_trait.methods[2].parameters[0].param_name, "self")
        self.assertEqual(ordinal_trait.methods[2].parameters[0].param_type, None)
        self.assertEqual(ordinal_trait.methods[2].parameters[1].param_name, "other")
        self.assertEqual(ordinal_trait.methods[2].parameters[1].param_type, None)
        self.assertEqual(ordinal_trait.methods[2].return_type, Boolean())
        
        self.assertEqual(ordinal_trait.methods[3].name, "ge")
        self.assertEqual(len(ordinal_trait.methods[3].parameters), 2)
        self.assertEqual(ordinal_trait.methods[3].parameters[0].param_name, "self")
        self.assertEqual(ordinal_trait.methods[3].parameters[0].param_type, None)
        self.assertEqual(ordinal_trait.methods[3].parameters[1].param_name, "other")
        self.assertEqual(ordinal_trait.methods[3].parameters[1].param_type, None)
        self.assertEqual(ordinal_trait.methods[3].return_type, Boolean()) 


    def test_traits_booleanops(self):
        booleanops_trait = BooleanOps()
        
        self.assertEqual(booleanops_trait.name, "BooleanOps")
        self.assertEqual(len(booleanops_trait.methods), 3)

        self.assertEqual(booleanops_trait.methods[0].name, "and")
        self.assertEqual(len(booleanops_trait.methods[0].parameters), 2)
        self.assertEqual(booleanops_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(booleanops_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(booleanops_trait.methods[0].parameters[1].param_name, "other")
        self.assertEqual(booleanops_trait.methods[0].parameters[1].param_type, None)
        self.assertEqual(booleanops_trait.methods[0].return_type, Boolean())   

        self.assertEqual(booleanops_trait.methods[1].name, "or")
        self.assertEqual(len(booleanops_trait.methods[1].parameters), 2)
        self.assertEqual(booleanops_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(booleanops_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(booleanops_trait.methods[1].parameters[1].param_name, "other")
        self.assertEqual(booleanops_trait.methods[1].parameters[1].param_type, None)
        self.assertEqual(booleanops_trait.methods[1].return_type, Boolean())

        self.assertEqual(booleanops_trait.methods[2].name, "not")
        self.assertEqual(len(booleanops_trait.methods[2].parameters), 1)
        self.assertEqual(booleanops_trait.methods[2].parameters[0].param_name, "self")
        self.assertEqual(booleanops_trait.methods[2].parameters[0].param_type, None)
        self.assertEqual(booleanops_trait.methods[2].return_type, Boolean())


    def test_traits_arithmeticops(self):
        arithmeticops_trait = ArithmeticOps()
        
        self.assertEqual(arithmeticops_trait.name, "ArithmeticOps")
        self.assertEqual(len(arithmeticops_trait.methods), 6)

        self.assertEqual(arithmeticops_trait.methods[0].name, "plus")
        self.assertEqual(len(arithmeticops_trait.methods[0].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[0].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[0].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[0].return_type, None)

        self.assertEqual(arithmeticops_trait.methods[1].name, "minus")
        self.assertEqual(len(arithmeticops_trait.methods[1].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[1].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[1].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[1].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[1].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[1].return_type, None)

        self.assertEqual(arithmeticops_trait.methods[2].name, "multiply")
        self.assertEqual(len(arithmeticops_trait.methods[2].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[2].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[2].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[2].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[2].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[2].return_type, None)

        self.assertEqual(arithmeticops_trait.methods[3].name, "divide")
        self.assertEqual(len(arithmeticops_trait.methods[3].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[3].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[3].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[3].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[3].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[3].return_type, None)

        self.assertEqual(arithmeticops_trait.methods[4].name, "modulo")
        self.assertEqual(len(arithmeticops_trait.methods[4].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[4].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[4].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[4].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[4].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[4].return_type, None)

        self.assertEqual(arithmeticops_trait.methods[5].name, "pow")
        self.assertEqual(len(arithmeticops_trait.methods[5].parameters), 2)
        self.assertEqual(arithmeticops_trait.methods[5].parameters[0].param_name, "self")
        self.assertEqual(arithmeticops_trait.methods[5].parameters[0].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[5].parameters[1].param_name, "other")
        self.assertEqual(arithmeticops_trait.methods[5].parameters[1].param_type, None)
        self.assertEqual(arithmeticops_trait.methods[5].return_type, None)
        

    def test_traits_numberrepresentable(self):
        numberrepresentable_trait = NumberRepresentable()
        
        self.assertEqual(numberrepresentable_trait.name, "NumberRepresentable")
        self.assertEqual(len(numberrepresentable_trait.methods), 1)

        self.assertEqual(numberrepresentable_trait.methods[0].name, "to_number")
        self.assertEqual(len(numberrepresentable_trait.methods[0].parameters), 1)
        self.assertEqual(numberrepresentable_trait.methods[0].parameters[0].param_name, "self")
        self.assertEqual(numberrepresentable_trait.methods[0].parameters[0].param_type, None)
        self.assertEqual(numberrepresentable_trait.methods[0].return_type, Number())   

# =================================================================================================
if __name__ == "__main__":
    unittest.main()

# vim: set tw=0 ai:
