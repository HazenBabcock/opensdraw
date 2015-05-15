#!/usr/bin/env python
#
# Lexer, Parser and abstract syntax tree model for lcad. Much of
# inspiration for this comes from the lexer / parser in the hy 
# project:
#
# https://github.com/hylang/hy/tree/master/hy/lex
#
# Hazen 07/14
#

from functools import wraps

# Lexer.
from rply import LexerGenerator

lg = LexerGenerator()

lg.add('LPAREN', r'\(')
lg.add('RPAREN', r'\)')
#lg.add('STRING', r'(".*?"|\'.*?\')')
lg.add('STRING', r'("[^"]*"|\'[^\']*\')')
lg.add('IDENTIFIER', r'[^()\[\]{}\'"\s;]+')

lg.ignore(r';.*(?=\r|\n|$)')
lg.ignore(r'\s+')

lexer = lg.build()


# Model.
class LCadObject(object):
    pass

class LCadConstant(LCadObject):
    pass

class LCadExpression(LCadObject):
    def __init__(self, expression):
        self.initialized = False
        self.lenv = None
        self.simple_type_name = "Expression"
        self.value = expression

class LCadFloat(LCadConstant):
    def __init__(self, value):
        self.simple_type_name = "Float"
        self.value = float(value)

class LCadInteger(LCadConstant):
    def __init__(self, value):
        self.simple_type_name = "Integer"
        self.value = int(value)

class LCadString(LCadConstant):
    def __init__(self, value):
        self.simple_type_name = "String"
        self.value = str(value[1:-1])

class LCadSymbol(LCadObject):
    def __init__(self, value):
        self.lenv = None
        self.simple_type_name = "Symbol"
        self.value = str(value)


# Parser.
from rply import ParserGenerator

def set_boundaries(fun):
    @wraps(fun)
    def wrapped(state, p):
        start = p[0].source_pos
        end = p[-1].source_pos
        ret = fun(state, p)
        ret.filename = state.filename
        ret.start_line = start.lineno
        ret.start_column = start.colno
        if start is not end:
            ret.end_line = end.lineno
            ret.end_column = end.colno
        else:
            ret.end_line = start.lineno
            ret.end_column = start.colno + len(p[0].value)
        return ret
    return wrapped

pg = ParserGenerator(
    [rule.name for rule in lexer.rules],
    cache_id="lcad_parser"
)

@pg.production('main : list')
def main(state, p):
    return p[0]

@pg.production('list : term list')
def list(state, p):
    return [p[0]] + p[1]

@pg.production('list : term')
def single_list(state, p):
    return [p[0]]

@pg.production('term : string')
@pg.production('term : identifier')
@pg.production('term : parens')
def term(state, p):
    return p[0]

@pg.production("string : STRING")
@set_boundaries
def string(state, p):
    return LCadString(p[0].getstr())

@pg.production("identifier : IDENTIFIER")
@set_boundaries
def identifier(state, p):
    text = p[0].getstr()

    try:
        return LCadInteger(text)
    except ValueError:
        pass

    try:
        return LCadFloat(text)
    except ValueError:
        pass

    return LCadSymbol(text)

@pg.production('parens : LPAREN list RPAREN')
@set_boundaries
def parens(state, p):
    return LCadExpression(p[1])

@pg.production('parens : LPAREN RPAREN')
@set_boundaries
def empty_parens(state, p):
    return LCadExpression([])

@pg.error
def error_handler(state, token):
    if (token.gettokentype() == '$end'):
        raise Exception("Unexpected EOF. Empty file? Unbalanced Parenthesis?")
    raise ValueError("Ran into a {!s} where it was't expected at row {!s} column {!s}".format(token.gettokentype(), 
                                                                                              token.source_pos.lineno, 
                                                                                              token.source_pos.colno))

parser = pg.build()

class ParserState(object):
    def __init__(self, filename):
        self.filename = filename

def parse(string, filename = "na"):
    return parser.parse(lexer.lex(string), 
                        state = ParserState(filename))

# For testing purposes.
if (__name__ == '__main__'):
    import sys

    if (len(sys.argv) != 2):
        print "usage: <file to parse>"
        exit()

    with open(sys.argv[1]) as fp:
        print parse(fp.read(), sys.argv[1])


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
