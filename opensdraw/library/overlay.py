#!/usr/bin/env python
#
# Makes a LDraw compatible semi-transparent image that can be overlaid
# on a MOC for scaling purposes. This requires PIL (or Pillow) to work.
#
# Hazen 05/15
#

import numbers
import numpy
import os
from PIL import Image

import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.lcadExceptions as lcadExceptions
import opensdraw.lcad_language.partFunctions as partFunctions

lcad_functions = {}

class Overlay(functions.LCadFunction):
    """
    **overlay** - Create a semi-transparent LDraw compatible image from a normal image.

    This function is useful for overlaying images for scaling purposes. It could also
    be used to create 2D stickers. The image will be in the XY plane with the upper 
    left corner of the image at 0,0.

    :param image: The name of the image file.
    :param scale: The conversion factor (LDU / pixel).
    :param transparency: Optional (0-255), default is 64.

    Usage::

     (overlay "blueprint.png" 2.0)
    """

    def __init__(self):
        functions.LCadFunction.__init__(self, "overlay")
        self.color_index = 1000
        self.header_fn = partFunctions.lcad_functions["header"]
        self.quad_fn = partFunctions.lcad_functions["quadrilateral"]
        self.setSignature([[basestring],
                           [numbers.Number],
                           ["optional", [numbers.Number]]])

    def call(self, model, filename, scale, *transparency):

        if (len(transparency) == 0):
            alpha = " ALPHA " + str(64)
        else:
            alpha = " ALPHA " + str(transparency[0])
            
        # Check that the requested picture exists.
        if os.path.exists(filename):

            #
            # There is some fiddling here because direct colors don't support alpha values,
            # so we have to create our own special colors with alpha values.
            #
            colors = {}
            
            pic = Image.open(filename)
            [width, height] = pic.size
            
            # Process the picture, white pixels are ignored.
            for i in range(width):
                for j in range(height):
                    [r, g, b] = pic.getpixel((i, j))
                    color = "#" + "".join(map(lambda(x): "{0:#0{1}x}".format(x,4).upper()[2:], [r, g, b]))
                    if (color == "#FFFFFF"):
                        continue

                    if not (color in colors):
                        self.color_index += 1
                        colors[color] = self.color_index
                        
                    self.quad_fn.call(model,
                                      [i * scale, j * scale, 0],
                                      [i * scale, (j + 1) * scale, 0],
                                      [(i + 1) * scale, (j + 1) * scale, 0],
                                      [(i + 1) * scale, j * scale, 0],
                                      colors[color])

            # Create the colors.
            for color in colors:
                color_index = str(colors[color])
                self.header_fn.call(model, "!COLOUR c" + color_index + " CODE " + color_index + " VALUE " + color + " EDGE " + color + alpha)

        # If not, throw an exception.
        else:
            raise lcadExceptions.LCadException("picture " + filename + " not found.")

lcad_functions["overlay"] = Overlay()
