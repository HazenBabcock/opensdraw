#!/usr/bin/env python
"""
.. module:: interpreter
   :synopsis: The interpreter for the lcad language as well as the
              LCadFunction class and the UserFunction class.

.. moduleauthor:: Hazen Babcock

"""

import copy
import importlib
import math
import numbers
import numpy
import os
import xml.etree.ElementTree as ElementTree

import opensdraw.lcad_language.lcadExceptions as lce
import opensdraw.lcad_language.lexerParser as lexerParser
import opensdraw.lcad_language.lcadTypes as lcadTypes

# Keeps track of all the built in symbols.
builtin_functions = {}
builtin_symbols = {}
mutable_symbols = []


#
# Classes
#

class EmptyTree(object):
    """
    An empty AST.
    """
    def __init__(self):
        self.value = [False]


class Group(object):
    """
    A group of parts.
    """
    def __init__(self, name):
        self.name = name

        self.have_comments = False
        self.header = []
        self.m = numpy.identity(4)
        self.n_parts = 0
        self.n_primitives = 0
        self.parts_list = []

    def addComment(self, comment):
        self.have_comments = True
        self.parts_list.append(comment)

    def addPart(self, part, is_primitive):
        if is_primitive:
            self.n_primitives += 1
        else:
            self.n_parts += 1
        self.parts_list.append(part)

    def getNParts(self):
        return self.n_parts

    def getNPrimitives(self):
        return self.n_primitives

    def getParts(self):
        """
        Return the parts list sorted by step, but only if there are no comments.
        """
        if self.have_comments:
            return self.parts_list
        else:
            return sorted(self.parts_list, key = lambda part: part.step)

    def matrix(self):
        return self.m

    def setMatrix(self, m):
        self.m = m


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

        # Import function modules (from modules.xml) here.
        xml = ElementTree.parse(os.path.dirname(__file__) + "/modules.xml").getroot()
        fn_modules = []
        for module in xml:
            fn_modules.append(importlib.import_module(module.text))

        for module in fn_modules:
            for fn_name in module.lcad_functions.keys():
                builtin_functions[fn_name] = True
                self.symbols[fn_name] = Symbol(fn_name, "builtin")
                self.symbols[fn_name].setv(module.lcad_functions[fn_name])


