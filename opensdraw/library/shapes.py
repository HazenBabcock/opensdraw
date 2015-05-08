#!/usr/bin/env python
"""
.. module:: shapes
   :synopsis: Python functions to create simple shapes from LDraw primitives.

.. moduleauthor:: Hazen Babcock
"""

import math
import numbers
import numpy

import opensdraw.lcad_language.curveFunctions as curveFunctions
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.geometry as geometry
import opensdraw.lcad_language.parts as parts
import opensdraw.lcad_language.lcadTypes as lcadTypes

lcad_functions = {}


#
# Helper functions.
#

def createRing(matrix, vectors):
    ring = []
    for vec in vectors:
        ring.append(numpy.dot(matrix, vec)[:3])
    return ring

def createVectors(matrices, vector):
    vectors = [vector]
    for mm in matrices:
        vectors.append(numpy.dot(mm, vector))
    return vectors

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


#
# Helper classes.
#
class Stepper(object):
    """
    Handles dynamically stepping along the curve 
    to minimize the number of sub-sections.
    """
    def __init__(self, curve, start, stop):
        self.curve = curve
        self.pos = start
        self.step = 1.0
        self.stop = stop

        self.mm = curve.getMatrix(start)

    def anglesDiffer(self, new_mm):
        diff = 0.0
        for i in range(3):
            diff += numpy.dot(self.mm[:3,i], new_mm[:3,i])
        diff = 3.0 - diff
        if (diff > 1.0e-4):
            return True
        else:
            return False

    def getMatrix(self):
        return self.mm

    def nextPos(self):
        cur = self.pos
        new_mm = self.mm
        while (cur < self.stop) and not self.anglesDiffer(new_mm):
            cur += self.step
            new_mm = self.curve.getMatrix(cur)
        if (cur > self.stop):
            self.pos = self.stop
        else:
            if ((cur - self.step) > self.pos):
                self.pos = cur - self.step
            else:
                self.pos += self.step
        self.mm = self.curve.getMatrix(self.pos)
        return self.pos



#
# Opensdraw functions.
#

class Axle(functions.LCadFunction):
    """
    **axle** - Draw an axle using LDraw primitives.
    
    :param curve: The curve that the axle should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.

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

        self.setSignature([[curveFunctions.CurveFunction],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, tree):
        [curve, start, stop] = self.getArgs(model, tree)
        
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        cm = numpy.dot(matrix, stepper.getMatrix())
        lastv = createRing(cm, self.vectors)
        n_vert = len(lastv) - 1

        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            curv = createRing(cm, self.vectors)
            for i in range(n_vert):
                group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)

            pos = stepper.nextPos()
            lastv = curv

        cm = numpy.dot(matrix, curve.getMatrix(stop))
        curv = createRing(cm, self.vectors)
        for i in range(n_vert):
            group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)

lcad_functions["axle"] = Axle()


class RibbonCable(functions.LCadFunction):
    """
    **ribbon-cable** - Draw a ribbon cable using LDraw primitives.

    :param curve: The curve that the cable should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.
    :param strands: The number of strands in the cable.
    :param radius: The radius of a single strand in the cable.

    The ribbon cable will have the color 16.

    Usage::

     (ribbon-cable curve 0 10 4 1) ; Draw a 4 stranded ribbon cable with each strand
                                   ; having a radius of 1 LDU.

    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "ribbon-cable")
        
        self.setSignature([[curveFunctions.CurveFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, tree):
        [curve, start, stop, strands, radius] = self.getArgs(model, tree)

        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors for a single segment of the cable.
        cable_width = radius * (strands - 1) * math.sqrt(2)
        y_inc = cable_width/(strands - 1)
        y_start = -0.5 * cable_width

        print strands, cable_width, y_start
        
        cable_vecs = []
        cur_y = y_start
        i = 0

        # Up one side.
        while (i < strands):

            # Create vectors for edge cables.
            if (i == 0):
                for j in range(6):
                    angle = math.radians(180.0 - 22.5 * j)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))
            elif (i == (strands - 1)):
                for j in range(6):
                    angle = math.radians(135 - 22.5 * j)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))
                

            # Create vectors for center cables.
            else:
                for j in range(4):
                    angle = math.radians(135 - 22.5 * j)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))

            cur_y += y_inc
            i += 1

        # Down the other.
        while (i > 0):
            cur_y -= y_inc
            i -= 1

            # Create vectors for edge cables.
            if (i == 0):
                for j in range(7):
                    angle = math.radians(-22.5 * j - 45.0)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))
            elif (i == (strands - 1)):
                for j in range(6):
                    angle = math.radians(-22.5 * j)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))
                

            # Create vectors for center cables.
            else:
                for j in range(4):
                    angle = math.radians(-22.5 * j - 45.0)
                    cable_vecs.append(numpy.array([radius * math.sin(angle),
                                                   cur_y + radius * math.cos(angle),
                                                   0,
                                                   1.0]))

                    
        # Draw the cable.
        cm = numpy.dot(matrix, stepper.getMatrix())
        last_v = createRing(cm, cable_vecs)

        n_vert = len(last_v) - 1
        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            cur_v = createRing(cm, cable_vecs)

            for i in range(n_vert):
                #group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

            pos = stepper.nextPos()
            last_v = cur_v

        cm = numpy.dot(matrix, curve.getMatrix(stop))
        cur_v = createRing(cm, cable_vecs)

        for i in range(n_vert):
            #group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

