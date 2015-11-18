#!/usr/bin/env python
#
## @file
#
# Viewer for choosing LEGO parts.
#
# Hazen 11/15
#

import os
import requests
import sys
import urllib
import urllib2
import warnings

from xml.etree import ElementTree

from PyQt4 import QtCore, QtGui

import opensdraw.lcad_lib.ldrawPath as ldrawPath
#import colorChooserWidget

import partviewer_ui


## getRBPartInfo
#
# Get part information from rebrickable.com.
#
cert_fails = False
def getRBPartInfo(api_key, part_id):
    query = {"key" : api_key,
             "format" : "json",
             "part_id" : part_id,
             "inc_colors" : "1"}

    url = "https://rebrickable.com/api/get_part?" + urllib.urlencode(query)

    global cert_fails
    if not cert_fails:
        try:
            # Try with verification first.
            response = requests.get(url, allow_redirects=False)
    
        except requests.exceptions.SSLError as e:
            print "Got SSL Error:", e
            print "Trying again without SSL certificate verification."
            cert_fails = True

    if cert_fails:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.get(url, allow_redirects=False, verify=False)

    if (response.text == "INVALIDKEY"):
        return {"error" : "Invalid API key."}
    elif (response.text == "NOPART"):
        return {"error" : "This part is not known to Rebrickable."}
    else:
        return response.json()
    

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

        self.xml_part_file = xml_part_file
        
        self.settings = QtCore.QSettings("OpenLCAD", "PartViewer")

        # Setup UI.
        self.ui = partviewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect signals.
        self.ui.actionQuit.triggered.connect(self.handleQuit)

        # Load parts.
        QtCore.QTimer.singleShot(100, self.handleLoadParts)
        
        # Load colors.
        #self.color_chooser = colorChooserWidget.ColorChooserWidget("../colors.xml")
        #layout = QtGui.QGridLayout(self.ui.colorGroupBox)
        #layout.addWidget(self.color_chooser)
        #self.ui.colorGroupBox.setLayout(layout)

        # Connect signals.
#        self.ui.filterLineEdit.textChanged.connect(self.handleTextChange)
#        self.color_chooser.colorPicked.connect(self.handleColorChange)
#        self.load_part_timer.timeout.connect(self.handleLoadPart)

        # Restore settings.
#        self.resize(self.settings.value("MainWindow/Size", self.size()).toSize())
#        self.move(self.settings.value("MainWindow/Position", self.pos()).toPoint())
#        self.ui.apiLineEdit.setText(self.settings.value("apiText", "").toString())
#        self.ui.rebrickCheckBox.setChecked(self.settings.value("rebrickCheckBox", False).toBool())
#        self.ui.splitter.restoreState(self.settings.value("splitterSizes").toByteArray())

    ## closeEvent
    #
    # @param event A QEvent object.
    #
    def closeEvent(self, event):
        pass
#        self.ui.openGLWidget.freePartGL()
#        self.settings.setValue("MainWindow/Size", self.size())
#        self.settings.setValue("MainWindow/Position", self.pos())
#        self.settings.setValue("apiText", self.ui.apiLineEdit.text())
#        self.settings.setValue("rebrickCheckBox", self.ui.rebrickCheckBox.isChecked())
#        self.settings.setValue("splitterSizes", self.ui.splitter.saveState())

    ## handleColorChange
    #
    # @param color A Color object (defined in colorChooserWidget.py)
    #
#    def handleColorChange(self, color):
#        self.ui.openGLWidget.setColor(color.getFaceColor(), color.getEdgeColor())
#        self.part_color = color.getDescription()
#        self.updatePartLabel()

    ## handleTextChange
    #
    # @param new_text The new text to use for filtering.
    #
#    def handleTextChange(self, new_text):
#        self.proxy_model.setFilterRegExp(new_text)

    ## handleQuit
    #
    # @param boolean This is ignored.
    #
    def handleQuit(self, boolean):
        self.close()

    ## handleLoadPartTimeout
    #
    def handleLoadParts(self):
        self.ui.partsTreeView.loadParts(self.xml_part_file)
        

#        pass
#        self.ui.openGLWidget.loadPart(self.part_path + self.part_file)
#        if self.ui.rebrickCheckBox.isChecked():
#            part_id = self.part_file.split(".")[0]
#            info = getRBPartInfo(self.ui.apiLineEdit.text(), part_id)
#            if ("error" in info):
#                self.color_chooser.markAvailableColors(None)
#                self.ui.rebrickLabel.setText(info["error"])
#            else:
#                colors = map(lambda(x): x.get("ldraw_color_id", ""), info.get("colors", []))
#                self.color_chooser.markAvailableColors(colors)
#                self.ui.rebrickLabel.setText(info.get("year1","?") + " - " + info.get("year2","?"))
#        else:
#            self.color_chooser.markAvailableColors(None)
            
    ## updatePartLabel
    #
    # Update the part label text based on the current part & color.
#    def updatePartLabel(self):
#        self.ui.partFileLabel.setText(self.part_file + ", " + self.part_color)


# Main
if (__name__ == '__main__'):
    app = QtGui.QApplication(sys.argv)

    if (len(sys.argv) == 2):
        window = PartViewer(sys.argv[1])
    else:
        directory = os.path.dirname(__file__)
        if (len(directory) > 0):
            window = PartViewer(directory + "/../xml/parts.xml")
        else:
            window = PartViewer("../xml/parts.xml")
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
