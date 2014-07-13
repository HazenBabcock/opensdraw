#!/usr/bin/env python
#
## @file
#
# A parser for outputting OpenGL. This is based in part on this 
# example: https://gist.github.com/deepankarsharma/3494203
#
# Hazen 07/14
#

import numpy

from OpenGL import arrays, GL

import lcad_lib.datFileParser as datFileParser


# Variables 

# Vertex Shader
vertex = """
#version 330
in vec3 vin_position;
in vec3 vin_color;
out vec3 vout_color;
uniform mat4 MVP;

void main(void)
{
    vout_color = vin_color;
    vec4 v = vec4(vin_position, 1.0);
    gl_Position = MVP * v;
}
"""

# Fragment Shader
fragment = """
#version 330
in vec3 vout_color;
out vec4 fout_color;

void main(void)
{
    fout_color = vec4(vout_color, 1.0);
}
"""


# Classes.

## GLParser
#
# Parser for creating GL objects. This is used to parse a DAT file and create
# the necessary GL to be able to render the DAT file.
#
class GLParser(datFileParser.Parser):

    ## __init__
    #
    # @param main_color The main color.
    # @param edge_color The edge color.
    # @param matrix (Optional) A 4x4 numpy matrix to use as the transformation matrix for this file. If this is None then the identity matrix is used.
    # @param shader (Optional) The GLShader object to use for this file. If None a GLShader object will be created.
    # @param inverted_w (Optional) Specify if the winding direction should be inverted. Default is False.
    #
    def __init__(self, main_color, edge_color, matrix = None, gl_shader = None, inverted_w = False):
        datFileParser.Parser.__init__(self, main_color, edge_color)

        self.cw_winding = False
        self.children = []
        self.depth = 0
        self.gl_shader = gl_shader
        self.inverted_w = inverted_w
        self.matrix = matrix
        self.vao_lines = GLVao(GL.GL_LINES, edge_color)
        self.vao_triangles = GLVao(GL.GL_TRIANGLES, main_color)

        if gl_shader is None:
            self.gl_shader = GLShader(vertex, fragment)

        if self.matrix is None:
            self.matrix = numpy.identity(4)

    ## addTriangle
    #
    # Add a triangle, winding is always counter-clockwise.
    #
    # @param p1 1st vertex.
    # @param p2 2nd vertex.
    # @param p3 3rd vertex.
    #
    def addTriangle(self, p1, p2, p3):
        self.vao_triangles.addVertex(p1)
        self.vao_triangles.addVertex(p2)
        self.vao_triangles.addVertex(p3)

    ## command
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def command(self, parsed_line):
        return

        if (len(parsed_line) > 1):

            # Handle winding commands.
            if (parsed_line[1] == "BFC"):
                if (parsed_line[2] == "INVERTNEXT"):
                    self.inverted_w = not self.inverted_w
                elif (parsed_line[2] == "CERTIFY"):
                    if (len(parsed_line) == 3):
                        self.cw_winding = False
                    else:
                        if (parsed_line[3] == "CCW"):
                            self.cw_winding = False
                        else:
                            self.cw_winding = True
                if self.inverted_w:
                    self.cw_winding = not self.cw_winding

                print parsed_line, self.cw_winding

    ## endFile
    #
    def endFile(self):
        self.vao_lines.finalize(self.gl_shader)
        self.vao_triangles.finalize(self.gl_shader)
    
    ## getInvertedW
    #
    # @return The current value of the inverted_w property.
    #
    def getInvertedW(self):
        return self.inverted_w

    ## line
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def line(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        self.vao_lines.addVertex(p1)
        self.vao_lines.addVertex(p2)
    
    ## newFile
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    # @return A Parser object.
    #
    def newFile(self, parsed_line):
        #print "newFile", self.depth, parsed_line[-1]

        # Parse transformation matrix.
        [x, y, z, a, b, c, d, e, f, g, h, i] = map(float, parsed_line[2:14])
        matrix = numpy.array([[  a,   b,   c,   x], 
                              [  d,   e,   f,   y], 
                              [  g,   h,   i,   z], 
                              [0.0, 0.0, 0.0, 1.0]])

        child = GLParser(self.main_color, 
                         self.edge_color, 
                         matrix,
                         self.gl_shader,
                         self.getInvertedW())
        self.children.append(child)
        return child

    ## optionalLine
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def optionalLine(self, parsed_line):
        pass
        #self.line(parsed_line)

    ## parsePoint
    #
    # Parses point text, applies the current transform matrix and returns the
    # transformed point.
    #
    # @param point A 3 element array containing the points text [x, y, z].
    #
    # @returns A 3 element array of floats.
    #
    def parsePoint(self, point):
        point.append("1.0")
        pi = numpy.array(map(float, point))
        pf = numpy.dot(self.matrix, pi)
        return pf.tolist()[:-1]

    ## quadrilateral
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def quadrilateral(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])
        p4 = self.parsePoint(parsed_line[11:14])

        if False:
            self.vao_lines.addVertex(p1)
            self.vao_lines.addVertex(p2)
            self.vao_lines.addVertex(p2)
            self.vao_lines.addVertex(p3)
            self.vao_lines.addVertex(p3)
            self.vao_lines.addVertex(p4)
            self.vao_lines.addVertex(p4)
            self.vao_lines.addVertex(p1)

        if self.cw_winding:
            self.addTriangle(p1,p2,p3)
            self.addTriangle(p1,p3,p4)
        else:
            self.addTriangle(p1,p3,p2)
            self.addTriangle(p1,p4,p3)

        #self.vao_lines.addVertex(p1)

    ## render
    #
    # Draw the object and all its child objects.
    #
    # @param mvp The model - view - projection matrix or None.
    #
    def render(self, mvp):

        # Draw object.
        GL.glUseProgram(self.gl_shader.program_id)

        matrix_id = self.gl_shader.uniform_location('MVP')
        GL.glUniformMatrix4fv(matrix_id, 1, GL.GL_FALSE, mvp)

        if (self.vao_triangles.size > 0):
            GL.glBindVertexArray(self.vao_triangles.gl_id)
            GL.glDrawArrays(self.vao_triangles.gl_type, 0, self.vao_triangles.size)

        if (self.vao_lines.size > 0):
            GL.glBindVertexArray(self.vao_lines.gl_id)
            GL.glDrawArrays(self.vao_lines.gl_type, 0, self.vao_lines.size)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        # Draw children.
        for child in self.children:
            child.render(mvp)
                        
    ## startFile
    #
    # @param depth The current recursion depth.
    #
    def startFile(self, depth):
        self.depth = depth

    ## triangle
    #
    # @param parsed_line A list containing the contents of one line of a parsed file.
    #
    def triangle(self, parsed_line):
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])

        if self.cw_winding:
            self.addTriangle(p1,p2,p3)
        else:
            self.addTriangle(p1,p3,p2)


