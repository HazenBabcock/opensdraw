#!/usr/bin/env python
"""
.. module:: functions
   :synopsis: The functions that are available in lcad.

.. moduleauthor:: Hazen Babcock


"""

from functools import wraps
from itertools import izip
import math
import numpy
import operator

import interpreter as interp
import lcadExceptions as lce
import lexerParser
import parts

builtin_functions = {}


def isTrue(model, tree, arg):
    temp = interp.interpret(model, arg)
    if (temp is interp.lcad_t):
        return True
    elif (temp is interp.lcad_nil):
        return False
    else:
        raise lce.BooleanException(tree)


#
# Function class.
#

class LCadFunction(object):
    def __init__(self, name):
        self.name = name

    def argCheck(self, tree):
        pass

    def call(self, model, tree):
        pass


#
# User functions class.
#

class UserFunction(LCadFunction):
    """
    'Normal' user defined functions.
    """
    def __init__(self, lenv, tree):
        flist = tree.value[1:]
        self.name = flist[0].value
        self.arg_list = flist[1].value
        self.body = flist[2]
        self.body.lenv = lenv

        for arg in self.arg_list:
            if not isinstance(arg, lexerParser.LCadSymbol):
                raise lce.IllegalArgumentTypeException(tree)
            if arg.value in self.body.lenv.symbols:
                print "Warning function argument", arg.value, "overrides existing variable with the same name."
            self.body.lenv.symbols[arg.value] = interp.Symbol(arg.value)

        interp.createLexicalEnv(lenv, flist[2])

    def argCheck(self, tree):
        if ((len(tree.value)-1) != len(self.arg_list)):
            raise lce.NumberArgumentsException(tree, len(self.arg_list), (len(tree.value)-1))

    def call(self, model, tree):
        args = tree.value[1:]

        for i in range(len(args)):
            self.body.lenv.symbols[self.arg_list[i].value].setv(interp.interpret(model, args[i]))
        return interp.interpret(model, self.body)


#
# Special functions classes.
#

class SpecialFunction(LCadFunction):
    """
    These are functions that cannot be written in the language itself.
    """
    pass


class LCadBlock(SpecialFunction):
    """
    A 'block' of code, similar to progn in Lisp.

    Usage:
     (block
       (def x 15)    ; local variable x
       (def inc-x () ; function to modify x (and return the current value).
         (+ x 1))
       inc-x)        ; return the inc-x function

    """
    def __init__(self):
        self.name = "block"

    def call(self, model, tree):
        val = None
        for node in tree.value[1:]:
            val = interp.interpret(model, node)
        return val

builtin_functions["block"] = LCadBlock()


class LCadDef(SpecialFunction):
    """
    Create a variable or function.

    Usage:
     (def x 15) - Create the variable x with the value 15.
     (def x 15 y 20) - Create x with value 15, y with value 20.
     (def incf (x) (+ x 1)) - Create the function incf.

    Note that you cannot create multiple functions at the same time.

    """
    def __init__(self):
        self.name = "def"

    # This only sets variables. Functions are created in createLexicalEnv().
    def call(self, model, tree):
        args = tree.value[1:]
        if ((len(args)%2) == 0):
            ret = None
            kv_pairs = izip(*[iter(args)]*2)
            for key, node in kv_pairs:

                # If the symbol is not already defined for this environment then something has gone seriously amiss.
                if not key.value in tree.lenv.symbols:
                    raise Exception("My hovercraft is full of eels!!")
                val = interp.interpret(model, node)
                tree.lenv.symbols[key.value].setv(val)
                ret = val
            return ret
        return None

builtin_functions["def"] = LCadDef()