class LCadFunction(object):
    """
    The base class for all functions.
    """
    def __init__(self, name):
        self.has_keyword_args = False
        self.has_optional_args = False
        self.minimum_args = None
        self.name = name
        self.signature = None
        
    def argCheck(self, tree):
        args = tree.value[1:]
        if self.has_keyword_args or self.has_optional_args:
            if (len(args) < self.minimum_args):
                raise lce.NumberArgumentsException("at least " + str(self.minimum_args), len(args))
        else:
            if (len(args) != self.minimum_args):
                raise lce.NumberArgumentsException("exactly " + str(self.minimum_args), len(args))
        tree.initialized = True

    def getArg(self, model, tree, index):
        """
        This will get the arguments one at time. It only works with 
        standard and optional arguments.
        """
        val = getv(interpret(model, tree.value[index+1]))

        # Standard arguments.
        if (index < self.minimum_args):
            if not isType(val, self.signature[index]):
                raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index])), typeToString(type(val)))
            return val
        
        # All arguments that are beyond the length of the signature are
        # have to have the type specified by the last argument of the signature.
        if (index >= len(self.signature)):
            index = len(self.signature) - 1
        if not isType(val, self.signature[index][1]):
            raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index][1])), type(val))
        return val

    def getArgs(self, model, tree):
        """
        This is what you want to use most of the time. It will return either (1) A list
        containing the standard arguments, followed by the optional arguments or (2) a 
        list containing a list of the standard arguments followed by the keyword dictionary.

        (1) [standard / optional arguments]
        (2) [[standard arguments], keyword dictionary]

        The defaults for the keywords are filled in with the defaults if they are 
        not found.
        """
        args = tree.value[1:]
        index = 0

        # Standard arguments.
        standard_args = []
        while (index < self.minimum_args):
            val = getv(interpret(model, args[index]))
            if not isType(val, self.signature[index]):
                raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index])), type(val))
            standard_args.append(val)
            index += 1

        # Optional arguments.
        if self.has_optional_args:
            sig_index = index
            while (index < len(args)):
                val = getv(interpret(model, args[index]))
                if not isType(val, self.signature[sig_index][1]):
                    raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[sig_index][1])), type(val))
                standard_args.append(val)
                index += 1
                if (sig_index < (len(self.signature) - 2)):
                    sig_index += 1
            return standard_args

        # Keyword arguments.
        if self.has_keyword_args:
            sig_dict = self.signature[index][1]

            # Fill in keyword dictionary.
            keyword_dict = {}
            if isinstance(self, UserFunction):
                for key in sig_dict.keys():
                    keyword_dict[key] = getv(interpret(model, sig_dict[key][1]))
            else:
                for key in sig_dict.keys():
                    keyword_dict[key] = sig_dict[key][1]

            # Parse keywords.
            while (index < len(args)):
                key = args[index].value
                if (key[0] != ":"):
                    raise lce.KeywordException(args[index].value)
                key = key[1:]
                if not key in sig_dict.keys():
                    raise lce.UnknownKeywordException(key)
                val = getv(interpret(model, args[index+1]))
                if not isType(val, sig_dict[key][0]):
                    raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[sig_index][1])), type(val))
                keyword_dict[key] = val
                index += 2
            return [standard_args, keyword_dict]

        return standard_args

    def numberArgs(self, tree):
        return len(tree.value) - 1
                                
    def setSignature(self, signature):
        """
        Signature is a list containing the following:

        (1) Standard arguments:
            [[ type ], [ type ], ..,
        (2) Optional arguments:
            [ "optional", [ type ]]]
            If the list or arguments is longer than standard + optional the remaining
            arguments must have the same type as the last optional argument.
        (3) Keyword arguments:
            [ "keyword", {'keyword1': [[ type ], default value], 'keyword2': ..}]]

        Note you should either have (2) or (3) but not both. All the functions that
        are not internal only take keywords.

        """
        self.minimum_args = 0
        self.signature = signature
        for arg in self.signature:
            if (len(arg) > 0):
                if not isinstance(arg[0], basestring):
                    self.minimum_args += 1
                else:
                    if (arg[0] == "optional"):
                        self.has_optional_args = True
                    elif (arg[0] == "keyword"):
                        self.has_keyword_args = True


class Model(object):
    """
    This keeps track of the current "model", i.e. the 
    current transformation matrix and groups of parts.
    """
    def __init__(self, is_main = True):
        self.is_main = is_main
        self.m_cur_group = []
        self.m_groups = []
        self.used_names = {}

        self.pushGroup("main")
        
    def curGroup(self):
        return self.m_cur_group[-1]

    def groups(self):
        return self.m_groups

    def popGroup(self):
        self.m_cur_group = self.m_cur_group[:-1]

    def pushGroup(self, name):
        if name in self.used_names:
            raise lce.GroupExistsException(name)
        new_group = Group(name)
        self.m_cur_group.append(new_group)
        self.m_groups.append(new_group)
        self.used_names[name] = 1


class SpecialFunction(LCadFunction):
    """
    Functions that operate on the AST.
    """
    pass


class Symbol(object):
    """
    Symbol class.
    """
    def __init__(self, name, filename):
        self.filename = filename
        self.is_set = False
        self.name = name
        self.used = False
        self.value = None

    def getv(self):
        if not self.is_set:
            raise lce.VariableNotSetException(self.name)
        self.used = True
        return self.value

    def setv(self, value):
        self.is_set = True
        self.value = value


