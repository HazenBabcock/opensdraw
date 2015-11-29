#!/usr/bin/python
#
# Run multiple LDViews in parallel to make pictures faster. On my computer I can
# get about a 2x speed-up with this.
#
# Hazen 11/15
#

import os
import Queue
import signal
import subprocess
import sys
import thread


def batchLDView(file_pairs, width = 400, height = 400, default_zoom = 0.95, max_processes = 6):
    """
    file_pairs is an array of [[input_file1, output_file1], [input_file2, output_file2], ..]
    """

    # Setup process queue.
    process_count = 0
    results = Queue.Queue()

    # Start processes.
    n_files = len(file_pairs)
    procs = []
    for i, file_pair in enumerate(file_pairs):

        try:
            # Wait for a process to stop before starting
            # the next one if we are at the limit.
            if(process_count >= max_processes):
                description, rc = results.get()
                print description
                process_count -= 1
            proc = subprocess.Popen(['LDView',
                                     file_pair[0],
                                     "-SaveSnapshot=" + file_pair[1],
                                     "-SaveActualSize=0",
                                     "-SaveWidth=" + str(width),
                                     "-SaveHeight=" + str(height),
                                     "-DefaultZoom=" + str(default_zoom)])
            procs.append(proc)
            thread.start_new_thread(process_waiter,
                                    (proc,
                                     "Rendered (" + str(i) + " / " + str(n_files) + ") " + file_pair[0],
                                     results))
            process_count += 1

        except KeyboardInterrupt:
            for proc in procs:
                if(not proc.poll()):
                    proc.send_signal(signal.CTRL_C_EVENT)

    # Wait until all the processes finish.
    try:
        while(process_count>0):
            description, rc = results.get()
            print description
            process_count -= 1

    except KeyboardInterrupt:
        for proc in procs:
            if(not proc.poll()):
                proc.send_signal(signal.CTRL_C_EVENT)

def process_waiter(popen, description, que):
    try:
        popen.wait()
    finally: 
        que.put((description, popen.returncode))


#
# If you run this in standalone mode it will generate pictures
# of all your parts in the current directory.
#
if (__name__ == '__main__'):
    
    import opensdraw.lcad_lib.ldrawPath as ldrawPath

    # Create list of parts.
    print "Creating part list."
    ldraw_path = ldrawPath.getLDrawPath()
    all_parts = []
    with open(ldraw_path + "parts.lst") as part_list:
        for part in part_list:

            text = ' '.join(part.split())
            file_name = text.split()[0]
            picture_name = file_name[:-4] + "_71.png"
            file_name = ldraw_path + "parts" + os.path.sep + file_name
            all_parts.append([file_name, picture_name])
            
            #if (len(all_parts) > 100):
            #    break

    # Render.
    print "Rendering."
    batchLDView(all_parts)
            
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
