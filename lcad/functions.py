#!/usr/bin/env python
#
# Special functions that are available in lcad.
#
# Hazen 07/14
#

import math
import numpy

import interpreter
import parts

fn = []

def addfn(n_args):
    def decorator(func):
        global fn
        fn.append([func.__name__, n_args])
        return func(*args, **kw)

@addfn(2)
def part(env part_id part_color):
    part_id = interpreter.interpret(env, part_id)
    part_color = interpreter.interpret(env, part_color)
    env.parts_list.append(parts.Part(env.m, part_id, part_color))

@addfn(3)
def rotate(env ax ay az *ast):
    new_env = env.make_copy()

    ax = interpreter.interpret(new_env, ax) * numpy.pi / 180.0
    ay = interpreter.interpret(new_env, ay) * numpy.pi / 180.0
    az = interpreter.interpret(new_env, az) * numpy.pi / 180.0

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

    new_env.m = numpy.dot(new_v.m, (numpy.dot(rx, numpy.dot(ry, rz))))

    interpreter.interpret(new_env, *ast)

@addfn(3)
def translate(env dx dy dz *ast):
    new_env = env.make_copy()

    m = numpy.identity(4)
    m[0,3] = interpreter.interpret(new_env, dx)
    m[1,3] = interpreter.interpret(new_env, dy)
    m[2,3] = interpreter.interpret(new_env, dz)
    new_env.m = numpy.dot(new_env.m, m)

    interpreter.interpret(new_env, *ast)

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
