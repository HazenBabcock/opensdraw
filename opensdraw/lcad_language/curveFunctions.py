#!/usr/bin/env python
"""
.. module:: curveFunctions
   :synopsis: The curve function.

.. moduleauthor:: Hazen Babcock
"""

import numbers

import functions
import interpreter as interp
import lcadTypes


class CurveFunction(functions.LCadFunction):
    """
    The functions chain(), curve() and spring() all return this function
    so that they can be used interchangeably.
    """
    def __init__(self, curve, name):
        functions.LCadFunction.__init__(self, name)
        self.setSignature([[lcadTypes.LCadObject, numbers.Number]])
        self.curve = curve

    def call(self, model, tree):
        arg = self.getArg(model, tree, 0)

        # If arg is t return the curve length.
        if not isinstance(arg, numbers.Number):
            if functions.isTrue(arg):
                return self.curve.getLength()
            else:
                return interp.lcad_nil

        # Return transform matrix.
        return self.curve.getMatrix(arg)

    # This is to make it easier to call directly from other Python modules.
    def getMatrix(self, pos):
        return self.curve.getMatrix(pos)

