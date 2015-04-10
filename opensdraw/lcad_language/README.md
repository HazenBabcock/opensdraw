### Summary ###
This folder contains the modules that define the lcad language. This is a [prefix](http://en.wikipedia.org/wiki/Polish_notation) notation language similar to [Scheme](http://en.wikipedia.org/wiki/Scheme_%28programming_language%29).

### Files ###
* belt.py - A function for creating belts.
* chain.py - A function for creating chains, tracks, ..
* comparisonFunctions.py - >, <, = , ..
* coreFunctions.py - The basic functions in OpenLDraw.
* curve.py - A function for creating curves (cubic splines).
* curveFunctions.py - The LCadFunction returned by belt, curve, chain, spring, ..
* functions.py - The LCadFunction and UserFunction classes.
* geometry.py - Geometry utility functions.
* geometryFunctions.py - Rotate, Translate, ..
* interpreter.py - The lcad language interpreter.
* lcadExceptions.py - Lcad language specific exceptions.
* lcadTypes.py - Lcad language types.
* lexerParser.py - The lexer/parser for the lcad language.
* logicFunctions.py - And, Or, Not.
* mathFunctions.py - /, *, +, -, ..
* modules.xml - The standard modules that opensdraw will load.
* partFunctions.py - LDraw parts and primitives (line, triangle, ..).
* pulleySystem - A function for creating pulley and string systems.
* parts.py - The Part object.
* randomNumberFunctions.py - Random number generating functions.
* spring.py - A function for creating springs.

### Directories ###
* test - Nose tests.
