#!/usr/bin/env python
"""
.. module:: geometryFunctions
   :synopsis: rotate, translate, etc.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import angles
import functions
import interpreter as interp
import lcadExceptions as lce

lcad_functions = {}


mapping = [[0, (0,3)], [1, (1,3)], [2, (2,3)],
           [3, (0,0)], [ 4, (0,1)], [ 5, (0,2)],
           [6, (1,0)], [ 7, (1,1)], [ 8, (1,2)],
           [9, (2,0)], [10, (2,1)], [11, (2,2)]]

def ldrawCoeffsToMatrix(model, coeffs):

    m = numpy.identity(4)
    for x in mapping:
        val = interp.getv(interp.interpret(model, coeffs[x[0]]))
        if not isinstance(val, numbers.Number):
            raise lce.WrongTypeException("number", type(val))
        m[x[1]] = val
    return m


def parseArgs(model, args):

    val = interp.getv(interp.interpret(model, args))

    # Numpy array. This should be a 4 element vector. A 3 element list will be returned.
    if isinstance(val, numpy.ndarray):
        if (len(val.shape) != 1):
            raise lce.LCadException("Expected a 1D vector, got a " + str(len(val.shape)) + "D matrix.")
        return val.tolist()[0:3]

    # LCad list.
    elif isinstance(val, interp.List):
        if not (val.size > 2):
            raise lce.LCadException("Expected a list with 3+ members, got " + str(val.size))
        ret = []
        for i in range(val.size):
            temp = interp.getv(val.getv(i))
            if not isinstance(temp, numbers.Number):
                raise lce.WrongTypeException("number", type(temp))
            ret.append(temp)
        return ret

    else:
        raise lce.WrongTypeException("list, numpy.ndarray", type(val))

def translationMatrix(tx, ty, tz):
    m = numpy.identity(4)
    m[0,3] = tx
    m[1,3] = ty
    m[2,3] = tz

    return m


class GeometryFunction(functions.LCadFunction):

    def argCheck(self, tree):
        args = tree.value[1:]
        if (len(args) < 2):
            raise lce.NumberArgumentsException("2+", len(args))


class Matrix(GeometryFunction):
    """
    **matrix** - Return a 4 x 4 transform matrix. The matrix is a numpy 
    array. Currently this matrix is immutable, but the plan is to fix this.

    The arguments are (list x y z a b c d e f g h i) as defined here:

    http://www.ldraw.org/article/218.html#lt1

    :param x: translation in x in LDU.
    :param y: translation in y in LDU.
    :param z: translation in z in LDU.
    :param a: m(0,0)
    :param b: m(0,1)
    :param c: m(0,2)
    :param d: m(1,0)
    :param e: m(1,1)
    :param f: m(1,2)
    :param g: m(2,0)
    :param h: m(2,1)
    :param i: m(2,2)

    Alternatively, you can provide the list (x y z ax ay ax).

    :param x: translation in x in LDU.
    :param y: translation in y in LDU.
    :param z: translation in z in LDU.
    :param ax: rotation angle around x axis (degrees).
    :param ay: rotation angle around y axis (degrees).
    :param az: roration angle around z axis (degrees).

    Usage::

     (def m (matrix (list x y z a b c d e f g h i))) ; Supply all the coefficients.
     (def m (matrix (list x y z ax ay az)))          ; Supply translation & rotation values.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "matrix")

    def argCheck(self, tree):
        args = tree.value[1:]
        if (len(args) != 1):
            raise lce.NumberArgumentsException("1", len(args))

    def call(self, model, tree):
        vals = parseArgs(model, tree.value[1])
        
        # 12 elements.
        if (len(vals) == 12):
            m = numpy.identity(4)
            for i in range(12):
                m[mapping[i][1]] = vals[i]
            return m

        # 6 elements.
        elif (len(vals) == 6):
            return numpy.dot(translationMatrix(*vals[0:3]), angles.rotationMatrix(*vals[3:6]))

        else:
            raise lce.LCadException("Expected a list with 6 or 12 members, got " + str(len(vals)))
            

lcad_functions["matrix"] = Matrix()


