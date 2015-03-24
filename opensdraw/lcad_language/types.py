#!/usr/bin/env python
"""
.. module:: types
   :synopsis: LCad types.

.. moduleauthor:: Hazen Babcock

"""

import math
import numpy

class LCadObject(object):
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)

