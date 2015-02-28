#!/usr/bin/env python
"""
.. module:: randomNumberFunctions
   :synopsis: Random number functions.

.. moduleauthor:: Hazen Babcock

"""

import random

import interpreter as interp
import lcadExceptions as lce
import mathFunctions as mathFunctions

lcad_functions = {}

class RandomNumberFunction(mathFunctions.MathFunction):
    pass


class RandSeed(RandomNumberFunction):
    """
    **rand-seed** - Initialize the random number generator.

    Usage::

     (rand-seed 10)
    """
    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lce.NumberArgumentsException("1", len(tree.value) - 1)

    def call(self, model, tree):
        seed = self.isNumber(interp.interpret(model, tree.value[1]))
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
    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lce.NumberArgumentsException("1", len(tree.value) - 1)

    def call(self, model, tree):
        tlist = interp.getv(interp.interpret(model, tree.value[1]))

        if not isinstance(tlist, interp.List):
            raise lce.WrongTypeException("List", type(tlist))

        return random.choice(tlist.getl())

lcad_functions["rand-choice"] = RandChoice("rand-choice")


class RandGauss(RandomNumberFunction):
    """
    **rand-gauss** - Return a gaussian distributed random number.

    Usage::

     (rand-gauss)      ; mean = 0, standard deviation = 1.0
     (rand-gauss 1 10) ; mean = 1, standard deviation = 10.0
    """
    def argCheck(self, tree):
        if (len(tree.value) != 1) and (len(tree.value) != 3):
            raise lce.NumberArgumentsException("0 or 2", len(tree.value) - 1)

    def call(self, model, tree):
        if (len(tree.value) == 3):
            mu = self.isNumber(interp.interpret(model, tree.value[1]))
            sigma = self.isNumber(interp.interpret(model, tree.value[2]))
            return random.gauss(mu, sigma)
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
    def argCheck(self, tree):
        if (len(tree.value) != 3):
            raise lce.NumberArgumentsException("2", len(tree.value) - 1)

    def call(self, model, tree):
        start = self.isNumber(interp.interpret(model, tree.value[1]))
        end = self.isNumber(interp.interpret(model, tree.value[2]))
        return random.randint(start, end)

lcad_functions["rand-integer"] = RandInteger("rand-integer")


class RandUniform(RandomNumberFunction):
    """
    **rand-uniform** - Return a uniformly distributed random number.

    Usage::

     (rand-uniform)      ; distributed on 0 - 1.
     (rand-uniform 1 10) ; distributed on 1 - 10.
    """
    def argCheck(self, tree):
        if (len(tree.value) != 1) and (len(tree.value) != 3):
            raise lce.NumberArgumentsException("0 or 2", len(tree.value) - 1)

    def call(self, model, tree):
        if (len(tree.value) == 3):
            start = self.isNumber(interp.interpret(model, tree.value[1]))
            end = self.isNumber(interp.interpret(model, tree.value[2]))
            return random.uniform(start, end)
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
