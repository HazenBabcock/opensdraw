#!/usr/bin/env python
"""
.. module:: curve
   :synopsis: The curve function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import functions
import interpreter as interp
import lcadExceptions

builtin_functions = {}


#
# These classes create a chain function that can be used in openldraw.
#
class CurveFunction(functions.LCadFunction):

    def __init__(self, chain):
        self.chain = chain
        self.name = "user created curve function"

    def argCheck(self, tree):
        pass

    def call(self, model, tree):
        pass


class LCadCurve(functions.SpecialFunction):
    """
    **curve** - Creates a curve function.
    
    """
    def __init__(self):
        self.name = "curve"

    def argCheck(self, tree):
        pass

    def call(self, model, tree):
        pass

builtin_functions["curve"] = LCadCurve()

        
class NumberControlPointsException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A curve must have at least 2 control points, got " + str(got))


class ControlPointException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A control point must have 6 arguments, got " + str(got))


#
# The classes below do the math necessary to create a curve.
#
class Curve(object):

    def __init__(self):
        pass


#
# Testing
#
if (__name__ == "__main__"):

    vx = numpy.array([0, 0.5, 1, 0.5])
    vy = numpy.array([0, 3, 0, -3])

    A = numpy.array([[0, 0, 0, 1],
                     [0, 0, 1, 0],
                     [1, 1, 1, 1],
                     [3, 2, 1, 0]])

    xc = numpy.linalg.solve(A, vx)
    yc = numpy.linalg.solve(A, vy)

    if 0:
        print xc
        print yc
        exit()
    
    # Check derivatives.
    if 0:
        print xc[2], yc[2]
        print 3.0*xc[0] + 2.0*xc[1] + xc[2], 3.0*yc[0] + 2.0*yc[1] + yc[2]
        exit()


    x = numpy.arange(0.0, 1.001, 0.01)
    xf = numpy.zeros(x.size)
    yf = numpy.zeros(x.size)
    for i in range(x.size):
        x1 = x[i]
        x2 = x1*x1
        x3 = x2*x1
        xf[i] = xc[0]*x3 + xc[1]*x2 + xc[2]*x1 + xc[3]
        yf[i] = yc[0]*x3 + yc[1]*x2 + yc[2]*x1 + yc[3]

    import matplotlib.pyplot as plt
    fig = plt.figure()
    #ax = fig.add_subplot(1,1,1, aspect = 1.0)
    ax = fig.add_subplot(1,1,1)
    ax.plot(xf, yf)
    plt.show()


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
