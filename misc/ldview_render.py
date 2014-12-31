#!/usr/bin/env python
#
# Use LDView to convert all the .dat files in a directory into .png files.
# This is probably most useful for animations.
#
# Hazen 12/14
#

import glob
import os
import subprocess
import sys

if (len(sys.argv) != 2):
    print "usage <directory>"
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

for dat_file in glob.glob(sys.argv[1] + "*.dat"):
    print "Processing:", dat_file
    proc_params = ["LDView", 
                   dat_file,
                   "-SaveSnapshot=" + os.path.splitext(dat_file)[0] + ".png"]
    subprocess.call(proc_params + options)
