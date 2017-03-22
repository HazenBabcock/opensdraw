#!/usr/bin/env python

import numbers

import opensdraw.lcad_language.interpreter as interp

lcad_functions = {}

class Plus(interp.LCadFunction):

    def __init__(self):
        interp.LCadFunction.__init__(self, "plus")
        self.setSignature([[numbers.Number], [numbers.Number]])

    def call(self, model, v1, v2):
        return v1 + v2


lcad_functions["plus"] = Plus()
