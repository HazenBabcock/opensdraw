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


class Env(object):
    """
    This class keeps track of what is currently in scope as well
    as the current transformation matrix.
    """

    def __init__(self, debug = False):
        self.debug = debug
        self.fn_line = 0
        self.fn_name = None
        self.functions = {}
        self.special_forms = functions.special_forms
        self.parts_list = []
        self.variables = {}

    def make_copy(self):
        a_copy = Env()
        a_copy.debug = self.debug
        a_copy.fn_name = self.fn_name
        a_copy.functions = self.functions.copy()
        a_copy.special_forms = self.special_forms
        a_copy.parts_list = self.parts_list
        a_copy.variables = self.variables.copy()
        return a_copy

class Matrix(object):
    """
    This class keeps track of the current transformation matrix.
    """
    def __init(self, debug = False):
        self.m = numpy.identity(4)

    def make_copy(self):
        a_copy.m = self.m.copy()

class Variable(object):
    """
    Box variables so that they don't get copied when the environment gets copied.
    """
    def __init__(self, name):
        self.name = name
        self.set = False
        self.used = False
        self.value = None

    def getv(self, env = None):
        if not self.set:
            raise VariableNotSetException(env, self.name)
        self.used = True
        return self.value

    def setv(self, value):
        self.set = True
        self.value = value


def dispatch(fn, env, tree):
    """
    This handles function calls to both user-defined and built-in functions.
    """
    
    args = []
    if (len(tree.value) > 1):
        args = tree.value[1:]

    #
    # For builtin functions the function signature information is stored
    # as part of the function.
    #
    # These functions handle argument interpretation on their own so that we
    # can do things like loops and branching.
    #
    if hasattr(fn, "builtin"):
        args_number = fn.args_number
        if fn.args_gt:
            if (len(args) < args_number):
                raise lce.NumberArgumentsException(env,
                                                   str(args_number) + " or more",
                                                   len(args))
        else:
            if (len(args) != args_number):
                raise lce.NumberArgumentsException(env,
                                                   str(args_number), 
                                                   len(args))
        return fn(env, args)

    #
    # User defined functions get "pre-interpreted" arguments.
    #
    else:
        pass

def symbolTable(env, tree):
    """
    Recursively walk the AST to determine the lexical environment creating
    variables and functions, along with environment in which the function
    will be called.
    """
    
    if hasattr(tree, "start_line"):
        env.fn_line = tree.start_line

    if isinstance(tree, lexerParser.LCadExpression):

        flist = tree.value
        if isinstance(flist[0], lexerParser.LCadExpression):
            pass

        elif isinstance(flist[0], lexerParser.LCadSymbol):

            # Is something defined?
            if (flist[0].value == "def"):
                env.fn_name = "def"

                # def needs at least 3 arguments.
                if (len(flist)<3):
                    raise lce.NumberArgumentsException(env, "2 or more", len(flist) - 1)

                # 4 arguments means this is a function definition.
                if (len(flist)==4):
                    env.functions[flist[1].value] = functions.UserFunction(env, tree)

                # Must be divisible by 2.
                elif ((len(flist)%2)!=1):
                    raise lce.NumberArgumentsException(env, "an even number of arguments", len(flist) - 1)

                # Otherwise it is a variable.
                else:
                    i = 1
                    while(i < len(flist)):
                        if not isinstance(flist[i], lexerParser.LCadSymbol):
                            raise lce.CannotSetException(env, flist[i].simple_type_name)
                        symbolTable(env, flist[0])
                        env.variables[flist[i].value] = Variable(flist[i])
                        i += 2

            # If not it must be a function that is already defined.
            else:
                env.fn_name = flist[0].value
                if (len(flist) > 1):
                    for node in flist[1:]:
                        new_env = env.make_copy()
                        symbolTable(new_env, node)

        # The first element of list has to be a symbol or another expression.
        else:
            raise lce.ExpressionException(env)

    elif isinstance(tree, list):
        for node in tree:
            symbolTable(env, node)

def interpret(matrix, env, tree):
    """
    Recursively walks the AST evaluating the nodes in the context 
    of the current environment and transform matrix.

    Variables and functions have lexical scope.
    """

    if env.debug:
        print ""
        print tree
        
    if hasattr(tree, "start_line"):
        env.fn_line = tree.start_line

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
            return env.variables[tree.value].value
        except KeyError:
            raise lce.VariableNotDefined(env, tree.value)

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
            fname = interpret(matrix, env, flist[0])

        elif isinstance(flist[0], lexerParser.LCadSymbol):
            fname = flist[0].value

        else:
            raise lce.ExpressionException(env)

        try:
            return dispatch(env.functions[fname], matrix, env, tree)
        except KeyError:
            raise lce.NoSuchFunctionException(env, fname)

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
        ast = parser.parse(lexer.lex(fp.read()))
        symbolTable(env, ast)

    print ""
    print "Functions", env.functions.keys()
    print "Variables", env.variables.keys()
    #print "Total parts", len(env.parts_list)

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
