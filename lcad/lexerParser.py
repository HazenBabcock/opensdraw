#!/usr/bin/env python
#
## @file
#
# Lexer, Parser and abstract syntax tree model for lcad.
#
# Hazen 07/14
#


# Lexer.
from rply import LexerGenerator

lg = LexerGenerator()

lg.add('LPAREN', r'\(')
lg.add('RPAREN', r'\)')
lg.add('STRING', r'(".*?"|\'.*?\')')
lg.add('IDENTIFIER', r'[^()\[\]{}\'"\s;]+')

lg.ignore(r';.*(?=\r|\n|$)')
lg.ignore(r'\s+')

lexer = lg.build()


# Model.
class LCadObject(object):
    pass

class LCadExpression(LCadObject):
    def __init__(self, expression):
        self.value = expression

class LCadFloat(LCadObject):
    def __init__(self, value):
        self.value = float(value)

class LCadInteger(LCadObject):
    def __init__(self, value):
        self.value = int(value)

class LCadString(LCadObject):
    def __init__(self, value):
        self.value = str(value)

class LCadSymbol(LCadObject):
    def __init__(self, value):
        self.value = str(value)


# Parser.
from rply import ParserGenerator

pg = ParserGenerator(
    [rule.name for rule in lexer.rules],
    cache_id="lcad_parser"
)

@pg.production('main : list')
def main(p):
    return p[0]

@pg.production('list : term list')
def list(p):
    return [p[0]] + p[1]

@pg.production('list : term')
def single_list(p):
    return [p[0]]

@pg.production('term : string')
@pg.production('term : identifier')
@pg.production('term : parens')
def term(p):
    return p[0]

@pg.production("string : STRING")
def string(p):
    return LCadString(p[0].getstr())

@pg.production("identifier : IDENTIFIER")
def identifier(p):
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
def parens(p):
    return LCadExpression(p[1])

@pg.error
def error_handler(token):
    raise ValueError("Ran into a {!s} where it was't expected at row {!s} column {!s}".format(token.gettokentype(), 
                                                                                              token.source_pos.lineno, 
                                                                                              token.source_pos.colno))

parser = pg.build()


if (__name__ == '__main__'):
    import sys

    if (len(sys.argv) != 2):
        print "usage: <file to parse>"
        exit()

    with open(sys.argv[1]) as fp:
        print parser.parse(lexer.lex(fp.read()))


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
