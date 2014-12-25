API
===

Symbols
-------
* **t** - True.
* **nil** - False.
* **pi** - 3.14159
* **e** - 2.7182

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

