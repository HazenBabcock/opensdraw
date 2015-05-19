#!/usr/bin/env python
"""
.. module:: typeFunctions
   :synopsis: Functions for determining the type of an object.

.. moduleauthor:: Hazen Babcock
"""

import numbers

import functions
import interpreter as interp
import lcadTypes

lcad_functions = {}

def isBoolean(obj):
    return isinstance(obj, lcadTypes.LCadObject)

def isMatrix(obj):
    return isinstance(obj, lcadTypes.LCadMatrix)

def isNumber(obj):
    return isinstance(obj, numbers.Number)

def isString(obj):
    return isinstance(obj, basestring)

def isVector(obj):
    return isinstance(obj, lcadTypes.LCadVector)


class TypeFunction(functions.LCadFunction):
    def __init__(self, name):
        functions.LCadFunction.__init__(self, name)
        self.setSignature([[object]])

        
class IsBoolean(TypeFunction):
    """
    **boolean?** - Returns t/nil if argument is a boolean.

    Usage::
     
     (boolean? nil) ; t
     (boolean? 1)   ; nil
    """
    def call(self, model, obj):
        if isBoolean(obj):
            return interp.lcad_t
        else:
            return interp.lcad_nil

lcad_functions["boolean?"] = IsBoolean("boolean?")


class IsMatrix(TypeFunction):
    """
    **matrix?** - Returns t/nil if argument is a matrix.

    Usage::
     
     (matrix? (matrix 0 0 0 0 0 0)) ; t
     (matrix? (vector 0 0 0))       ; nil
    """
    def call(self, model, obj):
        if isMatrix(obj):
            return interp.lcad_t
        else:
            return interp.lcad_nil

lcad_functions["matrix?"] = IsMatrix("matrix?")


class IsNumber(TypeFunction):
    """
    **number?** - Returns t/nil if argument is a number.

    Usage::
     
     (number? 1)   ; t
     (number? "a") ; nil
    """
    def call(self, model, obj):
        if isNumber(obj):
            return interp.lcad_t
        else:
            return interp.lcad_nil

lcad_functions["number?"] = IsNumber("number?")


class IsString(TypeFunction):
    """
    **string?** - Returns t/nil if argument is a string.

    Usage::
     
     (string? 1)   ; nil
     (string? "a") ; t
    """
    def call(self, model, obj):
        if isString(obj):
            return interp.lcad_t
        else:
            return interp.lcad_nil

lcad_functions["string?"] = IsString("string?")


class IsVector(TypeFunction):
    """
    **vector?** - Returns t/nil if argument is a vector.

    Usage::

     (vector? (matrix 0 0 0 0 0 0)) ; nil
     (vector? (vector 0 0 0))       ; t     
    """
    def call(self, model, obj):
        if isVector(obj):
            return interp.lcad_t
        else:
            return interp.lcad_nil

lcad_functions["vector?"] = IsVector("vector?")
