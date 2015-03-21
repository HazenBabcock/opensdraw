#!/usr/bin/env python
"""
.. module:: angles
   :synopsis: Functions for converting angles to rotation matrices & vice-versa.

.. moduleauthor:: Hazen Babcock

"""

import math
import numpy


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

    rz = numpy.identity(4)
    rz[0,0] = math.cos(az)
    rz[0,1] = -math.sin(az)
    rz[1,0] = -rz[0,1]
    rz[1,1] = rz[0,0]

    return numpy.dot(rx, numpy.dot(ry, rz))

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

    return map(lambda(x): x * 180.0/math.pi, [rx, ry, rz])
