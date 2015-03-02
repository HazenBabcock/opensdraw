#!/usr/bin/env python
#
## @file
#
# Parses all the parts in a LDraw parts directory and generates the
# XML file that is used by the partviewer.
#
# Hazen 07/14
#

import glob
import os
import sys

from xml.dom import minidom
from xml.etree import ElementTree

import lcad_lib.ldrawPath

if (len(sys.argv) != 2):
    print "usage: <path/to/parts/directory>"
    exit()

# Generate XML.
file_xml = ElementTree.Element("ldraw-parts")

# Save part information.
categories = {}
parts_xml = ElementTree.SubElement(file_xml, "parts")
part_files = glob.glob(sys.argv[1] + "*.dat")
for part_file in part_files:
    print "parsing", part_file

    part_xml = ElementTree.SubElement(parts_xml, "part")
    with open(part_file) as part_filep:

        # The first line contains the category and description.
        line_data = part_filep.readline().split(" ")
        original_category = line_data[1].strip()
        description = unicode(" ".join(line_data[2:]), encoding = "utf-8").strip()


        # Remove category modifier, if any.
        category = original_category
        if not original_category[0].isalpha():
            category = original_category[1:]

        # Update categories.
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1

        # Save info in the XML node.
        part_xml.set("description", description)
        part_xml.set("original-category", original_category)
        part_xml.set("category", category)
        part_xml.set("file", os.path.basename(part_file))
        #part_xml.set("fullpath", part_file)

# Save category information.
cats_xml = ElementTree.SubElement(file_xml, "categories")
for key in sorted(categories.keys()):
    cat_xml = ElementTree.SubElement(cats_xml, "category")
    cat_xml.set("name", key)
    cat_xml.set("counts", str(categories[key]))

# Save results in a pretty-printed XML file.
print ""
print "saving.."
rough_string = ElementTree.tostring(file_xml, 'utf-8')
reparsed = minidom.parseString(rough_string)

with open("parts.xml", "w") as out_fp:
    out_fp.write(reparsed.toprettyxml(indent=" ", encoding = "utf-8"))

print "Found", len(part_files), "parts"
print "  ", len(categories.keys()), "categories"

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
