#!/usr/bin/env python
#
# The language interpreter for lcad.
#
# Hazen 07/14
#

import copy
import numpy

import functions

# Variables are objects so that they don't get copied.
class Variable(object):

    def __init__(self, value):
        self.value = value

# This class keeps track of what is currently in scope as well
# as the current transformation matrix.
class Env(object):

    def __init__(self):
        self.m = numpy.identity(4)
        self.functions = functions.fn
        self.modules = {}
        self.variables = {}

    def make_copy(self):
        return copy.copy(self)

def interpret(env, tree):

    # Fixed value terminal node.
    if (type(tree) in [type(lexerParser.LCadFloat),
                       type(lexerParser.LCadInteger),
                       type(lexerParser.LCadString)]):
        return tree.value

    # Variable or single argument function
    elif (type(tree) == type(lexerParser.LCadSymbol)):
        try:
            return env.variables[tree.value].value
        except ValueError:
            pass

        return eval(tree.value)

        # Evaluate function arguments first.
        fn_args = []
        for node in enumerate(ast[1:]):
            fn_args.append(interpret(env, node))

            # Check if it is a lcad function.
            if node[0] in functions.fn:
                
        

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
