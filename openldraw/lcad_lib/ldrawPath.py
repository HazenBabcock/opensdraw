#!/usr/bin/env python
#
# Path to LDraw handling.
#
# Hazen 3/15
#

import os
import sys

from xml.dom import minidom
from xml.etree import ElementTree

path = os.path.dirname(__file__)
if (len(path) == 0):
    path_xml_file = "./../xml/ldraw_path.xml"
else:
    path_xml_file = path + "/../xml/ldraw_path.xml"

def getLDrawPath():
    xml = ElementTree.parse(path_xml_file).getroot()
    return xml.find("path").attrib["path"]

def saveLDrawPath(path):
    xml = ElementTree.Element("ldraw-path")
    path_xml = ElementTree.SubElement(xml, "path")
    path_xml.set("path", path)

    rough_string = ElementTree.tostring(xml, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    with open(path_xml_file, "w") as out_fp:
        out_fp.write(reparsed.toprettyxml(indent=" ", encoding = "utf-8"))


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
