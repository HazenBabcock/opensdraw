#!/usr/bin/env python
#
# Using Python functions in OpenSDraw example. This requires PIL
# (or Pillow) to work.
#
# Hazen 03/15
#

import numbers
import os
from PIL import Image

# These OpenSDraw modules have some classes that we will use.
import opensdraw.lcad_language.functions as functions
import opensdraw.lcad_language.interpreter as interpreter

# This OpenSDraw module defines some exceptions that we will use.
import opensdraw.lcad_language.lcadExceptions as lcadExceptions

# OpenSDraw will look for this dictionary to figure out what functions to import.
lcad_functions = {}

#
# Your function(s) (like all functions in OpenSDraw) should be a sub-class of 
# the functions.LCadFunction class.
#
# This class will open a user requested picture and return another class that
# the user can use to access various properties of the picture.
#
class OpenPicture(functions.LCadFunction):

    def __init__(self):

        # functions.LCadFunction.__init__ takes one argument, the name of the function.
        functions.LCadFunction.__init__(self, "picture")

        # Set the function signature so that OpenSDraw will type check for a single 
        # argument of type string (the name of the picture file). Use basestring since
        # this will also work with unicode strings.
        self.setSignature([[basestring]])

    # 
    # model is an instance of interpreter.Model. This stores the parts, groups,
    #    primitives and etc.
    # tree is the current node, i.e. the node where this function was called,
    #    of the parse tree returned by lexerParser.
    #
    # Typically you don't do anything directly with these arguments, but you
    # can if you want to. Examples of functions that use and/or manipulate
    # the parse tree can be found in coreFunctions, such as def(), if(), for().
    #
    def call(self, model, tree):

        # Call this method to get the arguments that were passed to the function
        # as a Python list.
        args = self.getArgs(model, tree)

        # Check that the requested picture exists.
        if os.path.exists(args[0]):
            
            # Return an instance of the Picture class.
            return Picture(Image.open(args[0]))
    
        # If not, throw an exception.
        else:
            raise lcadExceptions.LCadException("picture " + args[0] + " not found.")

# Make sure to add an instance of your function to the functions dictionary.
lcad_functions["open-picture"] = OpenPicture()


#
# This class will return either the picture size, or the color at a particular
# pixel depending on the arguments that the user supplies
#
class Picture(functions.LCadFunction):

    def __init__(self, im):
        functions.LCadFunction.__init__(self, "user created picture function")

        # Store the PIL Image object.
        self.im = im

        # Set signature to be exactly two arguments both of which are numbers
        # or the symbols t/nil.
        self.setSignature([[numbers.Number, interpreter.LObject], [numbers.Number, interpreter.LObject]])

    def call(self, model, tree):
        
        args = self.getArgs(model, tree)

        # If we got t/nil return the size of the picture.
        if isinstance(args[0], interpreter.LObject) or isinstance(args[1], interpreter.LObject):
            return list(self.im.size)

        # Otherwise return the color of the pixel as a LDraw "direct" color. Best
        # practice might be to do some range checking. This will also fail for
        # certain types of images (such as .gif).
        [r, g, b] = self.im.getpixel((args[0], args[1]))

        # Convert colors (0-255) to upper case hex & concatenate.
        return "0x2" + "".join(map(lambda(x): "{0:#0{1}x}".format(x,4).upper()[2:], [r, g, b]))

