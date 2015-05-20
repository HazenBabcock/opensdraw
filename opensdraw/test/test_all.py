#!/usr/bin/env python
"""
.. module:: test_all
   :synopsis: Nose tests of the lcad language.

.. moduleauthor:: Hazen Babcock

"""

import math
import nose
import numbers
import numpy

import opensdraw.lcad_language.belt as belt
import opensdraw.lcad_language.chain as chain
import opensdraw.lcad_language.curve as curve
import opensdraw.lcad_language.interpreter as interpreter
import opensdraw.lcad_language.lcadExceptions as lcadExceptions
import opensdraw.lcad_language.lexerParser as lexerParser
import opensdraw.lcad_language.lcadTypes as lcadTypes
import opensdraw.lcad_language.pulleySystem as pulleySystem

def exe(string):
    """
    Wrap interpreter call for convenience.
    """
    lenv = interpreter.LEnv(add_built_ins = True)
    model = interpreter.Model()
    ast = lexerParser.parse(string, "test")
    interpreter.createLexicalEnv(lenv, ast)
    sym = interpreter.interpret(model, ast)
    return interpreter.getv(sym)

## Symbols

# t (true)
def test_t():
    assert exe("(if t 0 1)") == 0

# nil (false)
def test_nil():
    assert exe("(if nil 0 1)") == 1

# e
def test_e():
    assert exe("e") == math.e

# pi
def test_pi():
    assert exe("pi") == math.pi

# time-index
def text_time_index():
    assert exe("time-index") == 0


## Comparison Functions.

# equal
def test_eq_1():
    assert exe("(if (= 1 1) 0 1)") == 0

def test_eq_2():
    assert exe("(if (= 1 0) 0 1)") == 1

# gt
def test_gt_1():
    assert exe("(if (> 1 2) 0 1)") == 1

def test_gt_2():
    assert exe("(if (> 1 0) 0 1)") == 0

# lt
def test_lt_1():
    assert exe("(if (< 1 2) 0 1)") == 0

def test_lt_2():
    assert exe("(if (< 1 0) 0 1)") == 1

# le
def test_le_1():
    assert exe("(if (<= 1 1) 0 1)") == 0

def test_le_2():
    assert exe("(if (<= 1 0) 0 1)") == 1

# ge
def test_ge_1():
    assert exe("(if (>= 1 2) 0 1)") == 1

def test_ge_2():
    assert exe("(if (>= 1 1) 0 1)") == 0

# ne
def test_ne_1():
    assert exe("(if (!= 1 2) 0 1)") == 0

def test_ne_2():
    assert exe("(if (!= 1 1) 0 1)") == 1


## coreFunctions

# append
def test_append_1():
    assert exe("(def m (list 1)) (append m 2) (aref m 1)") == 2

def test_append_2():
    assert exe("(def m (list 1)) (append m 2 3) (aref m 2)") == 3

# aref
def test_aref_1():
    assert exe("(aref (list 1 2 3) 1)") == 2
    
def test_aref_2():
    assert exe("(def x (list 1 2 3)) (set (aref x 1) 4) (aref x 1)") == 4

def test_aref_3():
    assert exe("(def x (vector 1 2 3)) (set (aref x 1) 4) (aref x 1)") == 4

def test_aref_4():
    assert exe("(def m (matrix (list 1 2 3 4 5 6 7 8 9 10 11 12))) (set (aref m 1 1) 0) (aref m 1 1)") == 0

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_aref_5():
    exe("(aref (matrix (list 0 0 0 0 0 0)) 1)")

@nose.tools.raises(lcadExceptions.OutOfRangeException)
def test_aref_6():
    exe("(aref (list 1 2 3) 5)")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_aref_7():
    exe("(aref (vector 0 0 0) 1 2)")
    
@nose.tools.raises(lcadExceptions.LCadException)
def test_aref_8():
    exe("(aref (matrix (list 0 0 0 0 0 0)) 5 5)")

# block
def test_block_1():
    assert exe("(def fn (block (def x 5) (def inc-x () (+ x 1)) inc-x)) (fn)") == 6

# concatenate
def test_concatenate_1():
    assert exe("(concatenate \"as\" 1)") == "as1"

# cond
def test_cond_1():
    assert exe("(def x 2) (cond ((= x 1) 2) ((= x 2) 3) ((= x 3) 4) (t 5))") == 3

# copy
def test_copy_1():
    assert exe("(def a (list 1 2 3) b (copy a)) (set (aref b 0) 5) (aref a 0)") == 1
    
# def
def test_def_1():
    assert exe("(def x 15) x") == 15

