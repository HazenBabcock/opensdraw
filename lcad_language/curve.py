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

def normVector(vector):
    return vector/numpy.sqrt(numpy.sum(vector * vector))


class Curve(object):

    def __init__(self):
        pass


class ControlPoint(object):

    def __init__(self, x, y, z, dx, dy, dz, tx = 0, ty = 0, tz = 0):
        
        self.location = numpy.array([x, y, z])
        self.derivative = numpy.array([dx, dy, dz])
        self.tangent = numpy.array([tx, ty, tz])

        self.norm_derivative = normVector(self.derivative)

        # Only the first point has a tangent vector.
        if (numpy.sum(self.tangent * self.tangent) > 0.1):
            self.norm_tangent = normVector(self.tangent)
            
            # Adjust tangent to make exactly normal to derivative
            # and normalize it's length to one.
            proj = numpy.dot(self.norm_derivative, self.norm_tangent) * self.norm_derivative
            self.norm_tangent = normVector(self.norm_tangent - proj)
        else:
            self.tangent = None
            self.norm_tangent = None


class Segment(object):

    def __init__(self, control_point_1, control_point_2, normalize, scale):
        self.cp1 = control_point_1
        self.cp2 = control_point_2

        # Calculate x, y, z polynomial coefficients. Basically we are creating
        # a cubic-spline that goes through the two control points with the
        # specified derivative at the control points.
        A = numpy.array([[0, 0, 0, 1],
                         [0, 0, 1, 0],
                         [1, 1, 1, 1],
                         [3, 2, 1, 0]])

        # If normalization is requested, then we scale the magnitude of the
        # derivative by the distance between the control points. This is
        # somewhat arbitrary, but hopefully looks reasonable to the eye.
        if normalize:
            dv = self.cp1.location - self.cp2.location
            scale = scale * numpy.sqrt(numpy.sum(dv * dv))
            deriv1 = self.cp1.norm_derivative
            deriv2 = self.cp2.norm_derivative
        else:
            scale = 1.0
            deriv1 = self.cp1.derivative
            deriv2 = self.cp2.derivative
        print scale

        vx = numpy.array([self.cp1.location[0],
                          deriv1[0]*scale,
                          self.cp2.location[0],
                          deriv2[0]*scale])

        vy = numpy.array([self.cp1.location[1],
                          deriv1[1]*scale,
                          self.cp2.location[1],
                          deriv2[1]*scale])

        vz = numpy.array([self.cp1.location[2],
                          deriv1[2]*scale,
                          self.cp2.location[2],
                          deriv2[2]*scale])

        self.x_coeff = numpy.linalg.solve(A, vx)
        self.y_coeff = numpy.linalg.solve(A, vy)
        self.z_coeff = numpy.linalg.solve(A, vz)

    def xyz(self, p):
        p_vec = numpy.array([p*p*p, p*p, p, 1.0])
        return [numpy.sum(self.x_coeff * p_vec),
                numpy.sum(self.y_coeff * p_vec),
                numpy.sum(self.z_coeff * p_vec)]


#
# Testing
#
if (__name__ == "__main__"):

    cp1 = ControlPoint(0, 0, 0, -1.0, 1.0, 0)
    cp2 = ControlPoint(5, 0, 0, 1.0, -1.0, 0)

    s = Segment(cp1, cp2, True, 1.9)
    #print s.x_coeff, s.y_coeff
    #exit()

    x = numpy.arange(0.0, 1.001, 0.05)
    xf = numpy.zeros(x.size)
    yf = numpy.zeros(x.size)
    for i in range(x.size):
        xyz = s.xyz(x[i])
        xf[i] = xyz[0]
        yf[i] = xyz[1]

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, aspect = 1.0)
    #ax = fig.add_subplot(1,1,1)
    #ax.plot(xf, yf)
    ax.scatter(xf, yf)
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
