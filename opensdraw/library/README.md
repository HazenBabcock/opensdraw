
### Summary ###
This is the directory in which to place "generic" .lcad modules. When the lcad language is looking for a module it will first search the current working directory, then it will search this directory.

This directory also includes Python modules that are not loaded automatically by the lcad interpreter, but can be loaded with the pyimport() function.

### Files ###

* flexible-axle.lcad - A function for creating flexible axles.
* flexible-hose.lcad - A function for creating flexible hoses.
* flexible-rod.lcad - A function for creating flexible rods.
* knots.py - Function for creating a knot.
* ldu.lcad - Functions for converting from ldu (LDraw Units) to standard brick sizes.
* locate.lcad - Functions for placing bricks.
* ribbed-hose.lcad - A function for creating ribbed hoses.
* shapes.py - Functions for creating shapes (faster LDraw primitives).
* string.lcad - A function for creating strings.
* triangles.lcad - Functions for determining side lengths and angles of triangles.
