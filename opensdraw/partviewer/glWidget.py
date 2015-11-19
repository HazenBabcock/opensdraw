#!/usr/bin/env python
"""
A PyQt OpenGL widget for rendering parts.

Hazen 11/15
"""

import math
import numpy
import sys

from OpenGL import GL, GLU, GLUT
from PyQt4 import QtCore, QtGui, QtOpenGL

import opensdraw.lcad_lib.colorsParser as colorsParser
import opensdraw.lcad_lib.datFileParser as datFileParser
import opensdraw.lcad_lib.glParser as glParser
import opensdraw.lcad_lib.ldrawPath as ldrawPath


all_colors = colorsParser.loadColors()


class GLWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent, width = 400, height = 400):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.last_pos = QtCore.QPoint()
        self.offset = numpy.array([[0], [0], [0], [0]], dtype = numpy.float32)
        self.part = None
        self.mvp_matrix = None
        self.verbose = True

        self.setFixedSize(width, height)

    def freePartGL(self):
        if self.part is not None:
            self.part.freeGL()

    def initializeGL(self):

        if self.verbose:
            print 'OpenGL info'
            print ' Vendor: %s' % (GL.glGetString(GL.GL_VENDOR))
            print ' Opengl version: %s' % (GL.glGetString(GL.GL_VERSION))
            print ' GLSL Version: %s' % (GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))
            print ' Renderer: %s' % (GL.glGetString(GL.GL_RENDERER))
            
    def renderPart(self, filename, color_id):
        self.freePartGL()
        color = all_colors[str(color_id)]
        self.part = glParser.GLParser(color.getFaceColor(),
                                      color.getEdgeColor())
        datFileParser.parsePartFile(self.part, filename)
        self.updateView()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)
        
    def paintGL(self):
        pass

    def offscreen(self, picture_file):
        
        _format = QtOpenGL.QGLFramebufferObjectFormat()
        _format.setAttachment(QtOpenGL.QGLFramebufferObject.CombinedDepthStencil)
        _format.setSamples(16)
        
        fbo = QtOpenGL.QGLFramebufferObject(400, 400, _format)
        fbo.bind()
        
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glLineWidth(2.0)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        self.mvp_matrix = self.mvp_matrix.astype(numpy.float32)
        self.part.render(self.mvp_matrix)
        
        GL.glFlush()
        
        fbo.release()
        image = fbo.toImage().mirrored(horizontal = True)
        image.save(picture_file)

    def updateView(self):

        [min_x, min_y, min_z, max_x, max_y, max_z] = self.part.getRange()
        cx = 0.5 * (max_x + min_x)
        cy = 0.5 * (max_y + min_y)
        cz = 0.5 * (max_z + min_z)

        dx = max_x - cx
        dy = max_y - cy
        dz = max_z - cz

        rr = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        self.mvp_matrix = numpy.identity(4)
        scale = 0.9/rr
        self.mvp_matrix[0,0] = scale
        self.mvp_matrix[1,1] = scale
        self.mvp_matrix[2,2] = scale

        # Center object
        t_mat = numpy.identity(4)
        t_mat[3,0] = -cx * scale
        t_mat[3,1] = -cy * scale
        t_mat[3,2] = -cz * scale

        # LDView matrix
        r_mat = numpy.array([ 0.707107, 0,        0.707107, 0,
                              0.353553, 0.866025,-0.353553, 0,
                             -0.612373, 0.5,      0.612372, 0,
                              0,        0,        0,        1.0]).reshape(4,4)

        r_mat = numpy.transpose(r_mat)
        
        # Rotate around x axis.
        ax = math.radians(-45)
        rot_x = numpy.identity(4)
        rot_x[1,1] = math.cos(ax)
        rot_x[2,2] = rot_x[1,1]
        rot_x[1,2] = math.sin(ax)
        rot_x[2,1] = -rot_x[1,2]
        
        # Rotate around y axis.
        ay = math.radians(45)
        rot_y = numpy.identity(4)
        rot_y[0,0] = math.cos(ay)
        rot_y[2,2] = rot_y[0,0]
        rot_y[0,2] = math.sin(ay)
        rot_y[2,0] = -rot_y[0,2]

        # Rotate around z axis.
        az = math.radians(0)
        rot_z = numpy.identity(4)
        rot_z[0,0] = math.cos(az)
        rot_z[1,1] = rot_z[0,0]
        rot_z[0,1] = math.sin(az)
        rot_z[1,0] = -rot_z[0,1]
        
#        self.mvp_matrix = numpy.dot(self.mvp_matrix,
#                                    numpy.dot(rot_x,
#                                              numpy.dot(rot_y,
#                                                        numpy.dot(rot_z, t_mat))))

        self.mvp_matrix = numpy.dot(self.mvp_matrix, numpy.dot(r_mat, t_mat))

## GLWidgetTest
#
# For testing the GLWidget.
#
class GLWidgetTest(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.gl_widget = GLWidget(self)
        self.setCentralWidget(self.gl_widget)
        QtCore.QTimer.singleShot(0, self.renderPart)

    def renderPart(self):
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/32523.dat", 2)
        self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/57519.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/3622.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/42003.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/58119.dat", 3)
        #self.gl_widget.renderPixmap(100,100)
        self.gl_widget.offscreen("test.png")
        self.close()
        
        #pixmap = self.gl_widget.grabFrameBuffer()
        #print pixmap
        #pixmap.save("snap.png")

if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)
    window = GLWidgetTest()
    window.show()
    app.exec_()

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
