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


## PartProxyModel
#
# A PyQt QSortFilterProxyModel adapted for sorting and filtering parts.
#
class PartProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent):
        QtGui.QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index0 = model.index(source_row, 0, source_parent)
        index1 = model.index(source_row, 1, source_parent)

        if (model.data(index0).toString().contains(self.filterRegExp()) or
            model.data(index1).toString().contains(self.filterRegExp())):
            return True
        else:
            return False


## PartStandardItem
#
# A PyQt QStandardItem specialized to hold the information related to a part.
#
class PartStandardItem(QtGui.QStandardItem):

    ## __init__
    #
    # @param text The item text.
    #
    def __init__(self, text, part_name):
        QtGui.QStandardItem.__init__(self, text)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setData(part_name)


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

        # Setup models.
        self.part_model = QtGui.QStandardItemModel(self)
        self.proxy_model = PartProxyModel(self)
        self.proxy_model.setSourceModel(self.part_model)

        # Setup UI.
        self.ui = partviewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionQuit.triggered.connect(self.handleQuit)

        # Parse part file.
        xml = ElementTree.parse(xml_part_file).getroot()
        self.part_path = xml.find("path").attrib["path"]
        for part_entry in xml.find("parts"):
            if (part_entry.attrib["category"] != "Moved"):
                part_name = part_entry.attrib["file"]
                self.part_model.appendRow([PartStandardItem(part_entry.attrib["category"], part_name),
                                           PartStandardItem(part_entry.attrib["description"], part_name)])

        # Connect signals.
        self.ui.filterLineEdit.textChanged.connect(self.handleTextChange)
        
        # Configure parts table view.
        self.ui.partsTableView.setModel(self.proxy_model)
        self.ui.partsTableView.verticalHeader().setDefaultSectionSize(18)
        self.ui.partsTableView.verticalHeader().setVisible(False)
        self.ui.partsTableView.resizeColumnsToContents()
        self.ui.partsTableView.setSortingEnabled(True)
        self.ui.partsTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.partsTableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.selection_model = self.ui.partsTableView.selectionModel()
        self.selection_model.currentRowChanged.connect(self.handleCurrentRowChange)

        self.proxy_model.setHeaderData(0, QtCore.Qt.Horizontal, "Category")
        self.proxy_model.setHeaderData(1, QtCore.Qt.Horizontal, "Description")

    def handleCurrentRowChange(self, new_row, old_row):
        part_file = self.part_model.itemFromIndex(self.proxy_model.mapToSource(new_row)).data().toString()
        self.ui.partFileLabel.setText(part_file)
        self.ui.openGLWidget.loadPart(self.part_path + part_file)
        
        print part_file
        print ""

    def handleTextChange(self, new_text):
        self.proxy_model.setFilterRegExp(new_text)

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
