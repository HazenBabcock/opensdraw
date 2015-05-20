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

def createVectors(matrices, vector):
    vectors = [vector]
    for mm in matrices:
        vectors.append(numpy.dot(mm, vector))
    return vectors

def matrixXVectors(matrix, vectors, truncate = True):
    results_list = []
    if truncate:
        for vec in vectors:
            results_list.append(numpy.dot(matrix, vec)[:3])
    else:
        for vec in vectors:
            results_list.append(numpy.dot(matrix, vec))
    return results_list

def renderShape(curve, group, matrix, vectors, stepper, stop):
    cm = numpy.dot(matrix, stepper.getMatrix())
    last_v = matrixXVectors(cm, vectors)

    n_vert = len(last_v) - 1
    pos = stepper.nextPos()
    while (pos < stop):
        cm = numpy.dot(matrix, stepper.getMatrix())
        cur_v = matrixXVectors(cm, vectors)

        for i in range(n_vert):
            #group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

        pos = stepper.nextPos()
        last_v = cur_v

    cm = numpy.dot(matrix, curve.call(None, stop))
    cur_v = matrixXVectors(cm, vectors)

    for i in range(n_vert):
        #group.addPart(parts.Line(None, numpy.append(last_v[i], cur_v[i]), 16), True)
        group.addPart(parts.Triangle(None, numpy.append(last_v[i], [last_v[i+1], cur_v[i]]), 16), True)
        group.addPart(parts.Triangle(None, numpy.append(last_v[i+1], [cur_v[i+1], cur_v[i]]), 16), True)

