#!/usr/bin/env python
#
## @file
#
# Parse a dat file as described here:
# http://www.ldraw.org/article/218.html
#
# Hazen 07/14
#

import os
import sys
from xml.etree import ElementTree

import ldrawPath

#
# Find all the possible part directories & cache this.
# This uses the path specified in the parts.xml file.
#
directory = os.path.dirname(__file__)
if (directory == ""):
    directory = "./"
else:
    directory += "/"

ldraw_path = ldrawPath.getLDrawPath()

all_part_dirs = [""]
for a_dir in ["p", "parts"]:
    for [path_original, dirs, files] in os.walk(ldraw_path + a_dir):
        all_part_dirs.append(path_original + "/")

## findPartFile
#
# @param filename The name of the part file.
#
# @return The full path to a part file
#
def findPartFile(filename):
    filename = filename.replace("\\", "/")
    for part_dir in getPartDirectories():
        full_path = part_dir + filename
        if os.path.exists(full_path):
            return full_path
    raise IOError("Could not find file " + filename)

## getPartDirectories
#
# @return A list of the part directories
#
def getPartDirectories():
    global all_part_dirs
    return all_part_dirs

## parsePartFile
#
# This is the main entry point for parsing a part file.
#
# @param parser A part file parser object.
# @param filename The filename of the part file.
#
def parsePartFile(parser, filename):
    with open(findPartFile(str(filename))) as filep:
        parsePartFileP(parser, filep, 0)

## parsePartFileP
#
# This is called recursively to parse a part file.
#
# @param parser A part file parser object.
# @param filep A file pointer to the open part file.
# @param depth The current recursion depth.
#
def parsePartFileP (parser, filep, depth):
    parser.startFile(depth)
    for line in filep:
        
        parsed_line = filter(None, line.strip().split(" "))
        if (len(parsed_line) == 0):
            continue
            
        cmd_type = int(parsed_line[0])
            
        # Command.
        if (cmd_type == 0):
            parser.command(parsed_line)

        # Part file.
        elif (cmd_type == 1):
            new_parser = parser.newFile(parsed_line)
            if new_parser is not None:
                with open(findPartFile(parsed_line[-1].lower())) as new_part_filep:
                    parsePartFileP(new_parser, new_part_filep, depth + 1)

        # Line.
        elif (cmd_type == 2):
            parser.line(parsed_line)

        # Triangle.
        elif (cmd_type == 3):
            parser.triangle(parsed_line)

        # Quadrilateral.
        elif (cmd_type == 4):
            parser.quadrilateral(parsed_line)

        # Optional line.
        elif (cmd_type == 5):
            parser.optionalLine(parsed_line)

        else:
            raise Exception("Unrecognized command type " + str(cmd_type))

    parser.endFile()

## Parser
#
# The base class for parser objects.
#
class Parser(object):

    ## __init__
    #
    # @param main_color The main color.
    # @param edge_color The edge color.
    #
    def __init__(self, main_color, edge_color):
        self.depth = None
        self.edge_color = edge_color
        self.main_color = main_color

    ## command
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def command(self, parsed_line):
        self.prettyPrint("command")

    ## endFile
    #
    def endFile(self):
        self.prettyPrint("end file")

    ## line
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def line(self, parsed_line):
        self.prettyPrint("line")

    ## newFile
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    # @return A Parser object.
    #
    def newFile(self, parsed_line):
        self.prettyPrint("new file")
        return Parser(self.main_color, self.edge_color)

    ## optionalLine
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def optionalLine(self, parsed_line):
        self.prettyPrint("optional line")

    ## prettyPrint
    #
    # @param text The text to pretty print.
    #
    def prettyPrint(self, text):
        for i in range(self.depth):
            sys.stdout.write("  ")
        sys.stdout.write(text + "\n")
        
    ## quadrilateral
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def quadrilateral(self, parsed_line):
        self.prettyPrint("quadrilateral")

    ## startFile
    #
    # @param depth The current recursion depth.
    #
    def startFile(self, depth):
        self.depth = depth
        self.prettyPrint("start file")

    ## triangle
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def triangle(self, parsed_line):
        self.prettyPrint("triangle")


# Testing
if (__name__ == "__main__"):
    
    if 1:
        dirs = list(getPartDirectories())
        for dir in dirs:
            print dir

    if 0:
        parsePartFile(Parser(True, True), "c:/Program Files (x86)/LDraw/parts/15.dat")

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
