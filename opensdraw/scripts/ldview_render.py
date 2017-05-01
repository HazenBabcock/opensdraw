#!/usr/bin/env python
"""
Use LDView to convert all the .dat files in a directory into .png files.
This is probably most useful for animations.

Hazen 12/14
"""

import glob
import os
import subprocess
import sys

if (len(sys.argv) != 2):
    print("usage <directory>")
    exit()

# Adjust accordingly based on your desired results.
options = ["-DefaultMatrix=-0.861209,0.362189,0.356561,0.455131,0.861824,0.223857,-0.226214,0.35507,-0.907054",
           "-DefaultZoom=0.683013",
           "-SaveActualSize=0",
           "-SaveImageType=2",
           "-SaveZoomToFit=1",
           "-SaveWidth=640",
           "-SaveHeight=480",
           "-FOV=10"]

# This is a better angle for the crane animation.
if 0:
    options[0] = "-DefaultMatrix=-0.921756,0.386996,-0.0251828,-0.0175983,-0.106619,-0.994136,-0.387407,-0.915901,0.105077"
    options[1] = "-DefaultZoom=0.985235"

# This is a better angle for the suspension animation.
if 0:
    options[0] = "-DefaultMatrix=0.681231,-0.731242,-0.034584,-0.146912,-0.090277,-0.984997,0.71715,0.676115,-0.168931"
    options[1] = "-DefaultZoom=1"

# This is a better angle for the power functions cable animation.
if 1:
    options[0] = "-DefaultMatrix=-0.209952,0.0763675,-0.974724,-0.0662947,0.993537,0.092118,0.975462,0.0839602,-0.203532"
    options[1] = "-DefaultZoom=1"

for dat_file in sorted(glob.glob(sys.argv[1] + "*.mpd")):
    print("Processing:", dat_file)
    proc_params = ["LDView", 
                   dat_file,
                   "-SaveSnapshot=" + os.path.splitext(dat_file)[0] + ".png"]
    subprocess.call(proc_params + options)