def test_def_2():
    assert exe("(def x 15 y 20) y") == 20

def test_def_3():
    assert exe("(def incf (x) (+ x 1)) (incf 2)") == 3

def test_def_4():
    assert exe("(def incf (x :y 0) (+ x y 1)) (incf 1)") == 2

def test_def_5():
    assert exe("(def incf (x :y 0) (+ x y 1)) (incf 1 :y 2)") == 4

def test_def_6():
    assert exe("(def incf (:y 0) (+ y 1)) (incf :y 2)") == 3

def test_def_7():
    assert exe("(def incf (:y 0) (+ y 1)) (incf)") == 1

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_def_8():
    exe("(def a)")

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_def_9():
    exe("(def a 1 b 2 c)")

@nose.tools.raises(lcadExceptions.CannotSetException)
def test_def_10():
    exe("(def 1 1)")

@nose.tools.raises(lcadExceptions.CannotOverrideBuiltIn)
def test_def_11():
    exe("(def t 1)")

@nose.tools.raises(lcadExceptions.SymbolAlreadyExists)
def test_def_11():
    exe("(def x 1) (def x 2)")

@nose.tools.raises(lcadExceptions.NotAFunctionException)
def test_def_12():
    exe("(def a 1) (a)")

@nose.tools.raises(TypeError)
def test_def_13():
    exe("(def fn (x :y 2) (+ x y)) (fn 1 2)")

@nose.tools.raises(lcadExceptions.KeywordException)
def test_def_14():
    exe("(def fn (x :y 2) (+ x y)) (fn 1 y 2)")

@nose.tools.raises(lcadExceptions.UnknownKeywordException)
def test_def_15():
    exe("(def fn (x :y 2) (+ x y)) (fn 1 :z 3)")

# for
def test_for_1():
    assert exe("(def x 0) (for (i 10) (set x (+ 1 x))) x") == 10

def test_for_2():
    assert exe("(def x 0) (for (i 1 11) (set x (+ 1 x))) x") == 10

def test_for_3():
    assert exe("(def x 0) (for (i 1 0.1 2) (set x (+ 1 x))) x") == 10

def test_for_4():
    assert exe("(def x 0) (for (i (list 1 2 3)) (set x (+ i x))) x") == 6

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_for_5():
    exe("(for 10)")

@nose.tools.raises(lcadExceptions.LCadException)
def test_for_6():
    exe("(for i 1)")
    
@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_for_7():
    exe("(for (i) 1)")

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_for_8():
    exe("(for (i 1 10 20 30) 1)")

@nose.tools.raises(lcadExceptions.LCadException)
def test_for_9():
    exe("(for (1 10) 1)")
    
# if
def test_if_1():
    assert exe("(if t 1 2)") == 1

def test_if_2():
    assert exe("(if (= 1 2) 1 2)") == 2

def test_if_3():
    assert exe("(if (if (= 1 2) t nil) 1 2)") == 2

def test_if_4():
    assert exe("(if (if (= 1 2) t) 1 2)") == 2

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_if_5():
    exe("(if t)")

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_if_6():
    exe("(if t 0 1 2)")
    
# import
def test_import_1():
    assert exe("(import mod) (mod:fn)") == math.pi

def test_import_2():
    assert exe("(import mod :local) (fn)") ==  math.pi

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_import_3():
    exe("(import)")
    
# lambda
def test_lambda_1():
    assert exe("(def fn (lambda (x) (+ x 1))) (fn 1)") == 2

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_lambda_2():
    exe("(lambda (x))")
    
# len
def test_len_1():
    assert exe("(len (list 1 2 3))") == 3

# list
def test_list_1():
    assert exe("(def x (list 1 2 3)) (aref x 0)") == 1

def test_list_2():
    assert exe("(list 1 2 3)")[1] == 2

# print
def test_print_1():
    assert exe("(print \"123\")") == "123"

# pyimport
def test_pyimport_1():
    assert exe("(pyimport pyimp1) (plus 1 1)") == 2

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_pyimport_2():
    exe("(pyimport)")

# set
def test_set_1():
    assert exe("(def x 10) (set x 15)") == 15

def test_set_2():
    assert exe("(def x 10 y 10) (set x 15 y 20)") == 20

def test_set_3():
    assert exe("(def fn () 1) (def x 2) (set x fn) (x)") == 1

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_set_4():
    exe("(set x)")

@nose.tools.raises(lcadExceptions.CannotSetException)
def test_set_5():
    exe("(set 1 2)")

@nose.tools.raises(lcadExceptions.CannotOverrideBuiltIn)
def test_set_6():
    exe("(set t nil)")