def rotationMatrices():
    matrices = []
    d_angle = math.radians(22.5)
    angle = d_angle
    while (angle < (2.0 * math.pi + 0.1 * d_angle)):
        matrices.append(geometry.rotationMatrixZ(angle))
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

        self.mm = curve.call(None, start)

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
            new_mm = self.curve.call(None, cur)
        if (cur > self.stop):
            self.pos = self.stop
        else:
            if ((cur - self.step) > self.pos):
                self.pos = cur - self.step
            else:
                self.pos += self.step
        self.mm = self.curve.call(None, self.pos)
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
    :param orientation: (optional) Angle in degrees in the XY plane.

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
                           [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, curve, start, stop, orientation = 0.0):
        if (orientation != 0.0):
            vectors = matrixXVectors(geometry.rotationMatrixZ(math.radians(orientation)),
                                     self.vectors,
                                     truncate = False)
        else:
            vectors = self.vectors
        
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        cm = numpy.dot(matrix, stepper.getMatrix())
        lastv = matrixXVectors(cm, vectors)
        n_vert = len(lastv) - 1

        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            curv = matrixXVectors(cm, vectors)
            for i in range(n_vert):
                group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
                group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)

            pos = stepper.nextPos()
            lastv = curv

        cm = numpy.dot(matrix, curve.call(None, stop))
        curv = matrixXVectors(cm, vectors)
        for i in range(n_vert):
            group.addPart(parts.Line(None, numpy.append(lastv[i], curv[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(lastv[i], [lastv[i+1], curv[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(lastv[i+1], [curv[i+1], curv[i]]), 16), True)

lcad_functions["axle"] = Axle()


class FlatCable(functions.LCadFunction):
    """
    **flat-cable** - Draw a flat cable (i.e. EV3 or NXT style) using LDraw primitives.

    :param curve: The curve that the cable should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.
    :param width: The width of the cable.
    :param radius: The edge radius of the cable.
    :param orientation: (optional) Angle in degrees in the XY plane, default is 0 (the long axis of the cable is along the X axis).

    The flat cable will have the color 16.

    Usage::

     (flat-cable curve 0 10 4 1) ; Draw a 4 LDU wide flat cable with 1 LDU radius edges.

    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "flat-cable")
        
        self.setSignature([[functions.LCadFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, curve, start, stop, width, radius, orientation = 0.0):
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors for a single segment of the cable.
        x_start = 0.5 * width
        
        cable_vecs = []

        # First edge.
        for i in range(9):
            angle = math.radians(270 - 22.5 * i)
            cable_vecs.append(numpy.array([radius * math.cos(angle) - x_start,
                                           radius * math.sin(angle),
                                           0,
                                           1.0]))

        # Second edge.
        for i in range(9):
            angle = math.radians(90 - 22.5 * i)
            cable_vecs.append(numpy.array([radius * math.cos(angle) + x_start,
                                           radius * math.sin(angle),                                           
                                           0,
                                           1.0]))

        cable_vecs.append(cable_vecs[0])
        cable_vecs.reverse()

        # Rotate the cable if necessary.        
        if (orientation != 0):
            cable_vecs = matrixXVectors(geometry.rotationMatrixZ(math.radians(orientation)),
                                        cable_vecs,
                                        truncate = False)
        
        # Draw the cable.
        renderShape(curve, group, matrix, cable_vecs, stepper, stop)

lcad_functions["flat-cable"] = FlatCable()

    
class RibbonCable(functions.LCadFunction):
    """
    **ribbon-cable** - Draw a ribbon cable using LDraw primitives.

    :param curve: The curve that the cable should follow.
    :param start: The starting point on the curve.
    :param stop: The stopping point on the curve.
    :param strands: The number of strands in the cable.
    :param radius: The radius of a single strand in the cable.
    :param orientation: (optional) Angle in degrees in the XY plane, default is 0 (the long axis of the cable is along the X axis).

    The ribbon cable will have the color 16.

    Usage::

     (ribbon-cable curve 0 10 4 1) ; Draw a 4 stranded ribbon cable with each strand
                                   ; having a radius of 1 LDU.

    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "ribbon-cable")
        
        self.setSignature([[functions.LCadFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, curve, start, stop, strands, radius, orientation = 0.0):
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors for a single segment of the cable.
        cable_width = radius * (strands - 1) * math.sqrt(2)
        x_inc = cable_width/(strands - 1)
        x_start = -0.5 * cable_width

        cable_vecs = []
        cur_x = x_start
        i = 0

        # Up one side.
        while (i < strands):

            # Create vectors for edge cables.
            if (i == 0):
                for j in range(6):
                    angle = math.radians(180.0 - 22.5 * j)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))
            elif (i == (strands - 1)):
                for j in range(6):
                    angle = math.radians(135 - 22.5 * j)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))
                

            # Create vectors for center cables.
            else:
                for j in range(4):
                    angle = math.radians(135 - 22.5 * j)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))

            cur_x += x_inc
            i += 1

        # Down the other.
        while (i > 0):
            cur_x -= x_inc
            i -= 1

            # Create vectors for edge cables.
            if (i == 0):
                for j in range(7):
                    angle = math.radians(-22.5 * j - 45.0)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))
            elif (i == (strands - 1)):
                for j in range(6):
                    angle = math.radians(-22.5 * j)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))
                

            # Create vectors for center cables.
            else:
                for j in range(4):
                    angle = math.radians(-22.5 * j - 45.0)
                    cable_vecs.append(numpy.array([cur_x + radius * math.cos(angle),
                                                   radius * math.sin(angle),
                                                   0,
                                                   1.0]))

        cable_vecs.reverse()
        
        # Rotate the cable if necessary.
        if (orientation != 0):
            cable_vecs = matrixXVectors(geometry.rotationMatrixZ(math.radians(orientation)),
                                        cable_vecs,
                                        truncate = False)
                    
        # Draw the cable.
        renderShape(curve, group, matrix, cable_vecs, stepper, stop)

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
                           [lcadTypes.LCadBoolean]])

    def call(self, model, m1, v1, m2, v2, ccw):
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
        self.setSignature([[functions.LCadFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, curve, start, stop, radius):
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors.
        vectors = createVectors(self.matrices, numpy.array([radius, 0, 0, 1]))

        # Draw.
        renderShape(curve, group, matrix, vectors, stepper, stop)
        
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
        self.setSignature([[functions.LCadFunction],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number],
                           [numbers.Number]])

    def call(self, model, curve, start, stop, inner_radius, outer_radius):
        group = model.curGroup()
        matrix = group.matrix()
        stepper = Stepper(curve, start, stop)

        # Create vectors.
        inner_vecs = createVectors(self.matrices, numpy.array([inner_radius, 0, 0, 1]))
        outer_vecs = createVectors(self.matrices, numpy.array([outer_radius, 0, 0, 1]))
        
        # Starting ring.
        cm = numpy.dot(matrix, stepper.getMatrix())
        last_inner = matrixXVectors(cm, inner_vecs)
        last_outer = matrixXVectors(cm, outer_vecs)

        n_vert = len(last_inner) - 1
        pos = stepper.nextPos()
        while (pos < stop):
            cm = numpy.dot(matrix, stepper.getMatrix())
            cur_inner = matrixXVectors(cm, inner_vecs)
            cur_outer = matrixXVectors(cm, outer_vecs)

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

        cm = numpy.dot(matrix, curve.call(None, stop))
        cur_inner = matrixXVectors(cm, inner_vecs)
        cur_outer = matrixXVectors(cm, outer_vecs)

        for i in range(n_vert):

            # Inner wall.
            group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [last_inner[i], cur_inner[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_inner[i+1], [cur_inner[i], cur_inner[i+1]]), 16), True)

            # Outer wall.
            group.addPart(parts.Line(None, numpy.append(last_outer[i], cur_outer[i]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_outer[i], [last_outer[i+1], cur_outer[i]]), 16), True)
            group.addPart(parts.Triangle(None, numpy.append(last_outer[i+1], [cur_outer[i+1], cur_outer[i]]), 16), True)

lcad_functions["tube"] = Tube()
