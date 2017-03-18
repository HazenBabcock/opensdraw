#!/usr/bin/env python
"""
.. module:: logicFunctions
   :synopsis: Logic functions like and(), not().

.. moduleauthor:: Hazen Babcock

"""

import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.interpreter as interp
import opensdraw.lcad_language.lcadExceptions as lce
import opensdraw.lcad_language.lcadTypes as lcadTypes
 
lcad_functions = {}


# Logic functions.

class LogicFunction(functions.LCadFunction):
    """
    Logic functions, and, or, not
    """
    pass

class And(functions.SpecialFunction):
    """
    **and** - And statement.

    Usage::

     (and (< 1 2) (< 2 3)) ; t
     (and (fn x) nil)      ; nil
    """
    def __init__(self, name):
        functions.SpecialFunction.__init__(self, name)
        self.setSignature([[lcadTypes.LCadBoolean], [lcadTypes.LCadBoolean], ["optional", [lcadTypes.LCadBoolean]]])

    def call(self, model, tree):
        for i in range(self.numberArgs(tree)):
            if not (functions.isTrue(self.getArg(model, tree, i))):
                return interp.lcad_nil
        return interp.lcad_t

lcad_functions["and"] = And("and")


class Or(functions.SpecialFunction):
    """
    **or** - Or statement.

    Usage::

     (or (< 1 2) (> 1 3))  ; t
     (or (fn x) t)         ; t
     (or nil nil)          ; nil
    """
    def __init__(self, name):
        functions.SpecialFunction.__init__(self, name)
        self.setSignature([[lcadTypes.LCadBoolean], [lcadTypes.LCadBoolean], ["optional", [lcadTypes.LCadBoolean]]])

    def call(self, model, tree):
        for i in range(self.numberArgs(tree)):
            if functions.isTrue(self.getArg(model, tree, i)):
                return interp.lcad_t
        return interp.lcad_nil

lcad_functions["or"] = Or("or")


class Not(LogicFunction):
    """
    **not** - Not statement.

    Usage::

     (not t)  ; nil
     (not ()) ; t
    """
    def __init__(self, name):
        LogicFunction.__init__(self, name)
        self.setSignature([[lcadTypes.LCadBoolean]])

    def call(self, model, val):
        if functions.isTrue(val):
            return interp.lcad_nil
        else:
            return interp.lcad_t

lcad_functions["not"] = Not("not")


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
