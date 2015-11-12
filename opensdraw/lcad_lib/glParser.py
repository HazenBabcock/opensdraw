#!/usr/bin/env python
"""
A parser for outputting OpenGL. This is based in part on this 
example: https://gist.github.com/deepankarsharma/3494203

This works for most parts, but it is not known to be completely
conformant with the LDraw specification defined here:

http://www.ldraw.org/article/218.html

In particular it has at least the following issues:
1. Optional lines are ignored.
2. Culling is disabled as I could not figure out how to get it
   to work properly.

It is not designed to be fast as it is used mostly for static
rendering.

Hazen 11/15

"""

import numpy

from OpenGL import arrays, GL

import datFileParser


# Variables 

# Vertex shader
vertex = """
#version 330
in vec4 vin_position;
in vec4 vin_color;
out vec4 vout_color;
uniform mat4 MVP;

void main(void)
{
    vout_color = vin_color;
    gl_Position = MVP * vin_position;
}
"""

# Fragment shader
fragment = """
#version 330
in vec4 vout_color;
out vec4 fout_color;

void main(void)
{
    fout_color = vout_color;
}
"""

class GLParserException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

        
class GLParser(datFileParser.Parser):
    """
    Parser for creating GL objects. This is used to parse a DAT file and create
    the necessary GL to be able to render the DAT file. This is also a GL object
    so you can draw it in a GL context by calling the render() function. When
    you are finished with it you need to call freeGL() to free the memory associated
    with this object.
    """

    gl_shader = None

    def __init__(self, face_color, edge_color, matrix = None, invert_winding = False):
        datFileParser.Parser.__init__(self, None, None)

        self.cw_winding = False
        self.children = []
        self.depth = 0
        self.edge_color = edge_color
        self.face_color = face_color
        self.invert_next = False
        self.invert_winding = invert_winding
        self.lines_only = False  # This is mostly for debugging.
        self.matrix = matrix
        self.vao_lines = GLVao(GL.GL_LINES)
        self.vao_triangles = GLVao(GL.GL_TRIANGLES)

        if GLParser.gl_shader is None:
            GLParser.gl_shader = GLShader(vertex, fragment)
            
        if self.matrix is None:
            self.matrix = numpy.identity(4)

    def addLine(self, p1, p2):
        self.vao_lines.addVertex(p1)
        self.vao_lines.addColor(self.edge_color)
        self.vao_lines.addVertex(p2)
        self.vao_lines.addColor(self.edge_color)
        
    def addTriangle(self, p1, p2, p3):
        if self.lines_only:
            self.addLine(p1, p2)
            self.addLine(p2, p3)
            self.addLine(p3, p1)            
        else:
            self.vao_triangles.addVertex(p1)
            self.vao_triangles.addColor(self.face_color)
            self.vao_triangles.addVertex(p2)
            self.vao_triangles.addColor(self.face_color)            
            self.vao_triangles.addVertex(p3)
            self.vao_triangles.addColor(self.face_color)

    def command(self, parsed_line):
        if (len(parsed_line) > 1):

            # FIXME:
            #  This doesn't work properly in that if you enable face culling then
            #  things will look a bit strange.
            #
            # Handle winding commands.
            if (parsed_line[1] == "BFC"):
                if (parsed_line[2] == "INVERTNEXT"):
                    self.invert_next = True
                elif (parsed_line[2] == "CERTIFY"):
                    if (len(parsed_line) == 3):
                        self.cw_winding = False
                    else:
                        if (parsed_line[3] == "CCW"):
                            self.cw_winding = False
                        else:
                            self.cw_winding = True
                if self.invert_winding:
                    self.cw_winding = not self.cw_winding

                #print "  ", self.depth, parsed_line, self.cw_winding

    def endFile(self):
        self.vao_lines.finalize(GLParser.gl_shader)
        self.vao_triangles.finalize(GLParser.gl_shader)
    
    def freeGL(self):
        if (self.vao_triangles.v_size > 0):
            self.vao_triangles.freeBuffers()
        if (self.vao_lines.v_size > 0):
            self.vao_lines.freeBuffers()

        for child in self.children:
            child.freeGL()

    def line(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        self.addLine(p1, p2)

    def newFile(self, parsed_line):

        # Parse transformation matrix.
        [x, y, z, a, b, c, d, e, f, g, h, i] = map(float, parsed_line[2:14])
        matrix = numpy.array([[  a,   b,   c,   x], 
                              [  d,   e,   f,   y], 
                              [  g,   h,   i,   z], 
                              [0.0, 0.0, 0.0, 1.0]])
        matrix = numpy.dot(self.matrix, matrix)

        # Figure out windings.
        if self.invert_next:
            invert_winding = not self.invert_winding
        else:
            invert_winding = self.invert_winding

        child = GLParser(self.face_color,
                         self.edge_color,
                         matrix = matrix,
                         invert_winding = invert_winding)
        self.invert_next = False
        self.children.append(child)
        return child

    def optionalLine(self, parsed_line):
        pass

    def parsePoint(self, point):
        point.append("1.0")
        pi = numpy.array(map(float, point))
        pf = numpy.dot(self.matrix, pi)
        return pf.tolist()[:-1] + [1.0]

    def quadrilateral(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])
        p4 = self.parsePoint(parsed_line[11:14])

        if self.lines_only:
            self.addLine(p1, p2)
            self.addLine(p2, p3)
            self.addLine(p3, p4)
            self.addLine(p4, p1)

        else:
            if self.cw_winding:
                self.addTriangle(p1,p2,p3)
                self.addTriangle(p1,p3,p4)
            else:
                self.addTriangle(p1,p3,p2)
                self.addTriangle(p1,p4,p3)

    def render(self, mvp):

        # Draw object.
        GL.glUseProgram(GLParser.gl_shader.program_id)

        matrix_id = GLParser.gl_shader.uniformLocation('MVP')

        GL.glUniformMatrix4fv(matrix_id, 1, GL.GL_FALSE, mvp)

        if not self.lines_only:
            if (self.vao_triangles.v_size > 0):
                GL.glBindVertexArray(self.vao_triangles.gl_id)
                GL.glDrawArrays(self.vao_triangles.gl_type, 0, self.vao_triangles.v_size)

        if (self.vao_lines.v_size > 0):
            GL.glBindVertexArray(self.vao_lines.gl_id)
            GL.glDrawArrays(self.vao_lines.gl_type, 0, self.vao_lines.v_size)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        # Draw children.
        for child in self.children:
            child.render(mvp)
                        
    def startFile(self, depth):
        self.depth = depth

    def triangle(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])

        if self.cw_winding:
            self.addTriangle(p1,p2,p3)
        else:
            self.addTriangle(p1,p3,p2)


