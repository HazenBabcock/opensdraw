User's Guide
============

Dependencies
------------

* `LDraw <http://www.ldraw.org>`_
* `numpy <http://www.numpy.org>`_
* `Python 2.7 <https://www.python.org>`_
* `PyQt4 <http://www.riverbankcomputing.com/software/pyqt/intro>`_ (For the partviewer).
* `rply <https://github.com/alex/rply>`_
* `scipy <http://www.scipy.org>`_

Setup
-----

Python path
~~~~~~~~~~~
The project root directory needs to be in your Python path. One way to
do this is to edit the *opensdraw.pth* file to have the correct path,
then copy this file into your Python dist-packages directory. An example file: ::

   /home/username/Downloads/opensdraw/

LDraw path
~~~~~~~~~~
Edit the path in *opensdraw/xml/ldraw_path.xml* to point to your LDraw directory
(not the parts sub-directory). An example file: ::

   <?xml version="1.0" encoding="utf-8"?>
   <ldraw-path>
    <path path="/home/username/Downloads/ldraw/"/>
   </ldraw-path>

Emacs
~~~~~
Any text editor can be used to create .lcad files, however emacs
integration is provided. The following steps should enable this:

1. Add a sub-folder to your .emacs.d directory called *lcad-mode*.
2. Copy the *lcad-mode.el* file into this directory.
3. Edit the path to *lcad_to_ldraw.py* in the **compile()** function in *lcad-mode.el*.
4. Add the following to your .emacs file. ::

   (add-to-list 'load-path "~/.emacs.d/lcad-mode")
   (require 'lcad-mode)
   (add-hook 'lcad-mode-hook 'lcad-disable-slime) ; You only need this if you also use the SLIME mode.

Once everything is setup up this will provide syntax high-lighting
and pressing **F5** will automatically convert your .lcad file to a .mpd
file as well as saving it.

Usage
-----

The basic work flow is:

1. Use the partviewer to determine the LDraw part number and LDraw color of the part you wish to add to your MOC. ::

     cd /path/to/opensdraw/opensdraw/partviewer
     python partviewer.py

   .. note::

      The first time this is run it will take a while (15 - 30 minutes) to generate the thumbnails of all the parts.

   .. note::

      This program will create a file called "ldview_part.mpd" that you can view with LDView (or equivalent). This file is updated with the current selected part and color.

   .. note::

      This program can query `Rebrickable <https://www.rebrickable.com/>`_ to provide more detailed part information such as what years it was available and in what colors. You will need an account at Rebrickable and an `API <https://rebrickable.com/api/>`_ key for this to work.

2. Edit your MOC .lcad file to include this part in the desired location.
3. Convert the MOC .lcad file to a .mpd file using *lcad_to_ldraw.py*. ::

     python /path/to/opensdraw/scripts/lcad_to_ldraw.py file.lcad file.mpd

4. Visualize the .mpd file with LDView (or equivalent).

Example .lcad files are provided in the examples directory.

.. note::

   LDView can be configured to automatically poll for changes to .mpd files.

Understanding Error Messages
----------------------------

Occasionally things will go wrong and you will get a possibly long and confusing back-trace like this: ::

   !Error in function 'chain1' at line 75 in file 'chain.lcad'

   Traceback (most recent call last):
     File "../scripts/lcad_to_ldraw.py", line 46, in <module>
       model = interpreter.execute(ldraw_file_contents, filename = sys.argv[1], time_index = index)
     File "/home/hbabcock/Code/opensdraw/opensdraw/lcad_language/interpreter.py", line 335, in execute
       interpret(model, ast)
     File "/home/hbabcock/Code/opensdraw/opensdraw/lcad_language/interpreter.py", line 422, in interpret
       ret = interpret(model, node)
     File "/home/hbabcock/Code/opensdraw/opensdraw/lcad_language/interpreter.py", line 407, in interpret
       val = dispatch(func, model, tree)
     File "/home/hbabcock/Code/opensdraw/opensdraw/lcad_language/interpreter.py", line 311, in dispatch
       func.argCheck(tree)
     File "/home/hbabcock/Code/opensdraw/opensdraw/lcad_language/functions.py", line 115, in argCheck
       raise lce.NumberArgumentsException(self.min_args, len(args))
   opensdraw.lcad_language.lcadExceptions.NumberArgumentsException: !Error, wrong number of standard arguments, got 0 expected 1

This trace consists of 3 parts:

1. One or more lines telling you what line in the .lcad file caused the problem.
2. A Python traceback.
3. A final line containing the exception that was triggered and some additional information.

At some point in the future the Python traceback may disappear, but at present I don't yet have enough confidence that the .lcad traceback alone is always sufficient to figure out what went wrong.
