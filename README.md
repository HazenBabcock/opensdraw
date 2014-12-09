### openldraw ###
A programming language (and some related utilities) for creating [LDraw](http://www.ldraw.org) format files.

### Getting Started ###
You will need to add this directory to your Python path. One way to do this is to copy the openldraw.pth file into your Python dist-packages directory, then edit it to have the correct path.

I use partviewer.py to find ldraw part information, emacs to edit the .lcad files and [LDView](http://ldview.sourceforge.net/) for rendering. I configure LDView to poll for changes to the .dat file so that when I press "F5" in emacs (in lcad minor mode), the updated .dat file is displayed almost immediately.

### Directory Layout ###
* emacs - Minor mode for editing .lcad files with emacs.
* examples - Sample .lcad format files.
* lcad_language - The lcad language interpreter.
* lcad_lib - Supporting modules for partviewer.
* library - Modules that are part of the lcad language.
* misc - Some utility scripts.
* partviewer - A simple utility for finding ldraw part numbers and colors.

### Files ###
* lcad_to_ldraw.py - Uses the lcad language interpreter to convert a .lcad file to a ldraw .dat file.
* openldraw.pth - A sample .pth file.
* colors.xml - XML file describing the LDraw colors (created using misc/make_colors_xml.py).
* parts.xml - XML file describing the available parts (created using misc/make_parts_xml.py).

### Dependencies ###
* [Python](https://www.python.org/)
* [PyQt4](http://www.riverbankcomputing.com/software/pyqt/intro)
* [rply](https://github.com/alex/rply)

### Disclaimer ###
LEGO(R) is a trademark of The LEGO Group of companies which does not sponsor, authorize or endorse this repository.
