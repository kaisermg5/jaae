# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/insert_to_rom.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InsertToRomDialog(object):
    def setupUi(self, InsertToRomDialog):
        InsertToRomDialog.setObjectName("InsertToRomDialog")
        InsertToRomDialog.resize(586, 300)
        self.gridLayout = QtWidgets.QGridLayout(InsertToRomDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(InsertToRomDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.needed_bytes_label = QtWidgets.QLabel(self.groupBox)
        self.needed_bytes_label.setAlignment(QtCore.Qt.AlignCenter)
        self.needed_bytes_label.setObjectName("needed_bytes_label")
        self.gridLayout_2.addWidget(self.needed_bytes_label, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.free_space_txt = QtWidgets.QLineEdit(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.free_space_txt.sizePolicy().hasHeightForWidth())
        self.free_space_txt.setSizePolicy(sizePolicy)
        self.free_space_txt.setObjectName("free_space_txt")
        self.gridLayout_2.addWidget(self.free_space_txt, 1, 1, 1, 1)
        self.insert_btn = QtWidgets.QPushButton(self.groupBox)
        self.insert_btn.setObjectName("insert_btn")
        self.gridLayout_2.addWidget(self.insert_btn, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 1, 1, 1)
        self.output_txt = QtWidgets.QTextEdit(self.groupBox)
        self.output_txt.setReadOnly(True)
        self.output_txt.setObjectName("output_txt")
        self.gridLayout_2.addWidget(self.output_txt, 0, 2, 4, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(InsertToRomDialog)
        QtCore.QMetaObject.connectSlotsByName(InsertToRomDialog)

    def retranslateUi(self, InsertToRomDialog):
        _translate = QtCore.QCoreApplication.translate
        InsertToRomDialog.setWindowTitle(_translate("InsertToRomDialog", "Insert to ROM"))
        self.groupBox.setTitle(_translate("InsertToRomDialog", "Insert animations"))
        self.needed_bytes_label.setText(_translate("InsertToRomDialog", "0"))
        self.label.setText(_translate("InsertToRomDialog", "Free space offset:"))
        self.label_2.setText(_translate("InsertToRomDialog", "Needed bytes:"))
        self.insert_btn.setText(_translate("InsertToRomDialog", "Insert to ROM"))

