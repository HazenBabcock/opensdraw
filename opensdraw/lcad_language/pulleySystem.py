#!/usr/bin/env python
"""
.. module:: pulley-system
   :synopsis: The pulley-system function.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import belt
import curveFunctions
import functions
import geometry
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
    last specifies either the end point of the string, or the direction
    that string goes after the last sprocket. All units are LDU.

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

    The final end point is specified by a 2 element position list,
    *(position/direction type)* where position/direction is a 3 element
    list and type is either "point" or "tangent".

    When you call the created pulley-system function you will get a 4 x 4 
    transform matrix which will translate to the requested position on the 
    string and orient to a coordinate system where the z-axis is pointing 
    along the string, the y-axis is in the plane of the string and the 
    x-axis is perpendicular to the plane of the string, pointing in the 
    direction of the pulley perpendicular vector.

    If you call the created pulley-system function with the argument 
    **t** it will return the length of the string.

    Usage::

     ; Drum at 0,0,0 rotating counter-clockwise in the x-y plane with radius
     ; 5, width 50 and 50LDU of 1LDU diameter string. The string then goes
     ; around a pulley 20,0,1 rotating counter-clockwise in the x-y plane
     ; with radius 5. After passing the pulley the string continues in the
     ; -x direction.
     (def ps1 (pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50)
                                   (list (list 20 0 1) (list 0 0 1) 5.0 1)
                                   (list (list -1 0 0) "tangent"))))

     ; Drum at 0,0,0 rotating counter-clockwise in the x-y plane with radius
     ; 5, width 50 and 50LDU of 1LDU diameter string. The string then passes 
     ; through the point 20,0,0.
     (def ps2 (pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50)
                                   (list (list 20 0 0) "point"))))

     (def m (ps1 1))   ; m is a 4 x 4 transform matrix.
     (ps1 t)           ; Returns the length of pulley system ps1 including the 
                       ;  string on the drum.
     (ps2 t)           ; Returns the length of pulley system ps2 including the
                       ;  string on the drum.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "pulley-system")
        self.setSignature([[list]])

    def call(self, model, tree):
        [pulley_list] = self.getArgs(model, tree)
        if (len(pulley_list) < 2):
            raise NumberPulleysException(len(pulley_list))

        # Create pulley-system.
        p_system = belt.Belt(False)

        # Starting drum.
        drum = pulley_list[0]
        pulley_list = pulley_list[1:]

        if not isinstance(drum, list):
            raise lcadExceptions.WrongTypeException("list", type(drum))

        if (len(drum) != 7):
            DrumException(len(drum))

        drum_pos = geometry.parseArgs(drum[0])
        drum_zvec = geometry.parseArgs(drum[1])
        for arg in drum[2:]:
            if not isinstance(arg, numbers.Number):
                raise lcadExceptions.WrongTypeException("number", type(arg))

        # Ending point.
        end_point = pulley_list[-1]
        pulley_list = pulley_list[:-1]

        if not isinstance(end_point, list):
            raise lcadExceptions.WrongTypeException("list", type(end_point))

        if (len(end_point) != 2):
            EndPointException(len(end_point))

        end_vec = geometry.parseArgs(end_point[0])
        end_type = end_point[1]
        if not isinstance(end_type, basestring):
            raise lcadExceptions.WrongTypeException("string", type(end_type))

        if not (end_type in ["point", "tangent"]):
            raise EndPointTypeException(end_type)

        # Drum only pulley system.
        if (len(pulley_list) == 0):
            p_system.addSprocket(EndDrum(drum_pos, drum_zvec, drum[2], drum[3], drum[4], drum[5], drum[6], end_vec, end_type))

        # "Standard" pulley system.
        else:
            p_system.addSprocket(StdDrum(drum_pos, drum_zvec, drum[2], drum[3], drum[4], drum[5], drum[6]))

            # Middle pulleys.
            for pulley in pulley_list[:-1]:
                p_system.addSprocket(belt.Sprocket(*belt.parsePulley(pulley)))

            # End pulley
            [end_pos, end_zvec, end_radius, end_winding] = belt.parsePulley(pulley_list[-1])
            p_system.addSprocket(EndSprocket(end_pos, end_zvec, end_radius, end_winding, end_vec, end_type))

        p_system.finalize()

        # Return chain function.
        return curveFunctions.CurveFunction(p_system, "user created pulley system.")

lcad_functions["pulley-system"] = LCadPulleySystem()

class EndPointException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A pulley system end point must have 2 arguments, got " + str(got))

class EndPointTypeException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "End point type must be either 'point' or 'tangent', got '" + got + "'")

class DrumException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A drum must have 7 arguments, got " + str(got))

class NumberPulleysException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A pulley-system must have at least a drum and an end-point, got " + str(got) + " arguments")


class EndSprocket(belt.Sprocket):
    """
    The last sprocket in the pulley system.
    """
    def __init__(self, pos, z_vec, radius, ccw, pd_vec, pd_type):
        belt.Sprocket.__init__(self, pos, z_vec, radius, ccw)

        self.pd_type = pd_type
        self.pd_vec = numpy.array(pd_vec)

    def adjustAngles(self):
        belt.Sprocket.adjustAngles(self)

        # Subtract contribution of unit length tangent 
        # vector in case of derivative.
        if not (self.pd_type == "point"):
            self.length = self.sp_length

    def nextSprocket(self, next_sp):

        # Calculate sprocket coordinate system.
        if (self.pd_type == "point"):
            self.n_vec = self.pd_vec - self.pos
        else:
            self.n_vec = self.pd_vec

        self.n_vec = self.n_vec/numpy.linalg.norm(self.n_vec)

        self.x_vec = numpy.cross(self.n_vec, self.z_vec)
        self.x_vec = self.x_vec/numpy.linalg.norm(self.x_vec)

        self.y_vec = numpy.cross(self.z_vec, self.x_vec)

        self.matrix[:,0] = self.x_vec
        self.matrix[:,1] = self.y_vec
        self.matrix[:,2] = self.z_vec

        #
        # Calculate tangent.
        #
        if self.ccw:
            self.leave_angle = 0
        else:
            self.leave_angle = math.pi
            
        # Point.
        if (self.pd_type == "point"):
                
            # Refine angle.
            for i in range(5):
                leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
                t_vec = self.pd_vec - (self.pos + leave_vec)
                t_vec = t_vec/numpy.linalg.norm(t_vec)
            
                d_leave = math.acos(numpy.dot(t_vec, leave_vec)/numpy.linalg.norm(leave_vec)) - 0.5 * math.pi

                if (abs(d_leave) < 1.0e-3):
                    break

                if self.ccw:
                    self.leave_angle += d_leave
                else:
                    self.leave_angle -= d_leave

            # Tangent vector.
            self.leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
            self.t_vec = self.pd_vec - (self.pos + self.leave_vec)

        # Direction.
        else:
            self.leave_vec = self.rotateVector(numpy.array([self.radius, 0, 0]), self.leave_angle)
            self.t_vec = self.pd_vec/numpy.linalg.norm(self.pd_vec)

        self.t_twist = 0


class Drum(object):
    """
    The initial drum on which the string is wound.
    """
    def __init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length):

        # string_length is the amount of string that is wound around the drum.
        self.sprocket.sp_length = string_length

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
        while (length <= string_length):

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
            if not self.sprocket.ccw:
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
            if not self.sprocket.ccw:
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

    def adjustAngles(self):
        self.sprocket.adjustAngles()

    def calcTangent(self, next_sp):
        self.sprocket.calcTangent(next_sp)

        # Re-calculate exit and tangent vectors.
        self.sprocket.leave_vec = self.sprocket.rotateVector(numpy.array([self.exit_radius, 0, self.exit_pos]), self.sprocket.leave_angle)
        self.sprocket.t_vec = (next_sp.pos + next_sp.enter_vec) - (self.sprocket.pos + self.sprocket.leave_vec)

    def getLength(self):
        return self.sprocket.getLength()

    def getMatrix(self, distance):

        # On the drum.
        if (distance < self.sprocket.sp_length):

            last_len = 0
            for seg in self.winding_fn:
                if (distance < seg[0]):
                    ds = distance - last_len
                    angle = seg[1] + ds * seg[4] - self.exit_angle + self.sprocket.leave_angle
                    pos = seg[2] + ds * seg[5]
                    radius = seg[3] + ds * seg[6]

                    # Position in drum coordinate system.
                    p_vec = numpy.array([math.cos(angle) * radius,
                                         math.sin(angle) * radius,
                                         pos])

                    # Position in real space.
                    p_vec = numpy.dot(self.sprocket.matrix, p_vec) + self.sprocket.pos

                    # Derivative in drum coordinate system.
                    z_vec = numpy.array([math.cos(angle) * seg[6] - math.sin(angle) * radius * seg[4],
                                         math.sin(angle) * seg[6] + math.cos(angle) * radius * seg[4],
                                         seg[5]])

                    # Derivative in real space.
                    z_vec = numpy.dot(self.sprocket.matrix, z_vec)
                    z_vec = z_vec/numpy.linalg.norm(z_vec)

                    y_vec = numpy.cross(z_vec, self.sprocket.z_vec)
                    y_vec = y_vec/numpy.linalg.norm(y_vec)

                    x_vec = numpy.cross(y_vec, z_vec)

                    return geometry.vectorsToMatrix(p_vec, x_vec, y_vec, z_vec)

                last_len = seg[0]

        # Between the drum and the next sprocket.
        else:
            dist = (distance - self.sprocket.sp_length)/numpy.linalg.norm(self.sprocket.t_vec)
            pos = self.sprocket.pos + self.sprocket.leave_vec + dist * self.sprocket.t_vec
            twist = dist * self.sprocket.t_twist

            z_vec = self.sprocket.t_vec / numpy.linalg.norm(self.sprocket.t_vec)
            y_vec = numpy.cross(z_vec, self.sprocket.z_vec)
            y_vec = y_vec/numpy.linalg.norm(y_vec)
            x_vec = numpy.cross(y_vec, z_vec)

            m = geometry.vectorsToMatrix(pos, x_vec, y_vec, z_vec)
            if (twist == 0):
                return m
            else:
                return numpy.dot(m, geometry.rotationMatrixZ(twist)).view(lcadTypes.LCadMatrix)

    def nextSprocket(self, next_sp):
        self.sprocket.nextSprocket(next_sp)

    def rotateVector(self, vector, az):
        return self.sprocket.rotateVector(vector, az)


class EndDrum(Drum):
    """
    If there is only a drum and nothing else.
    """
    def __init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length, pd_vec, pd_type):
        self.sprocket = EndSprocket(pos, z_vec, radius, ccw, pd_vec, pd_type)
        Drum.__init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length)

    def nextSprocket(self, next_sp):
        self.sprocket.nextSprocket(next_sp)

        # Re-calculate exit and tangent vectors.
        self.sprocket.leave_vec = self.sprocket.rotateVector(numpy.array([self.exit_radius, 0, self.exit_pos]), self.sprocket.leave_angle)
        if (self.sprocket.pd_type == "point"):
            self.sprocket.t_vec = self.sprocket.pd_vec - (self.sprocket.pos + self.sprocket.leave_vec)


class StdDrum(Drum):
    """
    If there are also other sprockets.
    """
    def __init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length):
        self.sprocket = belt.Sprocket(pos, z_vec, radius, ccw)
        Drum.__init__(self, pos, z_vec, radius, ccw, drum_width, string_gauge, string_length)


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
