#!/usr/bin/env python
#
## @file
#
# Viewer for choosing LEGO parts.
#
# Hazen 07/14
#

import sys

from PyQt4 import QtCore, QtGui, QtOpenGL

import partviewer_ui

## PartViewer
#
# The PartViewer QMainWindow.
#
class PartViewer(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = partviewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionQuit.triggered.connect(self.handleQuit)

    def handleQuit(self, boolean):
        self.close()


if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)
    window = PartViewer()
    window.show()
    app.exec_()

