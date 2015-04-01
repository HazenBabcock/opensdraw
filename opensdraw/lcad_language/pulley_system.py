#!/usr/bin/env python
"""
.. module:: pulley-system
   :synopsis: The pulley-system function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import angles
import belt
import curveFunctions
import functions
import interpreter as interp
import lcadExceptions
import lcadTypes

lcad_functions = {}


class LCadPulleySystem(functions.LCadFunction):
    """
    **pulley-system** - Creates a pulley-system function.
    
    This function creates and returns a function that parametrizes a 
    pulley-system making it easier to add pulleys and string to a MOC.
    The function is very similar to belt(), except that the first
    element specifies a drum on which the string is wound and the
    last specifies the end point of the string. All units are LDU.

    A pulley-system must have at least two elements (including the initial
    drum and the final end point). Like belt, the pulleys are specified by 
    a 4 element list consisting of *(position orientation radius winding-direction)* 
    where position and orientation are 3 element lists specifying the 
    location and the  vector perpendicular to the pulley respectively. 
    Winding-direction specifies which way string goes around the pulley 
    (1 = counter-clockwise, -1 = clockwise). The string goes around the 
    pulleys in the order in which they are specified.

    The initial drum is specified by the 7 element list *(position
    orientation radius winding-direction drum-width string-thickness
    string-length)* where string-length is the amount of string
    would around the drum, **not** the total string length.

    The final end point is specified by a 3 element position list.

    When you call the created pulley-system function you will get a 6 
    element list *(x y z rx ry rz)* where *x*, *y*, and *z* specify the 
    position of the string at distance *d*. The angle *rx*, *ry* and *rz* 
    will rotate the coordinate system such that z-axis is pointing along 
    the string, the y-axis is in the plane of the string and the x-axis 
    is perpendicular to the plane of the string, pointing in the direction 
    of the pulley perpendicular vector.

    If you call the created pulley-system function with the argument 
    **t** it will return the length of the string.

    Usage::



    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "pulley-system")
        self.setSignature([[list]])

    def call(self, model, tree):
        [args] = self.getArgs(model, tree)

        # Get list of pulleys.
        pulley_list = args[0]
        if (len(pulley_list) < 2):
            raise belt.NumberPulleysException(len(pulley_list))

        # Create sprockets.
        chain = belt.Belt(continuous)
        for sprocket in sprocket_list:
        
            if not isinstance(sprocket, list):
                raise lcadExceptions.WrongTypeException("list", type(sprocket))

            if (len(sprocket) != 4):
                raise belt.PulleyException(len(sprocket))

            for elt in sprocket:
                if not isinstance(elt, numbers.Number):
                    raise lcadExceptions.WrongTypeException("number", type(elt))

            chain.addSprocket(belt.Sprocket([sprocket[0], sprocket[1], 0], [0, 0, 1],
                                            sprocket[2], sprocket[3]))

        chain.finalize()

        # Return chain function.
        return curveFunctions.CurveFunction(chain, "user created chain function.")

lcad_functions["pulley-system"] = LCadPulleySystem()


class EndPoint(object):
    """
    The end point of the string. This pretends to be a Sprocket so that
    it works properly as part of a belt.
    """
    def __init__(self, pos):        
        self.pos = pos

        # Dummy variables so that this will behave like a Sprocket.
        self.ccw = True
        self.enter_angle = None
        self.radius = 0.0

    def adjustAngles(self):
        pass

    def nextSprocket(self, next_sp):
        pass

    def rotateVector(self, vector, az):
        return numpy.zeros(3)