lcad_functions["ribbon-cable"] = RibbonCable()

        
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
        self.setSignature([[lcadTypes.LCadMatrix],
                           [lcadTypes.LCadVector],
                           [lcadTypes.LCadMatrix],
                           [lcadTypes.LCadVector],
                           [lcadTypes.LCadObject]])

    def call(self, model, tree):
        [m1, v1, m2, v2, ccw] = self.getArgs(model, tree)

        group = model.curGroup()
        matrix = group.matrix()

        m1 = numpy.dot(matrix, m1)
        m2 = numpy.dot(matrix, m2)

        p1 = numpy.dot(m1, v1)
        p2 = numpy.dot(m2, v2)
        if functions.isTrue(ccw):
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


class Rod(functions.LCadFunction):
    """
    **rod** - Draw a rod using LDraw primitives.

    :param curve: The curve that the rod should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.
    :param radius: The radius of the rod.

    The rod will have the color 16.

    Usage::

     (rod curve 0 10 2) ; Draw a 2 LDU diameter rod from 0 to 10 along curve.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "rod")

        self.matrices = rotationMatrices()
        self.setSignature([[curveFunctions.CurveFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, tree):
        [curve, start, stop, radius] = self.getArgs(model, tree)

        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors.
        vectors = createVectors(self.matrices, numpy.array([radius, 0, 0, 1]))
        
        # Starting ring.
        cm = numpy.dot(matrix, stepper.getMatrix())
        last_v = createRing(cm, vectors)

        n_vert = len(last_v) - 1
        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            cur_v = createRing(cm, vectors)

            for i in range(n_vert):
                group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

            pos = stepper.nextPos()
            last_v = cur_v

        cm = numpy.dot(matrix, curve.getMatrix(stop))
        cur_v = createRing(cm, vectors)

        for i in range(n_vert):
            group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

lcad_functions["rod"] = Rod()


class Tube(functions.LCadFunction):
    """
    **tube** - Draw a tube using LDraw primitives.

    :param curve: The curve that the tube should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.
    :param inner_radius: The inner radius of the tube.
    :param outer_radius: The outer radius of the tube.

    The tube will have the color 16.

    Usage::

     (tube curve 0 10 2 3) ; Draw a 2 LDU inner diameter, 3 LDU outer diameter 
                           ; tube from 0 to 10 along curve.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "tube")

        self.matrices = rotationMatrices()
        self.setSignature([[curveFunctions.CurveFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, tree):
        [curve, start, stop, inner_radius, outer_radius] = self.getArgs(model, tree)

        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors.
        inner_vecs = createVectors(self.matrices, numpy.array([inner_radius, 0, 0, 1]))
        outer_vecs = createVectors(self.matrices, numpy.array([outer_radius, 0, 0, 1]))
        
        # Starting ring.
        cm = numpy.dot(matrix, stepper.getMatrix())
        last_inner = createRing(cm, inner_vecs)
        last_outer = createRing(cm, outer_vecs)

        n_vert = len(last_inner) - 1
        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            cur_inner = createRing(cm, inner_vecs)
            cur_outer = createRing(cm, outer_vecs)

            for i in range(n_vert):

                # Inner wall.
                group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [last_inner[i], cur_inner[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [cur_inner[i], cur_inner[i+1]]), 16), True)

                # Outer wall.
                group.addPart(parts.Line(None, numpy.append(last_outer[i], cur_outer[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_outer[i], [last_outer[i+1], cur_outer[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(last_outer[i+1], [cur_outer[i+1], cur_outer[i]]), 16), True)

            pos = stepper.nextPos()
            last_inner = cur_inner
            last_outer = cur_outer

        cm = numpy.dot(matrix, curve.getMatrix(stop))
        cur_inner = createRing(cm, inner_vecs)
        cur_outer = createRing(cm, outer_vecs)

        for i in range(n_vert):

            # Inner wall.
            group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [last_inner[i], cur_inner[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [cur_inner[i], cur_inner[i+1]]), 16), True)

            # Outer wall.
            group.addPart(parts.Line(None, numpy.append(last_outer[i], cur_outer[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_outer[i], [last_outer[i+1], cur_outer[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_outer[i+1], [cur_outer[i+1], cur_outer[i]]), 16), True)

lcad_functions["tube"] = Tube()
