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

Basic Functions
---------------

.. automodule:: lcad_language.functions
   :members: LCadAref, LCadBlock, LCadCond, LCadDef, LCadFor, LCadIf, LCadImport, LCadList, LCadMirror, LCadPart, LCadPrint, LCadRotate, LCadSet, LCadTranslate, LCadWhile

Comparison Operators
--------------------

.. automodule:: lcad_language.functions
   :members: LCadEqual, LCadNe, LCadGt, LCadGe, LCadLt, LCadLe

Logical Operators
-----------------

.. automodule:: lcad_language.functions
   :members: LCadAnd, LCadOr, LCadNot

Math Functions
--------------

.. automodule:: lcad_language.functions
   :members: LCadPlus, LCadMinus, LCadMultiply, LCadDivide, LCadModulo

Python Math Functions
---------------------

All the functions in the python math library are also available:

Usage::

  (cos x)
  (sin x)
  ...

Random Number Functions
-----------------------

.. automodule:: lcad_language.functions
   :members: LCadRandSeed, LCadRandChoice, LCadRandGauss, LCadRandInteger, LCadRandUniform
