#!/usr/bin/python
"""
Handles the parts treeview.

Hazen 11/15
"""

import os
from PyQt4 import QtCore, QtGui

import opensdraw.lcad_lib.ldrawPath as ldrawPath


#
# Change this to False is you have issues with LDView working from the command line
# and you want to use the built in (and much less capable) part renderer.
#
use_ldview = True

if use_ldview:
    import subprocess
else:    
    import glWidget


class PartItemDelegate(QtGui.QStyledItemDelegate):
    """
    Custom item including a rendering of the part.
    """
    def __init__(self, model, proxy_model):
        QtGui.QStyledItemDelegate.__init__(self)
        self.model = model
        self.proxy_model = proxy_model

    def itemFromProxyIndex(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self.model.itemFromIndex(source_index)
    
    def paint(self, painter, option, index):
        part = self.itemFromProxyIndex(index)
    
        if isinstance(part, PartStandardItem):

            # Draw correct background.
            style = option.widget.style()
            style.drawControl(QtGui.QStyle.CE_ItemViewItem, option, painter, option.widget)

            left = option.rect.left()
            top = option.rect.top()

            # Draw background rectangle.
            #painter.drawRect(left, top, option.rect.width(), option.rect.height())

            # Draw image.
            painter.drawImage(left + 1, top + 1, part.part_image_scaled)
        
            # Draw description and part filename.
            painter.drawText(left + part.part_image_scaled.width() + 5,
                             top + 0.33 * part.part_image_scaled.height(),
                             part.text())
            painter.drawText(left + part.part_image_scaled.width() + 5,
                             top + 0.66 * part.part_image_scaled.height(),
                             part.part_file)
        else:
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        part = self.itemFromProxyIndex(index)
        result = QtGui.QStyledItemDelegate.sizeHint(self, option, index)
        if isinstance(part, PartStandardItem):
            result.setHeight(part.part_image_scaled.height() + 2)
        return result

    
class PartProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent):
        QtGui.QSortFilterProxyModel.__init__(self, parent)


class PartStandardItem(QtGui.QStandardItem):

    def __init__(self, category, part_file, part_picture, part_description):        
        QtGui.QStandardItem.__init__(self, part_description)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.category = category
        self.part_file = part_file
        self.part_image = QtGui.QImage(part_picture)
        self.part_image_scaled = self.part_image.scaled(70, 70, transformMode = QtCore.Qt.SmoothTransformation)

        
class PartTreeView(QtGui.QTreeView):
    """
    Encapsulates a tree view specialized for displaying parts.
    """
    selectedPartChanged = QtCore.pyqtSignal(object)

    def __init__(self, parent = None):
        QtGui.QTreeView.__init__(self, parent)

        self.part_path = None

        # Configure.
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #self.setUniformRowHeights(True)
        self.setHeaderHidden(True)

        # Set model.
        self.part_model = QtGui.QStandardItemModel(self)
        self.part_proxy_model = PartProxyModel(self)
        self.part_proxy_model.setSourceModel(self.part_model)
        self.setModel(self.part_proxy_model)

        # Rendering
        self.setItemDelegate(PartItemDelegate(self.part_model, self.part_proxy_model))

        # Get selection changes
        self.selectionModel().selectionChanged.connect(self.handleSelectionChange)
        
        # GLWidget for part rendering.
        if not use_ldview:
            self.gl_widget = glWidget.GLWidget(self)

        # Create working directory for part renders.
        self.part_dir = os.path.dirname(__file__)
        if (self.part_dir == ""):
            self.part_dir = "./part_pics"
        else:
            self.part_dir += "/part_pics"

        if not os.path.exists(self.part_dir):
            os.makedirs(self.part_dir)

    def loadParts(self):
        self.part_path = ldrawPath.getLDrawPath() + "parts/"

        categories = {}
        count = 0
        with open(self.part_path + "../parts.lst") as part_list:
            for part in part_list:
                text = ' '.join(part.split())
                data = text.split()

                file_name = data[0]
                category = data[1]
                description = ' '.join(data[2:])

                if not category[0].isalpha():
                    continue

                # Create category if it does not exist.
                if not category in categories:
                    qs_item = QtGui.QStandardItem(category)
                    qs_item.setFlags(QtCore.Qt.ItemIsEnabled)
                    categories[category] = qs_item
                    self.part_model.appendRow(qs_item)
                else:
                    qs_item = categories[category]

                count += 1
                qs_item.appendRow(PartStandardItem(category,
                                                   file_name,
                                                   self.renderPart(file_name, 71, count),
                                                   description))

                # Pause to process other events as the loading can be very slow.
                QtGui.qApp.processEvents()

                #if (count == 10):
                #    break

        print "Loaded", count, "parts."

    def handleSelectionChange(self, new_item_selection, old_item_selection):
        if (len(self.selectedIndexes()) > 0):
            self.selectedPartChanged.emit(self.partFromProxyIndex(self.selectedIndexes()[0]))
        
    def partFromProxyIndex(self, proxy_index):
        source_index = self.part_proxy_model.mapToSource(proxy_index)
        return self.part_model.itemFromIndex(source_index)
    
    def renderPart(self, file_name, color_id, count):
        color_id = str(color_id)
        pic_name = self.part_dir + os.path.sep + file_name[:-4] + "_" + color_id + ".png"
        if not os.path.exists(pic_name):
            print "Rendering", count, pic_name
            if use_ldview:

                # Create 400 x 400 image.
                subprocess.call(['LDView',
                                 ldrawPath.getLDrawPath() + "parts" + os.path.sep + file_name,
                                 "-SaveSnapshot=" + pic_name,
                                 "-SaveActualSize=0",
                                 "-SaveWidth=400",
                                 "-SaveHeight=400",
                                 "-DefaultZoom=0.95"])
                
                # Load, downsample to 200 x 200 and save so that the part looks nicer.
                part_image = QtGui.QImage(pic_name)
                part_image = part_image.scaled(200, 200, transformMode = QtCore.Qt.SmoothTransformation)
                part_image.save(pic_name)

            else:
                self.gl_widget.renderPart(file_name, color_id)
                self.gl_widget.offscreen(pic_name)
        if not use_ldview:
            self.gl_widget.hide()
        return pic_name


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
