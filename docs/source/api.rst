API
===

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

.. automodule:: lcad_language.coreFunctions
   :members: Aref, Block, Cond, Def, For, Header, If, Import, Lambda, Len, List, Part, Print, Set, While

Comparison Operators
--------------------

.. automodule:: lcad_language.comparisonFunctions
   :members: Equal, Ne, Gt, Ge, Lt, Le

Geometry Functions
------------------

.. automodule:: lcad_language.geometryFunctions
   :members: Mirror, Rotate, Scale, Translate

Logical Operators
-----------------

.. automodule:: lcad_language.logicFunctions
   :members: And, Or, Not

Math Functions
--------------

.. automodule:: lcad_language.mathFunctions
   :members: Plus, Minus, Multiply, Divide, Modulo

All the functions in the python math library are also available:

Usage::

  (cos x)
  (sin x)
  ...


Miscellaneous Functions
-----------------------

.. automodule:: lcad_language.chain
   :members: LCadChain

.. automodule:: lcad_language.curve
   :members: LCadCurve

Random Number Functions
-----------------------

.. automodule:: lcad_language.randomNumberFunctions
   :members: RandSeed, RandChoice, RandGauss, RandInteger, RandUniform
