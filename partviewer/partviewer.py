#!/usr/bin/env python
#
## @file
#
# Viewer for choosing LEGO parts.
#
# Hazen 06/14
#

import sys

from OpenGL import GL, GLU
from PyQt4 import QtCore, QtGui, QtOpenGL

import lcad_lib.datFileParser as datFileParser
import lcad_lib.glParser as glParser

## GLWidget
#
# The GL widget for displaying a part.
#
class GLWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.last_pos = QtCore.QPoint()
        self.part = None
        self.scale = 0.05
        self.verbose = True
        self.x_rotation = 0.0
        self.y_rotation = 0.0
        self.z_rotation = 0.0

        self.setMinimumSize(500, 500)

    def initializeGL(self):

        if self.verbose:
            print 'Vendor: %s' % (GL.glGetString(GL.GL_VENDOR))
            print 'Opengl version: %s' % (GL.glGetString(GL.GL_VERSION))
            print 'GLSL Version: %s' % (GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))
            print 'Renderer: %s' % (GL.glGetString(GL.GL_RENDERER))

        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, [5.0, 5.0, 10.0, 0.0])
        #GL.glEnable(GL.GL_CULL_FACE)
        #GL.glEnable(GL.GL_LIGHTING)
        #GL.glEnable(GL.GL_LIGHT0)
        #GL.glEnable(GL.GL_DEPTH_TEST)

        #self.loadPart("C:/Program Files (x86)/LDraw/parts/1.dat")
        self.loadPart("../test/test3.dat")

    def loadPart(self, filename):
        self.part = glParser.GLParser(None, [1.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        datFileParser.parsePartFile(self.part, filename)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        gain = 4.0
        if (event.buttons() and QtCore.Qt.LeftButton):
            self.x_rotation += gain * dy
            self.y_rotation += gain * dx
        elif (event.buttons() and QtCore.Qt.RightButton):
            self.x_rotation += gain * dy
            self.z_rotation += gain * dx

        self.lastPos = event.pos()
        self.updateGL()

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if self.part is not None:
            #GL.glMatrixMode(GL.GL_MODELVIEW)
            #GL.glLoadIdentity()
            #GL.glPushMatrix()
            #GL.glTranslatef(0.0, 0.0, -50.0)
            #GL.glScalef(self.scale, self.scale, self.scale);
            #GL.glRotatef(self.x_rotation * 0.1, 1.0, 0.0, 0.0)
            #GL.glRotatef(self.y_rotation * 0.1, 0.0, 1.0, 0.0)
            #GL.glRotatef(self.z_rotation * 0.1, 0.0, 0.0, 1.0)
            
            self.part.render()
            #GL.glPopMatrix()

        GL.glFlush()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(60.0, 1.0, 0.01, 100.0)

    def wheelEvent(self, event):
        gain = 1.2
        if (event.delta() > 0):
            self.scale = self.scale * gain
        else:
            self.scale = self.scale * (1.0/gain)
        self.updateGL()


## GLWidgetTest
#
# For testing the GLWidget.
#
class GLWidgetTest(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        widget = GLWidget(self)
        #widget = GLWidget("test.dat", self)
        self.setCentralWidget(widget)
        #widget.loadPart("C:/Program Files (x86)/LDraw/parts/1.dat")

if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)
    window = GLWidgetTest()
    window.show()
    app.exec_()

