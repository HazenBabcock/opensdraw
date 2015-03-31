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

        # Calculate how many layers of string.
        turns_per_layer = int(round(drum_width/string_gauge))
        temp_r = radius
        temp_l = string_length
        self.layers = 0
        while (temp_l > 0):
            dr = 2.0 * math.pi * temp_r * turns_per_layer
            dl = turns_per_layer * string_gauge
            temp_l -= math.sqrt(dr*dr + dl*dl)
            temp_r += string_gauge
            self.layers += 1


        # Calculate how to wind the string.

        #
        # This parameterizes the helical winding, it is a list of lists where
        # each sub-list is [segment end length, segment start angle, d_angle
        # in the segment, d_pos (along the helix), d_rad (outward from the
        # helix)].
        #
        self.winding_fn = []  

        temp_r = radius
        temp_l = string_length
        angle = 0
        length = 0
        index = 0
        start = True
        while (length < string_length):

            # Initial half-turn.
            if start:
                d_angle = math.pi
                length += math.pi * radius
                self.winding_fn.append([length, 0, d_angle/length, 0, 0])
                angle += d_angle
                start = False
            else:
                d_angle = math.pi
                d_length = 0.5 * math.pi * (2.0 * temp_r - string_gauge)
                length += d_length
                self.winding_fn.append([length, angle, d_angle/length, 0, string_gauge / d_length])
                angle += d_angle
                
            # Remaining turns.
            dl = turns_per_layer * string_gauge
            if ((index % 2) != 0):
                dl = -dl
            d_angle = 2.0 * math.pi * turns_per_layer
            dr = d_angle * temp_r
            d_length = math.sqrt(dl*dl + dr*dr)
            length += d_length
            self.winding_fn.append([length, angle, d_angle/length, dl / d_length, 0])
            angle += d_angle

            temp_r += string_gauge
            index += 1

        self.winding_fn[-1][0] = string_length

        # Calculate angle at which the string exits the drum.
        if (len(self.winding_fn) > 1):
            diff = string_length - self.winding_fn[-2][0]
        else:
            diff = string_length
        self.exit_angle = self.winding_fn[-1][1] + diff * self.winding_fn[-1][2]

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
