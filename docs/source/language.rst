Language
========

Symbols
-------
* **t** - True
* **nil** - False
* **pi** - 3.14159
* **e** - 2.7182
* **step-offset** - User settable to a number, or a function with no arguments that returns a number. This number is added to the *part_step* parameter of the **part()** function. The default value is 0.
* **time-index** - 0..N, for creating animations.

Functions
---------

.. automodule:: opensdraw.lcad_language.coreFunctions
   :members: Append, Aref, Block, Concatenate, Cond, Copy, Def, For, If, Import, Lambda, Len, List, Print, PyImport, Set, While

Part Functions
--------------

.. automodule:: opensdraw.lcad_language.partFunctions
   :members: Comment, Group, Header, Line, OptionalLine, Part, Quadrilateral, Triangle

Comparison Operators
--------------------

.. automodule:: opensdraw.lcad_language.comparisonFunctions
   :members: Equal, Ne, Gt, Ge, Lt, Le

Geometry Functions
------------------

.. automodule:: opensdraw.lcad_language.geometryFunctions
   :members: CrossProduct, DotProduct, Matrix, Mirror, Rotate, Scale, Transform, Translate, Vector

Logical Operators
-----------------

.. automodule:: opensdraw.lcad_language.logicFunctions
   :members: And, Or, Not

Math Functions
--------------

.. automodule:: opensdraw.lcad_language.mathFunctions
   :members: Absolute, Plus, Minus, Multiply, Divide, Modulo

All the functions in the python math library are also available:

Usage::

  (cos x)
  (sin x)
  (degrees (atan2 2 3))
  ...

Random Number Functions
-----------------------

.. automodule:: opensdraw.lcad_language.randomNumberFunctions
   :members: RandSeed, RandChoice, RandGauss, RandInteger, RandUniform
