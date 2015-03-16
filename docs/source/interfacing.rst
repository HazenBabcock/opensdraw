Interfacing with Python
=======================

Writing your own Python modules that you can use with OpenSDraw.

Step 1
------

Create the Python file.

.. literalinclude:: ./../../opensdraw/examples/picture.py

.. note::
   
   This is the *picture.py* file in the examples folder.
   
Step 2
------

Create the lcad file.

.. literalinclude:: ./../../opensdraw/examples/picture.lcad

.. note::

   This is the *picture.lcad* file in the examples folder.

Step 3
------
Convert the .lcad file to a .mpd file using *lcad_to_ldraw.py*. ::
  
  cd opensdraw/opensdraw/examples
  python ../scripts/lcad_to_ldraw.py picture.lcad

.. note::
   
   Large pictures can easily overwhelm both OpenSDraw and LDView. Picture size less than 100 x 100 or so are probably the best.

Also
----

If you want your module to always be available you can add it to the *lcad_language/modules.xml* file.
