#!/usr/bin/env python
"""
.. module:: functions
   :synopsis: The LCadFunction class and the UserFunction class.

.. moduleauthor:: Hazen Babcock

"""

from functools import wraps
from itertools import izip
import math
import numbers
import numpy
import operator
import os
import random

import interpreter as interp
import lcadExceptions as lce
import lexerParser
import parts

# Keep track of built-in functions.
builtin_functions = {}

def isTrue(val):
    if (val is interp.lcad_t):
        return True
    if (val is interp.lcad_nil):
        return False
    raise lce.BooleanException()

def isType(val, types):
    for a_type in types:
        if isinstance(val, a_type):
            return True
    return False

def typeToString(a_type):
    a_string = a_type.__name__
    if (a_string == "basestring"):
        return "string"
    if (a_string == "CurveFunction"):
        return "curve function"
    if (a_string == "LCadBoolean"):
        return "t, nil"
    if (a_string == "interp.Symbol"):
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
        val = interp.getv(interp.interpret(model, tree.value[index+1]))

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
            val = interp.getv(interp.interpret(model, args[index]))
            if not isType(val, self.signature[index]):
                raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index])), type(val))
            standard_args.append(val)
            index += 1

        # Optional arguments.
        if self.has_optional_args:
            sig_index = index
            while (index < len(args)):
                val = interp.getv(interp.interpret(model, args[index]))
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
                    keyword_dict[key] = interp.getv(interp.interpret(model, sig_dict[key][1]))
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
                val = interp.getv(interp.interpret(model, args[index+1]))
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


class SpecialFunction(LCadFunction):
    """
    Functions that operate on the AST.
    """
    pass


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
                interp.createLexicalEnv(self.lenv, arg_value)
                keyword_dict[arg_name] = [[object], arg_value]
                i += 2
            else:
                self.arg_names.append(arg_name)
                standard_args.append([object])
                i += 1

            interp.checkOverride(self.lenv, arg_name)
            self.lenv.symbols[arg_name] = interp.Symbol(arg_name, tree.filename)

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
        return interp.interpret(model, self.body)


#
# The MIT License
#
# Copyright (c) 2015 Hazen Babcock
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
