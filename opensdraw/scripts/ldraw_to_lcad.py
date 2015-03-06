#!/usr/bin/env python
#
# Generates a .lcad file from a LDraw format .dat, .ldr or .mpd file.
# Depending on the LDraw file the conversion may not be that pretty.
# In particular matrices that include a scale term are going to play
# havoc with angle extraction.
#
# Since opensdraw does not handle primitives, subfiles that contain
# primitives are broken out into separate files.
#
# In "standard" mode it will use the sbs() function for brick placement,
# and in "technic" mode it use the tbs() function.
#
# This assumes that the path to the ldraw parts directory in the 
# parts.xml file is correct.
#
# Refs:
#  1. http://nghiaho.com/?page_id=846
#
# Hazen 02/15
#

import math
import numpy
import os
import re
import sys

import opensdraw.lcad_lib.datFileParser as datFileParser

if (len(sys.argv) < 3):
    print "usage: <ldraw file (input)> <lcad file (output)> <(0 - std|1 - technic)"
    exit()


def arrayToString(array):
    """
    Convert an array to a string & clean it up. The assumption is that
    no part in the LDraw library is going to have a space in the name..
    """
    return re.sub(r'[^a-zA-Z0-9\.]', '_', "".join(array))

def formatNumber(a_number):
    return "{0:.3f}".format(a_number)

class FileFinder(datFileParser.Parser):
    """
    This class determines the what (if any) sub-files are contained in the file
    and whether or not the sub-files contain any primitives (i.e. lines, etc..).
    """
    def __init__(self):
        datFileParser.Parser.__init__(self, None, None)
        self.sub_files = []

    def command(self, parsed_line):
        if (parsed_line[1] == "FILE"):
            self.endSubFile()
            self.no_primitives = True

            # Is the file name always the next elements?
            self.sub_files.append([arrayToString(parsed_line[2:]), True])

    def endFile(self):
        self.endSubFile()
        
    def endSubFile(self):
        if (len(self.sub_files) > 0):
            if not self.no_primitives:
                self.sub_files[-1][1] = False

    def line(self, parsed_line):
        self.no_primitives = False

    def newFile(self, parsed_line):
        pass

    def optionalLine(self, parsed_line):
        self.no_primitives = False

    def quadrilateral(self, parsed_line):
        self.no_primitives = False

    def startFile(self, depth):
        pass

    def triangle(self, parsed_line):
        self.no_primitives = False


