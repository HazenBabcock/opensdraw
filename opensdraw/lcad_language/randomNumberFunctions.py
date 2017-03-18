#!/usr/bin/env python
"""
.. module:: randomNumberFunctions
   :synopsis: Random number functions.

.. moduleauthor:: Hazen Babcock

"""

import numbers
import random

import opensdraw.lcad_language.functions as functions
import interpreter as interp
import lcadExceptions as lce

lcad_functions = {}

class RandomNumberFunction(functions.LCadFunction):
    pass


class RandSeed(RandomNumberFunction):
    """
    **rand-seed** - Initialize the random number generator.

    Usage::

     (rand-seed 10)
    """
    def __init__(self, name):
        RandomNumberFunction.__init__(self, name)
        self.setSignature([[numbers.Number]])

    def call(self, model, seed):
        random.seed(seed)
        return seed

lcad_functions["rand-seed"] = RandSeed("rand-seed")


class RandChoice(RandomNumberFunction):
    """
    **rand-choice** - Return a random element from a list.

    Usage::

     (rand-choice (list 1 2 3)) ; return 1,2 or 3.
     (rand-choice (list a b)) ; return a or b
    """
    def __init__(self, name):
        RandomNumberFunction.__init__(self, name)
        self.setSignature([[list]])

    def call(self, model, *args):
        return random.choice(*args)

lcad_functions["rand-choice"] = RandChoice("rand-choice")


class RandGauss(RandomNumberFunction):
    """
    **rand-gauss** - Return a gaussian distributed random number.
    This can be called with either 0 or 2 arguments.

    Usage::

     (rand-gauss)      ; mean = 0, standard deviation = 1.0
     (rand-gauss 1 10) ; mean = 1, standard deviation = 10.0
    """
    def __init__(self, name):
        RandomNumberFunction.__init__(self, name)
        self.setSignature([["optional", [numbers.Number]]])

    def call(self, model, *args):
        if (len(args) == 2):
            return random.gauss(*args)
        else:
            return random.gauss(0, 1)

lcad_functions["rand-gauss"] = RandGauss("rand-gauss")


class RandInteger(RandomNumberFunction):
    """
    **rand-integer** - Return a random integer

    Usage::

     (rand-integer 0 100) ; random integer between 0 and 100.
     (rand-integer 2 30)  ; random integer between 2 and 30.
    """
    def __init__(self, name):
        RandomNumberFunction.__init__(self, name)
        self.setSignature([[numbers.Number], [numbers.Number]])

    def call(self, model, start, end):
        return random.randint(start, end)

lcad_functions["rand-integer"] = RandInteger("rand-integer")


class RandUniform(RandomNumberFunction):
    """
    **rand-uniform** - Return a uniformly distributed random number.
    This can be called with either 0 or 2 arguments.

    Usage::

     (rand-uniform)      ; distributed on 0 - 1.
     (rand-uniform 1 10) ; distributed on 1 - 10.
    """
    def __init__(self, name):
        RandomNumberFunction.__init__(self, name)
        self.setSignature([["optional", [numbers.Number]]])

    def call(self, model, *args):
        if (len(args) == 2):
            return random.uniform(*args)
        else:
            return random.random()

lcad_functions["rand-uniform"] = RandUniform("rand-uniform")


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
