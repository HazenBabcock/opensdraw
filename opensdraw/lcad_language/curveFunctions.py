#!/usr/bin/env python
"""
.. module:: curveFunctions
   :synopsis: The curve function.

.. moduleauthor:: Hazen Babcock
"""

import numbers

import opensdraw.lcad_language.interpreter as interp
import opensdraw.lcad_language.lcadTypes as lcadTypes


class CurveFunction(interp.LCadFunction):
    """
    The functions chain(), curve() and spring() all return this function
    so that they can be used interchangeably.
    """
    def __init__(self, curve, name):
        interp.LCadFunction.__init__(self, name)
        self.setSignature([[lcadTypes.LCadBoolean, numbers.Number]])
        self.curve = curve

    def call(self, model, arg):

        # If arg is t return the curve length.
        if not isinstance(arg, numbers.Number):
            if interp.isTrue(arg):
                return self.curve.getLength()
            else:
                return interp.lcad_nil

        # Return transform matrix.
        return self.curve.getMatrix(arg)