class LCadFor(SpecialFunction):
    """
    For statement.

    Usage:
     (for (i 10) ..)       ; increment i from 0 to 9.
     (for (i 1 11) ..)     ; increment i from 1 to 11.
     (for (i 1 0.1 5) ..)  ; increment i from 1 to 5 in steps of 0.1.
    """
    def __init__(self):
        self.name = "for"

    def call(self, model, tree):

        # Determine loop parameters.
        loop_args = tree.value[1].value
        inc_var = tree.lenv.symbols[loop_args[0].value]
        start = 0
        inc = 1
        if (len(loop_args)==2):
            stop = interp.interpret(model, loop_args[1])
        elif (len(loop_args)==3):
            start = interp.interpret(model, loop_args[1])
            stop = interp.interpret(model, loop_args[2])
        else:
            start = interp.interpret(model, loop_args[1])
            inc = interp.interpret(model, loop_args[2])
            stop = interp.interpret(model, loop_args[3])

        # loop.
        ret = None
        cur = start
        while(cur < stop):
            inc_var.setv(cur)
            for node in tree.value[2:]:
                ret = interp.interpret(model, node)
            cur += inc
        return ret

builtin_functions["for"] = LCadFor()


class LCadIf(SpecialFunction):
    """
    If statement. The first argument must be t or nil.

    Usage:
     (if t 1 2)       ; returns 1
     (if 1 2 3)       ; error
     (if (= 1 1) 1 2) ; returns 1

     (if x 1 0)       ; error if x is not t or nil
     (if (= x 2) 3)
     (if (= (fn) 0) 
       (block 
          (fn1 1) 
          (fn2))
       (fn3 1 2))
    """
    def __init__(self):
        self.name = "if"

    def argCheck(self, tree):
        if (len(tree.value) != 3) and (len(tree.value) != 4):
            raise lce.NumberArgumentsException(tree, "2 or 3", len(tree.value) - 1)

    def call(self, model, tree):
        args = tree.value[1:]
        if isTrue(model, tree, args[0]):
            return interp.interpret(model, args[1])
        else:
            if (len(args)==3):
                return interp.interpret(model, args[2])
            else:
                return False

builtin_functions["if"] = LCadIf()

#class LCadMirror(SpecialFunction):


class LCadPart(SpecialFunction):
    """
    Add a part to the model.

    :param part_id: The name of the LDraw .dat file for this part.
    :param part_color: The LDraw name or id of the color.

    Usage:
     (part "32524" 13)
     (part '32524' "yellow")

    """
    def __init__(self):
        self.name = "part"

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist) != 3):
            raise lce.NumberArgumentsException(tree, 2, len(flist) - 1)

    def call(self, model, tree):
        args = tree.value[1:]
        part_id = interp.interpret(model, args[0])
        part_color = interp.interpret(model, args[1])
        model.parts_list.append(parts.Part(model.m, part_id, part_color))
        return None

builtin_functions["part"] = LCadPart()


class LCadPrint(SpecialFunction):
    """
    Print to the console.

    Usage:
     (print x "=" 10)

    """
    def __init__(self):
        self.name = "print"

    def call(self, model, tree):
        string = ""
        for node in tree.value[1:]:
            string += str(interp.interpret(model, node))
        print string
        return string

builtin_functions["print"] = LCadPrint()


