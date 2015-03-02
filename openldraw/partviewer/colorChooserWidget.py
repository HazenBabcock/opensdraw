#!/usr/bin/env python
#
## @file
#
# A PyQt widget for picking ldraw colors.
#
# Hazen 07/14
#

import sys

from PyQt4 import QtCore, QtGui

import lcad_lib.colorsParser


## ColorChooserWidget
#
# A widget containing a grid of clickable color choices.
#
class ColorChooserWidget(QtGui.QWidget):
    colorPicked = QtCore.pyqtSignal(object)

    ## __init__
    #
    # @param color_file A colors.xml file.
    #
    def __init__(self, color_file, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.color_panels = []

        max_x = 400
        n_groups = 0
        colors = lcad_lib.colorsParser.loadColors()
        #x_pos = 2
        y_pos = 2
        for color_group in colors:
            if (n_groups < 3):
                x_pos = 2
            for color_entry in color_group:
                if (x_pos > max_x):
                    x_pos = 2
                    y_pos += 14
                panel = ColorPanelFrame(color_entry, self)
                panel.move(x_pos, y_pos)
                panel.clicked.connect(self.handleClick)
                self.color_panels.append(panel)
                x_pos += 22
            if (n_groups < 2):
                y_pos += 16
            #else:
            #    x_pos += 22
            n_groups += 1
                
        self.setFixedSize(max_x + 20, y_pos + 14)
        QtCore.QTimer.singleShot(0, self.initialColor)

    ## initialColor
    #
    # Generates a colorPicked signal for initialization purposes.
    #
    def initialColor(self):
        self.colorPicked.emit(self.color_panels[0].color)

    ## handleClick
    #
    # @param color A color object.
    #
    def handleClick(self, color):
        self.colorPicked.emit(color)


## ColorPanelFrame
#
# Clickable frame that displays a color.
#
class ColorPanelFrame(QtGui.QFrame):
    clicked = QtCore.pyqtSignal(object)

    ## __init__
    #
    # @param color A color object.
    #
    def __init__(self, color, parent):
        QtGui.QFrame.__init__(self, parent)

        self.color = color
        self.widget = ColorPanelWidget(color, self)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.setFixedSize(20, 12)
        #self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setLineWidth(1)

        self.setToolTip("LDraw color code: " + self.color.code + "\nLDraw name: " + self.color.name)

    ## mousePressEvent
    #
    # @param event A QMouseEvent
    #
    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.clicked.emit(self.color)


## ColorPanelWidget
#
# Widget that displays a color.
#
class ColorPanelWidget(QtGui.QWidget):

    ## __init__
    #
    # @param color A color object.
    #
    def __init__(self, color, parent):
        QtGui.QWidget.__init__(self, parent)

        self.q_color = QtGui.QColor(*color.getFaceColor(scale = "256"))

    ## paintEvent
    #
    # @param event A QPaintEvent.
    #
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.q_color)
        painter.setBrush(self.q_color)
        painter.drawRect(0, 0, self.width(), self.height())


## parseColor
#
# @param color_string A color string like "256,256,256,256".
# @param scale (Optional) "256" or "1.0", defaults to "1.0".
#
# @return [r, g, b, a]
#
def parseColor(color_string, scale = "1.0"):
    if (scale == "1.0"):
        return map(lambda(x): float(x)/256.0, color_string.split(","))
    else:
        return map(int, color_string.split(","))


# Main
if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)

    if (len(sys.argv) == 2):
        window = ColorChooserWidget(sys.argv[1])
    else:
        window = ColorChooserWidget("../colors.xml")

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