class FileGenerator(datFileParser.Parser):
    """
    This class generates all the output files.
    """
    def __init__(self, lcad_filename, sub_files, technic = False):
        datFileParser.Parser.__init__(self, None, None)
        self.dat_filep = None
        self.file_number = 0
        self.indent = ""
        self.in_header = False
        self.lcad_filename = lcad_filename
        self.lcad_filep = open(lcad_filename, "w")
        self.sub_files = sub_files
        self.step = 1

        # Add locate library.
        self.lcad_filep.write("\n")
        self.lcad_filep.write("(import locate :local)")
        self.lcad_filep.write("\n")

        # Figure out which locate function to use.
        self.brick_w = 20.0
        if (len(sys.argv) == 4) and (sys.argv[3] != "0"):
            print "Using technic coordinates."
            self.brick_h = 20.0
            self.is_technic = True
        else:
            print "Using standard coordinates."
            self.brick_h = 24.0
            self.is_technic = False

    def addLineToDat(self, parsed_line):
        if self.dat_filep is not None:
            self.dat_filep.write(" ".join(parsed_line) + "\n")
            return True
        else:
            return False

    def command(self, parsed_line):
        if (parsed_line[1] == "FILE"):
            file_name = arrayToString(parsed_line[2:])

            # Close current raw data file (if any).
            if self.dat_filep is not None:
                self.dat_filep.close()
                self.dat_filep = None

            # Open next raw data file (if necessary).
            for sfile in self.sub_files:
                if not sfile[1] and (file_name == sfile[0]):
                    self.dat_filep = open(file_name, "w")
                    self.addLineToDat(parsed_line)
                    break

            # If this is not a raw data file, start the next function.
            if self.dat_filep is None:

                # End previous function.
                if (self.file_number > 1):
                    self.lcad_filep.write(" )\n")

                self.lcad_filep.write("\n")
                
                if (self.file_number > 0):
                    self.lcad_filep.write("(group \"" + file_name + "\"\n")
                    self.indent = " "

                self.file_number += 1

            # Reset step counter.
            self.step = 1

            # Header starts after FILE, goes to first command.
            self.in_header = True
        else:
            if not self.addLineToDat(parsed_line):
                if (parsed_line[1] == "STEP"):
                    self.step += 1
                if self.in_header:
                    self.lcad_filep.write(self.indent + "(header \"" + " ".join(parsed_line[1:]) + "\")\n")

    def endFile(self):
        if self.dat_filep is not None:
            self.dat_filep.close()
            self.dat_filep = None
        if (len(self.sub_files) > 0):
            self.lcad_filep.write(" )\n")
            self.lcad_filep.write("\n")
        self.lcad_filep.close()

    def line(self, parsed_line):
        self.in_header = False
        self.addLineToDat(parsed_line)

    def newFile(self, parsed_line):
        self.in_header = False

        # Handle whitespace in the filename.
        if (len(parsed_line) > 15):
            parsed_line[14] = arrayToString(parsed_line[14:])
            parsed_line = parsed_line[0:15]

        if not self.addLineToDat(parsed_line):

            # Check if this part is a sub-file or a sub-part.
            a_file = parsed_line[14]
            sub_file = False
            sub_part = False
            for sfile in self.sub_files:
                if (sfile[0] == a_file):
                    if sfile[1]:
                        sub_file = True
                    else:
                        sub_part = True
                    break

            # If the part is not a sub-file or a sub-part, then get it's description.
            description = None
            if not sub_file and not sub_part:
                part_file = None
                try:
                    part_file = datFileParser.findPartFile(a_file)
                except IOError:
                    print "Could not find", a_file, "in", datFileParser.ldraw_path
                
                if part_file is not None:
                    fp = open(part_file)
                    description = fp.readline()[2:].strip()
                    fp.close()

            # Add part and description.
            self.lcad_filep.write("\n")
            if description is not None:
                self.lcad_filep.write(self.indent + "; " + str(description) + "\n")

            # Determine color, location and orientation.
            color = parsed_line[1]
            [x, y, z, a, b, c, d, e, f, g, h, i] = map(float, parsed_line[2:14])
            bx = x/self.brick_w
            by = y/self.brick_w
            bz = z/self.brick_h

            ry = math.atan2(-c, math.sqrt(f*f + i*i))

            # If the rotation around the y axis is +- 90 then we can't separate the x-axis rotation
            # from the z-axis rotation. In this case we just assume that the x-axis rotation is
            # zero and that there was only z-axis rotation.
            if (abs(math.cos(ry)) < 1.0e-3):
                rx = 0
                rz = math.atan2(d,e)
            else:
                rx = -math.atan2(f,i)
                rz = -math.atan2(b,a)

            rx = 180.0*rx/math.pi
            ry = 180.0*ry/math.pi
            rz = 180.0*rz/math.pi
            
            pos_string = " " + " ".join(map(formatNumber, [bx, by, bz, rx, ry, rz])) + " "
            sub_string = pos_string + "\"" + str(a_file) + "\" " + color + " " + str(self.step) + ")\n"
            if self.is_technic:
                self.lcad_filep.write(self.indent + "(tbs" + sub_string)
            else:
                self.lcad_filep.write(self.indent + "(sbs" + sub_string)

    def optionalLine(self, parsed_line):
        self.in_header = False
        self.addLineToDat(parsed_line)

    def quadrilateral(self, parsed_line):
        self.in_header = False
        self.addLineToDat(parsed_line)

    def startFile(self, depth):
        pass

    def triangle(self, parsed_line):
        self.in_header = False
        self.addLineToDat(parsed_line)


# Find sub-files (if any).
find = FileFinder()
datFileParser.parsePartFile(find, sys.argv[1])

# Generate .lcad
gen = FileGenerator(sys.argv[2], find.sub_files)
datFileParser.parsePartFile(gen, sys.argv[1])

if (len(find.sub_files) > 0):
    print "Created the following .dat files that will need to be findable by your rendering program:"
    for sfile in find.sub_files:
        if not sfile[1]:
            print sfile[0]

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
