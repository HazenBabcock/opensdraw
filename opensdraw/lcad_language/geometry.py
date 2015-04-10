#!/usr/bin/env python
"""
.. module:: geometry
   :synopsis: Various geometry related functions.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import interpreter as interp
import lcadExceptions as lce
import lcadTypes


mapping = [[0, (0,3)], [1, (1,3)], [2, (2,3)],
           [3, (0,0)], [ 4, (0,1)], [ 5, (0,2)],
           [6, (1,0)], [ 7, (1,1)], [ 8, (1,2)],
           [9, (2,0)], [10, (2,1)], [11, (2,2)]]


def ldrawCoeffsToMatrix(model, coeffs):

    m = numpy.identity(4).view(lcadTypes.LCadMatrix)
    for x in mapping:
        val = interp.getv(interp.interpret(model, coeffs[x[0]]))
        if not isinstance(val, numbers.Number):
            raise lce.WrongTypeException("number", type(val))
        m[x[1]] = val
    return m


def listToMatrix(a_list):
    if (len(a_list) == 12):
        m = numpy.identity(4).view(lcadTypes.LCadMatrix)
        for i in range(len(a_list)):
            if not isinstance(a_list[i], numbers.Number):
                raise lce.WrongTypeException("number", type(a_list[i]))
            m[mapping[i][1]] = a_list[i]
        return m

    if (len(a_list) == 6):
        return numpy.dot(translationMatrix(*a_list[:3]), rotationMatrix(*a_list[3:])).view(lcadTypes.LCadMatrix)

    raise lce.LCadException("Expected a list with 6 or 12 members, got " + str(len(a_list)))


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


# Mostly used externally, expects angles in degrees.
def rotationMatrix(ax, ay, az):
    ax = math.radians(ax)
    ay = math.radians(ay)
    az = math.radians(az)

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

    return numpy.dot(rx, numpy.dot(ry, rotationMatrixZ(az)))


# Mostly used internally, expects angles in radians.
def rotationMatrixZ(az):
    rz = numpy.identity(4)
    rz[0,0] = math.cos(az)
    rz[0,1] = -math.sin(az)
    rz[1,0] = -rz[0,1]
    rz[1,1] = rz[0,0]

    return rz


def translationMatrix(tx, ty, tz):
    m = numpy.identity(4)
    m[0,3] = tx
    m[1,3] = ty
    m[2,3] = tz

    return m


def vectorsToAngles(x_vec, y_vec, z_vec):
    ry = math.atan2(-z_vec[0], math.sqrt(z_vec[1]*z_vec[1] + z_vec[2]*z_vec[2]))

    # If the rotation around the y axis is +- 90 then we can't separate the x-axis rotation
    # from the z-axis rotation. In this case we just assume that the x-axis rotation is
    # zero and that there was only z-axis rotation.
    if (abs(math.cos(ry)) < 1.0e-3):
        rx = 0
        rz = math.atan2(x_vec[1], y_vec[1])
    else:
        rx = math.atan2(-z_vec[1], z_vec[2])
        rz = math.atan2(-y_vec[0], x_vec[0])

    return map(lambda(x): math.degrees(x), [rx, ry, rz])


def vectorsToMatrix(p_vec, x_vec, y_vec, z_vec):
    m = numpy.identity(4).view(lcadTypes.LCadMatrix)
    m[:3,0] = x_vec
    m[:3,1] = y_vec
    m[:3,2] = z_vec
    m[:3,3] = p_vec
    return m

