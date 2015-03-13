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

# Keeps track of all the built in functions.
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
    if (a_string == "interp.List"):
        return "list"
    if (a_string == "interp.Symbol"):
        return "symbol"        
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
        self.has_extra_args = False
        self.minimum_args = 0
        self.name = name
        self.signature = None
        
    def argCheck(self, tree):
        args = tree.value[1:]
        if self.has_extra_args:
            if (len(args) < self.minimum_args):
                raise lce.NumberArgumentsException("at least " + str(self.minimum_args), len(args))
        else:
            if (len(args) != self.minimum_args):
                raise lce.NumberArgumentsException("exactly " + str(self.minimum_args), len(args))
        tree.initialized = True

    def call(self, model, tree):
        pass

    def getArg(self, model, tree, index):
        """
        This will get the arguments one at time. It only works with 
        standard and optional arguments.
        """
        arg = interp.getv(interp.interpret(model, tree.value[index+1]))

        # Standard arguments.
        if (index < self.minimum_args):
            if not isType(val, self.signature[index]):
                raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index])), type(arg))
            return arg
        
        # Optional arguments.
        if (index >= len(self.signature)):
            index = len(self.signature) - 1
        if not isType(val, self.signature[index][1]):
            raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index][1])), type(arg))
        return arg

    def getArgs(self, model, tree):
        """
        This is what you want to use most of the time. It will return either (1) A list
        containing the standard arguments, followed by the optional arguments or (2) a
        a list containing the standard arguments followed by the keyword dictionary.

        (1) [[standard / optional arguments]]
        (2) [[standard arguments], keyword dictionary]

        The defaults for the keywords are filled in with the defaults if they are 
        not found.
        """
        
        args = tree.value[1:]
        index = 0

        # Standard arguments.
        standard_args = []
        while (not isinstance(self.signature[index][0], basestring)):
            val = interp.getv(interp.interpret(model, args[index]))
            if not isType(val, self.signature[index]):
                raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[index])), type(val))
            standard_args.append(val)
            index += 1
        if (index == len(args)):
            return standard_args

        # Optional arguments.
        if (self.signature[index][0] == "optional"):
            sig_index = index
            while (index < len(args)):
                val = interp.getv(interp.interpret(model, args[index]))
                if not isType(val, self.signature[sig_index][1]):
                    raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[sig_index][1])), type(val))
                standard_args.append(val)
                index += 1
                if (sig_index < (len(self.signature) - 2)):
                    sig_index += 1
            return [standard_args]

        # Keyword arguments.
        if (self.signature[index][0] == "keyword"):
            sig_dict = self.signature[index][1]

            # Fill in keyword dictionary.
            keyword_dict = {}
            for key in keys(sig_dict):
                keyword_dict[key] = sig_dict[key][1]

            # Parse keywords.
            while (index < len(args)):
                key = args[index].value
                if (key[0] != ":"):
                    raise lce.KeywordException(args[index].value)
                key = key[1:]
                if not key in keys(sig_dict):
                    raise lce.UnknownKeywordException(key)
                val = interp.getv(interp.interpret(model, args[index+1]))
                if not isType(val, sig_dict[key][0]):
                    raise lce.WrongTypeException(", ".join(map(typeToString, self.signature[sig_index][1])), type(val))
                index += 2
            return [standard_args, keyword_dict]

        raise lce.LCadException(str(self.signature[index][0]) + " function signature type not recognized.")

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
            [ "keyword", {'keyword1', [[ type ], default value], 'keyword2', ..}]]

        Note you should either have (2) or (3) but not both. All the functions that
        are not internal only take keywords.

        """
        self.signature = signature
        for arg in self.signature:
            if not isinstance (arg[0], basestring):
                self.minimum_args += 1
            else:
                self.has_extra_args = True


class UserFunction(LCadFunction):
    """
    'Normal' user defined functions.
    """
    def __init__(self, tree):
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

        self.default_values = []
        self.lenv = tree.lenv
        self.have_keyword_args = False
        self.min_args = 0

        i = 0
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
                self.default_values.append([arg_name, arg_value])
                i += 2
            else:
                self.min_args += 1
                i += 1

            interp.checkOverride(self.lenv, arg_name)
            self.lenv.symbols[arg_name] = interp.Symbol(arg_name, tree.filename)

    def argCheck(self, tree):
        args = tree.value[1:]
        if self.have_keyword_args:
            if (len(args) < self.min_args):
                raise lce.NumberArgumentsException("at least " + str(self.min_args), len(args))
            cnt = 0
            for i in range(self.min_args):
                if isinstance(args[i], lexerParser.LCadSymbol) and (args[i].value[0] == ":"):
                    break
                cnt += 1
            if (cnt < self.min_args):
                raise lce.NumberArgumentsException("at least " + str(self.min_args), cnt)

        else:
            if (len(args) != self.min_args):
                raise lce.NumberArgumentsException(self.min_args, len(args))

    def call(self, model, tree):
        args = tree.value[1:]

        # Fill in defaults (if any).
        for default in self.default_values:
            self.lenv.symbols[default[0]].setv(interp.getv(interp.interpret(model, default[1])))

        # Fill in arguments.
        i = 0

        # Standard arguments first.
        while (i < self.min_args):
            self.lenv.symbols[self.arg_list[i].value].setv(interp.getv(interp.interpret(model, args[i])))
            i += 1

        # Keyword arguments last.
        while (i < len(args)):
            arg = args[i]
            arg_name = arg.value
            if not isinstance(arg, lexerParser.LCadSymbol):
                raise lce.KeywordException(arg_name)
            if (arg_name[0] != ":"):
                raise lce.KeywordException(arg_name)

            self.lenv.symbols[arg_name[1:]].setv(interp.getv(interp.interpret(model, args[i+1])))
            i += 2

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
