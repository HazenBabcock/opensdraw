#!/usr/bin/env python
"""
.. module:: partsString
   :synopsis: Python functions to add parts using return delimited strings.

.. moduleauthor:: Hazen Babcock
"""

import numpy

import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.geometry as geometry
import opensdraw.lcad_language.interpreter as interpreter
import opensdraw.lcad_language.parts as parts

import opensdraw.lcad_language.lcadExceptions as lcadExceptions

lcad_functions = {}


def addParts(model, parts_string):
    """
    This does the actual parsing of the parts from the string.
    """
    lines = parts_string.splitlines()
    group = model.curGroup()
    matrix = group.matrix()
    step_offset = interpreter.getStepOffset(model)

    # Configure brick spacing.
    bw = 20.0
    bh = 24.0
    if ("technic" in lines[0]):
        bh = 20.0
        lines = lines[1:]

    # Process lines.
    for line in lines:
        line = line.strip()

        # Check that this is not a comment line.
        if (len(line) > 0) and (line[0] != ";"):
            data = line.split(" ")
            if ((len(data) == 8) or (len(data) == 9)):

                # Get position and orientation and adjust for brick spacing.
                pos_ori = map(float, data[0:6])
                pos_ori[0] = bw * pos_ori[0]
                pos_ori[1] = bw * pos_ori[1]
                pos_ori[2] = bh * pos_ori[2]
                
                # Calculate part matrix.
                partm = geometry.listToMatrix(pos_ori)
                curm = numpy.dot(matrix, partm)

                # Color
                try:
                    color = int(data[7])
                except ValueError:
                    color = data[7]
                    
                # Add the part to the model.
                if (len(data) == 8):
                    group.addPart(parts.Part(curm, data[6], color, step_offset), False)
                else:
                    group.addPart(parts.Part(curm, data[6], color, step_offset + int(data[8])), False)
            else:
                # Warning for non blank lines.
                if (len(data) > 1):
                    print(line, "has an unexpected number of elements", len(data))


class PartsFile(functions.LCadFunction):
    """
    **parts-file** - Specify parts in a text file.

    This lets you load parts from a text file that is formatted in the
    same fashion as for the *parts-string()* function.

    :param file: A string containing the name of the file to load.

    Usage::

     (parts-file "parts_file.txt") ; Load parts from parts_file.txt

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "parts-file")
        self.setSignature([[basestring]])
        
    def call(self, model, filename):
        with open(filename) as fp:
            addParts(model, fp.read())

lcad_functions["parts-file"] = PartsFile()


class PartsString(functions.LCadFunction):
    """
    **parts-string** - Specify parts using a return delimited string.
    
    This lets you specify parts using a return delimited string, instead
    of having to use a function like *tb()* or *sb()* from *locate.lcad*.
    When you have lots of parts with a relatively simple geometry this might 
    be faster and easier. If the first line of the string contains the word
    "technic" then technic brick spacing will be used instead of standard
    brick spacing. Any line that contains 8 or 9 elements is assumed to
    specify a part as *(x, y, z, x rotation, y rotation, z rotation,
    part, color, {optional} step)*. Other lines are ignored, including
    all lines that start with ";".
    
    :param string: The string of part locations and types.

    Usage::

     ; 3 2x1 bricks using standard brick units.
     (parts-string "0 0 0 -90 0 0 3004 Red
                    0 0 1 -90 0 0 3004 Green
                    0 0 2 -90 0 0 3004 Blue")

     ; 3 technic beam 2 using standard technic units.
     (parts-string "technic
                    0 2 0 90 0 0 43857 4
                    0 2 1 90 0 0 43857 2
                    0 2 2 90 0 0 43857 1")

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "parts-string")
        self.setSignature([[basestring]])

    def call(self, model, string):
        addParts(model, string)

lcad_functions["parts-string"] = PartsString()

