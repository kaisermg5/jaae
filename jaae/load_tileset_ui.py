# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/load_tileset.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoadTilesetDialog(object):
    def setupUi(self, LoadTilesetDialog):
        LoadTilesetDialog.setObjectName("LoadTilesetDialog")
        LoadTilesetDialog.resize(400, 235)
        self.gridLayout = QtWidgets.QGridLayout(LoadTilesetDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(LoadTilesetDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.amap_tileset_number_txt = QtWidgets.QLineEdit(self.groupBox)
        self.amap_tileset_number_txt.setObjectName("amap_tileset_number_txt")
        self.gridLayout_2.addWidget(self.amap_tileset_number_txt, 1, 1, 1, 1)
        self.translate_btn = QtWidgets.QPushButton(self.groupBox)
        self.translate_btn.setObjectName("translate_btn")
        self.gridLayout_2.addWidget(self.translate_btn, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 2, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 3)
        self.label = QtWidgets.QLabel(LoadTilesetDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.tileset_header_txt = QtWidgets.QLineEdit(LoadTilesetDialog)
        self.tileset_header_txt.setObjectName("tileset_header_txt")
        self.gridLayout.addWidget(self.tileset_header_txt, 1, 1, 1, 1)
        self.load_tileset_btn = QtWidgets.QPushButton(LoadTilesetDialog)
        self.load_tileset_btn.setObjectName("load_tileset_btn")
        self.gridLayout.addWidget(self.load_tileset_btn, 2, 1, 1, 1)

        self.retranslateUi(LoadTilesetDialog)
        QtCore.QMetaObject.connectSlotsByName(LoadTilesetDialog)

    def retranslateUi(self, LoadTilesetDialog):
        _translate = QtCore.QCoreApplication.translate
        LoadTilesetDialog.setWindowTitle(_translate("LoadTilesetDialog", "Load Tileset"))
        self.groupBox.setTitle(_translate("LoadTilesetDialog", "A-map"))
        self.translate_btn.setText(_translate("LoadTilesetDialog", "Translate to header offset"))
        self.label_2.setText(_translate("LoadTilesetDialog", "That thing LUHO called \n"
"tileset number for some\n"
"reason:"))
        self.label.setText(_translate("LoadTilesetDialog", "Tileset header offset:"))
        self.load_tileset_btn.setText(_translate("LoadTilesetDialog", "Load tileset"))

