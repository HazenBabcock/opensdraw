#!/usr/bin/env python
"""
.. module:: parts
   :synopsis: The part object.

.. moduleauthor:: Hazen Babcock
"""

import numpy

import lcad_lib.colorsParser as colorsParser

# Load colors and create dictionaries.
all_colors = colorsParser.loadColors()

lcad_name_dict = {}
for color_group in all_colors:
    for color in color_group:
        lcad_name_dict[color.name.lower()] = color

def formatNumber(a_number, precision):
    f_string = "{0:." + str(precision) + "f}"
    return f_string.format(a_number)

class Part(object):

    def __init__(self, model_matrix, part_id, part_color, step):
        self.model_matrix = model_matrix
        try:
            self.part_color = int(part_color)
        except ValueError:
            self.part_color = part_color

        self.part_id = part_id
        self.step = step

        self.loc = numpy.array([0.0, 0.0, 0.0, 1.0])
        self.loc = numpy.dot(self.model_matrix, self.loc)

    def toLDraw(self):
        """
        Return a string in ldraw format.

        :returns: str.
        """
        ld_str = "1 "

        # color
        if isinstance(self.part_color, int):
            ld_str += str(self.part_color) + " "
        else:
            ld_str += lcad_name_dict[self.part_color.lower()].code + " "

        # xyz
        ld_str += formatNumber(self.model_matrix[0,3], 2) + " "
        ld_str += formatNumber(self.model_matrix[1,3], 2) + " "
        ld_str += formatNumber(self.model_matrix[2,3], 2) + " "

        # abcdefghi
        for i in range(3):
            for j in range(3):
                ld_str += formatNumber(self.model_matrix[i,j], 3) + " "

        # part
        if not (".dat" in self.part_id):
            ld_str += self.part_id + ".dat"
        else:
            ld_str += self.part_id

        return ld_str

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