class UserFunction(LCadFunction):
    """
    'Normal' user defined functions.
    """
    def __init__(self, tree, name):
        LCadFunction.__init__(self, name)
        flist = tree.value[1:]

        # Named function.
        if (len(flist) == 3):
            self.name = flist[0].value
            self.arg_list = flist[1].value
            self.body = flist[2]

        # Anonymous (lambda) function.
        elif (len(flist) == 2):
            self.name = "anonymous"
            self.arg_list = flist[0].value
            self.body = flist[1]

        self.arg_names = []
        self.lenv = tree.lenv

        i = 0
        standard_args = []
        keyword_dict = {}
        while (i < len(self.arg_list)):
            arg = self.arg_list[i]
            if not isinstance(arg, lexerParser.LCadSymbol):
                raise lce.IllegalArgumentTypeException()

            arg_name = arg.value
            # Keyword arguments.
            if (arg_name[0] == ":"):
                self.have_keyword_args = True
                arg_name = arg_name[1:]
                arg_value = self.arg_list[i+1]
                if isinstance(arg_value, lexerParser.LCadSymbol):
                    if (arg_value.value[0] == ":"):
                        raise Exception("Keyword arguments must have a default value.")
                createLexicalEnv(self.lenv, arg_value)
                keyword_dict[arg_name] = [[object], arg_value]
                i += 2
            else:
                self.arg_names.append(arg_name)
                standard_args.append([object])
                i += 1

            checkOverride(self.lenv, arg_name)
            self.lenv.symbols[arg_name] = Symbol(arg_name, tree.filename)

        if (len(keyword_dict.keys()) > 0):
            standard_args.append(["keyword", keyword_dict])
        self.setSignature(standard_args)

    def call(self, model, *args, **kwargs):

        # Check argument count.
        if (len(args) != self.minimum_args):
            raise lce.NumberArgumentsException(self.minimum_args, len(args))
            
        # Fill in arguments.
        for i in range(len(args)):
            self.lenv.symbols[self.arg_names[i]].setv(args[i])

        if self.has_keyword_args:
            for key in kwargs.keys():
                self.lenv.symbols[key].setv(kwargs[key])

        # Evaluate function.
        return interpret(model, self.body)        


# t and nil are objects so that we can do comparisons using 'is' and
# be gauranteed that there is only one truth and one false.

lcad_t = lcadTypes.LCadBoolean("t")
builtin_symbols["t"] = Symbol("t", "builtin")
builtin_symbols["t"].setv(lcad_t)

lcad_nil = lcadTypes.LCadBoolean("nil")
builtin_symbols["nil"] = Symbol("nil", "builtin")
builtin_symbols["nil"].setv(lcad_nil)


builtin_symbols["e"] = Symbol("e", "builtin")
builtin_symbols["e"].setv(math.e)

builtin_symbols["pi"] = Symbol("pi", "builtin")
builtin_symbols["pi"].setv(math.pi)

builtin_symbols["step-offset"] = Symbol("step-offset", "builtin")
builtin_symbols["step-offset"].setv(0)
mutable_symbols.append("step-offset")

builtin_symbols["time-index"] = Symbol("time-index", "builtin")
builtin_symbols["time-index"].setv(0)


def checkOverride(lenv, symbol_name, external_filename = False):
    """
    Check if symbol_name overrides a builtin or user defined symbol.
    """

    # Error for shadowing built in symbols.
    if (symbol_name in builtin_symbols):
        raise lce.CannotOverrideBuiltIn()

    # Error for shadowing symbols at the same level of scope.
    if symbol_name in lenv.symbols:
        symbol = lenv.symbols[symbol_name]

        # This the standard check.
        if not external_filename:
            raise lce.SymbolAlreadyExists(symbol_name)

        # Import uses this to not give errors for multiple 
        # imports of same symbol from the same package.
        else:
            if (external_filename != symbol.filename):
                raise lce.SymbolAlreadyExists(symbol_name)

    # Warning for shadowing other existing symbols in higher level of scope.
    try:
        findSymbol(lenv.parent, symbol_name)
    except lce.SymbolNotDefined:
        return

    print("Warning", symbol_name, "shadows existing symbol with the same name!!")


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
                    # functions are evaluated in lexical environment of the def statement, so
                    # that their variables are not visible outside of the def statement.
                    #
                    if (len(flist)==4):
                        start = len(flist) - 1
                        checkOverride(lenv, flist[1].value)
                        lenv.symbols[flist[1].value] = Symbol(flist[1].value, tree.filename)
                        lenv.symbols[flist[1].value].setv(UserFunction(tree, flist[1].value))

            if (start != len(flist)):
                for node in flist[start:]:
                    createLexicalEnv(tree.lenv, node)

        except Exception:
            print("!Error in expression '" + tree.value[0].value + "' at line " + str(tree.start_line) + ":")
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
    if not isinstance(func, LCadFunction):
        raise lce.NotAFunctionException(func)
    if not tree.initialized:
        func.argCheck(tree)

    if isinstance(func, SpecialFunction):
        return func.call(model, tree)
    else:
        if func.has_keyword_args:
            [args, kwargs] = func.getArgs(model, tree)
            return func.call(model, *args, **kwargs)
        else:
            return func.call(model, *func.getArgs(model, tree))


