#!/usr/bin/env python
"""
Handles the colors listview.

Hazen 11/15
"""

import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import opensdraw.lcad_lib.colorsParser as colorsParser


class ColorItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Custom item including a square displaying the color.
    """
    def __init__(self, model = None, proxy_model = None, **kwds):
        super().__init__(**kwds)
        self.model = model
        self.proxy_model = proxy_model

    def itemFromProxyIndex(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self.model.itemFromIndex(source_index)
    
    def paint(self, painter, option, index):
        color = self.itemFromProxyIndex(index)

        # Draw correct background.
        style = option.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)

        # Draw color swatch.
        painter.setPen(color.face_color)
        painter.setBrush(color.face_color)
        painter.drawRoundedRect(option.rect.left() + 2,
                                option.rect.top() + 2,
                                option.rect.width() - 5,
                                option.rect.height() - 4,
                                3, 3)
        
        # Draw color description.
        painter.setPen(color.edge_color)
        text_rect = QtCore.QRect(option.rect.left() + 10,
                                 option.rect.top(),
                                 option.rect.width(),
                                 option.rect.height() * 9)
        painter.drawText(text_rect, QtCore.Qt.AlignLeft, color.text())
    

class ColorListView(QtWidgets.QListView):
    """
    Encapsulates a list view specialized for displaying LDraw colors.
    """

    selectedColorChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.color_items = {}
        self.color_model = QtGui.QStandardItemModel(self)
        self.color_proxy_model = ColorProxyModel(parent = self)
        self.color_proxy_model.setSourceModel(self.color_model)
        self.setModel(self.color_proxy_model)
                         
        # Rendering
        self.setItemDelegate(ColorItemDelegate(model = self.color_model,
                                               proxy_model = self.color_proxy_model))

        # Get selection changes
        self.selectionModel().selectionChanged.connect(self.handleSelectionChange)

    def handleSelectionChange(self, new_item_selection, old_item_selection):
        if (len(self.selectedIndexes()) > 0):
            source_index = self.color_proxy_model.mapToSource(self.selectedIndexes()[0])
            self.selectedColorChanged.emit(self.color_model.itemFromIndex(source_index).color_id)
                         
    def loadColors(self):
        colors = colorsParser.loadColors()
        for c_id in sorted(colors, key = lambda x: int(x)):
            c_item = ColorStandardItem(c_id,
                                       "(" + c_id + ") " + colors[c_id].name,
                                       colors[c_id].getFaceColor("256"),
                                       colors[c_id].getEdgeColor("256"))
            self.color_items[c_id] = c_item
            self.color_model.appendRow(c_item)

    def filterColors(self, rb_color_list):
        if rb_color_list is None:
            for color in self.color_items.values():
                color.setText(color.color_name)
                color.show = True
        else:
            for color in self.color_items.values():
                color.show = False
            for rb_color in rb_color_list:
                try:
                    color = self.color_items[rb_color['ldraw_color_id']]
                except KeyError:
                    print("Unknown LDraw color", rb_color['ldraw_color_id'])
                    continue
                color.setText(color.color_name + " (" + rb_color['num_sets'] + " sets)")
                color.show = True

        self.color_proxy_model.invalidateFilter()
        

class ColorProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, **kwds):        
        super().__init__(**kwds)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        color = self.sourceModel().itemFromIndex(index)
        return color.show


class ColorStandardItem(QtGui.QStandardItem):

    def __init__(self, color_id, color_name, face_color, edge_color):
        super().__init__(color_name)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.color_id = color_id
        self.color_name = color_name
        self.edge_color = QtGui.QColor(*edge_color)
        self.face_color = QtGui.QColor(*face_color)
        self.show = True
        
        
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
