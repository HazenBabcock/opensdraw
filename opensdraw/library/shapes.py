#!/usr/bin/env python
"""
.. module:: shapes
   :synopsis: Python functions to create simple shapes from LDraw primitives.

.. moduleauthor:: Hazen Babcock
"""

import math
import numbers
import numpy

import opensdraw.lcad_language.angles as angles
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.geometryFunctions as geometryFunctions
import opensdraw.lcad_language.interpreter as interpreter
import opensdraw.lcad_language.parts as parts

lcad_functions = {}


def rotationMatrices():
    matrices = []
    d_angle = math.radians(22.5)
    angle = d_angle
    while (angle < (2.0 * math.pi + 0.1 * d_angle)):
        mz = numpy.identity(4)
        mz[0,0] = math.cos(angle)
        mz[0,1] = -math.sin(angle)
        mz[1,0] = -mz[0,1]
        mz[1,1] = mz[0,0]
        matrices.append(mz)
        angle += d_angle
    return matrices


def transformMatrix(posori):
    return numpy.dot(geometryFunctions.translationMatrix(*posori[0:3]),
                     angles.rotationMatrix(*posori[3:6]))


class Axle(functions.LCadFunction):
    """
    **axle** - Draw an axle using LDraw primitives.
    
    :param curve: The curve that the axle should follow.
    :param start: The starting point on the curve.
    :param stop: The ending point on the curve.

    The axle will have the color 16.

    Usage::

     (axle curve 0 10) ; Draw an axle along curve from 0 to 10 (LDU).

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "axle")

        self.vectors = [numpy.array([6, 0, 0, 1]),
                        numpy.array([5.602, 2, 0, 1]),
                        numpy.array([2, 2, 0, 1]),
                        numpy.array([2, 5.602, 0, 1]),
                        numpy.array([0, 6, 0, 1]),
                        numpy.array([-2, 5.602, 0, 1]),
                        numpy.array([-2, 2, 0, 1]),
                        numpy.array([-5.602, 2, 0, 1]),
                        numpy.array([-6, 0, 0, 1]),
                        numpy.array([-5.602, -2, 0, 1]),
                        numpy.array([-2, -2, 0, 1]),
                        numpy.array([-2, -5.602, 0, 1]),
                        numpy.array([0, -6, 0, 1]),
                        numpy.array([2, -5.602, 0, 1]),
                        numpy.array([2, -2, 0, 1]),
                        numpy.array([5.602, -2, 0, 1]),
                        numpy.array([6, 0, 0, 1])]

        self.setSignature([[functions.LCadFunction],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, tree):
        [curve, start, stop] = self.getArgs(model, tree)
        
        group = model.curGroup()
        matrix = group.matrix()

        lastv = []
        cm = numpy.dot(matrix, transformMatrix(curve.getPosOrientation(start)))
        for vec in self.vectors:
            lastv.append(numpy.dot(cm, vec)[:3])
        n_vert = len(lastv) - 1

        d_pos = 4.0
        pos = start + d_pos
        while (pos < stop):
            cm = numpy.dot(matrix, transformMatrix(curve.getPosOrientation(pos)))
            curv = []
            for vec in self.vectors:
                curv.append(numpy.dot(cm, vec)[:3])
            for i in range(n_vert):
                group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)
            lastv = curv
            pos += d_pos

        if (pos != stop):
            cm = numpy.dot(matrix, transformMatrix(curve.getPosOrientation(stop)))
            curv = []
            for vec in self.vectors:
                curv.append(numpy.dot(cm, vec)[:3])
            for i in range(n_vert):
                group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)

lcad_functions["axle"] = Axle()


class Ring(functions.LCadFunction):
    """
    **ring** - Draw a ring using LDraw primitives.

    :param m1: Transform matrix for the first edge of the ring.
    :param v1: Vector for the first edge of the ring.
    :param m2: Transform matrix for the second edge of the ring.
    :param v2: Vector for the second edge of the ring.
    :param ccw: Counterclockwise winding (t/nil).

    The ring will have the color 16.
    
    Usage::

     (ring m1 v1 m2 v2 t)  ; Draw a ring with edge 1 defined by m1, v1
                           ; and edge 2 defined by m2, v2, with ccw winding.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "ring")

        self.matrices = rotationMatrices()
        self.setSignature([[geometryFunctions.LCadMatrix],
                           [geometryFunctions.LCadVector],
                           [geometryFunctions.LCadMatrix],
                           [geometryFunctions.LCadVector],
                           [interpreter.LObject]])

    def call(self, model, tree):
        [m1, v1, m2, v2, ccw] = self.getArgs(model, tree)

        group = model.curGroup()
        matrix = group.matrix()

        m1 = numpy.dot(matrix, m1)
        m2 = numpy.dot(matrix, m2)

        p1 = numpy.dot(m1, v1)
        p2 = numpy.dot(m2, v2)
        if ccw is interpreter.lcad_t:
            for mz in self.matrices:            
                p3 = numpy.dot(m1, numpy.dot(mz, v1))
                p4 = numpy.dot(m2, numpy.dot(mz, v2))
                group.addPart(parts.Triangle(None, numpy.append(p1[0:3], [p2[0:3], p3[:3]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(p3[0:3], [p2[0:3], p4[:3]]), 16), True)
                p1 = p3
                p2 = p4
        else:
            for mz in self.matrices:            
                p3 = numpy.dot(m1, numpy.dot(mz, v1))
                p4 = numpy.dot(m2, numpy.dot(mz, v2))
                group.addPart(parts.Triangle(None, numpy.append(p2[:3], [p1[:3], p3[:3]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(p2[:3], [p3[:3], p4[:3]]), 16), True)
                p1 = p3
                p2 = p4

lcad_functions["ring"] = Ring()

