#!/usr/bin/env python
"""
.. module:: partFunctions
   :synopsis: Functions for creating parts, headers and groups.

.. moduleauthor:: Hazen Babcock

"""

import numbers
import numpy

import functions
import geometryFunctions
import interpreter as interp
import lcadExceptions as lce
import parts

lcad_functions = {}

class EmptyTree(object):
    """
    An empty AST.
    """
    def __init__(self):
        self.value = [False]

class PartFunction(functions.LCadFunction):
    pass


class PrimitiveFunction(PartFunction):
    """
    Base class for primitives like line, triangle, etc.
    """
    def __init__(self, name):
        PartFunction.__init__(self, name)

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        coords = []

        # Get color.
        if (len(args) == (self.num_vertices + 1)):
            color = args[-1]
            args = args[:-1]
        else:
            color = 16

        # Get coordinates.
        for vertex in args:
            coords.extend(geometryFunctions.parseArgs(vertex))

        group = model.curGroup()
        group.addPart(self.parts_fn(group.matrix(), coords, color), True)


class Comment(PartFunction):
    """
    **comment** - Adds comments into the model. This different 
    from header() in that these will appear in the body of the
    file along with parts, etc.. And if group has comments then
    the step parameter of the part() function will be ignored,
    so if steps are desired they'll need to be manually created
    with this function.

    This will add a line of text, prepended with "0 ", to the
    current model. Multiple calls will add multiple lines, in
    the same order as the calls.

    Usage::
    
     (comment "BFC INVERTNEXT")
     (comment "STEP")
    """
    def __init__(self):
        PartFunction.__init__(self, "comment")
        self.setSignature([[basestring, numbers.Number]])

    def call(self, model, tree):
        text = str(self.getArg(model, tree, 0))
        group = model.curGroup()
        group.addComment(parts.Comment(text))
        return text

lcad_functions["comment"] = Comment()


class Group(PartFunction):
    """
    **group** - Creates a group (or sub-file) in the model.

    This allows the grouping of parts to create a multi-part
    output file. Normally you probably want to group parts
    into a function, but sometimes you might want to 
    generate output that is better formatted for tools that
    work on mpd files.

    Note that:

    1. When created groups always have the identity transformation 
    matrix, not the current transformation matrix.

    2. Group names must be unique (and also not overlap with the
    names of any LDraw part files).

    Usage::

     (group "assembly1"   ; Create a group called "assembly1"
       (part ..))         ; containing a single part.

    """
    def __init__(self):
        PartFunction.__init__(self, "group")
        self.setSignature([[basestring], ["optional", [object]]])

    def call(self, model, tree):
        if (self.numberArgs(tree) > 1):
            model.pushGroup(self.getArg(model, tree, 0))
            val = interp.interpret(model, tree.value[2:])
            model.popGroup()
            return val
        else:
            return None

lcad_functions["group"] = Group()


class Header(PartFunction):
    """
    **header** - Adds header information to the model.

    This will add a line of text, prepended with "0 ", to the
    current model. Multiple calls will add multiple lines, in
    the same order as the calls.

    Usage::
    
     (header "FILE mymoc")
     (header "Name: mymoc")
     (header "Author: My Name")
    """
    def __init__(self):
        PartFunction.__init__(self, "header")
        self.setSignature([[basestring]])

    def call(self, model, tree):
        text = self.getArg(model, tree, 0)
        model.curGroup().header.append(text)
        return text

lcad_functions["header"] = Header()


class Line(PrimitiveFunction):
    """
    **line** - Add a line primitive to the model.

    The arguments are (list x1 yz 1) (list x2 y2 z2).

    :param x1: x position of vertex 1.
    :param y1: y position of vertex 1.
    :param z1: z position of vertex 1.
    :param x2: x position of vertex 2.
    :param y2: y position of vertex 2.
    :param z2: z position of vertex 2.
    :param color: (optional) line color, defaults to 16, the "main color".

    Usage::

     (line (list x1 y1 z1) (list x2 y2 z2) color)    ; A line from (x1, y1, z1) to (x2, y2, z2) with color color.
     (line (list x1 y1 z1) (list x2 y2 z2))          ; Same as above, but now color will be the "main color", i.e. 16.

    """
    def __init__(self):
        PrimitiveFunction.__init__(self, "line")
        self.num_vertices = 2
        self.parts_fn = parts.Line
        self.setSignature([[list, numpy.ndarray], 
                           [list, numpy.ndarray], 
                           ["optional", [basestring, int]]])

lcad_functions["line"] = Line()


