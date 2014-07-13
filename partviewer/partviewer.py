#!/usr/bin/env python
#
## @file
#
# Viewer for choosing LEGO parts.
#
# Hazen 07/14
#

import sys
from xml.etree import ElementTree

from PyQt4 import QtCore, QtGui, QtOpenGL

import partviewer_ui

## PartStandardItem
#
# A PyQt QStandardItem specialized to hold the information related to a part.
#
class PartStandardItem(QtGui.QStandardItem):

    ## __init__
    #
    # @param text The item text.
    #
    def __init__(self, text):
        QtGui.QStandardItem.__init__(self, text)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


## PartViewer
#
# The PartViewer QMainWindow.
#
class PartViewer(QtGui.QMainWindow):

    ## __init__
    #
    # @param xml_part_file The LDraw XML part descriptor file.
    #
    def __init__(self, xml_part_file):
        QtGui.QMainWindow.__init__(self)

        self.part_model = QtGui.QStandardItemModel()

        # Setup UI.
        self.ui = partviewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionQuit.triggered.connect(self.handleQuit)

        # Parse part file.
        xml = ElementTree.parse(xml_part_file).getroot()
        for part_entry in xml.find("parts"):
            if (part_entry.attrib["category"] != "Moved"):
                self.part_model.appendRow([PartStandardItem(part_entry.attrib["category"]),
                                           PartStandardItem(part_entry.attrib["description"])])

        # Configure parts table view.
        self.ui.partsTableView.setModel(self.part_model)
        self.ui.partsTableView.verticalHeader().setDefaultSectionSize(18)
        self.ui.partsTableView.verticalHeader().setVisible(False)
        self.ui.partsTableView.resizeColumnsToContents()

        self.part_model.setHeaderData(0, QtCore.Qt.Horizontal, "Category")
        self.part_model.setHeaderData(1, QtCore.Qt.Horizontal, "Description")

    def handleQuit(self, boolean):
        self.close()

if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)

    if (len(sys.argv) == 2):
        window = PartViewer(sys.argv[1])
    else:
        window = PartViewer("parts.xml")
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
