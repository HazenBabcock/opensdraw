#!/usr/bin/env python
"""
.. module:: types
   :synopsis: LCad types.

.. moduleauthor:: Hazen Babcock

"""

import numpy


class LCadMatrix(numpy.ndarray):
    """
    4x4 numpy array.
    """
    pass


class LCadObject(object):
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)


class LCadVector(numpy.ndarray):
    """
    4 element numpy array.
    """
    pass
