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
::

   (pyimport knots)

.. automodule:: opensdraw.library.knots
   :members: SheetBendKnot

Shapes
~~~~~~
::

   (pyimport shapes)

.. automodule:: opensdraw.library.shapes
   :members: Axle, Ring, Rod, Tube

Extra Functions (LCad)
----------------------

These are functions that you will need to import in order to use. They can all be found in the *opensdraw/library* directory.

* flexible-axle.lcad - Rendering flexible axle.
* flexible-hose.lcad - Rendering flexible hoses.
* flexible-rod.lcad - Rendering flexible rods.
* ldu.lcad - Converting from bricks to LDU.
* locate.lcad - Functions to make placing parts easier.
* ribbed-hose.lcad - Rendering ribbed hoses.
* triangles.lcad - Functions for calculating sides and angles of triangles.

TODO: Figure out how to import reST from non-Python code.
