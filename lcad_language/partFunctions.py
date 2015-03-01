#!/usr/bin/env python
"""
.. module:: partFunctions
   :synopsis: Functions for creating parts, headers and groups.

.. moduleauthor:: Hazen Babcock

"""

import numbers

import functions
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
    names of any LDRaw part files.

    Usage::

    (group "assembly1"   ; Create a group called "assembly1" with
     (part ..))          ; containing a single part.

    """
    def __init__(self):
        PartFunction.__init__(self, "group")

    def argCheck(self, tree):
        if (len(tree.value)<3):
            raise lce.NumberArgumentsException("2+", len(flist)-1)

    def call(self, model, tree):
        if (len(tree.value) > 2):
            name = interp.getv(interp.interpret(model, tree.value[1]))
            if not isinstance(name, basestring):
                raise lce.WrongTypeException("string", type(name))
            model.pushGroup(name)
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

    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lce.NumberArgumentsException("2", len(tree.value) - 1)

    def call(self, model, tree):
        text = str(tree.value[1].value)
        model.curGroup().header.append(text)
        return text

lcad_functions["header"] = Header()


class Part(PartFunction):
    """
    **part** - Add a part to the model.

    :param part_id: The name of the LDraw .dat file for this part.
    :param part_color: The LDraw name or id of the color.
    :param part_step: (Optional) Which building step to add the part (default = first step).

    Usage::

     (part "32524" 13)
     (part '32524' "yellow")
     (part "32524" "yellow" 10)

    """
    def __init__(self):
        PartFunction.__init__(self, "part")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist) != 3) and (len(flist) != 4):
            raise lce.NumberArgumentsException("2-3", len(flist) - 1)

    def call(self, model, tree):
        args = tree.value[1:]
        part_id = interp.getv(interp.interpret(model, args[0]))
        part_color = interp.getv(interp.interpret(model, args[1]))

        # Get step offset.
        step_offset = interp.getv(interp.builtin_symbols["step-offset"])

        # Check if it is a function, if so, call the function (which cannot take any arguments).
        if not isinstance(step_offset, numbers.Number):
            step_offset = interp.getv(step_offset.call(model, EmptyTree()))

        if not isinstance(step_offset, numbers.Number):
            raise lce.WrongTypeException("number", type(step_offset))

        if (len(args) == 3):
            part_step = interp.getv(interp.interpret(model, args[2])) + step_offset
        else:
            part_step = step_offset
        group = model.curGroup()
        group.addPart(parts.Part(group.matrix(), part_id, part_color, part_step))
        return None

lcad_functions["part"] = Part()


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