class GLShader(object):

    def __init__(self, vertex, fragment):
        self.program_id = GL.glCreateProgram()
        vs_id = self.add_shader(vertex, GL.GL_VERTEX_SHADER)
        frag_id = self.add_shader(fragment, GL.GL_FRAGMENT_SHADER)

        GL.glAttachShader(self.program_id, vs_id)
        GL.glAttachShader(self.program_id, frag_id)
        GL.glLinkProgram(self.program_id)

        if (GL.glGetProgramiv(self.program_id, GL.GL_LINK_STATUS) != GL.GL_TRUE):
            info = GL.glGetProgramInfoLog(self.program_id)
            GL.glDeleteProgram(self.program_id)
            GL.glDeleteShader(vs_id)
            GL.glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))
        GL.glDeleteShader(vs_id)
        GL.glDeleteShader(frag_id)

    def add_shader(self, source, shader_type):
        try:
            shader_id = GL.glCreateShader(shader_type)
            GL.glShaderSource(shader_id, source)
            GL.glCompileShader(shader_id)
            if (GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS) != GL.GL_TRUE):
                info = GL.glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            GL.glDeleteShader(shader_id)
            raise

    def uniformLocation(self, name):
        return GL.glGetUniformLocation(self.program_id, name)

    def attributeLocation(self, name):
        return GL.glGetAttribLocation(self.program_id, name)


class GLVao(object):

    def __init__(self, gl_type, color = None):

        self.color = color
        self.gl_type = gl_type

        self.c_size = 0
        self.gl_id = 0
        self.vertices = []
        self.colors = []
        self.vbo_id = 0
        self.v_size = 0

    def addColor(self, color):
        self.colors.extend(color)
        self.c_size += 4
        
    def addVertex(self, vertex):
        self.vertices.extend(vertex)
        self.v_size += 4

    def finalize(self, gl_shader):
        if (self.v_size == 0):
            return

        if (self.c_size != self.v_size):
            raise GLParserException("Number of colors vertices does not match number of position vertices")

        color_data = numpy.array(self.colors, dtype = numpy.float32)
        vertex_data = numpy.array(self.vertices, dtype = numpy.float32)
        
        self.gl_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.gl_id)

        # Create buffers.
        self.vbo_id = GL.glGenBuffers(2)

        # Fill first buffer with the vertices.
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo_id[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        arrays.ArrayDatatype.arrayByteCount(vertex_data), 
                        vertex_data, 
                        GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(gl_shader.attributeLocation('vin_position'), 
                                 4,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)
        GL.glEnableVertexAttribArray(0)

        # Fill second buffer with the colors.
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo_id[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        arrays.ArrayDatatype.arrayByteCount(color_data), 
                        color_data,
                        GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(gl_shader.attributeLocation('vin_color'), 
                                 4,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)
        GL.glEnableVertexAttribArray(1)
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def freeBuffers(self):
        GL.glDeleteBuffers(2, self.vbo_id)
        GL.glDeleteVertexArrays(1, [self.gl_id])
        self.v_size = 0

    def getColor(self):
        return self.color


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
