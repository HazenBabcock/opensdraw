#!/usr/bin/env python
"""
.. module:: functions
   :synopsis: The core functions (def, if, set, ..)

.. moduleauthor:: Hazen Babcock

"""

import importlib
from itertools import izip
import numbers
import numpy
import os

import functions
import interpreter as interp
import lcadExceptions as lce
import lexerParser

lcad_functions = {}


# This was useful for testing the import function.
def printSymbolTableIds(lenv):
    while lenv is not None:
        print id(lenv)
        lenv = lenv.parent
    print "-"


class ArefSymbol(interp.Symbol):
    """
    These are created by aref as a "pointer" into a list, so that
    you can both get and change the value of a particular element
    in a list, vector or matrix.
    """
    def __init__(self, tlist, index):
        interp.Symbol.__init__(self, "aref-symbol", "na")
        self.tlist = tlist
        self.index = index

    def getv(self):
        return self.tlist[self.index]

    def setv(self, value):
        if isinstance(self.tlist, numpy.ndarray) and not (isinstance(value, numbers.Number)):
            raise lce.WrongTypeException("number", type(value))
        self.tlist[self.index] = value


class CoreFunction(functions.LCadFunction):
    pass


class Append(CoreFunction):
    """
    **append** - Add one or more elements to a list.

    Usage::

     (def l (list 1))  ; Create the list (1).
     (append l 2)      ; The list is now (1, 2).
    """
    def __init__(self):
        CoreFunction.__init__(self, "append")
        self.setSignature([[list], [object], ["optional", [object]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        tlist = args[0]
        for arg in args[1:]:
            tlist.append(arg)
        return tlist

lcad_functions["append"] = Append()


class Aref(CoreFunction):
    """
    **aref** - Return an element of a list, vector or matrix.

    Usage::

     (aref (list 1 2 3) 1)           ; returns 2
     (set (aref (list 1 2 3) 1) 4)   ; list is now 1, 4, 3
     (aref (vector 1 2 3) 1)         ; returns 2
     (set (aref (vector 1 2 3) 1) 4) ; vector is now 1, 4, 3
    """
    def __init__(self):
        CoreFunction.__init__(self, "aref")
        self.setSignature([[list, numpy.ndarray], [int], ["optional", [int]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        tlist = args[0]

        # 1D list / vector.
        if (len(args) == 2):
            if (args[1] >= 0) and (args[1] < len(tlist)):
                return ArefSymbol(tlist, args[1])
            else:
                raise lce.OutOfRangeException(tlist.size - 1, args[1])

        # 2D matrix.
        else:
            if not isinstance(tlist, numpy.ndarray):
                raise lce.WrongTypeException("numpy.ndarray", type(elt))
            if (len(tlist.shape) != 2):
                raise lce.LCadException("Expected a 2D matrix, got a " + str(len(val.shape)) + "D matrix.")

            if (args[1] >= 0) and (args[1] < tlist.shape[0]) and (args[2] >= 0) and (args[2] < tlist.shape[1]):
                return ArefSymbol(tlist, tuple(args[1:]))
            else:
                raise lce.LCadException(" index " + str(tuple(args[1:])) + " is outside of " + str(tlist.shape))

lcad_functions["aref"] = Aref()


class Block(CoreFunction):
    """
    **block** - A block of code, similar to *progn* in Lisp.

    Usage::

     (block
       (def x 15)    ; local variable x
       (def inc-x () ; function to modify x (and return the current value).
         (+ x 1))
       inc-x)        ; return the inc-x function

    """
    def __init__(self):
        CoreFunction.__init__(self, "block")
        self.setSignature([["optional", [object]]])

    def call(self, model, tree):
        args = self.getArgs(model, tree)
        return args[-1]

lcad_functions["block"] = Block()


class Concatenate(CoreFunction):
    """
    **concatenate** - Concatenate 1 or more strings.

    Usage::

     (concatenate "as" "df")  ; Returns "asdf".
     (concatenate "as" 1)     ; Returns "as1".
    """
    def __init__(self):
        CoreFunction.__init__(self, "cond")
        self.setSignature([[basestring, numbers.Number], ["optional", [basestring, numbers.Number]]])

    def call(self, model, tree):
        a_string = ""
        for arg in self.getArgs(model, tree):
            a_string += str(arg)
        return a_string
                            
lcad_functions["concatenate"] = Concatenate()


class Cond(CoreFunction):
    """
    **cond** - Switch statement.

    Usage::

     (cond
       ((= x 1) ..) ; do this if x = 1
       ((= x 2) ..) ; do this if x = 2
       ((= x 3) ..) ; do this if x = 3
       (t ..))      ; otherwise do this
    """
    def __init__(self):
        CoreFunction.__init__(self, "cond")
        self.setSignature([[object], ["optional", [object]]])

    def call(self, model, tree):
        args = tree.value[1:]
        ret = interp.lcad_nil
        for arg in args:
            nodes = arg.value
            if functions.isTrue(interp.getv(interp.interpret(model, nodes[0]))):
                for node in nodes[1:]:
                    ret = interp.interpret(model, node)
                return ret
        return ret

lcad_functions["cond"] = Cond()


class Def(CoreFunction):
    """
    **def** - Create a variable or function.

    Usage::

     (def x 15) - Create the variable x with the value 15.
     (def x 15 y 20) - Create x with value 15, y with value 20.
     (def incf (x) (+ x 1)) - Create the function incf.

    Note: You cannot create multiple functions at the same time::

     (def fn (x y)  ; Wrong. def() will think you are trying to create
      (+ x 1)       ; two symbols, the first called 'fn' and the second
      (+ y 2))      ; called '(+ x 1)' and throw a likely confusing error
                    ; message.

     (def fn (x y)  ; Correct.
      (block
       (+ x 1)
       (+ y 2)))

    """
    def __init__(self):
        CoreFunction.__init__(self, "def")

    def argCheck(self, tree):
        # def needs at least 3 arguments.
        if (len(tree.value)<3):
            raise lce.NumberArgumentsException("2 or more", len(tree.value) - 1)

        # Check for the right number of arguments (4 for a function, 
        # a multiple of 2 for variables).
        if (len(tree.value)!=4) and ((len(tree.value)%2)!=1):
            raise lce.NumberArgumentsException("an even number of arguments", len(tree.value) - 1)

    def call(self, model, tree):
        args = tree.value[1:]

        # Symbols are created in the lexical environment of the parent expression.
        lenv = tree.lenv.parent

        # Functions have already been created (so that they can be called out of
        # order), just return the function.
        if (len(args) == 3):
            tree.initialized = True
            return lenv.symbols[args[0].value].getv()

        # Create Symbols.
        if ((len(args)%2) == 0):
            ret = None
            kv_pairs = izip(*[iter(args)]*2)
            for key, node in kv_pairs:

                # FIXME: Maybe something more appropriate for the error, like can only create symbols?
                if not isinstance(key, lexerParser.LCadSymbol):
                    raise lce.CannotSetException(type(key))

                symbol_name = key.value
                if not tree.initialized:
                    try:
                        interp.checkOverride(lenv, symbol_name)
                    except lce.SymbolNotDefined:
                        pass

                if not (symbol_name in lenv.symbols):
                    lenv.symbols[symbol_name] = interp.Symbol(symbol_name, tree.filename)

                val = interp.getv(interp.interpret(model, node))
                lenv.symbols[symbol_name].setv(val)
                ret = val
            tree.initialized = True
            return ret

lcad_functions["def"] = Def()


class For(CoreFunction):
    """
    **for** - For statement.

    Usage::

     (for (i 10) ..)           ; increment i from 0 to 9.
     (for (i 1 11) ..)         ; increment i from 1 to 11.
     (for (i 1 0.1 5) ..)      ; increment i from 1 to 5 in steps of 0.1.
     (for (i (list 1 3 4)) ..) ; increment i over the values in the list.
    """
    def __init__(self):
        CoreFunction.__init__(self, "for")

    def argCheck(self, tree):
        flist = tree.value

        # For needs at least 3 arguments.
        if (len(flist)<3):
            raise lce.NumberArgumentsException("2 or more", len(flist) - 1)
            
        # Check that loop arguments are correct.
        loop_args = flist[1]
        if not isinstance(loop_args, lexerParser.LCadExpression):
            raise lce.LCadException("first argument in for() must be a list.")
            
        # Check for the right number of arguments.
        loop_args = loop_args.value
        if (len(loop_args) < 2):
            raise lce.NumberArgumentsException("2,3 or 4", len(loop_args))
        elif (len(loop_args) > 4):
            raise lce.NumberArgumentsException("2,3 or 4", len(loop_args))

        # Check for correct type of loop variable.
        if not isinstance(loop_args[0], lexerParser.LCadSymbol):
            raise lce.LCadException("loop variable must be a symbol.")

        # Create loop variable.
        inc_name = loop_args[0].value
        interp.checkOverride(tree.lenv, inc_name)
        tree.lenv.symbols[inc_name] = interp.Symbol(inc_name, tree.filename)
        tree.initialized = True

    def call(self, model, tree):
        loop_args = tree.value[1].value
        inc_var = tree.lenv.symbols[loop_args[0].value]

        # Iterate over list.
        arg1 = interp.getv(interp.interpret(model, loop_args[1]))
        if ((len(loop_args)==2) and (isinstance(arg1, list))):
            ret = None
            for elt in arg1:
                inc_var.setv(elt)
                for node in tree.value[2:]:
                    ret = interp.interpret(model, node)
            return ret

        # "Normal" iteration.
        else:
            start = 0
            inc = 1
            if (len(loop_args)==2):
                stop = interp.getv(arg1)
            elif (len(loop_args)==3):
                start = interp.getv(interp.interpret(model, loop_args[1]))
                stop = interp.getv(interp.interpret(model, loop_args[2]))
            else:
                start = interp.getv(interp.interpret(model, loop_args[1]))
                inc = interp.getv(interp.interpret(model, loop_args[2]))
                stop = interp.getv(interp.interpret(model, loop_args[3]))

            # loop.
            ret = None
            cur = start
            while(cur < stop):
                inc_var.setv(cur)
                for node in tree.value[2:]:
                    ret = interp.interpret(model, node)
                cur += inc
            return ret
        print "end"

lcad_functions["for"] = For()


class If(CoreFunction):
    """
    **if** - If statement. 

    The first argument must be t or nil.

    Usage::

     (if t 1 2)       ; returns 1
     (if 1 2 3)       ; error
     (if (= 1 1) 1 2) ; returns 1
     (if x 1 0)       ; error if x is not t or nil
     (if (= x 2) 3)
     (if (= (fn) 0)   ; if / else
       (block 
          (fn1 1) 
          (fn2))
       (fn3 1 2))
    """
    def __init__(self):
        CoreFunction.__init__(self, "if")

    def argCheck(self, tree):
        if (len(tree.value) != 3) and (len(tree.value) != 4):
            raise lce.NumberArgumentsException("2 or 3", len(tree.value) - 1)
        tree.initialized = True

    def call(self, model, tree):
        args = tree.value[1:]
        if functions.isTrue(interp.getv(interp.interpret(model, args[0]))):
            return interp.interpret(model, args[1])
        else:
            if (len(args)==3):
                return interp.interpret(model, args[2])
            else:
                return interp.lcad_nil

lcad_functions["if"] = If()


class Import(CoreFunction):
    """
    **import** - Import a module.

    Module are searched for in the current working directory first,
    then in the library folder of the opensdraw project. The modules
    are assumed to be in files that end with the ".lcad" extension.

    Usage::

     (import mod1)      ; import mod1.lcad
     (print mod1:x)     ; print the value of x in the mod1.lcad module.
     (mod1:fn 1)        ; call the function fn in the mod1.lcad module.

     (import mod1 mod2) ; import mod1.lcad and mod2.lcad.
     (def mx mod1:x)    ; use m1 as an alternate name for mod1:x.
     (print mx)         ; print the value of x in the mod1.lcad module.

     (import mod1 mod2 :local) ; import mod1.lcad and mod2.lcad into the name space of current module.
    """
    def __init__(self):
        CoreFunction.__init__(self, "import")
        self.paths = ["./", os.path.dirname(__file__) + "/../library/"]

    def argCheck(self, tree):

        # Import needs at least 1 arguments.
        if (len(tree.value)<2):
            raise lce.NumberArgumentsException("1 or more", len(tree.value) - 1)

    def call(self, model, tree):

        if tree.initialized:
            return
        else:
            tree.initialized = True

        args = tree.value[1:]
        local = True if (args[-1].value == ":local") else False
        if local:
            args = args[:-1]
        for arg in args:
            module_lenv = interp.LEnv(add_built_ins = True)
            module_model = interp.Model()
            for path in self.paths:
                filename = path + arg.value + ".lcad"
                if os.path.exists(filename):
                    with open(filename) as fp:
                        module_ast = lexerParser.parse(fp.read(), filename)
                        interp.createLexicalEnv(module_lenv, module_ast)
                        interp.interpret(module_model, module_ast)
                    break
            else:
                raise lce.FileNotFoundException(arg.value + ".lcad")

            lenv = tree.lenv.parent
            for sym_name in module_lenv.symbols:
                if (not sym_name in interp.builtin_symbols) and (not sym_name in functions.builtin_functions):
                    if local:
                        interp.checkOverride(lenv, sym_name, module_lenv.symbols[sym_name].filename)
                        lenv.symbols[sym_name] = module_lenv.symbols[sym_name]
                    else:
                        full_name = arg.value + ":" + sym_name
                        interp.checkOverride(lenv, full_name)
                        lenv.symbols[full_name] = module_lenv.symbols[sym_name]

lcad_functions["import"] = Import()


class Lambda(CoreFunction):
    """
    **lambda** - Create an anonymous function.

    Usage::

    (def fn (lambda (x) (+ x 1)))           ; Create a function and assign to symbol fn.
    (fn 1)                                  ; -> 2
    (def myp (lambda () (part "32524" 15))) ; Create function that creates a particular part.
    """
    def __init__(self):
        CoreFunction.__init__(self, "lambda")

    def argCheck(self, tree):
        if (len(tree.value) != 3):
            raise lce.NumberArgumentsException("2", len(tree.value) - 1)
        tree.initialized = True

    def call(self, model, tree):
        return functions.UserFunction(tree, "anonymous")

lcad_functions["lambda"] = Lambda()


class Len(CoreFunction):
    """
    **len** - Return the length of a list.

    Usage::

     (len (list 1 2 3)) ; returns 3
    """
    def __init__(self):
        CoreFunction.__init__(self, "len")
        self.setSignature([[list]])

    def call(self, model, tree):
        return len(self.getArg(model, tree, 0))

lcad_functions["len"] = Len()


class List(CoreFunction):
    """
    **list** - Create a list.

    Usage::

     (list 1 2 3)  ; returns the list 1,2,3
     (list)        ; an empty list
    """
    def __init__(self):
        CoreFunction.__init__(self, "list")
        self.setSignature([["optional", [object]]])

    def call(self, model, tree):
        vals = []
        for arg in self.getArgs(model, tree):
            vals.append(arg)
        return vals
    
lcad_functions["list"] = List()


class Print(CoreFunction):
    """
    **print** - Print to the console.

    Usage::

     (print x "=" 10)

    """
    def __init__(self):
        CoreFunction.__init__(self, "print")
        self.setSignature([["optional", [object]]])

    def call(self, model, tree):
        string = ""
        for arg in self.getArgs(model, tree):
            string += str(arg)
        print string
        return string

lcad_functions["print"] = Print()


class PyImport(CoreFunction):
    """
    **pyimport** - Import a Python module and add any functions in the
    modules lcad_functions{} dictionary (that are instances of LCadFunction)
    to the current lexical environment. The module must be on the Python
    path (which includes the current working directory).

    Usage::
   
     (pyimport mymodule)  ; Import the Python module mymodule.py.
    """
    def __init__(self):
        CoreFunction.__init__(self, "pyimport")

    def argCheck(self, tree):
        if (len(tree.value) < 2):
            raise lce.NumberArgumentsException("1 or more", len(tree.value) - 1)
        tree.initialized = True

    def call(self, model, tree):
        args = tree.value[1:]
        lenv = tree.lenv.parent
        for arg in args:
            module = importlib.import_module(arg.value)
            if hasattr(module, "lcad_functions"):
                for fn_name in module.lcad_functions.keys():
                    fn = module.lcad_functions[fn_name]
                    if isinstance(fn, functions.LCadFunction):
                        interp.checkOverride(lenv, fn_name)
                        lenv.symbols[fn_name] = interp.Symbol(fn_name, "pyimport")
                        lenv.symbols[fn_name].setv(fn)
                    else:
                        print "Warning! Did not load", fn_name, "because it is not of type LCadFunction"
            else:
                print "Warning! module", arg.value, "has no LCadFunctions."

lcad_functions["pyimport"] = PyImport()


class Set(CoreFunction):
    """
    **set** - Set the value of an existing symbol.

    Usage::

     (set x 15) - Set the value of x to 15.
     (set x 15 y 20) - Set x to 15 and y to 20.
     (set x fn) - Set x to be the function fn.
    """
    def __init__(self):
        CoreFunction.__init__(self, "set")

    def argCheck(self, tree):
        flist = tree.value
        if (len(flist) < 3) or ((len(flist[1:])%2) != 0):
            raise lce.NumberArgumentsException("A multiple of 2", len(flist[1:]))
        tree.initialized = True

    def call(self, model, tree):
        args = tree.value[1:]
        ret = None
        kv_pairs = izip(*[iter(args)]*2)
        for sym_node, val_node in kv_pairs:

            sym = interp.interpret(model, sym_node)
            if not isinstance(sym, interp.Symbol):
                raise lce.CannotSetException(type(sym))
            if (sym.name in functions.builtin_functions):
                print "Warning, overwriting builtin function:", sym.name, "!!"
            if (sym.name in interp.builtin_symbols):
                if not (sym.name in interp.mutable_symbols):
                    raise lce.CannotOverrideBuiltIn()

            val = interp.getv(interp.interpret(model, val_node))
            sym.setv(val)
            ret = val
        return ret

lcad_functions["set"] = Set()


class While(CoreFunction):
    """
    **while** - While loop.

    Usage::

     (def x 1)
     (while (< x 10) .. )
    """
    def __init__(self):
        CoreFunction.__init__(self, "while")

    def argCheck(self, tree):
        if (len(tree.value)<3):
            raise lce.NumberArgumentsException("2+", len(tree.value) - 1)
        tree.initialized = True

    def call(self, model, tree):
        args = tree.value[1:]
        ret = None
        while functions.isTrue(interp.getv(interp.interpret(model, args[0]))):
            for arg in args[1:]:
                ret = interp.interpret(model, arg)
        return ret

lcad_functions["while"] = While()


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
