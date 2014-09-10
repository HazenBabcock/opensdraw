#!/usr/bin/env python
"""
.. module:: lcad_to_ldraw
   :synopsis: Generates a ldraw format file from a lcad model.

.. moduleauthor:: Hazen Babcock
"""

import sys

import lcad_language.interpreter as interpreter

if (len(sys.argv)!=3):
    print "usage: <lcad file> <ldraw file>"
    exit()

with open(sys.argv[1]) as fp:
    parts = interpreter.execute(fp.read()).getParts()
    for part in parts:
        print part.toLDraw()

