#!/usr/bin/env python
"""
.. module:: geometryFunctions
   :synopsis: rotate, translate, etc.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import functions
import interpreter as interp
import lcadExceptions as lce

lcad_functions = {}

class GeometryFunction(functions.LCadFunction):
    pass


class Mirror(GeometryFunction):
    """
    **mirror** - Mirror child elements on a plane through the origin.

    :param mx: mirror on x axis.
    :param my: mirror on y axis.
    :param mz: mirror on z axis.

    Usage::

     (mirror (1 0 0) ..) ; mirrors on the x axis.
    """
    def __init__(self):
        GeometryFunction.__init__(self, "mirror")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<3):
            raise lce.NumberArgumentsException("2+", 0)
        if not isinstance(flist[1].value, list):
            raise lce.WrongTypeException("list", type(flist[1].value))
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException("3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        if (len(tree.value) > 2):

            mx = interp.getv(interp.interpret(model, args[0]))
            my = interp.getv(interp.interpret(model, args[1]))
            mz = interp.getv(interp.interpret(model, args[2]))

            if not isinstance(mx, numbers.Number):
                raise lce.WrongTypeException("number", type(mx))
            if not isinstance(my, numbers.Number):
                raise lce.WrongTypeException("number", type(my))
            if not isinstance(mz, numbers.Number):
                raise lce.WrongTypeException("number", type(mz))

            m = numpy.identity(4)
            if (mx == 1):
                m[0,0] = -1
            if (my == 1):
                m[1,1] = -1
            if (mz == 1):
                m[2,2] = -1

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["mirror"] = Mirror()


class Rotate(GeometryFunction):
    """
    **rotate** - Rotate child elements.

    Add a rotation to the current transformation matrix, rotation 
    is done first around z, then y and then x. Parts added inside
    a rotate block have this transformation applied to them.

    :param ax: Amount to rotate around the x axis in degrees.
    :param ay: Amount to rotate around the y axis in degrees.
    :param az: Amount to rotate around the z axis in degrees.

    Usage::

     (rotate (0 0 90) .. )

    """
    def __init__(self):
        GeometryFunction.__init__(self, "rotate")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<3):
            raise lce.NumberArgumentsException("2+", 0)
        if not isinstance(flist[1].value, list):
            raise lce.WrongTypeException("list", type(flist[1].value))
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException("3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        if (len(tree.value) > 2):

            ax = interp.getv(interp.interpret(model, args[0]))
            ay = interp.getv(interp.interpret(model, args[1]))
            az = interp.getv(interp.interpret(model, args[2]))

            if not isinstance(ax, numbers.Number):
                raise lce.WrongTypeException("number", type(ax))
            if not isinstance(ay, numbers.Number):
                raise lce.WrongTypeException("number", type(ay))
            if not isinstance(az, numbers.Number):
                raise lce.WrongTypeException("number", type(az))

            ax = ax * numpy.pi / 180.0
            ay = ay * numpy.pi / 180.0
            az = az * numpy.pi / 180.0

            rx = numpy.identity(4)
            rx[1,1] = math.cos(ax)
            rx[1,2] = -math.sin(ax)
            rx[2,1] = -rx[1,2]
            rx[2,2] = rx[1,1]

            ry = numpy.identity(4)
            ry[0,0] = math.cos(ay)
            ry[0,2] = -math.sin(ay)
            ry[2,0] = -ry[0,2]
            ry[2,2] = ry[0,0]

            rz = numpy.identity(4)
            rz[0,0] = math.cos(az)
            rz[0,1] = -math.sin(az)
            rz[1,0] = -rz[0,1]
            rz[1,1] = rz[0,0]

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, (numpy.dot(rx, numpy.dot(ry, rz)))))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["rotate"] = Rotate()


class Scale(GeometryFunction):
    """
    **scale** - Scale child elements.

    Add scale terms to the current transformation matrix. Parts inside a scale
    block have this transformation applied to them. This is probably not a good
    idea for standard parts, but it seems to be used with some part primitives.

    :param sx: Scale in x.
    :param sy: Scale in y.
    :param sz: Scale in z.

    Usage::

     (scale (2 1 1) .. )  ; stretch by a factor of two in the x dimension.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "scale")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<3):
            raise lce.NumberArgumentsException("2+", 1)
        if not isinstance(flist[1].value, list):
            raise lce.WrongTypeException("list", type(flist[1].value))
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException("3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        if (len(tree.value) > 2):

            sx = interp.getv(interp.interpret(model, args[0]))
            sy = interp.getv(interp.interpret(model, args[1]))
            sz = interp.getv(interp.interpret(model, args[2]))

            if not isinstance(sx, numbers.Number):
                raise lce.WrongTypeException("number", type(sx))
            if not isinstance(sy, numbers.Number):
                raise lce.WrongTypeException("number", type(sy))
            if not isinstance(sz, numbers.Number):
                raise lce.WrongTypeException("number", type(sz))

            m = numpy.identity(4)
            m[0,0] = sx
            m[1,1] = sy
            m[2,2] = sz

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["scale"] = Scale()


class Translate(GeometryFunction):
    """
    **translate** - Translate child elements.

    Add a translation to the current transformation matrix. Parts inside a translate
    block have this transformation applied to them.

    :param dx: Displacement in x in LDU.
    :param dy: Displacement in y in LDU.
    :param dz: Displacement in z in LDU.

    Usage::

     (translate (0 0 5) .. )

    """
    def __init__(self):
        GeometryFunction.__init__(self, "translate")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<3):
            raise lce.NumberArgumentsException("2+", 1)
        if not isinstance(flist[1].value, list):
            raise lce.WrongTypeException("list", type(flist[1].value))
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException("3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        if (len(tree.value) > 2):

            mx = interp.getv(interp.interpret(model, args[0]))
            my = interp.getv(interp.interpret(model, args[1]))
            mz = interp.getv(interp.interpret(model, args[2]))

            if not isinstance(mx, numbers.Number):
                raise lce.WrongTypeException("number", type(mx))
            if not isinstance(my, numbers.Number):
                raise lce.WrongTypeException("number", type(my))
            if not isinstance(mz, numbers.Number):
                raise lce.WrongTypeException("number", type(mz))

            m = numpy.identity(4)
            m[0,3] = mx
            m[1,3] = my
            m[2,3] = mz

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["translate"] = Translate()


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
