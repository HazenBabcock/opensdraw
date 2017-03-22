#!/usr/bin/env python
"""
.. module:: belt
   :synopsis: The belt function.

.. moduleauthor:: Hazen Babcock
"""

import math
import numbers
import numpy

import opensdraw.lcad_language.curveFunctions as curveFunctions
import opensdraw.lcad_language.geometry as geometry
import opensdraw.lcad_language.interpreter as interp
import opensdraw.lcad_language.lcadExceptions as lcadExceptions
import opensdraw.lcad_language.lcadTypes as lcadTypes

lcad_functions = {}


def parsePulley(pulley):
    if not isinstance(pulley, list):
        raise lcadExceptions.WrongTypeException("list", type(pulley))

    if (len(pulley) != 4):
        raise PulleyException(len(pulley))

    # Position vector.
    pos = geometry.parseArgs(pulley[0])

    # Orientation vector.
    z_vec = geometry.parseArgs(pulley[1])

    # Radius
    radius = pulley[2]
    if not isinstance(radius, numbers.Number):
        raise lcadExceptions.WrongTypeException("number", type(radius))

    # Winding.
    winding = pulley[3]
    if not isinstance(winding, numbers.Number):
        raise lcadExceptions.WrongTypeException("number", type(winding))

    return [pos, z_vec, radius, winding]


#
# These classes create a belt function that can be used in opensdraw.
#
class LCadBelt(interp.LCadFunction):
    """
    **belt** - Creates a belt function.

    This function creates and returns a function that parametrizes a belt
    making it easier to add custom belts / chains to a MOC. Unlike the
    chain function this allows for (almost) arbitrary locations and 
    orientations of the pulleys / sprockets. All units are in LDU.

    Each pulley / sprocket is specified by a 4 member list consisting of
    *(position orientation radius winding-direction)*.

    :param position: A 3 element list specifying the location of the pulley / sprocket.
    :param orientation: A 3 element list specifying the vector perpendicular to the plane of the pulley / sprocket.
    :param radius: The radius of the pulley / sprocket in LDU.
    :param winding-direction: Which way the belt goes around the pulley / sprocket (1 = counter-clockwise, -1 = clockwise).

    The belt goes around the pulleys / sprockets in the order in which they 
    are specified, and when *:continuous* is **t** returns from the last 
    pulley / sprocket to the first to close the loop.

    When you call the created belt function you will get a 4 x 4 transform
    matrix which will translate to the requested position on the belt and
    orient to a coordinate system where the z-axis is pointing along the 
    belt, the y-axis is in the plane of the belt and the x-axis is 
    perpendicular to the plane of the belt, pointing in the direction 
    of the pulley / sprocket perpendicular vector.

    If you call the created belt function with the argument **t** it will return the 
    length of the belt.

    Additionally belt has the keyword argument::

      :continuous t/nil  ; The default is t, distances will be interpreted modulo the belt length, and
                         ; the belt will go from that last pulley back to the first pulley. If nil
                         ; then negative distances will wrap around the first pulley and positive
                         ; distances will wrap around the last pulley.

    Usage::

     (def a-belt (belt (list (list (list 0 0 0) ; Create a belt with two pulleys.
                                   (list 0 0 1) ; Pulley one is at 0,0,0 and is in the
                                   1.0 1)       ; x-y plane with radius 1 and counter-clockwise
                             (list (list 4 0 0) ; winding direction.
                                   (list 0 0 1) ; Pulley two is at 4,0,0 with radius 1.5.
                                   1.5 1))))  

     (def m (a-belt 1))                         ; m is a 4 x 4 transform matrix.
     (a-belt t)                                 ; Returns the length of the belt.

    """

    def __init__(self):
        interp.LCadFunction.__init__(self, "belt")
        self.setSignature([[list], 
                           ["keyword", {"continuous" : [[lcadTypes.LCadBoolean], interp.lcad_t]}]])

    def call(self, model, pulley_list, continuous = interp.lcad_t):

        # Keywords
        continuous = True if interp.isTrue(continuous) else False

        # Get list of pulleys.
        if (len(pulley_list) < 2):
            raise NumberPulleysException(len(pulley_list))

        # Create belt.
        belt = Belt(continuous)
        for pulley in pulley_list:
            belt.addSprocket(Sprocket(*parsePulley(pulley)))
            
        belt.finalize()

        # Return belt function.
        return curveFunctions.CurveFunction(belt, "user created belt function.")

