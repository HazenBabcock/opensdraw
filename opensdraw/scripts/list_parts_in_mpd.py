#!/usr/bin/env python
"""
Lists all the unique parts and their colors in a .mpd file. This
is sometimes useful for determining the name of a part and/or a
color.

Hazen 04/15
"""

import os
import re
import sys

import opensdraw.lcad_lib.datFileParser as datFileParser

if (len(sys.argv) != 2):
    print("usage: <ldraw file (input)>")
    exit()

parts = {}

def arrayToString(array):
    """
    Convert an array to a string & clean it up. The assumption is that
    no part in the LDraw library is going to have a space in the name..
    """
    return re.sub(r'[^a-zA-Z0-9\.]', '_', "".join(array))

class PartsFinder(datFileParser.Parser):
    """
    This class finds all the parts in ldraw format file and records the
    name, id and color of the parts that also exist in the ldraw parts
    library.
    """
    def __init__(self):
        datFileParser.Parser.__init__(self, None, None)
        self.sub_parts = {}
        self.parts = {}

    def command(self, parsed_line):
        pass

    def endFile(self):
        pass
        
    def line(self, parsed_line):
        pass

    def newFile(self, parsed_line):
        
        ldraw_color = parsed_line[1]
        ldraw_id = parsed_line[14]
        part_file = None

        # Try and find part in parts folder.
        try:
            part_file = datFileParser.findPartFile(ldraw_id)
        except IOError:
            pass

        # If this part exists, figure out whether it is a part or a sub-part
        # based on the path & add to the appropriate dictionary.
        if part_file is not None:
            is_part = True
            if (os.path.split(os.path.split(part_file)[0])[1] != "parts"):
                is_part = False

            fp = open(part_file)
            description = fp.readline()[2:].strip()
            fp.close()
            
            part_id = ldraw_id + "_" + ldraw_color
            if is_part:
                self.parts[part_id] = description
            else:
                self.sub_parts[part_id] = description

    def optionalLine(self, parsed_line):
        pass

    def quadrilateral(self, parsed_line):
        pass

    def startFile(self, depth):
        pass

    def triangle(self, parsed_line):
        pass


# Find all the parts.
partsFinder = PartsFinder()
datFileParser.parsePartFile(partsFinder, sys.argv[1])

print("Parts:")
for key in sorted(partsFinder.parts, key = partsFinder.parts.get):
    [part_id, part_color] = key.split("_")
    print(part_id[:-4] + ", " + part_color + ", " + partsFinder.parts[key])
print("\n")

print("Sub Parts:")
for key in sorted(partsFinder.sub_parts, key = partsFinder.sub_parts.get):
    [part_id, part_color] = key.split("_")
    print(part_id[:-4] + ", " + part_color + ", " + partsFinder.sub_parts[key])
print("\n")

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
