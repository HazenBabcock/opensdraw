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
# The classes below do the math necessary to create a belt / chain.
#
class Belt(object):
    """
    Belt/chain.
    """
    def __init__(self, continuous):
        self.continuous = continuous
        self.dists = []
        self.length = 0
        self.sprockets = []

    def addSprocket(self, sprocket):
        self.sprockets.append(sprocket)

    def finalize(self):

        # Add sprockets.
        for i in range(len(self.sprockets - 1)):
            self.sprockets[i].nextSprocket(self.sprockets[i+1])
        if self.continuous:
            self.sprockets[-1].nextSprocket(self.sprockets[0])

        # Calculate tangents.
        for i in range(len(self.sprockets - 1)):
            self.sprockets[i].calcTangent(self.sprockets[i+1])
        if self.continuous:
            self.sprockets[-1].calcTangent(self.sprockets[0])

        # Adjust angles.
        for sp in self.sprockets:
            sp.adjustAngles()
            self.length += sp.length
            self.dists.append(self.length)

    def getCoords(self, distance):
        """
        Return the position and orientation for a segment at distance along the spring.
        The z-axis points along the spring. The x-axis is the radial direction.
        """
        if self.continuous:
            while (distance < 0):
                distance += self.length
            while (distance > self.length):
                distance -= self.length

        last_dist = 0
        for i in range(len(self.dists)):
            if (distance < self.dists[i]):
                return self.sprockets[i].getCoords(distance - last_dist)
            last_dist = self.dists[i]
        
        return self.sprockets[-1].getCoords(distance - self.dists[-2])

    def getLength(self):
        return self.length


