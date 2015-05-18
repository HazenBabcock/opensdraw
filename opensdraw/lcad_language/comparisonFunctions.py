#!/usr/bin/env python
"""
.. module:: comparisonFunctions
   :synopsis: <, >, =, etc.

.. moduleauthor:: Hazen Babcock

"""

import numbers
import operator

import functions
import interpreter as interp
import lcadExceptions as lce

lcad_functions = {}


# Comparison functions.

class ComparisonFunction(functions.LCadFunction):
    """
    Comparison functions, =, >, <, >=, <=, !=.
    """
    def __init__(self, name):
        functions.LCadFunction.__init__(self, name)
        self.setSignature([[basestring, numbers.Number], 
                           ["optional", [basestring, numbers.Number]]])

    def compare(self, model, cmp_func, val0, *vals):
        for val in vals:
            if not cmp_func(val0, val):
                return interp.lcad_nil
        return interp.lcad_t


class Equal(ComparisonFunction):
    """
    **=**

    Usage::

     (= 1 1)     ; t
     (= 1 2)     ; nil
     (= 2 2 2 2) ; t
     (= "a" "a") ; t
    """
    def call(self, model, *vals):
        return self.compare(model, operator.eq, vals[0], *vals[1:])

lcad_functions["="] = Equal("=")


class Gt(ComparisonFunction):
    """
    **>**

    Usage::

     (> 2 1) ; t
    """
    def call(self, model, *vals):
        return self.compare(model, operator.gt, vals[0], *vals[1:])

lcad_functions[">"] = Gt(">")


class Lt(ComparisonFunction):
    """
    **<**

    Usage::

     (< 2 1) ; nil
    """
    def call(self, model, *vals):
        return self.compare(model, operator.lt, vals[0], *vals[1:])

lcad_functions["<"] = Lt("<")


class Ge(ComparisonFunction):
    """
    **>=**

    Usage::

     (>= 2 1) ; t
    """
    def call(self, model, *vals):
        return self.compare(model, operator.ge, vals[0], *vals[1:])

lcad_functions[">="] = Ge(">=")


class Le(ComparisonFunction):
    """
    **<=**

    Usage::

     (<= 2 1) ; nil
    """
    def call(self, model, *vals):
        return self.compare(model, operator.le, vals[0], *vals[1:])    

lcad_functions["<="] = Le("<=")


class Ne(ComparisonFunction):
    """
    **!=**

    Usage::

     (!= 2 1) ; t
    """
    def call(self, model, *vals):
        return self.compare(model, operator.ne, vals[0], *vals[1:])    

lcad_functions["!="] = Ne("!=")


#
# The MIT License
#
# Copyright (c) 2015 Hazen Babcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