# while
def test_while_1():
    assert exe("(def x 0) (while (< x 9) (set x (+ 2 x))) x") == 10

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_while_2():
    exe("(while t)")

## Geometry Functions.

# cross product
def test_cross_product_1():
    assert exe("(aref (cross-product (vector 1 0 0) (vector 0 1 0)) 2)") == 1

def test_cross_product_2():
    assert exe("(aref (cross-product (vector 1 0 0) (vector 0 2 0) nil) 2)") == 2

# dot product
def test_dot_product_1():
    assert exe("(dot-product (vector 1 0 0) (vector 1 0 0))") == 1

def test_dot_product_2():
    assert exe("(dot-product (vector 1 0 0) (vector 0 1 0))") == 0

# matrix
def test_matrix_1():
    assert isinstance(exe("(matrix (list 1 2 3 1 2 3 1 2 3 1 2 3))"), lcadTypes.LCadMatrix)

def test_matrix_2():
    assert isinstance(exe("(matrix (list 1 2 3 1 2 3))"), lcadTypes.LCadMatrix)

def test_matrix_3():
    assert isinstance(exe("(matrix (list (list 1 2 3) (list 1 2 3) (list 1 2 3) (list 1 2 3)))"), lcadTypes.LCadMatrix)

def test_matrix_4():
    assert isinstance(exe("(matrix (matrix (list 1 2 3 1 2 3 1 2 3 1 2 3)))"), lcadTypes.LCadMatrix)

# mirror
def test_mirror_1():
    assert exe("(mirror (list 1 (if t 0 1) (if nil 0 1)) 1)") == 1

def test_mirror_2():
    assert exe("(mirror (vector 1 0 0) 1)") == 1

# rotate
def test_rotate_1():
    assert exe("(rotate (list 1 2 3) 1)") == 1

def test_rotate_2():
    assert exe("(rotate (vector 1 2 3) 1)") == 1

# scale
def test_scale_1():
    assert exe("(scale (list 1 2 3) 1)") == 1

def test_scale_2():
    assert exe("(scale (vector 1 2 3) 1)") == 1

# transform
def test_transform_1():
    assert exe("(transform (list 1 2 3 1 2 3 1 2 3 1 2 3) 1)") == 1

def test_transform_2():
    assert exe("(transform (list 1 2 3 1 2 3) 1)") == 1

def test_transform_3():
    assert exe("(transform (matrix (list 1 2 3 1 2 3 1 2 3 1 2 3)) 1)") == 1

# translate
def test_translate_1():
    assert exe("(translate (list 1 2 3) 1)") == 1

def test_translate_1():
    assert exe("(translate (vector 1 2 3) 1)") == 1

# vector
def test_vector_1():
    assert isinstance(exe("(vector 1 2 3)"), lcadTypes.LCadVector)

@nose.tools.raises(lcadExceptions.NumberArgumentsException)
def test_vector_2():
    exe("(vector 1)")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_vector_3():
    exe("(vector 1 2 'a')")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_vector_4():
    exe("(vector 1 2 3 4 'a')")
    
## Logic Functions.

# and
def test_and_1():
    assert exe("(if (and (< 1 2) (< 2 3)) 0 1)") == 0

def test_and_2():
    assert exe("(if (and (< 1 2) (> 2 3)) 0 1)") == 1

# or
def test_or_1():
    assert exe("(if (or (> 1 2) (< 2 3)) 0 1)") == 0

def test_or_2():
    assert exe("(if (or (> 1 2) (> 2 3)) 0 1)") == 1

# not
def test_not_1():
    assert exe("(if (not t) 0 1)") == 1

def test_not_2():
    assert exe("(if (not nil) 0 1)") == 0

def test_not_3():
    assert exe("(if (not ()) 0 1)") == 0


## Math Functions.

# basic math
def test_math_1():
    assert exe("(+ 1 1)") == 2

def test_math_2():
    assert exe("(- 1 1)") == 0

def test_math_3():
    assert exe("(* 2 2)") == 4

def test_math_4():
    assert exe("(/ 4 2)") == 2

def test_math_5():
    assert exe("(% 11 2)") == 1

def test_math_6():
    assert exe("(* (matrix (list 1 1 1 3 0 0 0 3 0 0 0 3)) (vector 1 2 3 1))")[1] == 7

def test_math_7():
    assert isinstance(exe("(* (matrix (list 1 1 1 3 0 0 0 3 0 0 0 3)) (vector 1 2 3 1))"), lcadTypes.LCadVector)

