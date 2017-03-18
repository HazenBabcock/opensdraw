#!/usr/bin/env python
"""
.. module:: chain
   :synopsis: The chain function.

.. moduleauthor:: Hazen Babcock

"""

import numbers

import opensdraw.lcad_language.belt as belt
import opensdraw.lcad_language.curveFunctions as curveFunctions
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.interpreter as interp
import opensdraw.lcad_language.lcadExceptions as lcadExceptions
import opensdraw.lcad_language.lcadTypes as lcadTypes

lcad_functions = {}


class LCadChain(functions.LCadFunction):
    """
    **chain** - Creates a chain function.
    
    This function creates and returns a function that parametrizes a chain,
    making it easier to add chains, tracks, etc. to a MOC. This is a 
    simplified version of the belt function where everything is confined
    to the XY plane. If you just want a simple chain this is probably the
    function that you want to use. All units are LDU.
    
    A chain must have at least two sprockets. Each sprocket is specified by 
    a 4 member list consisting of *(x y radius winding-direction)*.

    :param x: The x location of the sprocket.
    :param y: The y location of the sprocket.
    :param radius: The radius of the sprocket.
    :param winding-direction: Which way the belt goes around the sprocket (1 = counter-clockwise, -1 = clockwise).

    The chain goes around the sprockets in the order in which they are specified, 
    and when *:continuous* is **t** returns from the last sprocket to the first 
    sprocket to close the loop.

    When you call the created chain function you will get a 4 x 4 transform
    matrix which will translate to the requested position on the chain and
    orient to a coordinate system where the z-axis is pointing along the 
    chain, the y-axis is in the plane of the chain and the x-axis is 
    perpendicular to the plane of the chain.

    If you call the created chain function with the argument **t** it will return the 
    length of the chain.

    Additionally chain has the keyword argument::

      :continuous t/nil  ; The default is t, distances will be interpreted modulo the chain length, and
                         ; the chain will go from that last sprocket back to the first sprocket. If nil
                         ; then negative distances will wrap around the first sprocket and positive
                         ; distances will wrap around the last sprocket.

    Usage::

     (def a-chain (chain (list (list -4 0 1 1)    ; Create a chain with two sprockets, the 1st at (-4,0) and
                               (list 4 0 1 1))))  ; the second at (4,0). Both sprockets have radius 1 and a
                                                  ; counter-clockwise winding direction.
     (def m (a-chain 1))                          ; m is a 4 x 4 transform matrix.
     (a-chain t)                                  ; Returns the length of the chain.

    """
    def __init__(self):
        functions.LCadFunction.__init__(self, "chain")
        self.setSignature([[list], 
                           ["keyword", {"continuous" : [[lcadTypes.LCadBoolean], interp.lcad_t]}]])

    def call(self, model, sprocket_list, continuous = interp.lcad_t):

        # Keywords
        continuous = True if functions.isTrue(continuous) else False

        # Get list of sprockets.
        if (len(sprocket_list) < 2):
            raise NumberSprocketsException(len(sprocket_list))

        # Create sprockets.
        chain = belt.Belt(continuous)
        for sprocket in sprocket_list:
        
            if not isinstance(sprocket, list):
                raise lcadExceptions.WrongTypeException("list", type(sprocket))

            if (len(sprocket) != 4):
                raise SprocketException(len(sprocket))

            for elt in sprocket:
                if not isinstance(elt, numbers.Number):
                    raise lcadExceptions.WrongTypeException("number", type(elt))

            chain.addSprocket(belt.Sprocket([sprocket[0], sprocket[1], 0], [0, 0, 1],
                                            sprocket[2], sprocket[3]))

        chain.finalize()

        # Return chain function.
        return curveFunctions.CurveFunction(chain, "user created chain function.")

lcad_functions["chain"] = LCadChain()

        
class NumberSprocketsException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A chain must have 2 sprockets, got " + str(got))

class SprocketException(lcadExceptions.LCadException):
    def __init__(self, got):
        lcadExceptions.LCadException.__init__(self, "A sprocket must have 4 arguments, got " + str(got))


#
# The MIT License
#
# Copyright (c) 2015 Hazen Babcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
