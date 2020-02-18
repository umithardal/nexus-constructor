# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filewriter_command_frame.ui',
# licensing of 'filewriter_command_frame.ui' applies.
#
# Created: Mon Nov 11 16:21:42 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets
from nexus_constructor.BrokerTopicEdit import BrokerTopicEdit


class Ui_FilewriterCtrl(object):
    def setupUi(self, FilewriterCtrl):
        FilewriterCtrl.setObjectName("FilewriterCtrl")
        FilewriterCtrl.resize(649, 450)
        self.centralwidget = QtWidgets.QWidget(FilewriterCtrl)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.statusLayout = QtWidgets.QVBoxLayout()
        self.statusLayout.setContentsMargins(-1, -1, -1, 0)
        self.statusLayout.setObjectName("statusLayout")
        self.statusTopicLayout = QtWidgets.QHBoxLayout()
        self.statusTopicLayout.setContentsMargins(-1, -1, -1, 0)
        self.statusTopicLayout.setObjectName("statusTopicLayout")
        self.statusBrokerLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusBrokerLabel.setObjectName("statusBrokerLabel")
        self.statusTopicLayout.addWidget(self.statusBrokerLabel)
        self.statusBrokerEdit = BrokerTopicEdit(self.centralwidget)
        self.statusBrokerEdit.setPlaceholderText("address:port/topic")
        self.statusBrokerEdit.setObjectName("statusBrokerEdit")
        self.statusTopicLayout.addWidget(self.statusBrokerEdit)
        self.statusLayout.addLayout(self.statusTopicLayout)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.statusLayout.addWidget(self.line_2)
        self.fileWriterTableGroup = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.fileWriterTableGroup.sizePolicy().hasHeightForWidth()
        )
        self.fileWriterTableGroup.setSizePolicy(sizePolicy)
        self.fileWriterTableGroup.setObjectName("fileWriterTableGroup")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.fileWriterTableGroup)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.fileWritersList = QtWidgets.QTreeView(self.fileWriterTableGroup)
        self.fileWritersList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.fileWritersList.setIndentation(0)
        self.fileWritersList.setObjectName("fileWritersList")
        self.verticalLayout_3.addWidget(self.fileWritersList)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.statusLayout.addWidget(self.fileWriterTableGroup)
        self.filesGroup = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.filesGroup.sizePolicy().hasHeightForWidth())
        self.filesGroup.setSizePolicy(sizePolicy)
        self.filesGroup.setObjectName("filesGroup")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.filesGroup)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.filesList = QtWidgets.QTreeView(self.filesGroup)
        self.filesList.setIndentation(0)
        self.filesList.setObjectName("filesList")
        self.verticalLayout_6.addWidget(self.filesList)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_4.addItem(spacerItem)
        self.stopFileWritingButton = QtWidgets.QPushButton(self.filesGroup)
        self.stopFileWritingButton.setEnabled(False)
        self.stopFileWritingButton.setObjectName("stopFileWritingButton")
        self.horizontalLayout_4.addWidget(self.stopFileWritingButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.statusLayout.addWidget(self.filesGroup)
        self.horizontalLayout.addLayout(self.statusLayout)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.commandLayout = QtWidgets.QVBoxLayout()
        self.commandLayout.setContentsMargins(-1, 0, -1, 0)
        self.commandLayout.setObjectName("commandLayout")
        self.commandBrokerLayout = QtWidgets.QHBoxLayout()
        self.commandBrokerLayout.setObjectName("commandBrokerLayout")
        self.commandBrokerLabel = QtWidgets.QLabel(self.centralwidget)
        self.commandBrokerLabel.setObjectName("commandBrokerLabel")
        self.commandBrokerLayout.addWidget(self.commandBrokerLabel)
        self.commandBrokerEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.commandBrokerEdit.setObjectName("commandBrokerEdit")
        self.commandBrokerLayout.addWidget(self.commandBrokerEdit)
        self.commandLayout.addLayout(self.commandBrokerLayout)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.commandLayout.addWidget(self.line_3)
        self.commandFormLayout = QtWidgets.QFormLayout()
        self.commandFormLayout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.ExpandingFieldsGrow
        )
        self.commandFormLayout.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.commandFormLayout.setFormAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop
        )
        self.commandFormLayout.setObjectName("commandFormLayout")
        self.fileNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.commandFormLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.fileNameLabel
        )
        self.fileNameLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.fileNameLineEdit.setObjectName("fileNameLineEdit")
        self.commandFormLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.fileNameLineEdit
        )
        self.brokerLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.brokerLineEdit.setObjectName("brokerLineEdit")
        self.commandFormLayout.setWidget(
            1, QtWidgets.QFormLayout.FieldRole, self.brokerLineEdit
        )
        self.brokerLabel = QtWidgets.QLabel(self.centralwidget)
        self.brokerLabel.setObjectName("brokerLabel")
        self.commandFormLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.brokerLabel
        )
        self.startTimeLayout = QtWidgets.QHBoxLayout()
        self.startTimeLayout.setObjectName("startTimeLayout")
        self.useStartTimeCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.useStartTimeCheckBox.setText("")
        self.useStartTimeCheckBox.setObjectName("useStartTimeCheckBox")
        self.startTimeLayout.addWidget(self.useStartTimeCheckBox)
        self.startDateTime = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.startDateTime.setEnabled(False)
        self.startDateTime.setObjectName("startDateTime")
        self.startTimeLayout.addWidget(self.startDateTime)
        self.commandFormLayout.setLayout(
            2, QtWidgets.QFormLayout.FieldRole, self.startTimeLayout
        )
        self.startTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.startTimeLabel.setObjectName("startTimeLabel")
        self.commandFormLayout.setWidget(
            2, QtWidgets.QFormLayout.LabelRole, self.startTimeLabel
        )
        self.stopTimeLayout = QtWidgets.QHBoxLayout()
        self.stopTimeLayout.setObjectName("stopTimeLayout")
        self.useStopTimeCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.useStopTimeCheckBox.setText("")
        self.useStopTimeCheckBox.setObjectName("useStopTimeCheckBox")
        self.stopTimeLayout.addWidget(self.useStopTimeCheckBox)
        self.stopDateTime = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.stopDateTime.setEnabled(False)
        self.stopDateTime.setObjectName("stopDateTime")
        self.stopTimeLayout.addWidget(self.stopDateTime)
        self.commandFormLayout.setLayout(
            3, QtWidgets.QFormLayout.FieldRole, self.stopTimeLayout
        )
        self.stopTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.stopTimeLabel.setObjectName("stopTimeLabel")
        self.commandFormLayout.setWidget(
            3, QtWidgets.QFormLayout.LabelRole, self.stopTimeLabel
        )
        self.useSWMRCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.useSWMRCheckBox.setText("")
        self.useSWMRCheckBox.setObjectName("useSWMRCheckBox")
        self.commandFormLayout.setWidget(
            4, QtWidgets.QFormLayout.FieldRole, self.useSWMRCheckBox
        )
        self.swmrLabel = QtWidgets.QLabel(self.centralwidget)
        self.swmrLabel.setObjectName("swmrLabel")
        self.commandFormLayout.setWidget(
            4, QtWidgets.QFormLayout.LabelRole, self.swmrLabel
        )
        self.commandLayout.addLayout(self.commandFormLayout)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.commandLayout.addItem(spacerItem1)
        self.sendCommandLayout = QtWidgets.QHBoxLayout()
        self.sendCommandLayout.setObjectName("sendCommandLayout")
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.sendCommandLayout.addItem(spacerItem2)
        self.sendCommandButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendCommandButton.setEnabled(False)
        self.sendCommandButton.setObjectName("sendCommandButton")
        self.sendCommandLayout.addWidget(self.sendCommandButton)
        self.commandLayout.addLayout(self.sendCommandLayout)
        self.horizontalLayout.addLayout(self.commandLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        FilewriterCtrl.setCentralWidget(self.centralwidget)

        self.retranslateUi(FilewriterCtrl)
        QtCore.QMetaObject.connectSlotsByName(FilewriterCtrl)

    def retranslateUi(self, FilewriterCtrl):
        FilewriterCtrl.setWindowTitle(
            QtWidgets.QApplication.translate("FilewriterCtrl", "MainWindow", None, -1)
        )
        self.statusBrokerLabel.setText(
            QtWidgets.QApplication.translate(
                "FilewriterCtrl", "Status broker", None, -1
            )
        )
        self.fileWriterTableGroup.setTitle(
            QtWidgets.QApplication.translate("FilewriterCtrl", "File-writers", None, -1)
        )
        self.filesGroup.setTitle(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Files", None, -1)
        )
        self.stopFileWritingButton.setText(
            QtWidgets.QApplication.translate(
                "FilewriterCtrl", "Stop file-writing", None, -1
            )
        )
        self.commandBrokerLabel.setText(
            QtWidgets.QApplication.translate(
                "FilewriterCtrl", "Command broker", None, -1
            )
        )
        self.commandBrokerEdit.setPlaceholderText(
            QtWidgets.QApplication.translate(
                "FilewriterCtrl", "address:port/topic", None, -1
            )
        )
        self.fileNameLabel.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "File name", None, -1)
        )
        self.brokerLineEdit.setPlaceholderText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "address:port", None, -1)
        )
        self.brokerLabel.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Broker", None, -1)
        )
        self.startTimeLabel.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Start time", None, -1)
        )
        self.stopTimeLabel.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Stop time", None, -1)
        )
        self.swmrLabel.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Use SWMR", None, -1)
        )
        self.sendCommandButton.setText(
            QtWidgets.QApplication.translate("FilewriterCtrl", "Send command", None, -1)
        )
