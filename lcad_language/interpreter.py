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
    def __init__(self, debug = False, add_builtins = True):
        self.debug = debug

        self.parents = []
        self.symbols = {}

    def addBuiltIns(self):
        """
        This should only be called on the root lexical environment.
        """
        # Symbols.
        for sym_name in builtin_symbols.keys():
            self.symbols[sym_name] = builtin_symbols[sym_name]

        # Functions.
        for fn_name in functions.builtin_functions.keys():
            self.symbols[fn_name] = Symbol(fn_name, 0)
            self.symbols[fn_name].setv(functions.builtin_functions[fn_name])

    def makeCopy(self):
        a_copy = LEnv(add_builtins = False)
        a_copy.debug = self.debug
        a_copy.symbols = self.symbols.copy()
        return a_copy

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
                tmp = Symbol("list_object", 0)
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
    transformation matrix and the parts list.
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
    Box symbols so that they don't get copied when the environment gets copied.
    """
    def __init__(self, name, lenv_id):
        self.is_set = False
        self.lenv_id = lenv_id
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
builtin_symbols["t"] = Symbol("t", 0)
builtin_symbols["t"].setv(lcad_t)

lcad_nil = LObject("nil")
builtin_symbols["nil"] = Symbol("nil", 0)
builtin_symbols["nil"].setv(lcad_nil)

builtin_symbols["e"] = Symbol("e", 0)
builtin_symbols["e"].setv(math.e)

builtin_symbols["pi"] = Symbol("pi", 0)
builtin_symbols["pi"].setv(math.pi)

def checkOverride(tree, symbol_name):

    # Error for shadowing built in symbols.
    if (symbol_name in builtin_symbols):
        raise lce.CannotOverrideTNil()

    # Error for shadowing symbols at the same level of scope.
    # Warning for shadowing other existing symbols.
    if symbol_name in tree.lenv.symbols:
        if (id(tree.lenv.symbols) == tree.lenv.symbols[symbol_name].lenv_id):
            raise lce.SymbolAlreadyExists(symbol_name)
        else:
            print "Warning", symbol_name, "shadows existing symbol with the same name."

def createLexicalEnv(lenv, tree):
    """
    Recursively walk the AST to determine the lexical environment by creating
    variables and functions, along with environment in which the function
    will be called. 

    Expressions and Symbols in the tree are then decorated with this lexical environments.
    """

    if isinstance(tree, lexerParser.LCadExpression):
        try:
            tree.lenv = lenv
            flist = tree.value

            # Empty list.
            if (len(flist) == 0):
                return

            # First element is a symbol, have to handle this specially in
            # case the symbol is "def" or "for" as these create symbols.
            start = 0
            if isinstance(flist[0], lexerParser.LCadSymbol):
                start = 1
                flist[0].lenv = tree.lenv

                # First element is def.
                if (flist[0].value == "def"):
                    start = len(flist)
            
                    # def needs at least 3 arguments.
                    if (len(flist)<3):
                        raise lce.NumberArgumentsException("2 or more", len(flist) - 1)

                    # 4 arguments means this is a function definition.
                    if (len(flist)==4):
                        checkOverride(tree, flist[1].value)
                        tree.lenv.symbols[flist[1].value] = Symbol(flist[1].value, id(tree.lenv.symbols))
                        tree.lenv.symbols[flist[1].value].setv(functions.UserFunction(tree.lenv.makeCopy(), tree))

                    # Otherwise it defines one (or more variables).
                    else:
                        # Must be divisible by 2.
                        if ((len(flist)%2)!=1):
                            raise lce.NumberArgumentsException("an even number of arguments", len(flist) - 1)

                        i = 1
                        while(i < len(flist)):
                            if not isinstance(flist[i], lexerParser.LCadSymbol):
                                raise lce.CannotSetException(flist[i].simple_type_name)
                            flist[i].lenv = lenv
                            if isinstance(flist[i+1], lexerParser.LCadSymbol):
                                flist[i+1].lenv = lenv
                            else:
                                createLexicalEnv(tree.lenv.makeCopy(), flist[i+1])
                        
                            checkOverride(tree, flist[i].value)
                            tree.lenv.symbols[flist[i].value] = Symbol(flist[i].value, id(tree.lenv.symbols))
                            i += 2

                # First element is for.
                elif (flist[0].value == "for"):
                    start = len(flist)

                    # For needs at least 3 arguments.
                    if (len(flist)<3):
                        raise lce.NumberArgumentsException("2 or more", len(flist) - 1)

                    # Check that loop arguments are correct.
                    loop_args = flist[1]
                    if not isinstance(loop_args, lexerParser.LCadExpression):
                        raise lce.LCadException("first argument in for() must be a list.")

                    loop_args = loop_args.value
                    if (len(loop_args) < 2):
                        raise lce.NumberArgumentsException("2,3 or 4", len(loop_args))
                    elif (len(loop_args) > 4):
                        raise lce.NumberArgumentsException("2,3 or 4", len(loop_args))

                    if not isinstance(loop_args[0], lexerParser.LCadSymbol):
                        raise lce.LCadException("loop variable must be a symbol.")

                    checkOverride(tree, loop_args[0].value)

                    # Unlike def, iteration variable is not visible outside of the for loop.
                    new_env = tree.lenv.makeCopy()
                    new_env.symbols[loop_args[0].value] = Symbol(loop_args[0].value, id(new_env.symbols))
                    tree.lenv = new_env
                    for node in flist[1:]:
                        createLexicalEnv(new_env, node)

                # First element is import.
                elif (flist[0].value == "import"):
                    start = len(flist)

                    # Import needs at least 1 arguments.
                    if (len(flist)<2):
                        raise lce.NumberArgumentsException("1 or more", len(flist) - 1)

                    # All arguments must be symbols and can't override built in symbols.
                    for arg in flist[1:]:
                        if not isinstance(arg, lexerParser.LCadSymbol):
                            raise lce.LCadException("arguments in import() must be a symbols.")
                        checkOverride(tree, arg.value)

                    for arg in flist[1:]:
                        tree.lenv.symbols[arg.value] = Symbol(arg.value, id(tree.lenv.symbols))

            if (start != len(flist)):
                new_env = tree.lenv.makeCopy()
                for node in flist[start:]:
                    createLexicalEnv(new_env, node)

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
    func.argCheck(tree)
    return func.call(model, tree)

def execute(lcad_code):
    """
    Parses and executes the lcad code in the string lcad_code and returns the model.

    :param lcad_code: A string containing lcad code.
    :type lcad_code: str.
    :returns: Model.
    """
    lenv = LEnv()
    model = Model()
    ast = lexerParser.parser.parse(lexerParser.lexer.lex(lcad_code))
    createLexicalEnv(lenv, ast)
    interpret(model, ast)
    return model

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
        sym_name = tree.value
        
        try:
            # Check in current module.
            if sym_name in tree.lenv.symbols:
                return tree.lenv.symbols[sym_name]

            # Check in imported modules.
            tmp = sym_name.split(":")
            if (len(tmp)==2):
                [module_name, symbol_name] = tmp
                module = tree.lenv.symbols[module_name].getv()
                if symbol_name in module:
                    return module[symbol_name]

        except KeyError:
            raise lce.SymbolNotDefined(sym_name)

        # Not found, raise error.
        print id(tree.lenv.symbols)
        raise lce.SymbolNotDefined(sym_name)

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
        except Exception:
            #except lce.LCadException:
            print "!Error in function '" + func.name + "' at line " + str(tree.start_line) + ":"
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
