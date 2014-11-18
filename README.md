### Openlcad ###
A programming language (and some related utilities) for creating [LDraw](http://www.ldraw.org) format files.

### Directory Layout ###
* emacs - Minor mode for editing .lcad files with emacs.
* examples - Sample .lcad format files.
* lcad_language - The lcad language.
* lcad_lib - Supporting modules for partviewer.
* library - Modules that are part of the lcad language.
* misc - Some utility scripts.
* partviewer - A simple utility for finding ldraw part numbers and colors.

### Files ###
* colors.xml - XML file describing the LDraw colors (created using misc/make_colors_xml.py).
* lcad_to_ldraw.py - Uses the lcad language interpreter to convert a .lcad file to a ldraw .dat file.
* parts.xml - XML file describing the available parts (created using misc/make_parts_xml.py).

### Disclaimer ###
LEGO(R) is a trademark of The LEGO Group of companies which does not sponsor, authorize or endorse this repository.
