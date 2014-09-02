#!/usr/bin/env python
#
# The Exceptions thrown by lcad.
#
# Hazen 07/14
#

class LCadException(Exception):
    def __init__(self, message):
        message = "!Error, " + message
        Exception.__init__(self, message)

class BooleanException(LCadException):
    def __init__(self):
        LCadException.__init__(self, "value must be 't' or 'nil'.")

class CannotOverrideTNil(LCadException):
    def __init__(self):
        LCadException.__init__(self, "overriding builtin symbols (t, nil) is not allowed.")

class CannotSetException(LCadException):
    def __init__(self, item_type):
        LCadException.__init__(self, "type '" + item_type + "' is not settable.")

class ExpressionException(LCadException):
    def __init__(self):
        LCadException.__init__(self, "the first element of the list must be a function.")

class IllegalArgumentTypeException(LCadException):
    def __init__(self):
        LCadException.__init__(self, "arguments in function definition must be symbols.")

class IncorrectTypeException(LCadException):
    def __init__(self, expected, got):
        LCadException.__init__(self, "wrong argument type, got '" + got + "' expected '" + expected + "'")

class KeywordException(LCadException):
    def __init__(self, item):
        LCadException.__init__(self, str(item) + " is not a keyword.")

class NotAFunctionException(LCadException):
    def __init__(self):
        LCadException.__init__(self, "not a function.")

class NumberArgumentsException(LCadException):
    def __init__(self, expected, got):
        LCadException.__init__(self, "wrong number of standard arguments, got " + str(got) + " expected " + str(expected))

class OutOfRangeException(LCadException):
    def __init__(self, high, val):
        LCadException.__init__(self, "value out of range, got " + str(val) + ", range is 0 - " + str(high))

class SymbolNotDefined(LCadException):
    def __init__(self, variable_name):
        LCadException.__init__(self, "symbol '" + variable_name + "' not defined.")

class VariableNotSetException(LCadException):
    def __init__(self, variable_name):
        LCadException.__init__(self, "variable '" + variable_name + "' used before initialization.")

class WrongTypeException(LCadException):
    def __init__(self, expected, got):
        LCadException.__init__(self, "wrong type, got '" + str(got.__name__) + "' expected '" + str(expected) + "'.")


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