class LCadRotate(SpecialFunction):
    """
    Add a rotation to the current transformation matrix, rotation 
    is done first around z, then y and then x. Parts added inside
    a rotate block have this transformation applied to them.

    :param ax: Amount to rotate around the x axis in degrees.
    :param ay: Amount to rotate around the y axis in degrees.
    :param az: Amount to rotate around the y axis in degrees.

    Usage:
     (rotate (0 0 90) .. )

    """
    def __init__(self):
        self.name = "rotate"

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<2):
            raise lce.NumberArgumentsException(tree, "3", 0)
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException(tree, "3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        new_model = model.makeCopy()        
        ax = interp.interpret(new_model, args[0]) * numpy.pi / 180.0
        ay = interp.interpret(new_model, args[1]) * numpy.pi / 180.0
        az = interp.interpret(new_model, args[2]) * numpy.pi / 180.0

        rx = numpy.identity(4)
        rx[1,1] = math.cos(ax)
        rx[1,2] = -math.sin(ax)
        rx[2,1] = -rx[1,2]
        rx[2,2] = rx[1,1]

        ry = numpy.identity(4)
        ry[0,0] = math.cos(ay)
        ry[0,2] = -math.sin(ay)
        ry[2,0] = -ry[0,2]
        ry[2,2] = ry[0,0]

        rz = numpy.identity(4)
        rz[0,0] = math.cos(az)
        rz[0,1] = -math.sin(az)
        rz[1,0] = -rz[0,1]
        rz[1,1] = rz[0,0]

        new_model.m = numpy.dot(new_model.m, (numpy.dot(rx, numpy.dot(ry, rz))))

        if (len(tree.value) > 2):
            return interp.interpret(new_model, tree.value[2:])
        else:
            return None

builtin_functions["rotate"] = LCadRotate()


class LCadSet(SpecialFunction):
    """
    Set the value of an existing symbol.

    Usage:
     (set x 15) - Set the value of x to 15.
     (set x 15 y 20) - Set x to 15 and y to 20.
     (set x fn) - Set x to value of the symbol fn.
    """
    def __init__(self):
        self.name = "set"

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist) < 3) or ((len(flist[1:])%2) != 0):
            raise lce.NumberArgumentsException(tree, "A multiple of 2", len(flist[1:]))

    def call(self, model, tree):
        args = tree.value[1:]
        ret = None
        kv_pairs = izip(*[iter(args)]*2)
        for key, node in kv_pairs:
            if not isinstance(key, lexerParser.LCadSymbol):
                raise lce.CannotSetException(tree, key.simple_type_name)
            if not key.value in tree.lenv.symbols:
                raise lce.SymbolNotDefined(tree, key.value)
            if key.value in interp.builtin_symbols:
                raise lce.CannotOverrideTNil(tree)

            val = interp.interpret(model, node)
            tree.lenv.symbols[key.value].setv(val)
            ret = val
        return ret

builtin_functions["set"] = LCadSet()


class LCadTranslate(SpecialFunction):
    """
    Add a rotation to the current transformation matrix. Parts inside a translate
    block have this transformation applied to them.

    :param dx: Displacement in x in LDU.
    :param dy: Displacement in x in LDU.
    :param dz: Displacement in x in LDU.

    Usage:
     (translate (0 0 5) .. )

    """
    def __init__(self):
        self.name = "translate"

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist)<2):
            raise lce.NumberArgumentsException(tree, "3", 0)
        if (len(flist[1].value) != 3):
            raise lce.NumberArgumentsException(tree, "3", len(flist[1].value))

    def call(self, model, tree):
        args = tree.value[1].value

        new_model = model.makeCopy()
        m = numpy.identity(4)
        m[0,3] = interp.interpret(new_model, args[0])
        m[1,3] = interp.interpret(new_model, args[1])
        m[2,3] = interp.interpret(new_model, args[2])

        new_model.m = numpy.dot(new_model.m, m)
        if (len(tree.value) > 2):
            return interp.interpret(new_model, tree.value[2:])
        else:
            return None

builtin_functions["translate"] = LCadTranslate()


#
# Comparison functions.
#

class ComparisonFunction(SpecialFunction):
    """
    Comparison functions, =, >, <, >=, <=, !=.
    """
    def argCheck(self, tree):
        if (len(tree.value) < 3):
            raise lce.NumberArgumentsException(tree, "2+", len(tree.value) - 1)

    def compare(self, model, tree, cmp_func):
        args = tree.value[1:]
        val0 = interp.interpret(model, args[0])
        for arg in args[1:]:
            if not cmp_func(val0, interp.interpret(model, arg)):
                return interp.lcad_nil
        return interp.lcad_t
        

class LCadEqual(ComparisonFunction):
    """
    =

    Usage:
     (= 1 1)     ; t
     (= 1 2)     ; nil
     (= 2 2 2 2) ; t
     (= "a" "a") ; t
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.eq)

builtin_functions["="] = LCadEqual("=")


class LCadGt(ComparisonFunction):
    """
    >

    Usage:
     (> 2 1) ; t
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.gt)

builtin_functions[">"] = LCadGt(">")


