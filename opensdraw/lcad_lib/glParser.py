#!/usr/bin/env python
"""
A parser for outputting OpenGL. This is based in part on these web-pages:

1. https://gist.github.com/deepankarsharma/3494203
2. http://www.tomdalling.com/blog/modern-opengl/06-diffuse-point-lighting/

This works for most parts, but it is not known to be completely
conformant with the LDraw specification defined here:

http://www.ldraw.org/article/218.html

In particular it has at least the following issues:
1. Optional lines are ignored.
2. Culling is disabled as I could not figure out how to get it
   to work properly.

Also it is not that fast, but since it is mostly used for static
images this is not too much of an issue.

Hazen 11/15
"""

# Notes
#
# 1. Sort out winding problems using colors
#

import numpy

from OpenGL import arrays, GL

import colorsParser
import datFileParser


#
# Shader for lines.
#

# Line vertex shader
line_vertex = """
#version 150

in vec4 vert;
in vec4 vert_color;

out vec4 frag_color;

uniform mat4 mvp;

void main(void)
{
    frag_color = vert_color;
    gl_Position = mvp * vert;
}
"""

# Line fragment shader
line_fragment = """
#version 150

in vec4 frag_color;

out vec4 final_color;

void main(void)
{
    final_color = frag_color;
}
"""

#
# Shader for triangles.
#

# Triangle vertex shader
triangle_vertex = """
#version 150

in vec4 vert;
in vec4 vert_color;
in vec4 vert_normal;
 
out vec4 frag_color;
out vec4 frag_normal;
out vec4 frag_vert;
 
uniform mat4 mvp;
 
void main(void)
{
    frag_color = vert_color;
    frag_normal = vert_normal;
    frag_vert = vert;

    gl_Position = mvp * vert;
}
"""

# Triangle fragment shader
triangle_fragment = """
#version 150

uniform vec3 camera_position;
uniform vec3 light_position;
uniform mat4 mvp;

in vec4 frag_color;
in vec4 frag_normal;
in vec4 frag_vert;

out vec4 final_color;

void main(void)
{
    vec3 light_color = vec3(frag_color);
    vec3 specular_color = vec3(frag_color);

    vec3 normal = normalize(mat3(mvp) * vec3(frag_normal));
    vec3 surface_pos = vec3(mvp * frag_vert);
    vec3 surface_to_light = normalize(light_position - surface_pos);
    vec3 surface_to_camera = normalize(camera_position - surface_pos);
    
    // ambient
    float ambient_coefficient = 0.2;
    vec3 ambient = 0.05 * frag_color.rgb * light_color;

    // diffuse
    float diffuse_coefficient = max(0.0, dot(normal, surface_to_light));
    vec3 diffuse = diffuse_coefficient * frag_color.rgb * light_color;

    // specular
    float specular_coefficient = 0.0;
    if (diffuse_coefficient > 0.0){
        specular_coefficient = pow(max(0.0, dot(surface_to_camera, reflect(-surface_to_light, normal))), 2);
    }
    vec3 specular = specular_coefficient * specular_color * light_color;

    // linear color
    vec3 linear_color = min(ambient_coefficient + diffuse_coefficient + specular_coefficient, 1.0) * frag_color.rgb;
    //linear_color = min(linear_color, vec3(1.0, 1.0, 1.0));

    final_color = vec4(linear_color, frag_color.a);
}
"""

#
# Shader for checking that surface normals are correct for
# the purpose of identifying counter-clockwise vs clockwise
# winding errors.
#

# test (triangle) vertex shader
test_vertex = """
#version 150

in vec4 vert;
in vec4 vert_normal;

out vec4 frag_normal;
 
uniform mat4 mvp;
 
void main(void)
{
    frag_normal = vert_normal;

    gl_Position = mvp * vert;
}
"""

# test (triangle) fragment shader
test_fragment = """
#version 150

uniform mat4 mvp;

in vec4 frag_normal;

out vec4 final_color;

void main(void)
{
    mat3 normal_matrix = mat3(mvp);
    vec3 normal = normalize(normal_matrix * vec3(frag_normal));

    float ndot = dot(normal, vec3(0.0, 0.0, 1.0));
    if (ndot >= 0){
        final_color = vec4(0.0, 1.0, 0.0, 1.0);
    }
    else{
        final_color = vec4(1.0, 0.0, 0.0, 1.0);
    }
}
"""

all_colors = colorsParser.loadColors()

