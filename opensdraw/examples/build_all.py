#!/usr/bin/env python
"""
.. module:: build_all
   :synopsis: Builds all the examples.

.. moduleauthor:: Hazen Babcock
"""

import os
import subprocess


examples = ["auto-step.lcad",
            "chain.lcad",
            "curve.lcad",
            "dumper-truck.lcad",
            "gears.lcad",
            "gripper.lcad",
            "rib-hose.lcad",
            "steps.lcad",
            "trefoil.lcad",
            "wall.lcad"]

builder = "../scripts/lcad_to_ldraw.py"

for example in examples:
    proc_params = ["python",
                   builder,
                   example]
    print "Building:", example
    subprocess.call(proc_params)
    print ""

