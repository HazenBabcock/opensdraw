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


class LEnv(object):
    """
    This keeps track of the current lexical environment.
    """
    def __init__(self, debug = False, add_builtins = True):
        self.debug = debug

        self.symbols = {}
        if add_builtins:
            for fn_name in functions.builtin_functions.keys():
                self.symbols[fn_name] = Symbol(fn_name)
                self.symbols[fn_name].setv(functions.builtin_functions[fn_name])

    def makeCopy(self):
        a_copy = LEnv(add_builtins = False)
        a_copy.debug = self.debug
        a_copy.symbols = self.symbols.copy()
        return a_copy

class Model(object):
    """
    This keeps track of the current "model", i.e. the 
    transformation matrix and the parts list.
    """
    def __init__(self, debug = False):
        self.m = numpy.identity(4)
        self.parts_list = []

    def makeCopy(self):
        a_copy = Model()
        a_copy.m = self.m.copy()
        a_copy.parts_list = self.parts_list
        return a_copy

class Symbol(object):
    """
    Box symbols so that they don't get copied when the environment gets copied.
    """
    def __init__(self, name):
        self.is_set = False
        self.name = name
        self.used = False
        self.value = None

    def getv(self, env):
        if not self.is_set:
            raise lce.VariableNotSetException(env, self.name)
        self.used = True
        return self.value

    def setv(self, value):
        self.is_set = True
        self.value = value


def dispatch(func, model, tree):
    """
    This handles function calls to both user-defined and built-in functions.
    """
    func.argCheck(tree)
    return func.call(model, tree)

def createLexicalEnv(lenv, tree):
    """
    Recursively walk the AST to determine the lexical environment by creating
    variables and functions, along with environment in which the function
    will be called. 

    Expressions and Symbols in the tree are then decorated with this lexical environments.
    """

    if isinstance(tree, lexerParser.LCadExpression):
        tree.lenv = lenv
        flist = tree.value

        # Empty list.
        if (len(flist) == 0):
            return

        # First element is a symbol, have to handle this specially in
        # case the symbol is "def".
        start = 0
        if isinstance(flist[0], lexerParser.LCadSymbol):
            start = 1
            flist[0].lenv = tree.lenv

            # First element is def.
            if (flist[0].value == "def"):
                start = len(flist)
            
                # def needs at least 3 arguments.
                if (len(flist)<3):
                    raise lce.NumberArgumentsException(tree, "2 or more", len(flist) - 1)

                # 4 arguments means this is a function definition.
                if (len(flist)==4):
                    tree.lenv.symbols[flist[1].value] = Symbol(flist[i].value)
                    tree.lenv.symbols[flist[1].value].setv(functions.UserFunction(tree.lenv.makeCopy(), tree))

                # Otherwise it defines one (or more variables).
                else:
                    # Must be divisible by 2.
                    if ((len(flist)%2)!=1):
                        raise lce.NumberArgumentsException(tree, "an even number of arguments", len(flist) - 1)

                    i = 1
                    while(i < len(flist)):
                        if not isinstance(flist[i], lexerParser.LCadSymbol):
                            raise lce.CannotSetException(tree, flist[i].simple_type_name)
                        flist[i].lenv = lenv
                        if isinstance(flist[i+1], lexerParser.LCadSymbol):
                            flist[i+1].lenv = lenv
                        else:
                            createLexicalEnv(tree.lenv.makeCopy(), flist[i+1])

                        # Warning for shadowing existing symbols.
                        if flist[i].value in tree.lenv.symbols:
                            print "Warning", flist[i].value, "overrides existing variable with the same name."
                        tree.lenv.symbols[flist[i].value] = Symbol(flist[i].value)
                        i += 2

        new_env = tree.lenv.makeCopy()
        for node in flist[start:]:
            createLexicalEnv(new_env, node)

    elif isinstance(tree, lexerParser.LCadSymbol):
        tree.lenv = lenv

    elif isinstance(tree, list):
        for node in tree:
            createLexicalEnv(lenv, node)

def interpret(model, tree):
    """
    Recursively walks the AST evaluating the nodes in the context 
    of the their lexical environment and the current context.

    Variables and functions have lexical scope.
    """

    # Fixed value terminal node.
    if isinstance(tree, lexerParser.LCadConstant):
        return tree.value

    # Symbol.
    elif isinstance(tree, lexerParser.LCadSymbol):
        try:
            return tree.lenv.symbols[tree.value].getv(tree)
        except KeyError:
            raise lce.SymbolNotDefined(tree, tree.value)

    # Expression.
    #
    # The first value in the expression is the name of the function.
    #
    elif isinstance(tree, lexerParser.LCadExpression):
        flist = tree.value

        if isinstance(flist[0], lexerParser.LCadExpression) or isinstance(flist[0], lexerParser.LCadSymbol):
            func = interpret(model, flist[0])
        else:
            raise lce.ExpressionException(tree)

        try:
            val = dispatch(func, model, tree)
        except Exception:
            #except lce.LCadException:
            #print "!Error in function", func.name, "at line", tree.start_line, ":"
            raise

        return val

    # List
    else:
        ret = None
        for node in tree:
            ret = interpret(model, node)
        return ret

def walk(tree, func):
    """
    Recursively walks the AST evaluating func on each of the nodes.
    """
    if isinstance(tree, list):
        for node in tree:
            walk(node, func)
    else:
        func(tree)
        if isinstance(tree, lexerParser.LCadExpression):
            for node in tree.value:
                walk(node, func)


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
