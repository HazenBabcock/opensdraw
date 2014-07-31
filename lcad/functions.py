#!/usr/bin/env python
"""
.. module:: functions
   :synopsis: The functions that are available in lcad.

.. moduleauthor:: Hazen Babcock


"""

from functools import wraps
from itertools import izip
import math
import numpy

import lcadExceptions as lce
import lexerParser
from interpreter import Box, interpret
import parts

fn = {}

def addfn(func, args_number, args_gt = False, name = None):
    """
    This adds the function to the list of (built-in) functions and
    it decorates the function with some additional information
    that we can use later to verify that the function was called
    properly.
    """
    global fn
    func.builtin = True
    func.args_number = args_number
    func.args_gt = args_gt
    if name is not None:
        fn[name] = func
    else:
        fn[func.__name__] = func


# Work around that def already exists in Python.
def deflc(env, args):
    """
    Create a variable or function.

    Usage:
     (def x 15) - Create the variable x with the value 15.
     (def x 15 y 20) - Create x with value 15, y with value 20.
     (def incf (x) (+ x 1)) - Create the function incf.

    Note that you cannot create multiple functions at the same time.
    """
    # Variables.
    if ((len(args)%2) == 0):
        ret = None
        cur_env = env.make_copy()
        kv_pairs = izip(*[iter(args)]*2)
        for key, value in kv_pairs:
            if not isinstance(key, lexerParser.LCadSymbol):
                raise lce.CannotSetException(env,
                                             key.simple_type_name)

            val = interpret(cur_env, value)
            # This is so that later variable definitions can "see" earlier ones.
            cur_env.variables[key.value] = Box(val)

            # Warn about variable shadowing?
            if key.value in env.variables:
                print "!Warning in '" + env.fn_name + "' at line", env.fn_line, ",", key.value, "is already defined"
            env.variables[key.value] = Box(val)
            ret = val
        return ret

    # Functions.
    else:
        pass

    return None
addfn(deflc, 2, True, "def")

def part(env, args):
    """
    Add a part to the model.

    :param part_id: The name of the LDraw .dat file for this part.
    :param part_color: The LDraw name or id of the color.

    Usage:
     (part "32524" 13)
     (part '32524' "yellow")

    """
    part_id = interpret(env, args[0])
    part_color = interpret(env, args[1])
    env.parts_list.append(parts.Part(env.m, part_id, part_color))
    return None
addfn(part, 2, True)

def rotate(env, args):
    """
    Add a rotation to the current transformation matrix, rotation 
    is done first around z, then y and then x. Parts added inside
    a rotate block have this transformation applied to them.

    :param ax: Amount to rotate around the x axis in degrees.
    :param ay: Amount to rotate around the y axis in degrees.
    :param az: Amount to rotate around the y axis in degrees.

    Usage:
     (rotate 0 0 90 .. )

    """
    cur_env = env.make_copy()
    ax = interpret(cur_env, args[0]) * numpy.pi / 180.0
    ay = interpret(cur_env, args[1]) * numpy.pi / 180.0
    az = interpret(cur_env, args[2]) * numpy.pi / 180.0

    rx = numpy.identity(4)
    rx[1,1] = math.cos(ax)
    rx[1,2] = -math.sin(ax)
    rx[2,1] = -rx[1,2]
    rx[2,2] = rx[1,1]

    ry = numpy.identity(4)
    ry[0,0] = math.cos(ax)
    ry[0,2] = -math.sin(ax)
    ry[2,0] = -ry[0,2]
    ry[2,2] = ry[0,0]

    rz = numpy.identity(4)
    rz[0,0] = math.cos(ax)
    rz[0,1] = -math.sin(ax)
    rz[1,0] = -rz[0,1]
    rz[1,1] = rz[0,0]

    cur_env.m = numpy.dot(cur_env.m, (numpy.dot(rx, numpy.dot(ry, rz))))
    if (len(args) > 3):
        return interpret(cur_env, args[3:])
    else:
        return None
addfn(rotate, 3, True)

# Work around that set already exists in Python.
def setlc(env, args):
    """
    Set the value of an existing symbol.

    Usage:
     (set x 15) - Set the value of x to 15.
     (set x 15 y 20) - Set x to 15 and y to 20.
     (set x fn) - Set x to value of the symbol fn.
    """
    ret = None
    cur_env = env.make_copy()
    kv_pairs = izip(*[iter(args)]*2)
    for key, value in kv_pairs:
        if not isinstance(key, lexerParser.LCadSymbol):
            raise lce.CannotSetException(env,
                                         key.simple_type_name)

        if not key.value in env.variables:
            raise lce.VariableNotDefined(env,
                                         key.value)
        val = interpret(cur_env, value)
        env.variables[key.value].value = val
        ret = val
    return ret
addfn(setlc, 2, True, "set")

def translate(env, args):
    """
    Add a rotation to the current transformation matrix. Parts inside a translate
    block have this transformation applied to them.

    :param dx: Displacement in x in LDU.
    :param dy: Displacement in x in LDU.
    :param dz: Displacement in x in LDU.

    Usage:
     (translate 0 0 5 .. )

    """
    cur_env = env.make_copy()
    m = numpy.identity(4)
    m[0,3] = interpret(cur_env, args[0])
    m[1,3] = interpret(cur_env, args[1])
    m[2,3] = interpret(cur_env, args[2])

    cur_env.m = numpy.dot(cur_env.m, m)
    if (len(args) > 3):
        return interpret(cur_env, args[3:])
    else:
        return None
addfn(translate, 3, True)

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
