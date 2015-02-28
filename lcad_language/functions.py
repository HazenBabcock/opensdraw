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

def isTrue(model, arg):
    temp = interp.getv(interp.interpret(model, arg))
    if (temp is interp.lcad_t):
        return True
    elif (temp is interp.lcad_nil):
        return False
    else:
        raise lce.BooleanException()


class LCadFunction(object):
    """
    The base class for all functions.
    """
    def __init__(self, name):
        self.name = name

    def argCheck(self, tree):
        pass

    def call(self, model, tree):
        pass


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
