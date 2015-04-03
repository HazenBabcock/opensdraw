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
import geometryFunctions
import interpreter as interp
import lcadExceptions
import lcadTypes

lcad_functions = {}


def parsePulley(pulley):
    if not isinstance(pulley, list):
        raise lcadExceptions.WrongTypeException("list", type(pulley))

    if (len(pulley) != 4):
        raise PulleyException(len(pulley))

    # Position vector.
    pos = geometryFunctions.parseArgs(pulley[0])

    # Orientation vector.
    z_vec = geometryFunctions.parseArgs(pulley[1])

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
class LCadBelt(functions.LCadFunction):
    """
    **belt** - Creates a belt function.

    This function creates and returns a function that parametrizes a belt
    making it easier to add custom belts / chains to a MOC. Unlike the
    chain function this allows for (almost) arbitrary locations and 
    orientations of the pulleys / sprockets. All units are in LDU.

    Each pulley / sprocket is specified by a 4 member list consisting of
    *(position orientation radius winding-direction)* where position and
    orientation are 3 element lists specifying the location and the 
    vector perpendicular to the pulley / sprocket respectively. 
    Winding-direction specifies which way belt goes around the pulley 
    / sprocket (1 = counter-clockwise, -1 = clockwise). The belt goes 
    around the pulleys / sprockets in the order in which they are 
    specified, and when *:continuous* is **t** returns from the last pulley 
    / sprocket to the first to close the loop.

    When you call the created belt function you will get a 6 element list
    *(x y z rx ry rz)* where *x*, *y*, and *z* specify the position of the
    belt at distance *d*. The angle *rx*, *ry* and *rz* will rotate the
    coordinate system such that z-axis is pointing along the belt, the
    y-axis is in the plane of the belt and the x-axis is perpendicular
    to the plane of the belt, pointing in the direction of the pulley /
    sprocket perpendicular vector.

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

     (def b1 (a-belt 1))                        ; b1 is the list (x y z rx ry rz).
     (a-belt t)                                 ; Returns the length of the belt.

    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "belt")
        self.setSignature([[list], 
                           ["keyword", {"continuous" : [[lcadTypes.LCadObject], interp.lcad_t]}]])

    def call(self, model, tree):
        [args, keywords] = self.getArgs(model, tree)

        # Keywords
        continuous = True if functions.isTrue(keywords["continuous"]) else False

        # Get list of pulleys.
        pulley_list = args[0]
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
        
        if (len(self.dists) > 1):
            return self.sprockets[-1].getCoords(distance - self.dists[-2])
        else:
            return self.sprockets[-1].getCoords(distance)

    def getLength(self):
        return self.length


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

    def getCoords(self, distance):

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
            [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)

            return [pos[0], pos[1], pos[2], rx, ry, rz]

        # Between this sprocket and the next sprocket.
        else:
            dist = (distance - self.sp_length)/numpy.linalg.norm(self.t_vec)            
            pos = self.pos + self.leave_vec + dist * self.t_vec
            twist = dist * self.t_twist

            z_vec = self.t_vec / numpy.linalg.norm(self.t_vec)
            y_vec = numpy.cross(z_vec, self.z_vec)
            y_vec = y_vec/numpy.linalg.norm(y_vec)
            x_vec = numpy.cross(y_vec, z_vec)
            [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)

            return [pos[0], pos[1], pos[2], rx, ry, rz + math.degrees(twist)]

    def getLength(self):
        return self.length
        
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


#
# Testing
#
if (__name__ == "__main__"):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    sprockets = [Sprocket([0, 0, 0], [0, 0, 1], 1.0, 1),
                 Sprocket([4, -1, 1], [0, -1, 0], 1.0, 1),
                 Sprocket([5, 0, 5], [-1, 0, 0], 1.0, 1),
                 Sprocket([4, 1, 1], [0, 1, 0], 1.0, 1)]
    
    #sprockets = [Sprocket([0, 0, 0], [0, 0, 1], 1.0, True),
    #             Sprocket([4, 0, 0], [0, 0, 1], 1.5, True)]

    belt = Belt(True)
    for sp in sprockets:
        belt.addSprocket(sp)
    belt.finalize()

    fig = plt.figure()
    axis = fig.gca(projection='3d')
    MAX = 6
    for direction in (-1, 1):
        for point in numpy.diag(direction * MAX * numpy.array([1,1,1])):
            axis.plot([point[0]], [point[1]], [point[2]], 'w')

    #mpl.rcParams['legend.fontsize'] = 10

    az = numpy.linspace(0, 2.0 * math.pi, 40)
    for sp in sprockets:
        x = numpy.zeros(az.size)
        y = numpy.zeros(az.size)
        z = numpy.zeros(az.size)
        v = numpy.array([sp.radius, 0, 0])
        for i in range(az.size):
            [x[i], y[i], z[i]] = sp.rotateVector(v, az[i]) + sp.pos
        axis.plot(x, y, z, color = "black")

    if 0:
        for sp in sprockets:
            axis.scatter([sp.pos[0] + sp.enter_vec[0]],
                         [sp.pos[1] + sp.enter_vec[1]],
                         [sp.pos[2] + sp.enter_vec[2]],
                         color = "purple")

            axis.scatter([sp.pos[0] + sp.leave_vec[0]],
                         [sp.pos[1] + sp.leave_vec[1]],
                         [sp.pos[2] + sp.leave_vec[2]],
                         color = "black")

    if 0:
        d = numpy.linspace(0, belt.getLength(), 10)
        x = numpy.zeros(d.size)
        y = numpy.zeros(d.size)
        z = numpy.zeros(d.size)
        for i in range(d.size):
            x[i], y[i], z[i] = belt.getCoords(d[i])[:3]
        axis.scatter(x, y, z)

    if 1:
        vlen = 0.25
        #d = numpy.linspace(0, 20.0 + belt.getLength(), 40) - 10.0
        d = numpy.linspace(0, belt.getLength(), 40)
        for i in range(d.size):
            [x, y, z, rx, ry, rz] = belt.getCoords(d[i])
            m = angles.rotationMatrix(rx, ry, rz)
            vx = numpy.dot(m, numpy.array([vlen, 0, 0, 1]))
            vy = numpy.dot(m, numpy.array([0, vlen, 0, 1]))
            vz = numpy.dot(m, numpy.array([0, 0, vlen, 1]))

            for elt in [[vx, "red"], [vy, "green"], [vz, "blue"]]:
                axis.plot([x, x + elt[0][0]],
                          [y, y + elt[0][1]],
                          [z, z + elt[0][2]],
                          color = elt[1])

    #for ps in [[s1, s2], [s2, s3], [s3, s4], [s4, s1]]:
    #for ps in [[s1, s2]]:
    #    ps0 = ps[0]
    #    ps1 = ps[1]
    #    leave_vec = ps0.rotateVector(numpy.array([ps0.radius, 0, 0]), ps0.leave_angle)
    #    enter_vec = ps1.rotateVector(numpy.array([ps1.radius, 0, 0]), ps1.enter_angle) 
    #    axis.plot([ps0.pos[0] + leave_vec[0], ps1.pos[0] + enter_vec[0]],
    #              [ps0.pos[1] + leave_vec[1], ps1.pos[1] + enter_vec[1]],
    #              [ps0.pos[2] + leave_vec[2], ps1.pos[2] + enter_vec[2]])

    #axis.legend()

    plt.show()