def test_math_8():
    assert isinstance(exe("(* (matrix (list 1 2 3 1 2 3)) (matrix (list 1 2 3 1 2 3)))"), lcadTypes.LCadMatrix)

def test_math_9():
    assert exe("(* (vector 1 2 3) (vector 1 2 3))")[1] == 4

def test_math_10():
    assert exe("(/ (vector 1 2 3) (vector 1 2 3))")[1] == 1

def test_math_11():
    assert exe("(+ (vector 1 2 3) (vector 1 2 3))")[1] == 4

def test_math_12():
    assert exe("(- (vector 1 2 3) (vector 1 2 3))")[1] == 0

def test_math_13():
    assert exe("(- 1)") == -1

def test_math_14():
    assert exe("(abs 2)") == 2

def test_math_15():
    assert exe("(abs -2)") == 2

# python math module
def test_py_math_1():
    assert int(round(exe("(cos 0)"))) == 1

def test_py_math_2():
    assert int(round(exe("(cos (/ pi 2))"))) == 0

def test_py_math_3():
    assert int(round(exe("(sin 0)"))) == 0

def test_py_math_4():
    assert int(round(exe("(sin (/ pi 2))"))) == 1


## Part Functions.

# group
def test_group_1():
    assert exe("(group \"adsf\" 1)") == 1

# header
def test_header_1():
    assert exe("(header \"asdf\")") == "asdf"


# line
def test_line_1():
    assert exe("(line (list 1 2 3) (list 4 5 6)) 1") == 1

def test_line_2():
    assert exe("(line (vector 1 2 3) (vector 4 5 6)) 1") == 1

# optional line
def test_optional_line_1():
    assert exe("(optional-line (list 1 2 3) (list 4 5 6) (list 1 2 3) (list 4 5 6)) 1") == 1

def test_optional_line_1():
    assert exe("(optional-line (vector 1 2 3) (vector 4 5 6) (vector 1 2 3) (vector 4 5 6)) 1") == 1

# part
def test_part_1():
    assert exe("(part '1234' 5) 1") == 1

# quadrilateral
def test_quadrilateral_1():
    assert exe("(quadrilateral (list 1 2 3) (list 4 5 6) (list 1 2 3) (list 4 5 6)) 1") == 1

def test_quadrilateral_2():
    assert exe("(quadrilateral (vector 1 2 3) (vector 4 5 6) (vector 1 2 3) (vector 4 5 6)) 1") == 1

# triangle
def test_triangle_1():
    assert exe("(triangle (list 1 2 3) (list 4 5 6) (list 7 8 9)) 1") == 1

def test_triangle_1():
    assert exe("(triangle (vector 1 2 3) (vector 4 5 6) (vector 7 8 9)) 1") == 1


# Random Number Functions.
def test_rand_seed_1():
    assert isinstance(exe("(rand-seed 10)"), numbers.Number)

def test_rand_choice_1():
    assert isinstance(exe("(rand-choice (list 1 2 3))"), numbers.Number)

def test_rand_choice_2():
    assert isinstance(exe("(def a () 10) (def b () 20) (def c (rand-choice (list a b))) (c)"), numbers.Number)
    
def test_rand_gauss_1():
    assert isinstance(exe("(rand-gauss)"), numbers.Number)

def test_rand_gauss_2():
    assert isinstance(exe("(rand-gauss 1 2)"), numbers.Number)

def test_rand_integer_1():
    assert isinstance(exe("(rand-integer 0 10)"), numbers.Number)

def test_rand_uniform_1():
    assert isinstance(exe("(rand-uniform)"), numbers.Number)

def test_rand_uniform_2():
    assert isinstance(exe("(rand-uniform 1 10)"), numbers.Number)


## Type Functions.
def test_is_boolean_1():
    assert exe("(if (boolean? nil) 1 0)") == 1

def test_is_boolean_2():
    assert exe("(if (boolean? 1) 1 0)") == 0

def test_is_matrix_1():
    assert exe("(if (matrix? (matrix (list 0 0 0 0 0 0))) 1 0)") == 1

def test_is_matrix_2():
    assert exe("(if (matrix? (vector 0 0 0)) 1 0)") == 0

def test_is_number_1():
    assert exe("(if (number? 1) 1 0)") == 1

def test_is_number_2():
    assert exe("(if (number? 'a') 1 0)") == 0    

def test_is_string_1():
    assert exe("(if (string? 1) 1 0)") == 0

def test_is_string_2():
    assert exe("(if (string? 'a') 1 0)") == 1

def test_is_vector_1():
    assert exe("(if (vector? (matrix (list 0 0 0 0 0 0))) 1 0)") == 0