def execute(lcad_code, filename = "NA", time_index = 0):
    """
    Parses and executes the lcad code in the string lcad_code and returns the model.

    :param lcad_code: A string containing lcad code.
    :type lcad_code: str.
    :param filename: A string containing the filename of the file that contained the lcad code.
    :type filename: str.
    :param time_index: A time index.
    :type time_index: integer.
    :returns: Model.
    """
    # Set the value of the time-index symbol (for animations).
    builtin_symbols["time-index"].setv(time_index)

    lenv = LEnv(add_built_ins = True)
    model = Model()
    ast = lexerParser.parse(lcad_code, filename)
    createLexicalEnv(lenv, ast)
    try:
        interpret(model, ast)
    except Exception as e:
        if hasattr(e, "lcad_err"):
            print(e.lcad_err)
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


def getStepOffset(model):
    """
    Return the current value of step-offset.
    """
    # Get step offset.
    step_offset = getv(builtin_symbols["step-offset"])

    # Check if it is a function, if so, call the function (which cannot take any arguments).
    if not isinstance(step_offset, numbers.Number):
        step_offset = getv(step_offset.call(model))

    if not isinstance(step_offset, numbers.Number):
        raise lce.WrongTypeException("number", type(step_offset))

    return step_offset
    

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
            raise lce.NotAFunctionException(flist[0].value)

        try:
            val = dispatch(func, model, tree)
        except Exception as e:
            if hasattr(func, "name"):
                err_string = "!Error in function '" + func.name + "' at line " + str(tree.start_line) + " in file '" + str(tree.filename) + "'\n"
            else:
                err_string = "!Error at line "  + str(tree.start_line) + " in file '" + str(tree.filename) + "'\n"
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


def isTrue(val):
    """
    Returns True/False if val is lcad_t or lcad_nil.
    """
    if (val is lcad_t):
        return True
    if (val is lcad_nil):
        return False
    raise lce.BooleanException()


def isType(val, types):
    """
    Check if val is of a type in types.
    """
    for a_type in types:
        if isinstance(val, a_type):
            return True
    return False


def typeToString(a_type):
    """
    Convert a type name to the corresponding lcad string.
    """
    a_string = a_type.__name__
    if (a_string == "basestring"):
        return "string"
    if (a_string == "CurveFunction"):
        return "curve function"
    if (a_string == "LCadBoolean"):
        return "t, nil"
    if (a_string == "Symbol"):
        return "symbol"
    if (a_string == "LCadVector"):
        return "vector"
    if (a_string == "LCadMatrix"):
        return "matrix"
    if (a_string == "numpy.ndarray"):
        return "vector, matrix"
    if (a_string == "numbers.Number"):
        return "number"
    return a_string


def walk(tree, func, indent = ""):
    """
    Recursively walks the AST evaluating func on each of the nodes.
    """
    if isinstance(tree, list):
        for node in tree:
            walk(node, func, indent)
    else:
        func(tree, indent)
        if isinstance(tree, lexerParser.LCadExpression):
            for node in tree.value:
                walk(node, func, indent + " ")


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
