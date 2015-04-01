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
    element specifies a drum on which the string is wound. All units
    are LDU.

    A pulley-system must have at least two pulleys (including the initial
    drum). Each pulley is specified by a 4 member list consisting of
    *(position orientation radius winding-direction)* where position and
    orientation are 3 element lists specifying the location and the 
    vector perpendicular to the pulley respectively. Winding-direction 
    specifies which way string goes around the pulley (1 = counter-clockwise, 
    -1 = clockwise). The string goes around the pulleys in the order in 
    which they are specified.

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
            if not ccw:
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
            if not ccw:
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

        # Calculate where the string leaves the drum.
        if (len(self.winding_fn) > 1):
            s_length = string_length - self.winding_fn[-2][0]
        else:
            s_length = string_length
        self.exit_angle = self.winding_fn[-1][1] + s_length * self.winding_fn[-1][4]
        self.exit_pos = self.winding_fn[-1][2] + s_length * self.winding_fn[-1][5]
        self.exit_radius = self.winding_fn[-1][3] + s_length * self.winding_fn[-1][6]

    def getCoords(self, distance):
        
        # On the drum.
        if (distance < self.sp_length):

            last_len = 0
            for seg in self.winding_fn:
                if (distance < seg[0]):
                    ds = distance - last_len
                    angle = seg[1] + ds * seg[4]
                    pos = seg[2] + ds * seg[5]
                    radius = seg[3] + ds * seg[6]
                    return [math.cos(angle) * radius,
                            math.sin(angle) * radius,
                            pos]
                last_len = seg[0]


#
# Testing
#

if (__name__ == "__main__"):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    
    string_l = 250.0
    drum = Drum([0, 0, 0], [0, 0, 1], 5.0, 1, 5.0, 1.0, string_l)

    #print drum.winding_fn

    fig = plt.figure()
    axis = fig.gca(projection='3d')
    MAX = 6
    for direction in (-1, 1):
        for point in numpy.diag(direction * MAX * numpy.array([1,1,1])):
            axis.plot([point[0]], [point[1]], [point[2]], 'w')

    d = numpy.linspace(0, string_l - 1.0e-3, int(string_l))
    x = numpy.zeros(d.size)
    y = numpy.zeros(d.size)
    z = numpy.zeros(d.size)
    for i in range(d.size):
        x[i], y[i], z[i] = drum.getCoords(d[i])
        print x[i], y[i], z[i]
        
    axis.plot(x, y, z, color = "black")
    axis.scatter(x, y, z, color = "blue")

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
