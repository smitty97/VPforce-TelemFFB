# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sc_overrides.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SCOverridesDialog(object):
    def setupUi(self, SCOverridesDialog):
        SCOverridesDialog.setObjectName("SCOverridesDialog")
        SCOverridesDialog.resize(728, 409)
        self.verticalLayout = QtWidgets.QVBoxLayout(SCOverridesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 1, -1, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(SCOverridesDialog)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.tb_pattern = QtWidgets.QLineEdit(SCOverridesDialog)
        self.tb_pattern.setEnabled(False)
        self.tb_pattern.setMinimumSize(QtCore.QSize(250, 0))
        self.tb_pattern.setObjectName("tb_pattern")
        self.horizontalLayout_2.addWidget(self.tb_pattern)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_6 = QtWidgets.QLabel(SCOverridesDialog)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, 5, -1, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(SCOverridesDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(SCOverridesDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(SCOverridesDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 4, 1, 1)
        self.cb_name = QtWidgets.QComboBox(SCOverridesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cb_name.sizePolicy().hasHeightForWidth())
        self.cb_name.setSizePolicy(sizePolicy)
        self.cb_name.setMinimumSize(QtCore.QSize(100, 0))
        self.cb_name.setMaximumSize(QtCore.QSize(150, 16777215))
        self.cb_name.setObjectName("cb_name")
        self.gridLayout.addWidget(self.cb_name, 1, 0, 1, 1)
        self.tb_scale = QtWidgets.QLineEdit(SCOverridesDialog)
        self.tb_scale.setMaximumSize(QtCore.QSize(50, 16777215))
        self.tb_scale.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        self.tb_scale.setObjectName("tb_scale")
        self.gridLayout.addWidget(self.tb_scale, 1, 4, 1, 1)
        self.pb_add = QtWidgets.QPushButton(SCOverridesDialog)
        self.pb_add.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pb_add.setObjectName("pb_add")
        self.gridLayout.addWidget(self.pb_add, 1, 5, 1, 1)
        self.label = QtWidgets.QLabel(SCOverridesDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.tb_var = QtWidgets.QLineEdit(SCOverridesDialog)
        self.tb_var.setMinimumSize(QtCore.QSize(200, 0))
        self.tb_var.setObjectName("tb_var")
        self.gridLayout.addWidget(self.tb_var, 1, 1, 1, 1)
        self.cb_sc_unit = QtWidgets.QComboBox(SCOverridesDialog)
        self.cb_sc_unit.setMinimumSize(QtCore.QSize(100, 0))
        self.cb_sc_unit.setEditable(True)
        self.cb_sc_unit.setObjectName("cb_sc_unit")
        self.cb_sc_unit.addItem("")
        self.cb_sc_unit.setItemText(0, "")
        self.cb_sc_unit.addItem("")
        self.cb_sc_unit.addItem("")
        self.cb_sc_unit.addItem("")
        self.cb_sc_unit.addItem("")
        self.gridLayout.addWidget(self.cb_sc_unit, 1, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tableWidget = QtWidgets.QTableWidget(SCOverridesDialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pb_delete = QtWidgets.QPushButton(SCOverridesDialog)
        self.pb_delete.setObjectName("pb_delete")
        self.horizontalLayout.addWidget(self.pb_delete)
        self.bottomlabel = QtWidgets.QLabel(SCOverridesDialog)
        self.bottomlabel.setMinimumSize(QtCore.QSize(300, 0))
        self.bottomlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bottomlabel.setObjectName("bottomlabel")
        self.horizontalLayout.addWidget(self.bottomlabel)
        self.buttonBox = QtWidgets.QDialogButtonBox(SCOverridesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SCOverridesDialog)
        self.buttonBox.accepted.connect(SCOverridesDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(SCOverridesDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(SCOverridesDialog)

    def retranslateUi(self, SCOverridesDialog):
        _translate = QtCore.QCoreApplication.translate
        SCOverridesDialog.setWindowTitle(_translate("SCOverridesDialog", "SimConnect Overrides"))
        self.label_5.setText(_translate("SCOverridesDialog", "Editing Overrides for model:"))
        self.label_6.setText(_translate("SCOverridesDialog", "Changes are saved immediately"))
        self.label_2.setText(_translate("SCOverridesDialog", "Variable"))
        self.label_3.setText(_translate("SCOverridesDialog", "SC Unit"))
        self.label_4.setText(_translate("SCOverridesDialog", "Scale"))
        self.pb_add.setText(_translate("SCOverridesDialog", "Add"))
        self.label.setText(_translate("SCOverridesDialog", "Telem Property"))
        self.cb_sc_unit.setItemText(1, _translate("SCOverridesDialog", "bool"))
        self.cb_sc_unit.setItemText(2, _translate("SCOverridesDialog", "enum"))
        self.cb_sc_unit.setItemText(3, _translate("SCOverridesDialog", "number"))
        self.cb_sc_unit.setItemText(4, _translate("SCOverridesDialog", "Percent Over 100"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SCOverridesDialog", "Property"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SCOverridesDialog", "SC Variable"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SCOverridesDialog", "SC Unit"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("SCOverridesDialog", "Scale"))
        self.pb_delete.setText(_translate("SCOverridesDialog", "Delete Checked"))
        self.bottomlabel.setText(_translate("SCOverridesDialog", "SimConnect overrides are for MSFS only."))
