#!/usr/bin/env python
#
# The language interpreter for lcad.
#
# Hazen 07/14
#

import copy
import numpy

import lcadExceptions as lce
import functions
import lexerParser

class Variable(object):
    """
    Variables are objects so that they don't get copied.
    """
    def __init__(self, value):
        self.value = value

class Env(object):
    """
    This class keeps track of what is currently in scope as well
    as the current transformation matrix.
    """

    def __init__(self, debug = False):
        self.debug = debug
        self.functions = functions.fn
        self.m = numpy.identity(4)
        self.parts_list = []
        self.variables = {}

    def make_copy(self):
        a_copy = Env()
        a_copy.debug = self.debug
        a_copy.functions = self.functions.copy()
        a_copy.m = self.m
        a_copy.parts_list = self.parts_list
        a_copy.variables = self.variables.copy()
        return a_copy

def interpret(env, tree):
    """
    The interpreter recursively walks the AST evaluating the nodes
    in the context of the current environment.

    Variables and functions have lexical scope.
    """

    if env.debug:
        print ""
        print tree

    # Fixed value terminal node.
    if isinstance(tree, lexerParser.LCadConstant):
        if env.debug:
            print tree.value
        return tree.value

    # Symbol.
    elif isinstance(tree, lexerParser.LCadSymbol):
        if env.debug:
            print tree.value
        try:
            return env.variables[tree.value]
        except KeyError:
            raise lce.VariableNotDefined(tree.value, tree.start_line)

#        # Variable?
#        try:
#            return env.variables[tree.value].value
#        except ValueError:
#            pass

        # User defined function?

    # Expression.
    #
    # The first value in the expression is the name of the function.
    #
    elif isinstance(tree, lexerParser.LCadExpression):
        if env.debug:
            print tree.value
        flist = tree.value

        # Another expression?
        if isinstance(flist[0], lexerParser.LCadExpression):
            fname = interpret(env, flist[0])

        elif isinstance(flist[0], lexerParser.LCadSymbol):
            fname = flist[0].value

        else:
            raise lce.ExpressionException(tree.start_line)

        try:
            return env.functions[fname](env, tree)
        except KeyError:
            raise lce.NoSuchFunctionException(fname, tree.start_line)

    # List
    else:
        ret = None
        for node in tree:
            ret = interpret(env, node)
        return ret


# For testing purposes.
if (__name__ == '__main__'):
    import sys
    from lexerParser import lexer, parser

    if (len(sys.argv) != 2):
        print "usage: <file to interpret>"
        exit()

    env = Env(debug = False)
    with open(sys.argv[1]) as fp:
        interpret(env, parser.parse(lexer.lex(fp.read())))

    print "Functions", env.functions.keys()
    print "Variables", env.variables.keys()
    print "Total parts", len(env.parts_list)

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
