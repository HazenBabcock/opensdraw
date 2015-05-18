#!/usr/bin/env python

import numbers

import opensdraw.lcad_language.functions as functions

lcad_functions = {}

class Plus(functions.LCadFunction):

    def __init__(self):
        functions.LCadFunction.__init__(self, "plus")
        self.setSignature([[numbers.Number], [numbers.Number]])

    def call(self, model, v1, v2):
        return v1 + v2


lcad_functions["plus"] = Plus()
