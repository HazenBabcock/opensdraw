# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'partviewer.ui'
#
# Created: Sat Nov  7 15:23:07 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 620)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.partsTableView = QtGui.QTableView(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.partsTableView.sizePolicy().hasHeightForWidth())
        self.partsTableView.setSizePolicy(sizePolicy)
        self.partsTableView.setObjectName(_fromUtf8("partsTableView"))
        self.verticalLayout_2.addWidget(self.partsTableView)
        self.groupBox = QtGui.QGroupBox(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.partFileLabel = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.partFileLabel.sizePolicy().hasHeightForWidth())
        self.partFileLabel.setSizePolicy(sizePolicy)
        self.partFileLabel.setMaximumSize(QtCore.QSize(16777215, 20))
        self.partFileLabel.setObjectName(_fromUtf8("partFileLabel"))
        self.gridLayout.addWidget(self.partFileLabel, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.filterGroupBox = QtGui.QGroupBox(self.layoutWidget)
        self.filterGroupBox.setMinimumSize(QtCore.QSize(0, 100))
        self.filterGroupBox.setMaximumSize(QtCore.QSize(16777215, 120))
        self.filterGroupBox.setObjectName(_fromUtf8("filterGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.filterGroupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.filterLineEdit = QtGui.QLineEdit(self.filterGroupBox)
        self.filterLineEdit.setObjectName(_fromUtf8("filterLineEdit"))
        self.verticalLayout.addWidget(self.filterLineEdit)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.clearPushButton = QtGui.QPushButton(self.filterGroupBox)
        self.clearPushButton.setObjectName(_fromUtf8("clearPushButton"))
        self.horizontalLayout_2.addWidget(self.clearPushButton)
        self.filterPushButton = QtGui.QPushButton(self.filterGroupBox)
        self.filterPushButton.setObjectName(_fromUtf8("filterPushButton"))
        self.horizontalLayout_2.addWidget(self.filterPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.filterGroupBox)
        self.layoutWidget1 = QtGui.QWidget(self.splitter)
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.openGLWidget = GLWidget(self.layoutWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openGLWidget.sizePolicy().hasHeightForWidth())
        self.openGLWidget.setSizePolicy(sizePolicy)
        self.openGLWidget.setMinimumSize(QtCore.QSize(200, 200))
        self.openGLWidget.setObjectName(_fromUtf8("openGLWidget"))
        self.verticalLayout_3.addWidget(self.openGLWidget)
        self.colorWidget = QtGui.QWidget(self.layoutWidget1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorWidget.sizePolicy().hasHeightForWidth())
        self.colorWidget.setSizePolicy(sizePolicy)
        self.colorWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.colorWidget.setObjectName(_fromUtf8("colorWidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.colorWidget)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.colorGroupBox = QtGui.QGroupBox(self.colorWidget)
        self.colorGroupBox.setObjectName(_fromUtf8("colorGroupBox"))
        self.gridLayout_3.addWidget(self.colorGroupBox, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 0, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.colorWidget)
        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Part Viewer", None))
        self.groupBox.setTitle(_translate("MainWindow", "Part Information", None))
        self.partFileLabel.setText(_translate("MainWindow", "TextLabel", None))
        self.filterGroupBox.setTitle(_translate("MainWindow", "Filter", None))
        self.clearPushButton.setText(_translate("MainWindow", "Clear", None))
        self.filterPushButton.setText(_translate("MainWindow", "Filter", None))
        self.colorGroupBox.setTitle(_translate("MainWindow", "Colors", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))

from glWidget import GLWidget
