### Summary ###
This folder contains the modules that define the lcad language. This is a [prefix](http://en.wikipedia.org/wiki/Polish_notation) notation language similar to [Scheme](http://en.wikipedia.org/wiki/Scheme_%28programming_language%29).

### Files ###
* angles.py - Geometry utility functions.
* chain.py - A function for creating chains, tracks, ..
* comparisonFunctions.py - >, <, = , ..
* coreFunctions.py - The basic functions in OpenLDraw.
* curve.py - A function for creating curves (cubic splines).
* curveFunctions.py - The function returned by curve, chain.
* functions.py - The LCadFunction and UserFunction classes.
* geometryFunctions.py - Rotate, Translate, ..
* interpreter.py - The lcad language interpreter.
* lcadExceptions.py - Lcad language specific exceptions.
* lcadTypes.py - Lcad language types.
* lexerParser.py - The lexer/parser for the lcad language.
* logicFunctions.py - And, Or, Not.
* mathFunctions.py - /, *, +, -, ..
* modules.xml - The standard modules that opensdraw will load.
* partFunctions.py - LDraw parts and primitives (line, triangle, ..).
* parts.py - The Part object.
* randomNumberFunctions.py - Random number generating functions.

### Directories ###
* test - Nose tests.