def test_is_vector_2():
    assert exe("(if (vector? (vector 0 0 0)) 1 0)") == 1

    
## Library Functions.

# belt
def test_belt_1():
    assert exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1))) 1") == 1

def test_belt_2():
    assert exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)) :continuous nil) 1") == 1

@nose.tools.raises(belt.NumberPulleysException)
def test_belt_3():
    exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 1)))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_belt_4():
    exe("(belt (list (vector 1 1 1 1) (vector 1 1 1 1)))")

@nose.tools.raises(belt.PulleyException)
def test_belt_5():
    exe("(belt (list (list (list 0 0 0) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)))")
    
@nose.tools.raises(lcadExceptions.LCadException)
def test_belt_6():
    exe("(belt (list (list (list 0 0) (list 0 0 1) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)))")
    
@nose.tools.raises(lcadExceptions.LCadException)
def test_belt_7():
    exe("(belt (list (list (list 0 0 0) (list 0 0) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)))")
    
@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_belt_8():
    exe("(belt (list (list (list 0 0 0) (list 0 0 1) t 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)))")
    
@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_belt_9():
    exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 'a') (list (list 4 0 0) (list 0 0 1) 1.5 1)))")
    
# chain
def test_chain_1():
    assert exe("(chain (list (list -4 0 1 1) (list 4 0 1 1))) 1") == 1

def test_chain_2():
    assert exe("(chain (list (list -4 0 1 1) (list 4 0 1 1)) :continuous nil) 1") == 1

@nose.tools.raises(chain.NumberSprocketsException)
def test_chain_3():
    exe("(chain (list (list -4 0 1 1)))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_chain_4():
    exe("(chain (list (list -4 0 1 1) (vector 4 0 1 1)))")

@nose.tools.raises(chain.SprocketException)
def test_chain_5():
    exe("(chain (list (list -4 0 1 1) (list 0 1 1)))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_chain_6():
    exe("(chain (list (list -4 0 1 1) (list t 0 1 1)))")

# curve
def test_curve_1():
    assert exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0)))) 1") == 1

def test_curve_2():
    assert exe("(def my-curve (curve (list (list (list 0 0 0) (list 1 0 0) (list 0 0 1)) (list (list 1 0 0) (list 1 0 0))))) (my-curve t)") == 1.0

def test_curve_3():
    assert exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))) :auto-scale nil) 1") == 1

@nose.tools.raises(curve.NumberControlPointsException)
def test_curve_4():
    exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1))))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_curve_5():
    exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (vector 0 1 2)))")

@nose.tools.raises(curve.ControlPointException)
def test_curve_6():
    exe("(curve (list (list (list 0 0 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))))")

@nose.tools.raises(curve.ControlPointException)
def test_curve_7():
    exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0))))")

@nose.tools.raises(curve.ControlPointException)
def test_curve_8():
    exe("(curve (list (list (list 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_curve_9():
    exe("(curve (list (list (list t 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))))")

@nose.tools.raises(TypeError)
def test_curve_10():
    exe("(curve (list (list t (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))))")
    
@nose.tools.raises(curve.TangentException)
def test_curve_11():
    exe("(curve (list (list (list 0 0 0) (list 0 0 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))))")
    
# pulley system.
def test_pulley_system_1():
    assert exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 1) (list 0 0 1) 5.0 1) (list (list -1 0 0) \"tangent\"))) 1") == 1

def test_pulley_system_2():
    assert exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 0) \"point\"))) 1") == 1

@nose.tools.raises(pulleySystem.NumberPulleysException)
def test_pulley_system_3():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50)))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_pulley_system_4():
    exe("(pulley-system (list (vector 1 2 3) (list (list 20 0 0) \"point\")))")

@nose.tools.raises(pulleySystem.DrumException)
def test_pulley_system_5():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1) (list (list 20 0 0) \"point\")))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_pulley_system_6():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) t 1 5.0 1 50) (list (list 20 0 0) \"point\")))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_pulley_system_7():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (vector 0 0 0)))")

@nose.tools.raises(pulleySystem.EndPointException)
def test_pulley_system_8():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 0))))")

@nose.tools.raises(lcadExceptions.WrongTypeException)
def test_pulley_system_9():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 0) t)))")

@nose.tools.raises(pulleySystem.EndPointTypeException)
def test_pulley_system_10():
    exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 0) \"foo\")))")

# spring
def test_spring_1():
    assert exe("(spring 40 10 1 10) 1") == 1

def test_spring_2():
    assert exe("(spring 40 10 1 10 1) 1") == 1

    