## GLShader
#
# Helper class for using GLSL shader programs.
#
class GLShader(object):

    ## __init__
    #
    # @param vertex A string containing the shader source code for the vertex shader.
    # @param fragment A string containing the shader source code for the fragment shader.
    #
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

    ## add_shader
    #
    # Helper function for compiling a GLSL shader.
    #
    # @param source String containing shader source code.
    # @param shader_type A OpenGL shader type.
    #
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

    ## uniform_location
    #
    # Helper function to get location of an OpenGL uniform variable.
    #
    # @param name Name of the variable for which location is to be returned.
    #
    # @return Integer describing location.
    #
    def uniform_location(self, name):
        return GL.glGetUniformLocation(self.program_id, name)

    ## attribute_location
    #
    # Helper function to get location of an OpenGL attribute variable.
    #
    # @param name Name of the variable for which location is to be returned.
    #
    # @return Integer describing location.
    #
    def attribute_location(self, name):
        return GL.glGetAttribLocation(self.program_id, name)


## GLVao
#
# Encapsulates a OpenGL Vertex Array Object.
#
class GLVao(object):

    ## __init__
    #
    # @param gl_type The OpenGL object type.
    # @param color The color [r, g, b] to use for this VAO.
    #
    def __init__(self, gl_type, color):

        self.color = color
        self.gl_type = gl_type

        self.colors = []
        self.gl_id = 0
        self.size = 0
        self.vertices = []

        #self.n_components = 0
        #if (gl_type == GL.GL_LINES):
        #    self.n_components = 2
        #elif (gl_type ==GL.GL_TRIANGLES):
        #    self.n_components = 3
        #else:
        #    print "Unrecognized GL type:", gl_type

    ## addVertex.
    #
    # @param vertex [x, y, z] location of the vertex.
    #
    def addVertex(self, vertex):
        self.vertices.extend(vertex)
        self.colors.extend(self.color)
        self.size += 3

    ## finalize
    #
    # This is called once we have all the vertices to create the necessary OpenGL objects.
    #
    # @param gl_shader A GLShader object.
    #
    def finalize(self, gl_shader):
        if (self.size == 0):
            return

        #print self.vertices, self.n_components

        vertex_data = numpy.array(self.vertices, dtype = numpy.float32)
        color_data = numpy.array(self.colors, dtype = numpy.float32)
        
        self.gl_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.gl_id)
        
        vbo_id = GL.glGenBuffers(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        arrays.ArrayDatatype.arrayByteCount(vertex_data), 
                        vertex_data, 
                        GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(gl_shader.attribute_location('vin_position'), 
                                 3,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)
        GL.glEnableVertexAttribArray(0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        arrays.ArrayDatatype.arrayByteCount(color_data),
                        color_data,
                        GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(gl_shader.attribute_location('vin_color'),
                                 3,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

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