class Drum(belt.Sprocket):
    """
    The initial drum on which the string is wound.
    """
    def __init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length):
        belt.Sprocket.__init__(self, pos, z_vec, radius, ccw)

        # string_length is the amount of string that is wound around the drum.
        self.sp_length = string_length

        # Calculate how to wind the string.
        turns_per_layer = int(round(drum_width/string_gauge))

        #
        # This array parameterizes the helical winding, it is a list of lists 
        # where each sub-list describes a segment, and contains [length of the
        # string at the segmend end-point, segment start angle, segment start
        # position, segment start radius, d_angle, d_position (along the helix), 
        # d_radius (outward from the helix).
        #
        self.winding_fn = []  

        layer = 0
        length = 0
        start = True
        s_angle = 0
        s_radius = radius
        while (length < string_length):

            # Figure out which end we are starting from.
            if ((layer % 2) == 0):
                s_pos = 0
            else:
                s_pos = string_gauge * turns_per_layer

            d_pos = 0.0
            # Initial quarter-turn.
            if start:
                s_length = 0.5 * math.pi * radius
                d_angle = 0.5 * math.pi / s_length
                d_radius = 0.0
                start = False
            # Initial half-turn.
            else:
                s_length = 0.5 * math.pi * (2 * radius + string_gauge)
                d_angle = math.pi / s_length
                d_radius = string_gauge / s_length

            length += s_length
            if self.ccw:
                d_angle = -d_angle
            self.winding_fn.append([length, s_angle, s_pos, s_radius, d_angle, d_pos, d_radius])
            s_angle += s_length * d_angle
            s_radius += s_length * d_radius

            if (length >= string_length):
                continue

            # Remaining turns.

            dl = turns_per_layer * string_gauge
            dr = turns_per_layer * 2.0 * math.pi * s_radius
            s_length = math.sqrt(dl*dl + dr*dr)

            d_angle = dr / (s_length * s_radius)
            if self.ccw:
                d_angle = -d_angle
            d_pos = dl / s_length
            d_radius = 0.0

            if ((layer % 2) != 0):
                d_pos = -d_pos

            length += s_length
            self.winding_fn.append([length, s_angle, s_pos, s_radius, d_angle, d_pos, d_radius])
            s_angle += s_length * d_angle

            layer += 1

        self.winding_fn[-1][0] = string_length

        # Calculate where the string exits the drum.
        if (len(self.winding_fn) > 1):
            s_length = string_length - self.winding_fn[-2][0]
        else:
            s_length = string_length
        self.exit_angle = self.winding_fn[-1][1] + s_length * self.winding_fn[-1][4]
        self.exit_pos = self.winding_fn[-1][2] + s_length * self.winding_fn[-1][5]
        self.exit_radius = self.winding_fn[-1][3] + s_length * self.winding_fn[-1][6]

    def calcTangent(self, next_sp):
        belt.Sprocket.calcTangent(self, next_sp)

        # Re-calculate exit and tangent vectors.
        self.leave_vec = self.rotateVector(numpy.array([self.radius, 0, self.exit_pos]), self.leave_angle)
        self.t_vec = (next_sp.pos + next_sp.enter_vec) - (self.pos + self.leave_vec)

    def getCoords(self, distance):
        
        # On the drum.
        if (distance < self.sp_length):

            last_len = 0
            for seg in self.winding_fn:
                if (distance < seg[0]):
                    ds = distance - last_len
                    angle = seg[1] + ds * seg[4] - self.exit_angle + self.leave_angle
                    pos = seg[2] + ds * seg[5]
                    radius = seg[3] + ds * seg[6]

                    # Position in drum coordinate system.
                    p_vec = numpy.array([math.cos(angle) * radius,
                                         math.sin(angle) * radius,
                                         pos])

                    # Position in real space.
                    p_vec = numpy.dot(self.matrix, p_vec) + self.pos

                    # Derivative in drum coordinate system.
                    z_vec = numpy.array([math.cos(angle) * seg[6] - math.sin(angle) * radius * seg[4],
                                         math.sin(angle) * seg[6] + math.cos(angle) * radius * seg[4],
                                         seg[5]])

                    # Derivative in real space.
                    z_vec = numpy.dot(self.matrix, z_vec)
                    z_vec = z_vec/numpy.linalg.norm(z_vec)

                    y_vec = numpy.cross(z_vec, self.z_vec)
                    y_vec = y_vec/numpy.linalg.norm(y_vec)

                    x_vec = numpy.cross(y_vec, z_vec)
                    [rx, ry, rz] = angles.vectorsToAngles(x_vec, y_vec, z_vec)

                    return [p_vec[0], p_vec[1], p_vec[2], rx, ry, rz]

                last_len = seg[0]

        # Between the drum and the next sprocket.
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


#
# Testing
#

if (__name__ == "__main__"):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    
    drum = Drum([0, 0, 0], [0, 1, 0], 1.0, -1, 1.0, 0.1, 100.0)
    sprockets = [belt.Sprocket([4, 0, 1.0], [0, 0, 1], 1.0, 1)]
    
    a_belt = belt.Belt(False)
    a_belt.addSprocket(drum)
    for sp in sprockets:
        a_belt.addSprocket(sp)
    a_belt.finalize()

    fig = plt.figure()
    axis = fig.gca(projection='3d')
    MAX = 6
    for direction in (-1, 1):
        for point in numpy.diag(direction * MAX * numpy.array([1,1,1])):
            axis.plot([point[0]], [point[1]], [point[2]], 'w')

    # Draw sprockets.
    az = numpy.linspace(0, 2.0 * math.pi, 40)
    for sp in sprockets:
        x = numpy.zeros(az.size)
        y = numpy.zeros(az.size)
        z = numpy.zeros(az.size)
        v = numpy.array([sp.radius, 0, 0])
        for i in range(az.size):
            [x[i], y[i], z[i]] = sp.rotateVector(v, az[i]) + sp.pos
        axis.plot(x, y, z, color = "black")

    # Draw string.
    if 1:
        d = numpy.linspace(0, a_belt.getLength(), 500)
        x = numpy.zeros(d.size)
        y = numpy.zeros(d.size)
        z = numpy.zeros(d.size)
        for i in range(d.size):
            x[i], y[i], z[i] = a_belt.getCoords(d[i])[0:3]
        
        axis.plot(x, y, z, color = "black")
        #axis.scatter(x, y, z, color = "blue")

    # Draw coordinate system vectors.
    if 0:
        vlen = 0.25
        d = numpy.linspace(150, string_l - 1.0e-3, 200)
        for i in range(d.size):
            [x, y, z, rx, ry, rz] = drum.getCoords(d[i])
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

#
# The MIT License
#
# Copyright (c) 2015 Hazen Babcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
