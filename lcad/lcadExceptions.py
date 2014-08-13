#!/usr/bin/env python
#
# The Exceptions thrown by lcad.
#
# Hazen 07/14
#

class LCadException(Exception):
    def __init__(self, expr, message):
        message = "Error at line " + str(expr.start_line) + ", " + message
        Exception.__init__(self, message)

class CannotSetException(LCadException):
    def __init__(self, expr, item_type):
        LCadException.__init__(self, expr, "type '" + item_type + "' is not settable.")

class ExpressionException(LCadException):
    def __init__(self, expr):
        LCadException.__init__(self, expr, "the first element of the list must be a function.")

class IncorrectTypeException(LCadException):
    def __init__(self, expr, expected, got):
        LCadException.__init__(self, expr, "wrong argument type, got '" + got + "' expected '" + expected + "'")

class NoSuchFunctionException(LCadException):
    def __init__(self, expr, unknown_function):
        LCadException.__init__(self, expr, "unknown function '" + unknown_function + "'")

class NumberArgumentsException(LCadException):
    def __init__(self, expr, expected, got):
        LCadException.__init__(self, expr, "wrong number of arguments, got " + str(got) + " expected " + str(expected))

class SymbolNotDefined(LCadException):
    def __init__(self, expr, variable_name):
        LCadException.__init__(self, expr, "symbol '" + variable_name + "' not defined.")

class VariableNotSetException(LCadException):
    def __init__(self, expr, variable_name):
        LCadException.__init__(self, expr, "variable '" + variable_name + "' used before initialization.")

#
# The MIT License
#
# Copyright (c) 2014 Hazen Babcock
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
