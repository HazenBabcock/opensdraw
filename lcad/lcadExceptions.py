#!/usr/bin/env python
#
# The Exceptions thrown by lcad.
#
# Hazen 07/14
#

class CannotSetException(Exception):
    def __init__(self, env, item_type):
        message = "In '" + env.fn_name + "' at line " + str(env.fn_line)
        message += " type '" + item_type + "' is not settable."
        Exception.__init__(self, message)

class ExpressionException(Exception):
    def __init__(self, env):
        message = "Expected a function as the first element of the list at line " + str(env.fn_line)
        if env.fn_name is not None:
            message += " in function '" + env.fn_name + "'"
        Exception.__init__(self, message)

class IncorrectTypeException(Exception):
    def __init__(self, env, expected, got):
        message = "Wrong arguments type for '" + env.fn_name + "' at line " + str(env.fn_line)
        message += ", got '" + got + "' expected '" + expected + "'"
        Exception.__init__(self, message)

class NoSuchFunctionException(Exception):
    def __init__(self, env, unknown_function):
        message = "No such function '" + unknown_function + "' at line " + str(env.fn_line)
        if env.fn_name is not None:
            message += " in function '" + env.fn_name + "'"
        Exception.__init__(self, message)

class NumberArgumentsException(Exception):
    def __init__(self, env, expected, got):
        message = "Wrong number of arguments to '" + env.fn_name + "' at line " + str(env.fn_line)
        message += ", got " + str(got) + " expected " + str(expected)
        Exception.__init__(self, message)

class VariableNotDefined(Exception):
    def __init__(self, env, variable_name):
        if env.fn_name is not None:
            message = "Variable '" + variable_name + "' not defined in function '" + env.fn_name + "' "
            message += "at line " + str(env.fn_line)
        else:
            message = "Variable '" + variable_name + "' not defined at line " + str(env.fn_line)
        Exception.__init__(self, message)

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
