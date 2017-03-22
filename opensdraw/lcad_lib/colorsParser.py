#!/usr/bin/env python
"""
.. module:: colorsParser
   :synopsis: Parse the colors.xml file and return a list of Color objects
              grouped by color group.

.. moduleauthor:: Hazen Babcock

"""

import os
from xml.etree import ElementTree


class Color(object):
    """
    Color information class.
    """

    def __init__(self, color_node):
        """
        :param color_node: A colors.xml ElementTree XML node containing the color information.
        :type color_node: ElementTree.
        """
        self.code = color_node.attrib["code"]
        self.edge = color_node.attrib["edge"]
        self.lego_color = color_node.attrib["lego_color"]
        self.lego_id = color_node.attrib["lego_id"]
        self.name = color_node.attrib["name"]
        self.value = color_node.attrib["value"]

    def getDescription(self):
        return self.code + ", " + self.name
        
    def getEdgeColor(self, scale = "1"):
        """
        :param scale: (Optional) either 1 or 256.
        :type scale: int.
        :returns: tuple -- [r, g, b, a]
        """
        return self.parseColor(self.edge, scale)

    def getFaceColor(self, scale = "1"):
        """
        :param scale: (Optional) either 1 or 256.
        :type scale: int.
        :returns: tuple -- [r, g, b, a]
        """
        return self.parseColor(self.value, scale)

    def parseColor(self, color_string, scale = "1"):
        """
        :param color_string: A color string like "256,256,256,256".
        :type color_string: str.
        :param scale: (Optional) "256" or "1", defaults to "1".
        :type scale: int.
        :returns: tuple -- [r, g, b, a]
        """
        if (scale == "1"):
            return map(lambda x: float(x)/256.0, color_string.split(","))
        else:
            return map(int, color_string.split(","))


def loadColors(colors_file = None):
    """
    Parse a colors.xml file and return a dictionary of Color objects
    keyed by the color id.
    """
    color_xml = loadColorsFile()
    all_colors = {}
    for color_group in color_xml.find("colors"):
        cur_group = []
        for color_entry in color_group:
            color_obj = Color(color_entry)
            all_colors[color_obj.code] = color_obj

    return all_colors    

    
def loadColorsFile(colors_file = None):
    if colors_file is None:
        # The colors.xml file is assumed to exist in the xml directory, one directory above this module.
        colors_file = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0] + "/xml/colors.xml"

    return ElementTree.parse(colors_file).getroot()


def loadColorGroups(colors_file = None):
    """
    Parse a colors.xml file and return a list of Color of objects
    grouped by color group.
    """

    color_xml = loadColorsFile()
    all_colors = []
    for color_group in color_xml.find("colors"):
        cur_group = []
        for color_entry in color_group:
            cur_group.append(Color(color_entry))
        all_colors.append(cur_group)

    return all_colors


if (__name__ == '__main__'):
    all_colors = loadColors()
    for key in sorted(all_colors.keys()):
        print(key, all_colors[key].name)

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
