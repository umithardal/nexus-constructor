# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transformation.ui',
# licensing of 'transformation.ui' applies.
#
# Created: Wed Jul 17 14:07:33 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Transformation(object):
    def setupUi(self, Transformation):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Transformation)
        self.verticalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setSpacing(7)
        self.mainLayout.setObjectName("mainLayout")
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.setSpacing(-1)
        self.nameLayout.setObjectName("nameLayout")
        self.nameLabel = QtWidgets.QLabel(Transformation)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(Transformation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLineEdit.sizePolicy().hasHeightForWidth())
        self.nameLineEdit.setSizePolicy(sizePolicy)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLayout.addWidget(self.nameLineEdit)
        self.mainLayout.addLayout(self.nameLayout)
        self.line = QtWidgets.QFrame(Transformation)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.mainLayout.addWidget(self.line)
        self.vectorLabel = QtWidgets.QLabel(Transformation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vectorLabel.sizePolicy().hasHeightForWidth())
        self.vectorLabel.setSizePolicy(sizePolicy)
        self.vectorLabel.setObjectName("vectorLabel")
        self.mainLayout.addWidget(self.vectorLabel)
        self.vectorLayout = QtWidgets.QHBoxLayout()
        self.vectorLayout.setSpacing(-1)
        self.vectorLayout.setObjectName("vectorLayout")
        self.xPosLabel = QtWidgets.QLabel(Transformation)
        self.xPosLabel.setObjectName("xPosLabel")
        self.vectorLayout.addWidget(self.xPosLabel)
        self.xLineEdit = QtWidgets.QDoubleSpinBox(Transformation)
        self.xLineEdit.setObjectName("xLineEdit")
        self.vectorLayout.addWidget(self.xLineEdit)
        self.yPosLabel = QtWidgets.QLabel(Transformation)
        self.yPosLabel.setObjectName("yPosLabel")
        self.vectorLayout.addWidget(self.yPosLabel)
        self.yLineEdit = QtWidgets.QDoubleSpinBox(Transformation)
        self.yLineEdit.setObjectName("yLineEdit")
        self.vectorLayout.addWidget(self.yLineEdit)
        self.zPosLabel = QtWidgets.QLabel(Transformation)
        self.zPosLabel.setObjectName("zPosLabel")
        self.vectorLayout.addWidget(self.zPosLabel)
        self.zLineEdit = QtWidgets.QDoubleSpinBox(Transformation)
        self.zLineEdit.setObjectName("zLineEdit")
        self.vectorLayout.addWidget(self.zLineEdit)
        self.mainLayout.addLayout(self.vectorLayout)
        self.line_3 = QtWidgets.QFrame(Transformation)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.mainLayout.addWidget(self.line_3)
        self.lengthLayout = QtWidgets.QHBoxLayout()
        self.lengthLayout.setSpacing(-1)
        self.lengthLayout.setObjectName("lengthLayout")
        self.valueLabel = QtWidgets.QLabel(Transformation)
        self.valueLabel.setObjectName("valueLabel")
        self.lengthLayout.addWidget(self.valueLabel)
        self.valueLineEdit = QtWidgets.QDoubleSpinBox(Transformation)
        self.valueLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.valueLineEdit.setObjectName("valueLineEdit")
        self.lengthLayout.addWidget(self.valueLineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.lengthLayout.addItem(spacerItem)
        self.line_2 = QtWidgets.QFrame(Transformation)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.lengthLayout.addWidget(self.line_2)
        self.editButton = QtWidgets.QPushButton(Transformation)
        self.editButton.setObjectName("editButton")
        self.lengthLayout.addWidget(self.editButton)
        self.mainLayout.addLayout(self.lengthLayout)
        self.verticalLayout_2.addLayout(self.mainLayout)

        self.retranslateUi(Transformation)
        QtCore.QMetaObject.connectSlotsByName(Transformation)

    def retranslateUi(self, Transformation):
        Transformation.setWindowTitle(QtWidgets.QApplication.translate("Transformation", "GroupBox", None, -1))
        Transformation.setTitle(QtWidgets.QApplication.translate("Transformation", "Translation", None, -1))
        self.nameLabel.setText(QtWidgets.QApplication.translate("Transformation", "Name", None, -1))
        self.vectorLabel.setText(QtWidgets.QApplication.translate("Transformation", "Vector", None, -1))
        self.xPosLabel.setText(QtWidgets.QApplication.translate("Transformation", "x", None, -1))
        self.yPosLabel.setText(QtWidgets.QApplication.translate("Transformation", "y", None, -1))
        self.zPosLabel.setText(QtWidgets.QApplication.translate("Transformation", "z", None, -1))
        self.valueLabel.setText(QtWidgets.QApplication.translate("Transformation", "Length", None, -1))
        self.editButton.setText(QtWidgets.QApplication.translate("Transformation", "Edit", None, -1))

