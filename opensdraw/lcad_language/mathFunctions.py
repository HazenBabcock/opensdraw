#!/usr/bin/env python
"""
.. module:: mathFunctions
   :synopsis: Math functions such as addition, subtraction, etc. 

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import functions
import interpreter as interp
import lcadExceptions as lce
import lcadTypes


lcad_functions = {}


class MathFunction(functions.LCadFunction):
    """
    Math functions.
    """
    pass


class Absolute(MathFunction):
    """
    **abs** - Return the absolute value of a number.

    Usage::

     (abs 2)  ; 2
     (abs -2) ; 2

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number]]),

    def call(self, model, tree):
        return abs(self.getArg(model, tree, 0))

lcad_functions["abs"] = Absolute("abs")


class Divide(MathFunction):
    """
    **/** - Divide the first number, vector or matrix by one or more additional 
    numbers, vectors or matrices. Vectors and matrices are divided pointwise.

    Usage::

     (/ 4 2) ; 2

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number, numpy.ndarray],
                           [numbers.Number, numpy.ndarray],
                           ["optional", [numbers.Number, numpy.ndarray]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        total = args[0]
        for arg in args[1:]:
            total = total/arg
        return total

lcad_functions["/"] = Divide("/")


class Minus(MathFunction):
    """
    **-** - Subtract one or more numbers, vectors or matrices from the first 
    number, vector or matrix.

    Usage::

     (- 50 20 y) ; -30 - y
     (- 50)      ; -50

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number, numpy.ndarray],
                           ["optional", [numbers.Number, numpy.ndarray]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        if (len(args) == 1):
            return -args[0]
        else:
            total = args[0]

            # If this a numpy array, make a copy to avoid destroying the original.
            if isinstance(total, numpy.ndarray):
                total = total.copy()

            for arg in args[1:]:
                total -= arg
            return total

lcad_functions["-"] = Minus("-")


class Modulo(MathFunction):
    """
    **%** - Return remainder of the first number divided by the second number.

    Usage::

     (% 10 2) ; 0

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number], [numbers.Number]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        return args[0] % args[1]

lcad_functions["%"] = Modulo("%")


class Multiply(MathFunction):
    """
    ***** - Multiply two or more numbers, vectors or matrices. If the first 
    number is a matrix, then multiplication will be done using matrix 
    multiplication, i.e. (* mat vec) will return a vector and (* mat mat)
    will return a matrix.

    Usage::

     (* 2 2 y) ; 4 * y

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number, numpy.ndarray],
                           [numbers.Number, numpy.ndarray],
                           ["optional", [numbers.Number, numpy.ndarray]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        total = 1.0
        for arg in args:
            if isinstance(total, lcadTypes.LCadMatrix):
                total = numpy.dot(total, arg)
                if (len(total.shape) == 2):
                    total = total.view(lcadTypes.LCadMatrix)
                else:
                    total = total.view(lcadTypes.LCadVector)
            else:
                total = total * arg
        return total

lcad_functions["*"] = Multiply("*")


class Plus(MathFunction):
    """
    **+** - Add together two or more numbers, vectors or matrices.

    Usage::

     (+ 10 20 y) ; 30 + y

    """
    def __init__(self, name):
        MathFunction.__init__(self, name)
        self.setSignature([[numbers.Number, numpy.ndarray],
                           [numbers.Number, numpy.ndarray],
                           ["optional", [numbers.Number, numpy.ndarray]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        total = 0
        for arg in args:
            total += arg
        return total

lcad_functions["+"] = Plus("+")


# "Advanced" math functions.

class AdvMathFunction(MathFunction):
    """
    The functions in Python's math module.
    """
    def __init__(self, name, py_func):
        MathFunction.__init__(self, name)
        self.py_func = py_func
        self.setSignature([[numbers.Number], ["optional", [numbers.Number]]])

    def call(self, model, tree):
        return self.py_func(*self.getArgs(model, tree))

for name in dir(math):
    obj = getattr(math, name)
    if callable(obj):
        lcad_functions[name] = AdvMathFunction(name, obj)



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
