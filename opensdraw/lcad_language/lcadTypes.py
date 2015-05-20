#!/usr/bin/env python
"""
.. module:: types
   :synopsis: LCad types.

.. moduleauthor:: Hazen Babcock

"""

import numpy


class LCadBoolean(object):
    """
    boolean type, t/nil
    """
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)
    
class LCadMatrix(numpy.ndarray):
    """
    4x4 numpy array.
    """
    pass

class LCadVector(numpy.ndarray):
    """
    4 element numpy array.
    """
    pass