class Mirror(GeometryFunction):
    """
    **mirror** - Mirror child elements on a plane through the origin.

    The arguments are (list mx my mz), or (vector mx my mz).

    :param mx: mirror on x axis.
    :param my: mirror on y axis.
    :param mz: mirror on z axis.

    Usage::

     (mirror (list 1 0 0) ..) ; mirrors on the x axis.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "mirror")

    def call(self, model, tree):
        if (len(tree.value) > 2):
            [mx, my, mz] = parseArgs(model, tree.value[1])

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

    The arguments are (list ax ay az), or (vector ax ay az).

    :param ax: Amount to rotate around the x axis in degrees.
    :param ay: Amount to rotate around the y axis in degrees.
    :param az: Amount to rotate around the z axis in degrees.

    Usage::

     (rotate (list 0 0 90) .. )
     (rotate (vector 0 0 90) .. )

    """
    def __init__(self):
        GeometryFunction.__init__(self, "rotate")

    def call(self, model, tree):
        if (len(tree.value) > 2):
            m = angles.rotationMatrix(*parseArgs(model, tree.value[1]))
            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
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

    The arguments are (list sx sy sz), or (vector sx sy sz).

    :param sx: Scale in x.
    :param sy: Scale in y.
    :param sz: Scale in z.

    Usage::

     (scale (list 2 1 1) .. )  ; stretch by a factor of two in the x dimension.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "scale")

    def call(self, model, tree):
        if (len(tree.value) > 2):
            [sx, sy, sz] = parseArgs(model, tree.value[1])

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


class Transform(GeometryFunction):
    """
    **transform** - Sometimes it is just easier to enter the transform 
    matrix in LDraw form i.e. (list x y z a b c d e f g h i) as defined here:

    http://www.ldraw.org/article/218.html#lt1

    :param x: translation in x in LDU.
    :param y: translation in y in LDU.
    :param z: translation in z in LDU.
    :param a: m(0,0)
    :param b: m(0,1)
    :param c: m(0,2)
    :param d: m(1,0)
    :param e: m(1,1)
    :param f: m(1,2)
    :param g: m(2,0)
    :param h: m(2,1)
    :param i: m(2,2)

    Alternatively, you can provide a previously created 4x4 transform matrix.

    Usage::

     (transform (list x y z a b c d e f g h i) ; Supply all the coefficients.
      ..)
     (transform mat                            ; Supply a standard 4x4 transform matrix.
      ..)
    """
    def __init__(self):
        GeometryFunction.__init__(self, "transform")


    def call(self, model, tree):
        if (len(tree.value) > 2):
            
            val = interp.getv(interp.interpret(model, tree.value[1]))

            # Transform matrix.
            if isinstance(val, numpy.ndarray):
                if (len(val.shape) != 2):
                    raise lce.LCadException("Expected a 2D vector, got a " + str(len(val.shape)) + "D matrix.")
                m = val

            # LCad list.
            elif isinstance(val, interp.List):
                if not (val.size == 12):
                    raise lce.LCadException("Expected a list with 12 members, got " + str(val.size))
                m = numpy.identity(4)
                for i in range(12):
                    temp = interp.getv(val.getv(i))
                    if not isinstance(temp, numbers.Number):
                        raise lce.WrongTypeException("number", type(temp))
                    m[mapping[i][1]] = temp

            else:
                raise lce.WrongTypeException("list, numpy.ndarray", type(val))

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["transform"] = Transform()


class Translate(GeometryFunction):
    """
    **translate** - Translate child elements.

    Add a translation to the current transformation matrix. Parts inside a translate
    block have this transformation applied to them.

    The arguments are (list dx dy dz), or (vector dx dy dz).

    :param dx: Displacement in x in LDU.
    :param dy: Displacement in y in LDU.
    :param dz: Displacement in z in LDU.

    Usage::

     (translate (list 0 0 5) .. )

    """
    def __init__(self):
        GeometryFunction.__init__(self, "translate")

    def call(self, model, tree):

        if (len(tree.value) > 2):
            m = translationMatrix(*parseArgs(model, tree.value[1]))

            cur_matrix = model.curGroup().matrix().copy()
            model.curGroup().setMatrix(numpy.dot(cur_matrix, m))
            val = interp.interpret(model, tree.value[2:])
            model.curGroup().setMatrix(cur_matrix)
            return val
        else:
            return None

lcad_functions["translate"] = Translate()


class Vector(GeometryFunction):
    """
    **vector** - Return a 4 element position vector. The vector is a 
    numpy array. Currently this vector is immutable, but the plan is 
    to fix this.

    :param x: x in LDU.
    :param y: y in LDU.
    :param z: z in LDU.

    The 4th element of the vector is always 1.0.

    Usage::

     (def v (vector 0 0 5))

    """
    def __init__(self):
        GeometryFunction.__init__(self, "vector")

    def argCheck(self, tree):
        args = tree.value[1:]
        if (len(args) != 3):
            raise lce.NumberArgumentsException("3", len(args))

    def call(self, model, tree):
        args = tree.value[1:]
        vals = []
        for arg in args:
            val = interp.getv(interp.interpret(model, arg))
            if not isinstance(val, numbers.Number):
                raise lce.WrongTypeException("number", type(val))
            vals.append(val)

        vals.append(1.0)
        return numpy.array(vals)

lcad_functions["vector"] = Vector()


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
