#!/usr/bin/env python
"""
.. module:: parts
   :synopsis: The part object.

.. moduleauthor:: Hazen Babcock
"""

import numpy

import opensdraw.lcad_lib.colorsParser as colorsParser

# Load colors and create dictionaries.
all_colors = colorsParser.loadColors()

lcad_name_dict = {}
for color_group in all_colors:
    for color in color_group:
        lcad_name_dict[color.name.lower()] = color

def formatNumber(a_number, precision):
    f_string = "{0:." + str(precision) + "f}"
    s = f_string.format(a_number)

    # Remove trailing zeros.
    s = s.rstrip('0').rstrip('.') if '.' in s else s

    # Remove leading minus (if zero).
    if (s == "-0"):
        s = "0"
    return s

def toColor(color):

    # Integer color.
    if isinstance(color, int):
        return str(color)

    # Direct color "0x2FFAABB"
    elif (color[0:3] == "0x2"):
        return color

    # Look up the color based on the name.
    else:
        return lcad_name_dict[color.lower()].code


# LDraw comments.
class Comment(object):
    
    def __init__(self, text):
        self.text = "0 " + text

    def toLDraw(self):
        return self.text


# LDraw parts.
class Part(object):

    def __init__(self, matrix, part_id, part_color, step):

        self.matrix = matrix.copy()
        self.part_color = toColor(part_color)
        self.part_id = part_id
        self.step = step

        #self.loc = numpy.array([0.0, 0.0, 0.0, 1.0])
        #self.loc = numpy.dot(self.model_matrix, self.loc)

    def toLDraw(self):
        """
        Return a string in ldraw format.

        :returns: str.
        """
        ld_str = "1 "

        # color
        ld_str += self.part_color + " "

        # xyz
        ld_str += formatNumber(self.matrix[0,3], 2) + " "
        ld_str += formatNumber(self.matrix[1,3], 2) + " "
        ld_str += formatNumber(self.matrix[2,3], 2) + " "

        # abcdefghi
        for i in range(3):
            for j in range(3):
                ld_str += formatNumber(self.matrix[i,j], 3) + " "

        # part
        if not (".dat" in self.part_id) and not (".ldr" in self.part_id):
            ld_str += self.part_id + ".dat"
        else:
            ld_str += self.part_id

        return ld_str


# LDraw primitives.
class LDraw(object):

    def __init__(self, matrix, coords, color):
        self.coords = coords
        self.color = toColor(color)
        self.step = 0

        # Transform coordinates using transformation matrix.
        if matrix is not None:
            for i in range(len(coords)/3):
                vec = numpy.array([self.coords[3*i],
                                   self.coords[3*i+1],
                                   self.coords[3*i+2],
                                   1.0])
                loc = numpy.dot(matrix, vec)
                self.coords[3*i] = loc[0]
                self.coords[3*i+1] = loc[1]
                self.coords[3*i+2] = loc[2]

    def toLDraw(self):
        ld_str = self.prefix + self.color + " "
        ld_str += " ".join(map(lambda(x): formatNumber(x, 3), self.coords))
        return ld_str

class Line(LDraw):

    def __init__(self, matrix, coords, color):
        LDraw.__init__(self, matrix, coords, color)
        self.prefix = "2 "


class OptionalLine(LDraw):

    def __init__(self, matrix, coords, color):
        LDraw.__init__(self, matrix, coords, color)
        self.prefix = "5 "


class Quadrilateral(LDraw):

    def __init__(self, matrix, coords, color):
        LDraw.__init__(self, matrix, coords, color)
        self.prefix = "4 "


class Triangle(LDraw):

    def __init__(self, matrix, coords, color):
        LDraw.__init__(self, matrix, coords, color)
        self.prefix = "3 "




#
# The MIT License
#
# Copyright (c) 2014 Hazen Babcock
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