lcad_functions["belt"] = LCadBelt()

class NumberPulleysException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A belt must have 2 sprockets, got " + str(got))

class PulleyException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A pulley must have 4 arguments, got " + str(got))

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
        for i in range(len(self.sprockets) - 1):
            self.sprockets[i].nextSprocket(self.sprockets[i+1])
        self.sprockets[-1].nextSprocket(self.sprockets[0])

        # Calculate tangents.
        for i in range(len(self.sprockets) - 1):
            self.sprockets[i].calcTangent(self.sprockets[i+1])
        if self.continuous:
            self.sprockets[-1].calcTangent(self.sprockets[0])

        # Adjust angles.
        for sp in self.sprockets:
            sp.adjustAngles()
            self.length += sp.getLength()
            self.dists.append(self.length)

    def getLength(self):
        return self.length

    def getMatrix(self, distance):
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
                return self.sprockets[i].getMatrix(distance - last_dist)
            last_dist = self.dists[i]
        
        if (len(self.dists) > 1):
            return self.sprockets[-1].getMatrix(distance - self.dists[-2])
        else:
            return self.sprockets[-1].getMatrix(distance)



class Sprocket(object):
    """
    A sprocket / pulley. This does most of the work.
    """
    def __init__(self, pos, z_vec, radius, ccw):
        self.ccw = True
        if (ccw == -1):
            self.ccw = False
        self.enter_angle = None
        self.enter_vec = None
        self.leave_angle = None
        self.leave_vec = None
        self.length = 0
        self.matrix = numpy.zeros((3,3))
        self.n_vec = None
        self.pos = numpy.array(pos)
        self.radius = radius
        self.sp_length = 0
        self.t_twist = None
        self.t_vec = None
        self.z_vec = numpy.array(z_vec)
        
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

            self.sp_length = self.radius * abs(self.enter_angle - self.leave_angle)

        if (self.t_vec is not None):
            self.length = self.sp_length + numpy.linalg.norm(self.t_vec)

    def calcTangent(self, next_sp):
        """
        Calculate the tangent line between the current and the next sprocket.
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
        if next_sp.ccw:
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
        if not self.ccw:
            l_vec = -l_vec
        z_vec = self.t_vec / numpy.linalg.norm(self.t_vec)

        y_vec = numpy.cross(z_vec, next_sp.z_vec)
        y_vec = y_vec / numpy.linalg.norm(y_vec)
        x_vec = numpy.cross(y_vec, z_vec)

        self.t_twist = math.atan2(numpy.dot(l_vec, x_vec), numpy.dot(l_vec, y_vec))

    def getLength(self):
        return self.length

    def getMatrix(self, distance):

        # On the sprocket.
        if (distance < self.sp_length) or (self.t_vec is None):
            angle = self.enter_angle
            if (distance < 0):
                angle = self.leave_angle

            if self.ccw:
                angle += distance / self.radius
            else:
                angle -= distance / self.radius
            y_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), angle)
            pos = self.pos + y_vec
            y_vec = y_vec/numpy.linalg.norm(y_vec)

            if not self.ccw:
                y_vec = -y_vec

            z_vec = numpy.cross(self.z_vec, y_vec)
            x_vec = numpy.cross(y_vec, z_vec)
            return geometry.vectorsToMatrix(pos, x_vec, y_vec, z_vec)

        # Between this sprocket and the next sprocket.
        else:
            dist = (distance - self.sp_length)/numpy.linalg.norm(self.t_vec)            
            pos = self.pos + self.leave_vec + dist * self.t_vec
            twist = dist * self.t_twist

            z_vec = self.t_vec / numpy.linalg.norm(self.t_vec)
            y_vec = numpy.cross(z_vec, self.z_vec)
            y_vec = y_vec/numpy.linalg.norm(y_vec)
            x_vec = numpy.cross(y_vec, z_vec)

            m = geometry.vectorsToMatrix(pos, x_vec, y_vec, z_vec)
            if (twist == 0.0):
                return m
            else:
                return numpy.dot(m, geometry.rotationMatrixZ(twist)).view(lcadTypes.LCadMatrix)

    def nextSprocket(self, next_sp):
        """
        Calculate sprocket coordinate system.

        z_vec points up.
        y_vec is in the plane defined by z_vec and the centers of the current and the next sprocket.
        x_vec is perpendicular to y_vec and z_vec.
        """

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


