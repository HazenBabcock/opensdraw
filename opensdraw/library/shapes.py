#!/usr/bin/env python
"""
.. module:: shapes
   :synopsis: Python functions to create simple shapes from LDraw primitives.

.. moduleauthor:: Hazen Babcock
"""

import math
import numpy

import opensdraw.lcad_language.angles as angles
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.geometryFunctions as geometryFunctions
import opensdraw.lcad_language.interpreter as interpreter
import opensdraw.lcad_language.parts as parts

lcad_functions = {}


class Ring(functions.LCadFunction):
    """
    **ring** - Fast (relatively speaking) ring drawing using LDraw primitives.

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

        d_angle = math.radians(22.5)
        p1 = numpy.dot(m1, v1)
        p2 = numpy.dot(m2, v2)
        az = d_angle
        while (az < (2.0 * math.pi + 0.1 * d_angle)):
            mz = numpy.identity(4)
            mz[0,0] = math.cos(az)
            mz[0,1] = -math.sin(az)
            mz[1,0] = -mz[0,1]
            mz[1,1] = mz[0,0]
            
            p3 = numpy.dot(m1, numpy.dot(mz, v1))
            p4 = numpy.dot(m2, numpy.dot(mz, v2))
            if ccw is interpreter.lcad_t:
                group.addPart(parts.Triangle(None, numpy.append(p1[0:3], [p2[0:3], p3[:3]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(p3[0:3], [p2[0:3], p4[:3]]), 16), True)
            else:
                group.addPart(parts.Triangle(None, numpy.append(p2[:3], [p1[:3], p3[:3]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(p2[:3], [p3[:3], p4[:3]]), 16), True)

            p1 = p3
            p2 = p4

            az += d_angle

lcad_functions["ring"] = Ring()

