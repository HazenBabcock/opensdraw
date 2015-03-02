#!/usr/bin/env python
#
## @file
#
# Viewer for choosing LEGO parts.
#
# Hazen 07/14
#

import os
import sys
from xml.etree import ElementTree

from PyQt4 import QtCore, QtGui

import lcad_lib.ldrawPath as ldrawPath
import colorChooserWidget

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

        self.load_part_timer = QtCore.QTimer()
        self.part_color = ""
        self.part_file = ""
        self.settings = QtCore.QSettings("OpenLCAD", "PartViewer")

        # Setup part loading timer.
        self.load_part_timer.setSingleShot(True)
        self.load_part_timer.setInterval(100)

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
        self.part_path = ldrawPath.getLDrawPath() + "parts/"
        for part_entry in xml.find("parts"):
            if (part_entry.attrib["category"] != "Moved"):
                part_name = part_entry.attrib["file"]
                self.part_model.appendRow([PartStandardItem(part_entry.attrib["category"], part_name),
                                           PartStandardItem(part_entry.attrib["description"], part_name)])

        # Load colors.
        self.color_chooser = colorChooserWidget.ColorChooserWidget("../colors.xml")
        layout = QtGui.QGridLayout(self.ui.colorGroupBox)
        layout.addWidget(self.color_chooser)
        self.ui.colorGroupBox.setLayout(layout)

        # Connect signals.
        self.ui.filterLineEdit.textChanged.connect(self.handleTextChange)
        self.color_chooser.colorPicked.connect(self.handleColorChange)
        self.load_part_timer.timeout.connect(self.handleLoadPart)
        
        # Configure parts table view.
        self.ui.partsTableView.setModel(self.proxy_model)
        self.ui.partsTableView.verticalHeader().setDefaultSectionSize(18)
        self.ui.partsTableView.verticalHeader().setVisible(False)
        self.ui.partsTableView.resizeColumnsToContents()
        self.ui.partsTableView.setSortingEnabled(True)
        self.ui.partsTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.partsTableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.partsTableView.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.ui.partsTableView.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.selection_model = self.ui.partsTableView.selectionModel()
        self.selection_model.currentRowChanged.connect(self.handleCurrentRowChange)

        self.proxy_model.setHeaderData(0, QtCore.Qt.Horizontal, "Category")
        self.proxy_model.setHeaderData(1, QtCore.Qt.Horizontal, "Description")

        # Restore settings.
        self.resize(self.settings.value("MainWindow/Size", self.size()).toSize())
        self.move(self.settings.value("MainWindow/Position", self.pos()).toPoint())
        self.ui.splitter.restoreState(self.settings.value("splitterSizes").toByteArray())

    ## closeEvent
    #
    # @param event A QEvent object.
    #
    def closeEvent(self, event):
        self.ui.openGLWidget.freePartGL()
        self.settings.setValue("MainWindow/Size", self.size())
        self.settings.setValue("MainWindow/Position", self.pos())
        self.settings.setValue("splitterSizes", self.ui.splitter.saveState())

    ## handleCurrentRowChange
    #
    # @param new_row QModelIndex
    # @param old_row QModelIndex
    #
    def handleCurrentRowChange(self, new_row, old_row):
        item = self.part_model.itemFromIndex(self.proxy_model.mapToSource(new_row))
        if item is not None:
            self.part_file = item.data().toString()
            self.load_part_timer.start()
            self.updatePartLabel()

    ## handleColorChange
    #
    # @param color A Color object (defined in colorChooserWidget.py)
    #
    def handleColorChange(self, color):
        self.ui.openGLWidget.setColor(color.getFaceColor(), color.getEdgeColor())
        self.part_color = color.getDescription()
        self.updatePartLabel()

    ## handleTextChange
    #
    # @param new_text The new text to use for filtering.
    #
    def handleTextChange(self, new_text):
        self.proxy_model.setFilterRegExp(new_text)

    ## handleQuit
    #
    # @param boolean This is ignored.
    #
    def handleQuit(self, boolean):
        self.close()

    ## handleLoadPartTimeout
    #
    #
    def handleLoadPart(self):
        self.ui.openGLWidget.loadPart(self.part_path + self.part_file)

    ## updatePartLabel
    #
    # Update the part label text based on the current part & color.
    def updatePartLabel(self):
        self.ui.partFileLabel.setText(self.part_file+ ", " + self.part_color)


# Main
if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)

    if (len(sys.argv) == 2):
        window = PartViewer(sys.argv[1])
    else:
        directory = os.path.dirname(__file__)
        if (len(directory) > 0):
            window = PartViewer(directory + "/../parts.xml")
        else:
            window = PartViewer("../parts.xml")
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