class Sprocket(object):
    """
    A sprocket / pulley. This does most of the work.
    """
    def __init__(self, coords, radius, ccw):
        self.ccw = ccw
        self.enter_angle = None
        self.enter_vec = None
        self.leave_angle = None
        self.leave_vec = None
        self.length = 0
        self.matrix = numpy.zeros((3,3))
        self.n_vec = None
        self.pos = numpy.array(coords[:3])
        self.radius = radius
        self.sp_length = 0
        self.t_twist = None
        self.t_vec = None
        self.z_vec = numpy.array(coords[3:])
        
        self.z_vec = self.z_vec/numpy.linalg.norm(self.z_vec)

    def adjustAngles(self):
        """
        Adjust angles so that the leave > start in the winding direction.
        """
        if (self.enter_angle is not None) and (self.leave_angle is not None):
            if self.ccw:
                while (self.leave_angle < self.enter_angle):
                    self.leave_angle += 2.0 * math.pi
            else:
                while (self.leave_angle > self.enter_angle):
                    self.leave_angle -= 2.0 * math.pi

        if (self.t_vec is not None):
            self.sp_length = self.radius * abs(self.enter_angle - self.leave_angle)
            self.length = self.sp_length + numpy.linalg.norm(self.t_vec)

    def calcTangent(self, next_sp):
        """
        Calculate the tangle line between the current and the next sprocket.
        """

        # Starting points for enter & exit angles.
        if self.ccw:
            self.leave_angle = 0
        else:
            self.leave_angle = math.pi

        # Calculate angle offset for the next sprocket.
        p_vec = next_sp.pos - self.pos
        p_angle = math.atan2(numpy.dot(next_sp.x_vec, p_vec),
                             numpy.dot(next_sp.y_vec, p_vec))
        if self.ccw:
            next_sp.enter_angle = -p_angle
        else:
            next_sp.enter_angle = -p_angle + math.pi

        # Refine angles.
        for i in range(5):
            leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
            enter_vec = next_sp.rotateVector(numpy.array([next_sp.radius, 0, 0]), next_sp.enter_angle)
            t_vec = (next_sp.pos + enter_vec) - (self.pos + leave_vec)
            t_vec = t_vec/numpy.linalg.norm(t_vec)
            
            d_leave = math.acos(numpy.dot(t_vec, leave_vec)/numpy.linalg.norm(leave_vec)) - 0.5 * math.pi
            d_enter = math.acos(numpy.dot(t_vec, enter_vec)/numpy.linalg.norm(enter_vec)) - 0.5 * math.pi

            if (abs(d_leave) < 1.0e-3) and (abs(d_enter) < 1.0e-3):
                break

            if self.ccw:
                self.leave_angle += d_leave
            else:
                self.leave_angle -= d_leave

            if next_sp.ccw:
                next_sp.enter_angle += d_enter
            else:
                next_sp.enter_angle -= d_enter                

        # Calculate entrance, exit and tangent vectors.
        self.leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
        next_sp.enter_vec = next_sp.rotateVector(numpy.array([next_sp.radius, 0, 0]), next_sp.enter_angle)
        self.t_vec = (next_sp.pos + next_sp.enter_vec) - (self.pos + self.leave_vec)

        # Calculate twist along the tangent vector.
        l_vec = self.leave_vec / numpy.linalg.norm(self.leave_vec)
        z_vec = self.t_vec / numpy.linalg.norm(self.t_vec)
        
        if next_sp.ccw:
            y_vec = numpy.cross(z_vec, next_sp.z_vec)
        else:
            y_vec = numpy.cross(next_sp.z_vec, z_vec)
        y_vec = y_vec / numpy.linalg.norm(y_vec)
        x_vec = numpy.cross(y_vec, z_vec)

        self.t_twist = math.atan2(numpy.dot(l_vec, x_vec), numpy.dot(l_vec, y_vec))

    def getCoords(self, distance):

        # On the sprocket.
        if (distance < self.sp_length) or (self.t_vec is None):
            if self.ccw:
                angle = self.enter_angle + distance / self.radius
            else:
                angle = self.enter_angle - distance / self.radius
            y_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), angle)
            pos = self.pos + y_vec
            y_vec = y_vec/numpy.linalg.norm(y_vec)

            if self.ccw:
                z_vec = numpy.cross(self.z_vec, y_vec)
            else:
                z_vec = numpy.cross(y_vec, self.z_vec)

            x_vec = numpy.cross(y_vec, z_vec)
            angles = angles.vectorsToAngles(x_vec, y_vec, z_vec)

            return [pos[0], pos[1], pos[2], angles[0], angles[1], angles[2]]

        # Between this sprocket and the next sprocket.
        else:
            dist = (distance - self.sp_length)/numpy.linalg.norm(self.t_vec)            
            pos = self.leave_vec + dist * self.t_vec
            twist = dist * self.t_twist

            z_vec = self.t_vec / numpy.linalg.norm(self.t_vec)
            if self.ccw:
                y_vec = numpy.cross(z_vec, self.z_vec)
            else:
                y_vec = numpy.cross(self.z_vec, z_vec)
            y_vec = y_vec/numpy.linalg.norm(y_vec)
            x_vec = numpy.cross(y_vec, z_vec)
            angles = angles.vectorsToAngles(x_vec, y_vec, z_vec)

            return [pos[0], pos[1], pos[2], angles[0], angles[1], angles[2] + math.degree(twist)]

    def nextSprocket(self, next_sp):
        """
        z_vec points up.
        y_vec is in the plane defined by z_vec and the centers of the current and the next sprocket.
        x_vec is perpendicular to y_vec and z_vec.
        """

        # Calculate sprocket coordinate system.
        self.n_vec = next_sp.pos - self.pos
        self.n_vec = self.n_vec/numpy.linalg.norm(self.n_vec)

        self.x_vec = numpy.cross(self.n_vec, self.z_vec)
        self.x_vec = self.x_vec/numpy.linalg.norm(self.x_vec)

        self.y_vec = numpy.cross(self.z_vec, self.x_vec)

        self.matrix[:,0] = self.x_vec
        self.matrix[:,1] = self.y_vec
        self.matrix[:,2] = self.z_vec
    
    def rotateVector(self, vector, az):
        """
        Rotate vector in the plane of the circle around the circle center.
        """
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