def compileShaders():
    GLVaoLine()
    GLVaoTest()
    GLVaoTriangle()
    

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
        self.vao_lines = GLVaoLine()
        self.vao_triangles = GLVaoTriangle()
        #self.vao_triangles = GLVaoTest()

        if self.matrix is None:
            self.matrix = numpy.identity(4)

    def addLine(self, p1, p2):
        self.vao_lines.addVertex(p1)
        self.vao_lines.addColor(self.edge_color)
        
        self.vao_lines.addVertex(p2)
        self.vao_lines.addColor(self.edge_color)

    def addTriangle(self, p1, p2, p3):
        if not self.lines_only:
            normal = numpy.cross(numpy.array(p2[:-1]) - numpy.array(p1[:-1]),
                                 numpy.array(p3[:-1]) - numpy.array(p1[:-1]))
            normal = normal.tolist() + [1.0]

            self.vao_triangles.addVertex(p1)
            self.vao_triangles.addColor(self.face_color)
            self.vao_triangles.addNormal(normal)
            
            self.vao_triangles.addVertex(p2)
            self.vao_triangles.addColor(self.face_color)
            self.vao_triangles.addNormal(normal)
            
            self.vao_triangles.addVertex(p3)
            self.vao_triangles.addColor(self.face_color)
            self.vao_triangles.addNormal(normal)

    def checkColor(self, color):
        if (color != "16") and (color != "24"):
            print "Unexpected color", color

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
        self.vao_lines.finalize()
        self.vao_triangles.finalize()
    
    def freeGL(self):
        if (self.vao_triangles.v_size > 0):
            self.vao_triangles.freeBuffers()
        if (self.vao_lines.v_size > 0):
            self.vao_lines.freeBuffers()

        for child in self.children:
            child.freeGL()

    def line(self, parsed_line):
        self.checkColor(parsed_line[1])
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        self.addLine(p1, p2)

    def newFile(self, parsed_line):

        # Parse color
        if (parsed_line[1] == "16"):
            face_color = self.face_color
            edge_color = self.edge_color
        else:
            color = all_colors[parsed_line[1]]
            face_color = color.getFaceColor()
            edge_color = color.getEdgeColor()
            
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

        child = GLParser(face_color,
                         edge_color,
                         matrix = matrix,
                         invert_winding = invert_winding)
        self.invert_next = False
        self.children.append(child)
        return child

    def optionalLine(self, parsed_line):
        self.checkColor(parsed_line[1])

    def parsePoint(self, point):
        point.append("1.0")
        pi = numpy.array(map(float, point))
        pf = numpy.dot(self.matrix, pi)
        return pf.tolist()[:-1] + [1.0]

    def quadrilateral(self, parsed_line):
        self.checkColor(parsed_line[1])

        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])
        p4 = self.parsePoint(parsed_line[11:14])

        if 0:
            self.addLine(p1, p2)
            self.addLine(p2, p3)
            self.addLine(p3, p4)
            self.addLine(p4, p1)

        if not self.lines_only:
            if self.cw_winding:
                self.addTriangle(p1,p2,p3)
                self.addTriangle(p1,p3,p4)
            else:
                self.addTriangle(p1,p3,p2)
                self.addTriangle(p1,p4,p3)

    def render(self, mvp):

        self.vao_triangles.render(mvp)
        self.vao_lines.render(mvp)

        # Draw children.
        for child in self.children:
            child.render(mvp)
                        
    def startFile(self, depth):
        self.depth = depth

    def triangle(self, parsed_line):
        self.checkColor(parsed_line[1])
        p1 = self.parsePoint(parsed_line[2:5])
        p2 = self.parsePoint(parsed_line[5:8])
        p3 = self.parsePoint(parsed_line[8:11])

        if 0:
            self.addLine(p1, p2)
            self.addLine(p2, p3)
            self.addLine(p3, p1)

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


class GLVaoLine(object):
    """
    GL Vertex array object lines.
    """

    gl_shader = None
    
    def __init__(self):

        self.gl_id = 0
        self.gl_type = GL.GL_LINES
        self.vbo_id = 0
        
        self.c_size = 0
        self.v_size = 0
        
        self.colors = []
        self.vertices = []

        if GLVaoLine.gl_shader is None:
            GLVaoLine.gl_shader = GLShader(line_vertex, line_fragment)

    def addColor(self, color):
        self.colors.extend(color)
        self.c_size += 4

    def addVertex(self, vertex):
        self.vertices.extend(vertex)
        self.v_size += 4

    def fillBuffer(self, shader, buffer_id, buffer_data, buffer_name):
        if (shader.attributeLocation(buffer_name) < 0):
            print buffer_name, "has does not exist?"
            return
        
        np_buffer_data = numpy.array(buffer_data, dtype = numpy.float32)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo_id[buffer_id])
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        arrays.ArrayDatatype.arrayByteCount(np_buffer_data),
                        np_buffer_data, 
                        GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(shader.attributeLocation(buffer_name), 
                                 4,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)
        GL.glEnableVertexAttribArray(buffer_id)

    def finalize(self):
        if (self.v_size == 0):
            return

        if (self.c_size != self.v_size):
            raise GLParserException("Number of colors vertices does not match number of position vertices")

        self.gl_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.gl_id)

        # Create and fill buffers.
        self.vbo_id = GL.glGenBuffers(2)

        self.fillBuffer(GLVaoLine.gl_shader, 0, self.vertices, 'vert')
        self.fillBuffer(GLVaoLine.gl_shader, 1, self.colors, 'vert_color')
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def freeBuffers(self):
        GL.glDeleteBuffers(len(self.vbo_id), self.vbo_id)
        GL.glDeleteVertexArrays(1, [self.gl_id])
        self.v_size = 0

    def render(self, mvp):
        GL.glUseProgram(GLVaoLine.gl_shader.program_id)

        mvp_id = GLVaoLine.gl_shader.uniformLocation('mvp')
        GL.glUniformMatrix4fv(mvp_id, 1, GL.GL_FALSE, mvp)

        GL.glBindVertexArray(self.gl_id)
        GL.glDrawArrays(self.gl_type, 0, self.v_size)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)        
        