class LCadLt(ComparisonFunction):
    """
    <

    Usage:
     (< 2 1) ; nil
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.lt)

builtin_functions["<"] = LCadLt("<")


class LCadGe(ComparisonFunction):
    """
    >=

    Usage:
     (>= 2 1) ; t
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.ge)

builtin_functions[">="] = LCadGe(">=")


class LCadLe(ComparisonFunction):
    """
    <=

    Usage:
     (<= 2 1) ; nil
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.le)

builtin_functions["<="] = LCadLe("<=")


class LCadNe(ComparisonFunction):
    """
    !=

    Usage:
     (!= 2 1) ; t
    """
    def call(self, model, tree):
        return self.compare(model, tree, operator.ne)

builtin_functions["!="] = LCadNe("!=")


#
# Logic functions.
#

class LogicFunction(SpecialFunction):
    """
    Logic functions, and, or, not
    """
    def argCheck(self, tree):
        if (len(tree.value) < 3):
            raise lce.NumberArgumentsException(tree, "2+", len(tree.value) - 1)

class LCadAnd(LogicFunction):
    """
    And statement.

    Usage:
     (and (< 1 2) (< 2 3))  ; t
     (and (fn x) nil)      ; nil
    """
    def call(self, model, tree):
        for node in tree.value[1:]:
            if isTrue(model, tree, node):
                return interp.lcad_t
        return interp.lcad_nil

builtin_functions["and"] = LCadAnd("and")


class LCadOr(LogicFunction):
    """
    Or statement.

    Usage:
     (or (< 1 2) (> 1 3))  ; t
     (or (fn x) t)         ; t
     (or nil nil)          ; nil
    """
    def call(self, model, tree):
        for node in tree.value[1:]:
            if isTrue(model, tree, node):
                return interp.lcad_t
        return interp.lcad_nil

builtin_functions["or"] = LCadOr("or")


class LCadNot(SpecialFunction):
    """
    Not statement.

    Usage:
     (not t)  ; t
     (not ()) ; nil
    """
    def argCheck(self, tree):
        if (len(tree.value) != 2):
            raise lce.NumberArgumentsException(tree, "2", len(tree.value) - 1)

    def call(self, model, tree):
        if isTrue(model, tree, tree.value[1]):
            return interp.lcad_nil
        else:
            return interp.lcad_t

builtin_functions["not"] = LCadNot("not")


#
# (Basic) math functions.
#

class BasicMathFunction(SpecialFunction):
    """
    Basic math functions, + - * /.
    """
    def argCheck(self, tree):
        if (len(tree.value) < 3):
            raise lce.NumberArgumentsException(tree, "2+", len(tree.value) - 1)


class LCadDivide(BasicMathFunction):
    """
    Divide the first number by one or more additional numbers.

    Usage:
     (/ 4 2)

    """
    def call(self, model, tree):
        total = interp.interpret(model, tree.value[1])
        for node in tree.value[2:]:
            total = total/interp.interpret(model, node)
        return total

builtin_functions["/"] = LCadDivide("/")


class LCadMinus(BasicMathFunction):
    """
    Subtract one or more numbers from the first number.

    Usage:
     (- 50 20 y)

    """
    def call(self, model, tree):
        total = interp.interpret(model, tree.value[1])
        for node in tree.value[2:]:
            total -= interp.interpret(model, node)
        return total

builtin_functions["-"] = LCadMinus("-")


class LCadMultiply(BasicMathFunction):
    """
    Multiply two or more numbers.

    Usage:
     (* 2 2 y)

    """
    def call(self, model, tree):
        total = 1
        for node in tree.value[2:]:
            total = total * interp.interpret(model, node)
        return total

builtin_functions["*"] = LCadMultiply("*")


class LCadPlus(BasicMathFunction):
    """
    Add together two or more numbers.

    Usage:
     (+ 10 20 y)

    """
    def call(self, model, tree):
        total = 0
        for node in tree.value[1:]:
            total += interp.interpret(model, node)
        return total

builtin_functions["+"] = LCadPlus("+")


#
# The MIT License
#
# Copyright (c) 2014 Hazen Babcock
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