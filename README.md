### opensdraw ###
A programming language (and some related utilities) for creating [LDraw](http://www.ldraw.org) format files.

### Documentation ###
The documentation is [here](http://HazenBabcock.github.io/opensdraw).

### Getting Started ###
You will need to add this directory to your Python path. One way to do this is to copy the openldraw.pth file into your Python dist-packages directory, then edit it to have the correct path.

I use partviewer.py to find LDraw part information, emacs to edit the .lcad files and [LDView](http://ldview.sourceforge.net/) for rendering. I configure LDView to poll for changes to the .dat file so that when I press "F5" in emacs (in lcad minor mode), the updated .dat file is displayed almost immediately.

### Directory Layout ###
* docs - Sphinx documentation.
* emacs - Minor mode for editing .lcad files with emacs.
* opensdraw - The opensdraw package.

### Dependencies ###
* [LDraw](http://www.ldraw.org)
* [numpy](http://www.numpy.org)
* [Python](https://www.python.org/)
* [PyQt4](http://www.riverbankcomputing.com/software/pyqt/intro)
* [rply](https://github.com/alex/rply)
* [scipy](http://www.scipy.org)

### Disclaimer ###
LEGO(R) is a trademark of The LEGO Group of companies which does not sponsor, authorize or endorse this repository.
