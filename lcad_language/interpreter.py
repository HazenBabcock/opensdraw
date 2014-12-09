#!/usr/bin/env python
"""
.. module:: interpreter
   :synopsis: The interpreter for the lcad language.

.. moduleauthor:: Hazen Babcock

"""

import copy
import math
import numpy

import lcadExceptions as lce
import functions
import lexerParser

builtin_symbols = {}

class LEnv(object):
    """
    This keeps track of the current lexical environment.
    """
    def __init__(self, parent = None, add_built_ins = False):
        self.parent = parent
        self.symbols = {}

        if add_built_ins:
            self.addBuiltIns()

    def addBuiltIns(self):
        """
        This should only be called on the root lexical environment.
        """
        # Symbols.
        for sym_name in builtin_symbols.keys():
            self.symbols[sym_name] = builtin_symbols[sym_name]

        # Functions.
        for fn_name in functions.builtin_functions.keys():
            self.symbols[fn_name] = Symbol(fn_name)
            self.symbols[fn_name].setv(functions.builtin_functions[fn_name])

class List(object):
    """
    Array class.
    """
    def __init__(self, py_list):
        self.py_list = []
        for elt in py_list:
            if isinstance(elt, Symbol):
                self.py_list.append(elt)
            else:
                tmp = Symbol("list_object")
                tmp.setv(elt)
                self.py_list.append(tmp)

    def __str__(self):
        if (self.size() < 10):
            return "(" + " ".join(map(lambda(x): str(x), self.py_list)) + ")"
        else:
            tmp = "(" + " ".join(map(lambda(x): str(x), self.py_list[:3]))
            tmp += " .. " + " ".join(map(lambda(x): str(x), self.py_list[-3:])) + ")"
            return tmp

    def getl(self):
        return self.py_list

    def getv(self, index):
        return self.py_list[index]

    def size(self):
        return len(self.py_list)

class Model(object):
    """
    This keeps track of the current "model", i.e. the 
    current transformation matrix and the parts list.
    """
    def __init__(self, debug = False):
        self.m = numpy.identity(4)
        self.parts_list = []

    def getParts(self):
        return self.parts_list

    def makeCopy(self):
        a_copy = Model()
        a_copy.m = self.m.copy()
        a_copy.parts_list = self.parts_list
        return a_copy

class Symbol(object):
    """
    Symbol class.
    """
    def __init__(self, name):
        self.is_set = False
        self.name = name
        self.used = False
        self.value = None

    def __str__(self):
        #return self.name + " " + str(id(self))
        return str(self.value)

    def getv(self):
        if not self.is_set:
            raise lce.VariableNotSetException(self.name)
        self.used = True
        return self.value

    def setv(self, value):
        self.is_set = True
        self.value = value
        
# t and nil are objects so that we can do comparisons using 'is' and
# be gauranteed that there is only one truth and one false.

class LObject(object):
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)

lcad_t = LObject("t")
builtin_symbols["t"] = Symbol("t")
builtin_symbols["t"].setv(lcad_t)

lcad_nil = LObject("nil")
builtin_symbols["nil"] = Symbol("nil")
builtin_symbols["nil"].setv(lcad_nil)

builtin_symbols["e"] = Symbol("e")
builtin_symbols["e"].setv(math.e)

builtin_symbols["pi"] = Symbol("pi")
builtin_symbols["pi"].setv(math.pi)

def checkOverride(lenv, symbol_name, warn_only = False):
    """
    Check if symbol_name overrides a builtin or user defined symbol.
    """

    # Error for shadowing built in symbols.
    if (symbol_name in builtin_symbols):
        raise lce.CannotOverrideTNil()

    # Error for shadowing symbols at the same level of scope.
    if symbol_name in lenv.symbols:
        if not warn_only:
            raise lce.SymbolAlreadyExists(symbol_name)
        else:
            print "Warning", symbol_name, "shadows existing symbol with the same name."

    # Warning for shadowing other existing symbols in higher level of scope.
    try:
        findSymbol(lenv.parent, symbol_name)
    except lce.SymbolNotDefined:
        return

    print "Warning", symbol_name, "shadows existing symbol with the same name."

