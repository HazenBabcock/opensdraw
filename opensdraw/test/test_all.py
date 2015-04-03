#!/usr/bin/env python
"""
.. module:: test_all
   :synopsis: Nose tests of the lcad language.

.. moduleauthor:: Hazen Babcock

"""

import math
import numbers
import numpy

import opensdraw.lcad_language.interpreter as interpreter
import opensdraw.lcad_language.lexerParser as lexerParser
import opensdraw.lcad_language.lcadTypes as lcadTypes

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

# block
def test_block_1():
    assert exe("(def fn (block (def x 5) (def inc-x () (+ x 1)) inc-x)) (fn)") == 6

# concatenate
def test_concatenate_1():
    assert exe("(concatenate \"as\" 1)") == "as1"

# cond
def test_cond_1():
    assert exe("(def x 2) (cond ((= x 1) 2) ((= x 2) 3) ((= x 3) 4) (t 5))") == 3

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

# for
def test_for_1():
    assert exe("(def x 0) (for (i 10) (set x (+ 1 x))) x") == 10

def test_for_2():
    assert exe("(def x 0) (for (i 1 11) (set x (+ 1 x))) x") == 10

def test_for_3():
    assert exe("(def x 0) (for (i 1 0.1 2) (set x (+ 1 x))) x") == 10

def test_for_4():
    assert exe("(def x 0) (for (i (list 1 2 3)) (set x (+ i x))) x") == 6

# if
def test_if_1():
    assert exe("(if t 1 2)") == 1

def test_if_2():
    assert exe("(if (= 1 2) 1 2)") == 2

def test_if_3():
    assert exe("(if (if (= 1 2) t nil) 1 2)") == 2

def test_if_4():
    assert exe("(if (if (= 1 2) t) 1 2)") == 2

# import
def test_import_1():
    assert exe("(import mod) (mod:fn)") == math.pi

def test_import_2():
    assert exe("(import mod :local) (fn)") ==  math.pi

# lambda
def test_lambda_1():
    assert exe("(def fn (lambda (x) (+ x 1))) (fn 1)") == 2

# len
def test_len_1():
    assert exe("(len (list 1 2 3))") == 3

# list
def test_list_1():
    assert exe("(def x (list 1 2 3)) (aref x 0)") == 1

def test_list_2():
    assert exe("(list 1 2 3)")[1] == 2

# pyimport
def test_pyimport_1():
    assert exe("(pyimport pyimp1) (plus 1 1)") == 2

# print
def test_print_1():
    assert exe("(print \"123\")") == "123"

# set
def test_set_1():
    assert exe("(def x 10) (set x 15)") == 15

def test_set_2():
    assert exe("(def x 10 y 10) (set x 15 y 20)") == 20

def test_set_3():
    assert exe("(def fn () 1) (def x 2) (set x fn) (x)") == 1

# while
def test_while_1():
    assert exe("(def x 0) (while (< x 9) (set x (+ 2 x))) x") == 10


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


## Comparison Operators.

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
    assert isinstance(exe("(matrix (list 0 0 0 0 0 0))"), lcadTypes.LCadMatrix)

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
    assert exe("(transform (matrix (list 1 2 3 1 2 3 1 2 3 1 2 3)) 1)") == 1

def test_transform_3():
    assert exe("(transform (matrix (list 0 0 0 0 0 0)) 1)") == 1

# translate
def test_translate_1():
    assert exe("(translate (list 1 2 3) 1)") == 1

def test_translate_1():
    assert exe("(translate (vector 1 2 3) 1)") == 1

# vector
def test_vector_1():
    assert isinstance(exe("(vector 1 2 3)"), lcadTypes.LCadVector)


## Logical Operators.

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
    assert exe("(* (vector 1 2 3) (vector 1 2 3))")[1] == 4

def test_math_8():
    assert exe("(/ (vector 1 2 3) (vector 1 2 3))")[1] == 1

def test_math_9():
    assert exe("(+ (vector 1 2 3) (vector 1 2 3))")[1] == 4

def test_math_10():
    assert exe("(- (vector 1 2 3) (vector 1 2 3))")[1] == 0

def test_math_11():
    assert exe("(- 1)") == -1

# python math module
def test_py_math_1():
    assert int(round(exe("(cos 0)"))) == 1

def test_py_math_2():
    assert int(round(exe("(cos (/ pi 2))"))) == 0

def test_py_math_3():
    assert int(round(exe("(sin 0)"))) == 0

def test_py_math_4():
    assert int(round(exe("(sin (/ pi 2))"))) == 1


## Miscellaneous Functions.

# belt
def test_belt_1():
    assert exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1))) 1") == 1

def test_belt_2():
    assert exe("(belt (list (list (list 0 0 0) (list 0 0 1) 1.0 1) (list (list 4 0 0) (list 0 0 1) 1.5 1)) :continuous nil) 1") == 1

# chain
def test_chain_1():
    assert exe("(chain (list (list -4 0 1 1) (list 4 0 1 1))) 1") == 1

def test_chain_2():
    assert exe("(chain (list (list -4 0 1 1) (list 4 0 1 1)) :continuous nil) 1") == 1

# curve
def test_curve_1():
    assert exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0)))) 1") == 1

def test_curve_2():
    assert exe("(def my-curve (curve (list (list (list 0 0 0) (list 1 0 0) (list 0 0 1)) (list (list 1 0 0) (list 1 0 0))))) (my-curve t)") == 1.0

def test_curve_3():
    assert exe("(curve (list (list (list 0 0 0) (list 1 1 0) (list 0 0 1)) (list (list 5 0 0) (list 1 0 0))) :auto-scale nil) 1") == 1

# pulley system.
def test_pulley_system_1():
    assert exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 1) (list 0 0 1) 5.0 1) (list (list -1 0 0) \"tangent\"))) 1") == 1

def test_pulley_system_2():
    assert exe("(pulley-system (list (list (list 0 0 0) (list 0 0 1) 5.0 1 5.0 1 50) (list (list 20 0 0) \"point\"))) 1") == 1

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
