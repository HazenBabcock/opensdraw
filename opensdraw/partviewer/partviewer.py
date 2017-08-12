#!/usr/bin/env python
"""
Viewer for choosing LEGO parts.

Hazen 11/15
"""

import os
import requests
import sys
import urllib
import warnings

from xml.etree import ElementTree

from PyQt5 import QtCore, QtGui, QtWidgets

#import opensdraw.lcad_lib.ldrawPath as ldrawPath
#import colorChooserWidget

import partviewer_ui


cert_fails = False
def getRBPartInfo(api_key, part_id):
    """
    Get part information from rebrickable.com.
    """
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
            print("Got SSL Error:", e)
            print("Trying again without SSL certificate verification.")
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
    

class PartDisplay(QtWidgets.QWidget):
    """
    For displaying a picture of a part.
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.part_image = None

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.part_image is not None:
            painter.drawImage(1, 1, self.part_image)
        else:
            painter.setPen(QtGui.QColor(255, 255, 255))
            painter.setBrush(QtGui.QColor(255, 255, 255))
            painter.drawRect(0, 0, self.width(), self.height())

    def setPartImage(self, part_image):
        self.part_image = part_image
        self.update()
        
    
class PartViewer(QtWidgets.QMainWindow):
    """
    The PartViewer QMainWindow.
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.part_color = "71"
        self.part_file = ""
        self.part_id = ""
        self.part_text = ""
        self.rb_info = None
        self.settings = QtCore.QSettings("OpenLCAD", "PartViewer")

        # Setup UI.
        self.ui = partviewer_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        # Hide the filters since we are not using them.
        self.ui.filterGroupBox.hide()
        
        # Load parts.
        QtCore.QTimer.singleShot(100, self.handleLoadParts)
        
        # Load colors.
        self.ui.colorListView.loadColors()

        # Part image display.
        self.part_display = PartDisplay(parent = self)
        layout = QtWidgets.QGridLayout(self.ui.partImageFrame)
        layout.setContentsMargins(1,1,1,1)
        layout.addWidget(self.part_display)
        
        # Connect signals.
        self.ui.actionQuit.triggered.connect(self.handleQuit)
        self.ui.colorListView.selectedColorChanged.connect(self.handleColorChange)
        self.ui.partsTreeView.selectedPartChanged.connect(self.handleSelectedPartChange)

        # Restore settings.
        self.resize(self.settings.value("MainWindow/Size", self.size()))
        self.move(self.settings.value("MainWindow/Position", self.pos()))
        self.ui.apiLineEdit.setText(self.settings.value("apiText", ""))
        self.ui.rebrickCheckBox.setChecked(self.settings.value("rebrickCheckBox", False, bool))
        self.ui.splitter.restoreState(self.settings.value("splitterSizes", QtCore.QByteArray()))

    def closeEvent(self, event):
        self.ui.partsTreeView.stop_loading = True
        self.settings.setValue("MainWindow/Size", self.size())
        self.settings.setValue("MainWindow/Position", self.pos())
        self.settings.setValue("apiText", self.ui.apiLineEdit.text())
        self.settings.setValue("rebrickCheckBox", self.ui.rebrickCheckBox.isChecked())
        self.settings.setValue("splitterSizes", self.ui.splitter.saveState())

    def handleColorChange(self, color):
        self.part_color = color
        self.updatePartInfo()

    def handleSelectedPartChange(self, part):
        self.part_file = part.part_file
        self.part_text = part.text()
        self.part_display.setPartImage(part.part_image)

        self.part_id = self.part_file.split(".")[0]
        if self.ui.rebrickCheckBox.isChecked() and (len(self.ui.apiLineEdit.text()) > 0):
            self.rb_info = getRBPartInfo(self.ui.apiLineEdit.text(), self.part_id)
            self.ui.colorListView.filterColors(self.rb_info.get("colors", None))
            
        self.updatePartInfo()

    def handleQuit(self, boolean):
        self.close()

    def handleLoadParts(self):
        self.ui.partsTreeView.loadParts()

    def updatePartInfo(self):

        text = "(" + self.part_id + ")"
        text += " " + self.part_text
        text += ", " + self.part_color

        if self.rb_info is None:
            text += ", no Rebrickable information."
        elif "error" in self.rb_info:
            text += ", " + self.rb_info["error"]
        else:
            if not "year1" in self.rb_info:
                self.rb_info["year1"] = "?"
            if (str(self.rb_info["year1"]) == "0"):
                self.rb_info["year1"] = "?"
            if not u"year2" in self.rb_info:
                self.rb_info["year2"] = "?"
            if (str(self.rb_info["year2"]) == "0"):
                self.rb_info["year2"] = "?"
            text += ", years " + str(self.rb_info["year1"]) + " - " + str(self.rb_info["year2"])
            
        self.ui.partInfoLabel.setText(text)

        # Create file for LDView.
        with open("ldview_part.mpd", "w") as fp:
            fp.write("1 " + self.part_color + " 0 0 0 1 0 0 0 1 0 0 0 1 " + self.part_id + ".dat")


# Main
if (__name__ == '__main__'):
    app = QtWidgets.QApplication(sys.argv)

    window = PartViewer()            
    window.show()
    app.exec_()


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
