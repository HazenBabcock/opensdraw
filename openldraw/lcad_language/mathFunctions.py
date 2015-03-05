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


lcad_functions = {}


class MathFunction(functions.LCadFunction):
    """
    Math functions.
    """
    def isNumber(self, value):
        num = interp.getv(value)
        if not isinstance(num, numbers.Number):
            raise lce.WrongTypeException("number", type(num))
        return num

    def isScalarOrVector(self, value):
        num = interp.getv(value)
        if not isinstance(num, numbers.Number) and not isinstance(num, numpy.ndarray):
            raise lce.WrongTypeException("number, numpy.ndarray", type(num))
        return num


# "Basic" math functions.

class BasicMathFunction(MathFunction):
    """
    Basic math functions, + - * /.
    """
    def argCheck(self, tree):
        if (len(tree.value) < 3):
            raise lce.NumberArgumentsException("2+", len(tree.value) - 1)

class Divide(BasicMathFunction):
    """
    **/** - Divide the first number, vector or matrix by one or more additional 
    numbers, vectors or matrices. Vectors and matrices are divided pointwise.

    Usage::

     (/ 4 2) ; 2

    """
    def call(self, model, tree):
        total = self.isScalarOrVector(interp.interpret(model, tree.value[1]))
        for node in tree.value[2:]:
            total = total/self.isScalarOrVector(interp.interpret(model, node))
        return total

lcad_functions["/"] = Divide("/")


class Minus(BasicMathFunction):
    """
    **-** - Subtract one or more numbers, vectors or matrices from the first 
    number, vector or matrix.

    Usage::

     (- 50 20 y) ; -30 - y
     (- 50)      ; -50

    """
    def argCheck(self, tree):
        if (len(tree.value) < 2):
            raise lce.NumberArgumentsException("1+", len(tree.value) - 1)

    def call(self, model, tree):
        if (len(tree.value) == 2):
            return -self.isScalarOrVector(interp.interpret(model, tree.value[1]))
        else:
            total = self.isScalarOrVector(interp.interpret(model, tree.value[1]))

            # If this a numpy array, make a copy to avoid destroying the original.
            if isinstance(total, numpy.ndarray):
                total = total.copy()

            for node in tree.value[2:]:
                total -= self.isScalarOrVector(interp.interpret(model, node))
            return total

lcad_functions["-"] = Minus("-")


class Modulo(BasicMathFunction):
    """
    **%** - Return remainder of the first number divided by the second number.

    Usage::

     (% 10 2) ; 0

    """
    def argCheck(self, tree):
        if (len(tree.value) != 3):
            raise lce.NumberArgumentsException("2", len(tree.value) - 1)

    def call(self, model, tree):
        n1 = self.isNumber(interp.interpret(model, tree.value[1]))
        n2 = self.isNumber(interp.interpret(model, tree.value[2]))
        return n1 % n2

lcad_functions["%"] = Modulo("%")


class Multiply(BasicMathFunction):
    """
    ***** - Multiply two or more numbers, vectors or matrices. If the first 
    number is a matrix, then multiplication will be done using matrix 
    multiplication, i.e. (* mat vec) will return a vector.

    Usage::

     (* 2 2 y) ; 4 * y

    """
    def call(self, model, tree):
        total = 1.0
        for node in tree.value[1:]:
            if isinstance(total, numpy.ndarray) and (len(total.shape) == 2):
                total = numpy.dot(total, self.isScalarOrVector(interp.interpret(model, node)))
            else:
                total = total * self.isScalarOrVector(interp.interpret(model, node))
        return total

lcad_functions["*"] = Multiply("*")


class Plus(BasicMathFunction):
    """
    **+** - Add together two or more numbers, vectors or matrices.

    Usage::

     (+ 10 20 y) ; 30 + y

    """
    def call(self, model, tree):
        total = 0
        for node in tree.value[1:]:
            total += self.isScalarOrVector(interp.interpret(model, node))
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

    def call(self, model, tree):
        args = tree.value[1:]

        i_args = []
        for arg in args:
            i_args.append(self.isNumber(interp.interpret(model, arg)))

        return self.py_func(*i_args)

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
