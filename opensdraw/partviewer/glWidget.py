#!/usr/bin/env python
"""
A PyQt OpenGL widget for (off-screen) rendering of parts for the part-viewer.

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


def chainMatrices(matrices):
    result = numpy.identity(4)
    for m in reversed(matrices):
        result = numpy.dot(m, result)
    return result


class GLWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent, width = 200, height = 200):
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
        
        fbo = QtOpenGL.QGLFramebufferObject(self.width(), self.height(), _format)
        fbo.bind()

        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        
        if self.part.bfc_certified:
            GL.glFrontFace(GL.GL_CW)
            GL.glEnable(GL.GL_CULL_FACE)
            
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)        
        GL.glLineWidth(1.0)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.mvp_matrix = self.mvp_matrix.astype(numpy.float32)
        self.part.render(self.mvp_matrix)
        
        GL.glFlush()
        
        fbo.release()
        #image = fbo.toImage()
        image = fbo.toImage().mirrored()
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

        s_mat = numpy.identity(4)
        scale = 0.85/rr
        s_mat[0,0] = scale
        s_mat[1,1] = scale
        s_mat[2,2] = scale

        # Perspective matrix.
        p_mat = numpy.zeros((4,4))
        mid = 0.0
        near = mid - rr
        far = mid + rr
        p_mat[0,0] = near/rr
        p_mat[1,1] = near/rr
        p_mat[2,2] = -(far + near)/(far - near)
        p_mat[2,3] = -2.0 * far * near/(far - near)
        p_mat[3,2] = -1
        
        # Translation matrix to center the model.
        t_mat1 = numpy.identity(4)
        t_mat1[3,0] = -cx
        t_mat1[3,1] = -cy
        t_mat1[3,2] = -cz

        t_mat2 = numpy.identity(4)
        t_mat2[3,1] = mid
        
        # LDView 2/3 matrix.
        ldv_mat = numpy.array([ 0.707107, 0.353553,-0.612373, 0,
                                0.0,      0.866025, 0.5,      0,
                                0.707107,-0.353553, 0.612372, 0,
                                0,        0,        0,        1.0]).reshape(4,4)

        # Rotate around x axis.
        #ax = math.radians(-45)
        ax = math.radians(0)
        rot_x = numpy.identity(4)
        rot_x[1,1] = math.cos(ax)
        rot_x[2,2] = rot_x[1,1]
        rot_x[1,2] = math.sin(ax)
        rot_x[2,1] = -rot_x[1,2]
        
        # Rotate around y axis.
        #ay = math.radians(90)
        ay = math.radians(0)
        rot_y = numpy.identity(4)
        rot_y[0,0] = math.cos(ay)
        rot_y[2,2] = rot_y[0,0]
        rot_y[0,2] = math.sin(ay)
        rot_y[2,0] = -rot_y[0,2]

        # Rotate around z axis.
        #az = math.radians(180)
        az = math.radians(0)
        rot_z = numpy.identity(4)
        rot_z[0,0] = math.cos(az)
        rot_z[1,1] = rot_z[0,0]
        rot_z[0,1] = math.sin(az)
        rot_z[1,0] = -rot_z[0,1]
        
        if False:
            self.mvp_matrix = chainMatrices([rot_x, rot_y, rot_z, t_mat1, s_mat])
        else:
            self.mvp_matrix = chainMatrices([ldv_mat, t_mat1, s_mat])
            #self.mvp_matrix = chainMatrices([p_mat, t_mat, rot_y, rot_z, ldv_mat])


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
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/3009.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/42003.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "parts/58119.dat", 3)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "p/box4t.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "p/box5.dat", 1)
        #self.gl_widget.renderPart(ldrawPath.getLDrawPath() + "p/stud.dat", 1)
        self.gl_widget.renderPixmap(100,100)
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