class OptionalLine(PrimitiveFunction):
    """
    **optional-line** - Add a optional line primitive to the model.

    The arguments are (list x1 yz 1) (list x2 y2 z2) (list x3 y3  z3) (list x4 y4 z4).

    :param x1: x position of line vertex 1.
    :param y1: y position of line vertex 1.
    :param z1: z position of line vertex 1.
    :param x2: x position of line vertex 2.
    :param y2: y position of line vertex 2.
    :param z2: z position of line vertex 2.
    :param x1: x position of control vertex 1.
    :param y1: y position of control vertex 1.
    :param z1: z position of control vertex 1.
    :param x2: x position of control vertex 2.
    :param y2: y position of control vertex 2.
    :param z2: z position of control vertex 2.
    :param color: (optional) line color, defaults to 16, the "main color".

    Usage::

     (optional-line (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3) (list x4 y4 z4) color) ; A optional line with vertices (x1, y1, z1), (x2, y2, z2) 
                                                                                           ; and control point vertices (x3, y3, z3), (x4, y4, z4).
     (optional-line (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3) (list x4 y4 z4))       ; Same as above, but now color will be the "main color", i.e. 16.

    """
    def __init__(self):
        PrimitiveFunction.__init__(self, "optional-line")
        self.num_vertices = 4
        self.parts_fn = parts.OptionalLine
        self.setSignature([[list, numpy.ndarray], 
                           [list, numpy.ndarray],
                           [list, numpy.ndarray],
                           [list, numpy.ndarray],
                           ["optional", [basestring, int]]])

lcad_functions["optional-line"] = OptionalLine()


class Part(PartFunction):
    """
    **part** - Add a part to the model.

    :param part_id: The name of the LDraw .dat file for this part.
    :param part_color: The LDraw name or id of the color.
    :param part_step: (Optional) Which building step to add the part (default = first step).

    Usage::

     (part "32524" 13)           ; Technic Beam 7, LDraw color 13.
     (part '32524' "yellow")     ; Technic Beam 7, LDraw color yellow.
     (part "32524" "yellow" 10)  ; Technic Beam 7, LDraw color yellow, step 10.
     (part "32524" "0x2808080")  ; Technic Beam 7, direct color (gray).

    """
    def __init__(self):
        PartFunction.__init__(self, "part")
        self.setSignature([[basestring],
                           [basestring, numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)

        # Get step offset.
        step_offset = interp.getv(interp.builtin_symbols["step-offset"])

        # Check if it is a function, if so, call the function (which cannot take any arguments).
        if not isinstance(step_offset, numbers.Number):
            step_offset = interp.getv(step_offset.call(model, EmptyTree()))

        if not isinstance(step_offset, numbers.Number):
            raise lce.WrongTypeException("number", type(step_offset))

        if (len(args) == 3):
            part_step = args[2] + step_offset
        else:
            part_step = step_offset
        group = model.curGroup()
        group.addPart(parts.Part(group.matrix(), args[0], args[1], part_step), False)
        return None

lcad_functions["part"] = Part()


class Quadrilateral(PrimitiveFunction):
    """
    **quadrilateral** - Add a quadrilateral primitive to the model.

    The arguments are (list x1 yz 1) (list x2 y2 z2) (list x3 y3  z3) (list x4 y4 z4).

    :param x1: x position of vertex 1.
    :param y1: y position of vertex 1.
    :param z1: z position of vertex 1.
    :param x2: x position of vertex 2.
    :param y2: y position of vertex 2.
    :param z2: z position of vertex 2.
    :param x3: x position of vertex 3.
    :param y3: y position of vertex 3.
    :param z3: z position of vertex 3.
    :param x4: x position of vertex 4.
    :param y4: y position of vertex 4.
    :param z4: z position of vertex 4.
    :param color: (optional) fill color, defaults to 16, the "main color".

    You should probably also specify a winding order using the header() function.

    Example::

     (header "BFC CERTIFY CCW")

    Usage::

     (quadrilateral (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3) (list x4 y4 z4) color) ; A quadrilateral with vertices (x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4).
     (quadrilateral (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3) (list x4 y4 z4))       ; Same as above, but now color will be the "main color", i.e. 16.

    """
    def __init__(self):
        PrimitiveFunction.__init__(self, "quadrilateral")
        self.num_vertices = 4
        self.parts_fn = parts.Quadrilateral
        self.setSignature([[list, numpy.ndarray], 
                           [list, numpy.ndarray],
                           [list, numpy.ndarray],
                           [list, numpy.ndarray],
                           ["optional", [basestring, int]]])

lcad_functions["quadrilateral"] = Quadrilateral()


class Triangle(PrimitiveFunction):
    """
    **triangle** - Add a triangle primitive to the model.

    The arguments are (list x1 yz 1) (list x2 y2 z2) (list x3 y3  z3).

    :param x1: x position of vertex 1.
    :param y1: y position of vertex 1.
    :param z1: z position of vertex 1.
    :param x2: x position of vertex 2.
    :param y2: y position of vertex 2.
    :param z2: z position of vertex 2.
    :param x3: x position of vertex 3.
    :param y3: y position of vertex 3.
    :param z3: z position of vertex 3.
    :param color: (optional) fill color, defaults to 16, the "main color".

    You should probably also specify a winding order using the header() function.

    Example::

     (header "BFC CERTIFY CCW")

    Usage::

     (triangle (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3) color)  ; A triangle with vertices (x1, y1, z1), (x2, y2, z2), (x3, y3, z3).
     (triangle (list x1 y1 z1) (list x2 y2 z2) (list x3 y3 z3)         ; Same as above, but now color will be the "main color", i.e. 16.

    """
    def __init__(self):
        PrimitiveFunction.__init__(self, "triangle")
        self.num_vertices = 3
        self.parts_fn = parts.Triangle
        self.setSignature([[list, numpy.ndarray], 
                           [list, numpy.ndarray],
                           [list, numpy.ndarray],
                           ["optional", [basestring, int]]])

lcad_functions["triangle"] = Triangle()


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
