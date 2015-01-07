User's Guide
============

Dependencies
------------

* `LDraw <http://www.ldraw.org>`_
* `Python <https://www.python.org>`_
* `PyQt4 <http://www.riverbankcomputing.com/software/pyqt/intro>`_ (For the partviewer).
* `rply <https://github.com/alex/rply>`_

Setup
-----

The project root directory needs to be in your Python path. One way to
do this is to edit the *openldraw.pth* file to have the correct path,
then copy this file into your Python dist-packages directory.

Any text editor can be used to create .lcad files, however emacs
integration is provided. The following steps should enable this:

1. Add a sub-folder to your .emacs.d directory called *lcad-mode*.
2. Copy the *lcad-mode.el* file into this directory.
3. Edit the path to *lcad_to_ldraw.py* in the compile function in *lcad-mode.el*.
4. Add the following to your .emacs file. ::

   (add-to-list 'load-path "~/.emacs.d/lcad-mode")
   (require 'lcad-mode)

Once everything is setup up this will provide syntax high-lighting
and pressing **F5** will automatically convert your .lcad file to a .dat
file as well as saving it.

Usage
-----

The basic work flow is:

1. Use the partviewer to determine the LDraw part number and LDraw color of the part you wish to add to your MOC. ::

     python /path/to/openldraw/partviewer/partviewer.py

2. Edit your MOC .lcad file to include this part in the desired location.
3. Convert the MOC .lcad file to a .dat file using *lcad_to_ldraw.py*. ::

     python /path/to/openldraw/lcad_to_ldraw.py file.lcad file.dat

4. Visualize the .dat file with LDView (or equivalent).

Example .lcad files are provided in the examples directory.

.. note::

   LDView can be configured to automatically poll for changes to .dat files.
