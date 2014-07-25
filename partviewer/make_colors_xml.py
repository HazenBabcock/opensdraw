#!/usr/bin/env python
#
## @file
#
# Parses a LDConfig.ldr file to create the colors.xml file.
#
# Hazen 07/14
#

import sys

from xml.dom import minidom
from xml.etree import ElementTree

if (len(sys.argv) != 2):
    print "usage: <path/and/LDConfig/file>"
    exit()

## parseColor
#
# @param color_string A string containing the color information as hex.
#
# @return [R, G, B] values given by the color string.
#
def parseColor(color_string):
    r = int(color_string[1:3], 16)
    g = int(color_string[3:5], 16)
    b = int(color_string[5:7], 16)
    
    return [r, g, b]

# Generate XML.
#file_xml = ElementTree.Element("ldraw-colors")

# Save part information.
with open(sys.argv[1]) as filep:
    ldraw_group = ""
    lego_id = ""
    lego_color = ""
    
    for line in filep:
        parsed_line = filter(None, line.strip().split(" "))
        if (len(parsed_line) < 3):
            continue

        if (parsed_line[0] == "0"):

            # LDraw color group.
            if (parsed_line[2] == "LDraw"):
                ldraw_group = " ".join(parsed_line[3:]).strip()
                print ldraw_group

            # Lego ID information.
            elif (parsed_line[2] == "LEGOID"):
                lego_id = parsed_line[3]
                lego_color = " ".join(parsed_line[5:]).strip()
                print " ", lego_id, lego_color
                
            # Color information
            elif (parsed_line[1] == "!COLOUR"):
                color = parsed_line[2]
                code = parsed_line[4]
                value = parsed_line[6]
                edge = parsed_line[8]
                alpha = 256
                if (len(parsed_line) > 9):
                    if (parsed_line[9] == "ALPHA"):
                        alpha = parsed_line[10]
                print "  ", color, code, value, parseColor(value), alpha
            
            
#            else:
#                print parsed_line

# Save results in a pretty-printed XML file.
#print ""
#print "saving.."
#rough_string = ElementTree.tostring(file_xml, 'utf-8')
#reparsed = minidom.parseString(rough_string)
#
#with open("parts.xml", "w") as out_fp:
#    out_fp.write(reparsed.toprettyxml(indent=" ", encoding = "utf-8"))
#
#print "Found", len(part_files), "parts"
#print "  ", len(categories.keys()), "categories"

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
