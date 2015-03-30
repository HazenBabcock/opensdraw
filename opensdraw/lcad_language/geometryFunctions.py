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
import lcadTypes

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


def parseArgs(val):
    """
    This is used by most of the geometry and part functions to parse list or vectors.
    The list / vector is truncated to 3 elements, as this is what they all use.
    """

    # Numpy array.
    if isinstance(val, numpy.ndarray):
        if (len(val.shape) != 1):
            raise lce.LCadException("Expected a 1D vector, got a " + str(len(val.shape)) + "D matrix.")
        if (val.size < 3):
            raise lce.LCadException("Expected a vector with 3+ members, got " + str(val.size))
        return val.tolist()[0:3]

    # LCad list.
    if isinstance(val, list):
        if (len(val) < 3):
            raise lce.LCadException("Expected a list with 3+ members, got " + str(val.size))
        for elt in val:
            if not isinstance(elt, numbers.Number):
                raise lce.WrongTypeException("number", type(elt))
        return val[0:3]

    raise lce.WrongTypeException("list, vector", type(val))

def translationMatrix(tx, ty, tz):
    m = numpy.identity(4)
    m[0,3] = tx
    m[1,3] = ty
    m[2,3] = tz

    return m


class GeometryFunction(functions.LCadFunction):
    pass


class CrossProduct(GeometryFunction):
    """
    **cross-product** - Return the cross product of two vectors.

    :param v1: The first vector.
    :param v2: The second vector.
    :param normalize: t/nil (Optional) Normalize the result vector, default is t.

    Usage::

     (cross-product (vector 1 0 0) (vector 0 1 0))     ; Returns (vector 0 0 1)
     (cross-product (vector 1 0 0) (vector 0 2 0) nil) ; Returns (vector 0 0 2)

    """
    def __init__(self):
        GeometryFunction.__init__(self, "cross-product")
        self.setSignature([[lcadTypes.LCadVector], [lcadTypes.LCadVector], ["optional", [lcadTypes.LCadObject]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)

        normalize = True
        if (len(args) == 3):
            normalize = True if functions.isTrue(args[2]) else False

        cp = numpy.cross(args[0][0:3], args[1][0:3])
        
        if normalize:
            cp = cp/numpy.linalg.norm(cp)

        cp = numpy.append(cp, 1)
        return cp.view(lcadTypes.LCadVector)

lcad_functions["cross-product"] = CrossProduct()


class DotProduct(GeometryFunction):
    """
    **dot-product** - Return the dot product of two vectors.

    :param v1: The first vector.
    :param v2: The second vector.

    Usage::

     (dot-product (vector 1 0 0) (vector 1 0 0))  ; Returns 1.
     (dot-product (vector 1 0 0) (vector 0 1 0))  ; Returns 0.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "dot-product")
        self.setSignature([[lcadTypes.LCadVector], [lcadTypes.LCadVector]])

    def call(self, model, tree):
        [v1, v2] = self.getArgs(model, tree)

        # Ignore 4th element.
        v1 = v1[0:3]
        v2 = v2[0:3]
        return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

lcad_functions["dot-product"] = DotProduct()


class Matrix(GeometryFunction):
    """
    **matrix** - Return a 4 x 4 transform matrix. 

    The matrix is a numpy array. The arguments are (list x y z a b c d e f g h i) as defined here:

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
    :param az: rotation angle around z axis (degrees).

    Usage::

     (def m (matrix (list x y z a b c d e f g h i))) ; Supply all the coefficients.
     (def m (matrix (list x y z ax ay az)))          ; Supply translation & rotation values.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "matrix")
        self.setSignature([[list]])

    def call(self, model, tree):
        vals = self.getArg(model, tree, 0)

        # Check that the elements have the right type.
        for elt in vals:
            if not isinstance(elt, numbers.Number):
                raise lce.WrongTypeException("number", type(elt))

        # 12 elements.
        if (len(vals) == 12):
            m = numpy.identity(4)
            for i in range(12):
                m[mapping[i][1]] = vals[i]
            return m.view(lcadTypes.LCadMatrix)

        # 6 elements.
        elif (len(vals) == 6):
            return numpy.dot(translationMatrix(*vals[0:3]), angles.rotationMatrix(*vals[3:6])).view(lcadTypes.LCadMatrix)

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
        self.setSignature([[list, lcadTypes.LCadVector], ["optional", [object]]])

    def call(self, model, tree):
        if (self.numberArgs(tree) > 1):
            [mx, my, mz] = parseArgs(self.getArg(model, tree, 0))

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
        self.setSignature([[list, lcadTypes.LCadVector], ["optional", [object]]])

    def call(self, model, tree):
        if (self.numberArgs(tree) > 1):
            m = angles.rotationMatrix(*parseArgs(self.getArg(model, tree, 0)))
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
        self.setSignature([[list, lcadTypes.LCadVector], ["optional", [object]]])

    def call(self, model, tree):
        if (self.numberArgs(tree) > 1):
            [sx, sy, sz] = parseArgs(self.getArg(model, tree, 0))

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
    **transform** - Transform child elements.

    Sometimes it is just easier to enter the transform 
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
        self.setSignature([[list, lcadTypes.LCadMatrix], ["optional", [object]]])

    def call(self, model, tree):
        if (self.numberArgs(tree) > 1):
            
            val = self.getArg(model, tree, 0)

            # Transform matrix.
            if isinstance(val, numpy.ndarray):
                if (len(val.shape) != 2):
                    raise lce.LCadException("Expected a 2D matrix, got a " + str(len(val.shape)) + "D matrix.")
                m = val

            # LCad list.
            elif isinstance(val, list):
                if not (len(val) == 12):
                    raise lce.LCadException("Expected a list with 12 members, got " + str(len(val)))
                m = numpy.identity(4)
                for i in range(len(val)):
                    if not isinstance(val[i], numbers.Number):
                        raise lce.WrongTypeException("number", type(val[i]))
                    m[mapping[i][1]] = val[i]

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
        self.setSignature([[list, lcadTypes.LCadVector], ["optional", [object]]])

    def call(self, model, tree):

        if (self.numberArgs(tree) > 1):
            m = translationMatrix(*parseArgs(self.getArg(model, tree, 0)))

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
    **vector** - Create a 4 element vector. 

    This is a numpy array. It can be used in place of a list for most of the geometry
    functions like rotate() and translate(). You can also multiply it with
    4 x 4 transformation matrices.

    :param e1: The first element in the vector.
    :param e2: The second element in the vector.
    :param e3: The third element in the vector.
    :param e4: (Optional) The fourth element in the vector, defaults to 1.0.

    Usage::

     (def v (vector 0 0 5))  ; Create the vector [0 0 5 1]
     (translate v .. )       ; Translate by 5 LDU in z.
     (* mat v)               ; Multiply the vector with the 4 x 4 matrix mat.

    """
    def __init__(self):
        GeometryFunction.__init__(self, "vector")
        self.setSignature([[numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        vals = []
        for arg in args:
            vals.append(arg)
        if (len(vals) == 3):
            vals.append(1.0)

        return numpy.array(vals).view(lcadTypes.LCadVector)

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