class GLVaoTest(GLVaoLine):
    """
    GL Vertex array object for testing surface normals.
    """

    gl_shader = None
    
    def __init__(self):
        GLVaoLine.__init__(self)

        self.gl_type = GL.GL_TRIANGLES
        self.n_size = 0
        self.normals = []

        if GLVaoTriangle.gl_shader is None:
            GLVaoTriangle.gl_shader = GLShader(test_vertex, test_fragment)

    def addNormal(self, normal):
        self.normals.extend(normal)
        self.n_size += 4
        
    def finalize(self):
        if (self.v_size == 0):
            return

        if (self.c_size != self.v_size):
            raise GLParserException("Number of colors vertices does not match number of position vertices")        
        
        if (self.c_size != self.n_size):
            raise GLParserException("Number of normal vertices does not match number of position vertices")
        
        self.gl_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.gl_id)

        # Create and fill buffers.
        self.vbo_id = GL.glGenBuffers(2)

        self.fillBuffer(GLVaoTriangle.gl_shader, 0, self.vertices, 'vert')
        self.fillBuffer(GLVaoTriangle.gl_shader, 1, self.colors, 'vert_normal')
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def render(self, mvp):
        GL.glUseProgram(GLVaoTriangle.gl_shader.program_id)

        mvp_id = GLVaoTriangle.gl_shader.uniformLocation('mvp')
        GL.glUniformMatrix4fv(mvp_id, 1, GL.GL_FALSE, mvp)

        GL.glBindVertexArray(self.gl_id)
        GL.glDrawArrays(self.gl_type, 0, self.v_size)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        
class GLVaoTriangle(GLVaoLine):
    """
    GL Vertex array object triangles.
    """

    gl_shader = None
    
    def __init__(self):
        GLVaoLine.__init__(self)

        self.gl_type = GL.GL_TRIANGLES
        self.n_size = 0
        self.normals = []

        if GLVaoTriangle.gl_shader is None:
            GLVaoTriangle.gl_shader = GLShader(triangle_vertex, triangle_fragment)

    def addNormal(self, normal):
        self.normals.extend(normal)
        self.n_size += 4
        
    def finalize(self):
        if (self.v_size == 0):
            return

        if (self.c_size != self.v_size):
            raise GLParserException("Number of colors vertices does not match number of position vertices")        
        
        if (self.c_size != self.n_size):
            raise GLParserException("Number of normal vertices does not match number of position vertices")
        
        self.gl_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.gl_id)

        # Create and fill buffers.
        self.vbo_id = GL.glGenBuffers(3)

        self.fillBuffer(GLVaoTriangle.gl_shader, 0, self.vertices, 'vert')
        self.fillBuffer(GLVaoTriangle.gl_shader, 1, self.colors, 'vert_color')
        self.fillBuffer(GLVaoTriangle.gl_shader, 2, self.colors, 'vert_normal')
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def render(self, mvp):
        GL.glUseProgram(GLVaoTriangle.gl_shader.program_id)

        mvp_id = GLVaoTriangle.gl_shader.uniformLocation('mvp')
        GL.glUniformMatrix4fv(mvp_id, 1, GL.GL_FALSE, mvp)

        camera_position_id = GLVaoTriangle.gl_shader.uniformLocation('camera_position')
        GL.glUniform3fv(camera_position_id, 1, numpy.array([0.0, 0.0, 0.5], dtype = numpy.float32))
        
        light_position_id = GLVaoTriangle.gl_shader.uniformLocation('light_position')
        GL.glUniform3fv(light_position_id, 1, numpy.array([0.0, 4.0, 0.0], dtype = numpy.float32))

        GL.glBindVertexArray(self.gl_id)
        GL.glDrawArrays(self.gl_type, 0, self.v_size)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

        
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
