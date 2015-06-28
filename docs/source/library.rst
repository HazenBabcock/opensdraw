Libraries
=========

Core Functions
--------------

.. automodule:: opensdraw.lcad_language.belt
   :members: LCadBelt

.. automodule:: opensdraw.lcad_language.chain
   :members: LCadChain

.. automodule:: opensdraw.lcad_language.curve
   :members: LCadCurve

.. automodule:: opensdraw.lcad_language.pulleySystem
   :members: LCadPulleySystem

.. automodule:: opensdraw.lcad_language.spring
   :members: LCadSpring

Extra Functions (Python)
------------------------

These are functions that you will need to import in order to use. They can all be found in the *opensdraw/library* directory.

Knots
~~~~~
This module makes it easier to add a knot to your MOC.

::

   (pyimport opensdraw.library.knots)

.. automodule:: opensdraw.library.knots
   :members: SheetBendKnot

Overlay
~~~~~~~
This module make LDraw compatible images that can be overlaid on a MOC for scaling pictures. It can also be used for creating 2D (i.e. flat) stickers.

::

   (pyimport opensdraw.library.overlay)

.. automodule:: opensdraw.library.overlay
   :members: Overlay

Parts Strings
~~~~~~~~~~~~~
This module lets you add parts using space delimited strings, instead of using functions like *tb()* and *sb()* from *locate.lcad*

::

   (pyimport opensdraw.library.partsString)

.. automodule:: opensdraw.library.partsString
   :members: PartsFile, PartsString	     
   
Shapes
~~~~~~
This module makes it easier (and faster) to create simple shapes from LDraw primitives.

::

   (pyimport opensdraw.library.shapes)

.. automodule:: opensdraw.library.shapes
   :members: Axle, FlatCable, RibbonCable, Ring, Rod, Tube

Extra Functions (LCad)
----------------------

These are functions that you will need to import in order to use. They can all be found in the *opensdraw/library* directory.

* cables.lcad - Rendering cables.
* flexible-axle.lcad - Rendering flexible axle.
* flexible-hose.lcad - Rendering flexible hoses.
* flexible-rod.lcad - Rendering flexible rods.
* ldu.lcad - Converting from bricks to LDU.
* locate.lcad - Functions to make placing parts easier.
* ribbed-hose.lcad - Rendering ribbed hoses.
* triangles.lcad - Functions for calculating sides and angles of triangles.

TODO: Figure out how to import reST from non-Python code.
