#!/usr/bin/env python
"""
.. module:: belt
   :synopsis: The belt function.

.. moduleauthor:: Hazen Babcock
"""

import math
import numbers
import numpy

import angles
import curveFunctions
import functions
import interpreter as interp
import lcadExceptions
import lcadTypes

lcad_functions = {}


#
# These classes create a belt function that can be used in opensdraw.
#
class LCadBelt(functions.LCadFunction):
    """
    **belt** - Creates a belt function.

    This function creates and returns a function that parametrizes a belt
    making it easier to add custom belts / chains to a MOC. Unlike the
    chain function this allows for (almost) arbitrary locations and 
    orientations of the pulleys / sprockets. All units are in LDU.

    The belt goes around each sprocket in the counter-clockwise direction.

    Usage::

     ...

    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "belt")
        self.setSignature([[numbers.Number], [numbers.Number], [numbers.Number], [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)

        # Return belt function.
        return curveFunctions.CurveFunction(belt, "user created belt function.")

lcad_functions["belt"] = LCadBelt()


#
# The classes below do the math necessary to create a belt.
#
class Belt(object):

    def __init__(self):
        pass

    def getCoords(self, distance):
        """
        Return the position and orientation for a segment at distance along the spring.
        The z-axis points along the spring. The x-axis is the radial direction.
        """
        pass

    def getLength(self):
        return self.length


class Sprocket(object):
    def __init__(self, coords, radius):
        self.matrix = numpy.zeros((3,3))
        self.n_vec = None
        self.pos = numpy.array(coords[:3])
        self.radius = radius
        self.z_vec = numpy.array(coords[3:])
        
        self.z_vec = self.z_vec/numpy.linalg.norm(self.z_vec)

    #
    # Calculate the tangent line between the current and the next sprocket.
    #
    def calcTangent(self, next_sp):
        self.leave_angle = 0

        # Calculate angle offset for the next sprocket.
        p_vec = next_sp.pos - self.pos
        p_angle = math.atan2(numpy.dot(next_sp.x_vec, p_vec),
                             numpy.dot(next_sp.y_vec, p_vec))
        next_sp.enter_angle = -p_angle

        for i in range(5):
            leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
            enter_vec = next_sp.rotateVector(numpy.array([next_sp.radius, 0, 0]), next_sp.enter_angle)
            t_vec = (next_sp.pos + enter_vec) - (self.pos + leave_vec)
            t_vec = t_vec/numpy.linalg.norm(t_vec)
            
            d_leave = math.acos(numpy.dot(t_vec, leave_vec)/numpy.linalg.norm(leave_vec)) - 0.5 * math.pi
            self.leave_angle += d_leave

            d_enter = math.acos(numpy.dot(t_vec, enter_vec)/numpy.linalg.norm(enter_vec)) - 0.5 * math.pi
            next_sp.enter_angle += d_enter

            if (abs(d_leave) < 1.0e-3) and (abs(d_enter) < 1.0e-3):
                break

    #
    # z_vec points up.
    # y_vec is in the plane defined by z_vec and the centers of the current and the next sprocket.
    # x_vec is perpendicular to y_vec and z_vec.
    #
    def nextSprocket(self, next_sp):

        # Calculate sprocket coordinate system.
        self.n_vec = next_sp.pos - self.pos
        self.n_vec = self.n_vec/numpy.linalg.norm(self.n_vec)

        self.x_vec = numpy.cross(self.n_vec, self.z_vec)
        self.x_vec = self.x_vec/numpy.linalg.norm(self.x_vec)

        self.y_vec = numpy.cross(self.z_vec, self.x_vec)

        self.matrix[:,0] = self.x_vec
        self.matrix[:,1] = self.y_vec
        self.matrix[:,2] = self.z_vec

    #
    # Rotate vector in the plane of the circle around the circle center.
    #
    def rotateVector(self, vector, az):
        rz = numpy.identity(3)
        rz[0,0] = math.cos(az)
        rz[0,1] = -math.sin(az)
        rz[1,0] = -rz[0,1]
        rz[1,1] = rz[0,0]

        return numpy.dot(self.matrix, numpy.dot(rz, vector))


#
# Testing
#
if (__name__ == "__main__"):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    s1 = Sprocket([0, 0, 0, 0, 0, 1], 1.0)
    s2 = Sprocket([4, -1, 1, 0, -1, 0], 1.0)
    s3 = Sprocket([0, 0, 2, 0, 0, 1], 1.0)
    s4 = Sprocket([4, 1, 1, 0, 1, 0], 1.0)

    s1.nextSprocket(s2)
    s2.nextSprocket(s3)
    s3.nextSprocket(s4)
    s4.nextSprocket(s1)

    s1.calcTangent(s2)
    s2.calcTangent(s3)
    s3.calcTangent(s4)
    s4.calcTangent(s1)

    az = numpy.linspace(0, 2.0 * math.pi, 40)

#    plt.figaspect(1.0)
    fig = plt.figure()
    axis = fig.gca(projection='3d')
#    axis.set_aspect('equal')
    MAX = 6
    for direction in (-1, 1):
        for point in numpy.diag(direction * MAX * numpy.array([1,1,1])):
            axis.plot([point[0]], [point[1]], [point[2]], 'w')
    #mpl.rcParams['legend.fontsize'] = 10

    for sp in [s1, s2, s3, s4]:
        x = numpy.zeros(az.size)
        y = numpy.zeros(az.size)
        z = numpy.zeros(az.size)
        v = numpy.array([sp.radius, 0, 0])
        for i in range(az.size):
            [x[i], y[i], z[i]] = sp.rotateVector(v, az[i]) + sp.pos
            axis.plot(x, y, z)

    for ps in [[s1, s2], [s2, s3], [s3, s4], [s4, s1]]:
    #for ps in [[s1, s2]]:
        ps0 = ps[0]
        ps1 = ps[1]
        leave_vec = ps0.rotateVector(numpy.array([ps0.radius, 0, 0]), ps0.leave_angle)
        enter_vec = ps1.rotateVector(numpy.array([ps1.radius, 0, 0]), ps1.enter_angle) 
        axis.plot([ps0.pos[0] + leave_vec[0], ps1.pos[0] + enter_vec[0]],
                  [ps0.pos[1] + leave_vec[1], ps1.pos[1] + enter_vec[1]],
                  [ps0.pos[2] + leave_vec[2], ps1.pos[2] + enter_vec[2]])

    #axis.legend()

    plt.show()