def createLexicalEnv(lenv, tree):
    """
    Recursively walk the AST creating the a lexical environment in which to
    evaluate all the symbols.
    """
    if isinstance(tree, lexerParser.LCadExpression):
        try:
            # Every expression has it's own lexical environment whose parent
            # is the lexical environment of the enclosing expression.
            tree.lenv = LEnv(lenv)
            flist = tree.value

            # Empty list.
            if (len(flist) == 0):
                return

            start = 0
            if isinstance(flist[0], lexerParser.LCadSymbol):
                start = 1
                flist[0].lenv = tree.lenv

                # First element is def.
                #
                # Create symbols for functions. Functions are created and initialized 
                # at this time so that they can be called out of order.
                #
                if (flist[0].value == "def"):

                    # 4 arguments means this is a function definition.
                    #
                    # def creates symbols in the lexical environment of the parent expression
                    # so that they are visible outside of the def statement.
                    #
                    # functions are evaulated in lexical environment of the def statement, so
                    # that their variables are not visible outside of the def statement.
                    #
                    if (len(flist)==4):
                        start = len(flist)
                        checkOverride(lenv, flist[1].value)
                        lenv.symbols[flist[1].value] = Symbol(flist[1].value)
                        lenv.symbols[flist[1].value].setv(functions.UserFunction(tree.lenv, tree))

            if (start != len(flist)):
                for node in flist[start:]:
                    createLexicalEnv(tree.lenv, node)

        except Exception:
            print "!Error in expression '" + tree.value[0].value + "' at line " + str(tree.start_line) + ":"
            raise

    elif isinstance(tree, lexerParser.LCadSymbol):
        tree.lenv = lenv

    elif isinstance(tree, list):
        for node in tree:
            createLexicalEnv(lenv, node)

def dispatch(func, model, tree):
    """
    This handles function calls to both user-defined and built-in functions.
    """
    if not isinstance(func, functions.LCadFunction):
        raise lce.NotAFunctionException()
    if not tree.initialized:
        func.argCheck(tree)
    return func.call(model, tree)

def execute(lcad_code, filename = "NA"):
    """
    Parses and executes the lcad code in the string lcad_code and returns the model.

    :param lcad_code: A string containing lcad code.
    :type lcad_code: str.
    :param filename: A string containing the filename of the file that contained the lcad code.
    :type filename: str.
    :returns: Model.
    """
    lenv = LEnv(add_built_ins = True)
    model = Model()
    ast = lexerParser.parse(lcad_code, filename)
    createLexicalEnv(lenv, ast)
    try:
        interpret(model, ast)
    except Exception as e:
        if hasattr(e, "lcad_err"):
            print e.lcad_err
        raise
    return model

def findSymbol(lenv, symbol_name):
    """
    Recursively searchs up the tree of lexical environments to find
    a symbol_name.

    :param lenv: A lexical environment.
    :type lenv: LEnv.
    :param symbol_name: The name of symbol to find.
    :type symbol_name: str.
    :returns: Symbol.
    :raises: SymbolNotDefined.
    """
    if lenv is None:
        raise lce.SymbolNotDefined(symbol_name)
    if symbol_name in lenv.symbols:
        return lenv.symbols[symbol_name]
    return findSymbol(lenv.parent, symbol_name)

def getv(node):
    """
    A convenience function, interpret() will return a symbol or a 
    constant. If node is a symbol this will return the value of the
    symbol, otherwise it will just return node.
    """
    if isinstance(node, Symbol):
        return node.getv()
    else:
        return node

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
        return findSymbol(tree.lenv, tree.value)

    # Expression.
    #
    # The first value in the expression is the name of the function.
    #
    elif isinstance(tree, lexerParser.LCadExpression):
        flist = tree.value

        # Empty list is false.
        if (len(flist) == 0):
            return lcad_nil

        if isinstance(flist[0], lexerParser.LCadExpression) or isinstance(flist[0], lexerParser.LCadSymbol):
            func = getv(interpret(model, flist[0]))
        else:
            raise lce.ExpressionException()

        try:
            val = dispatch(func, model, tree)
        except Exception as e:
            #except lce.LCadException:
            #print "!Error in function '" + func.name + "' at line " + str(tree.start_line) + " in file '" + str(tree.filename) + "'"
            err_string = "!Error in function '" + func.name + "' at line " + str(tree.start_line) + " in file '" + str(tree.filename) + "'\n"
            if hasattr(e, "lcad_err"):
                e.lcad_err = err_string + e.lcad_err
            else:
                e.lcad_err = err_string
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
