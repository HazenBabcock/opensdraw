#!/usr/bin/env python
"""
.. module:: knots
   :synopsis: Python functions to create knots.

.. moduleauthor:: Hazen Babcock
"""

import math
import numbers
import numpy
import os

import opensdraw.lcad_language.angles as angles
import opensdraw.lcad_language.curve as curve
import opensdraw.lcad_language.curveFunctions as curveFunctions
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.interpreter as interpreter

lcad_functions = {}


class SheetBendKnot(functions.LCadFunction):
    """
    **sheet-bend-knot** - Creates a sheet bend knot function.

    This creates and returns a function that parametrizes a sheet bend knot. All
    units are LDU.

    When you call the created function you will get the 6 element list *(x y z rx ry rz)*
    where x, y, z are the location along the knot and rx, ry, rz are the angles that
    will rotate from the current coordinate system to the knot coordinate system. In the
    knot coordinate system z is along the knot, x is in the plane of the knot and y is
    perpendicular to the plane of the knot.

    :param diameter: The diameter of the string.
    :param loop_size: The diameter of the loop.

    Usage::

     (def sbk (sheet-bend-knot 3 10)) ; A knot with 3 LDU diameter string and loop diameter of 10.
     (def p1 (sbk 1))                 ; p1 is the list (x y z rx ry rz) which defines the
                                      ; knot at distance 1 along the knot.
     (sbk t)                          ; Returns the length of the knot.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "sheet-bend-knot")
        
        self.setSignature([[numbers.Number], [numbers.Number]])

    def call(self, model, tree):
        [diameter, loop_size] = self.getArgs(model, tree)

        sbknot = SBKnot(diameter, loop_size)
        
        return curveFunctions.CurveFunction(sbknot, "user created sheet bend knot function.")


lcad_functions["sheet-bend-knot"] = SheetBendKnot()


#
# The sheet bend knot is created using two custom curves and a large loop.
#
class SBKnot(object):

    def __init__(self, diameter, loop_size):
        self.loop_size = loop_size
        self.scale = diameter

        # Curve 1.
        cpts1 = []
        cpts1.append(curve.ControlPoint(0, 0, 0, 0, 0, 1, 1, 0, 0))
        cpts1.append(curve.ControlPoint(2, 0, 6, 1, 0, 1))
        c1_fname = os.path.join(os.path.dirname(__file__), "sbk_curve1.txt")
        self.curve1 = KnotCurve(c1_fname, cpts1)
        self.curve1_stop = self.curve1.getLength() * self.scale

        self.seg1_stop = self.curve1_stop + 0.5 * self.loop_size - self.scale * math.sqrt(2*2 + 2*2)
        self.seg1_x_start = 2 * self.scale
        self.seg1_z_start = 6 * self.scale
        self.seg1_dx = 1.0/math.sqrt(2)
        self.seg1_dz = 1.0/math.sqrt(2)

        # This (sort of) handles small loops.
        if (self.seg1_stop < self.curve1_stop):
            self.curve1_stop = self.seg1_stop

        # Loop.
        self.loop_stop = self.seg1_stop + 0.75 * math.pi * self.loop_size
        self.loop_cx = 0
        self.loop_cz = math.sqrt(2) * 0.5 * self.loop_size + self.scale * 4

        # Straight segment 2.
        self.seg2_stop = self.loop_stop + 0.5 * self.loop_size - self.scale * math.sqrt(2*2 + 2*2)
        self.seg2_x_start = self.loop_cx - 0.5 * self.loop_size / math.sqrt(2)
        self.seg2_z_start = self.loop_cz - 0.5 * self.loop_size / math.sqrt(2)
        self.seg2_dx = 1.0/math.sqrt(2)
        self.seg2_dz = -1.0/math.sqrt(2)
        
        #Curve 2.
        cpts2 = []
        cpts2.append(curve.ControlPoint(-2, 0, 6, 1, 0, -1, -1, 0, 0))
        cpts2.append(curve.ControlPoint(-1, 0, 5, 1, 0, -1))
        cpts2.append(curve.ControlPoint(0.5, -0.8, 3.5, 1, 0, -1))
        cpts2.append(curve.ControlPoint(1, 0, 2.5, 0, 1, 0))
        cpts2.append(curve.ControlPoint(0, 0.8, 2, -1, 0, 0))
        cpts2.append(curve.ControlPoint(-0.8, 0, 2.2, 0, -1, 0))
        cpts2.append(curve.ControlPoint(-0.8, -1.2, 3.5, 0.2, 0, 1))
        cpts2.append(curve.ControlPoint(0.2, 0, 5.1, 0, 1, 0))
        cpts2.append(curve.ControlPoint(1.2, 0.8, 4.1, 1, -0.2, -1.2))
        cpts2.append(curve.ControlPoint(2, 0, 2.5, 0, -1, -1))
        cpts2.append(curve.ControlPoint(0, -0.9, 2.7, -1, 0.3, 1))
        cpts2.append(curve.ControlPoint(-1.5, 0, 4.2, -1, 0, 1))
        cpts2.append(curve.ControlPoint(-5, 0, 5.5, -1, 0, 0))
        c2_fname = os.path.join(os.path.dirname(__file__), "sbk_curve2.txt")
        self.curve2 = KnotCurve(c2_fname, cpts2)
        self.curve2_stop = self.seg2_stop + self.curve2.getLength() * self.scale

        self.length = self.curve2_stop
        
    def getCoords(self, dist):
        if (dist < self.curve1_stop):
            [x, y, z, rx, ry, rz] = self.curve1.getCoords(dist / self.scale)
            return [x * self.scale, y * self.scale, z * self.scale, rx, ry, rz]

        if (dist < self.seg1_stop):
            dist -= self.curve1_stop
            x = self.seg1_x_start + self.seg1_dx * dist
            z = self.seg1_z_start + self.seg1_dz * dist
            y_vec = [0, 0, 1]
            z_vec = [self.seg1_dx, 0, self.seg1_dz]
            x_vec = numpy.cross(y_vec, z_vec)
            [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)
            return [x, 0, z, rx, ry, rz]

        if (dist < self.loop_stop):
            dist -= self.seg1_stop
            angle = 0.75 * math.pi - 2.0 * dist/self.loop_size 
            x = self.loop_cx + 0.5 * self.loop_size * math.sin(angle)
            z = self.loop_cz + 0.5 * self.loop_size * math.cos(angle)
            dx = math.cos(angle)
            dz = -math.sin(angle)
            y_vec = [0, 0, 1]
            z_vec = [-dx, 0, -dz]
            x_vec = numpy.cross(y_vec, z_vec)
            [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)
            return [x, 0, z, rx, ry, rz]

        if (dist < self.seg2_stop):
            dist -= self.loop_stop
            x = self.seg2_x_start + self.seg2_dx * dist
            z = self.seg2_z_start + self.seg2_dz * dist
            y_vec = [0, 0, 1]
            z_vec = [self.seg2_dx, 0, self.seg2_dz]
            x_vec = numpy.cross(y_vec, z_vec)
            [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)
            return [x, 0, z, rx, ry, rz]

        dist -= self.seg2_stop
        [x, y, z, rx, ry, rz] = self.curve2.getCoords(dist / self.scale)
        return [x * self.scale, y * self.scale, z * self.scale, rx, ry, rz]

    def getLength(self):
        return self.length


def saveControlPoint(fp, cp):
    fp.write(" ".join(map(str, cp.location.tolist())))
    fp.write(" ")
    fp.write(" ".join(map(str, cp.raw_z_vec.tolist())))
    if cp.x_vec is not None:
        fp.write(" ")
        fp.write(" ".join(map(str, cp.x_vec.tolist())))
    fp.write("\n")


class KnotControlPoint(curve.ControlPoint):
    """
    Load and save control point from a file as an optimization.
    """
    def __init__(self, data):
        vals = map(float, data.split(" "))
        curve.ControlPoint.__init__(self, *vals)


class KnotCurve(curve.Curve):

    def __init__(self, filename, control_points):

        # Load control points from file.
        if os.path.exists(filename):
            curve.Curve.__init__(self, False, True, 1.0, 0.0)

            control_points = []
            with open(filename) as fp:
                for line in fp:
                    control_points.append(KnotControlPoint(line))

            i = 0
            while (i < len(control_points)):
                self.addSegment(control_points[i], control_points[i+1])
                i += 2

        # Calculate control points & save to file.
        else:
            curve.Curve.__init__(self, True, True, 1.0, 0.0)

            with open(filename, "w") as fp:
                for i in range(len(control_points)-1):
                    self.addSegment(control_points[i], control_points[i+1])
                    saveControlPoint(fp, control_points[i])
                    saveControlPoint(fp, control_points[i+1])


#
# Testing
#
if (__name__ == "__main__"):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    knot = SBKnot(1, 2)

    fig = plt.figure()
    axis = fig.gca(projection='3d')
    MAX = 10
    for direction in (-1, 1):
        for point in numpy.diag(direction * MAX * numpy.array([1,1,1])):
            axis.plot([point[0]], [point[1]], [point[2]], 'w')

    if 0:
        d = numpy.linspace(0, knot.length, 50)
        x = numpy.zeros(d.size)
        y = numpy.zeros(d.size)
        z = numpy.zeros(d.size)
        for i in range(d.size):
            x[i], y[i], z[i] = knot.getCoords(d[i])[:3]
        axis.plot(x, y, z)
        #axis.scatter(x, y, z)

    if 1:
        vlen = 0.25
        #d = numpy.linspace(0, 20.0 + belt.getLength(), 40) - 10.0
        d = numpy.linspace(0, knot.getLength(), 200)
        for i in range(d.size):
            [x, y, z, rx, ry, rz] = knot.getCoords(d[i])
            m = angles.rotationMatrix(rx, ry, rz)
            vx = numpy.dot(m, numpy.array([vlen, 0, 0, 1]))
            vy = numpy.dot(m, numpy.array([0, vlen, 0, 1]))
            vz = numpy.dot(m, numpy.array([0, 0, vlen, 1]))

            for elt in [[vx, "red"], [vy, "green"], [vz, "blue"]]:
                axis.plot([x, x + elt[0][0]],
                          [y, y + elt[0][1]],
                          [z, z + elt[0][2]],
                          color = elt[1])

    plt.show()

