# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'advanced_spring.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdvancedSpringDialog(object):
    def setupUi(self, AdvancedSpringDialog):
        AdvancedSpringDialog.setObjectName("AdvancedSpringDialog")
        AdvancedSpringDialog.resize(561, 835)
        self.gridLayout_2 = QtWidgets.QGridLayout(AdvancedSpringDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 3, 1, 1)
        self.pb_copy_down = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_copy_down.setObjectName("pb_copy_down")
        self.gridLayout_3.addWidget(self.pb_copy_down, 0, 2, 1, 1)
        self.pb_copy_up = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_copy_up.setObjectName("pb_copy_up")
        self.gridLayout_3.addWidget(self.pb_copy_up, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tog_live_view = LabeledToggle(AdvancedSpringDialog)
        self.tog_live_view.setObjectName("tog_live_view")
        self.horizontalLayout.addWidget(self.tog_live_view)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 1, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(AdvancedSpringDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.pb_airspeed_neg_hundred = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_airspeed_neg_hundred.setMaximumSize(QtCore.QSize(25, 16777215))
        self.pb_airspeed_neg_hundred.setObjectName("pb_airspeed_neg_hundred")
        self.horizontalLayout_5.addWidget(self.pb_airspeed_neg_hundred)
        self.pb_airspeed_neg_ten = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_airspeed_neg_ten.setMaximumSize(QtCore.QSize(25, 16777215))
        self.pb_airspeed_neg_ten.setObjectName("pb_airspeed_neg_ten")
        self.horizontalLayout_5.addWidget(self.pb_airspeed_neg_ten)
        self.pb_airspeed_manual = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_airspeed_manual.setObjectName("pb_airspeed_manual")
        self.horizontalLayout_5.addWidget(self.pb_airspeed_manual)
        self.pb_airspeed_pos_ten = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_airspeed_pos_ten.setMaximumSize(QtCore.QSize(25, 16777215))
        self.pb_airspeed_pos_ten.setObjectName("pb_airspeed_pos_ten")
        self.horizontalLayout_5.addWidget(self.pb_airspeed_pos_ten)
        self.pb_airspeed_pos_hundred = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_airspeed_pos_hundred.setMaximumSize(QtCore.QSize(25, 16777215))
        self.pb_airspeed_pos_hundred.setObjectName("pb_airspeed_pos_hundred")
        self.horizontalLayout_5.addWidget(self.pb_airspeed_pos_hundred)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.label = QtWidgets.QLabel(AdvancedSpringDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.cb_airspeed_unit = QtWidgets.QComboBox(AdvancedSpringDialog)
        self.cb_airspeed_unit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cb_airspeed_unit.setObjectName("cb_airspeed_unit")
        self.horizontalLayout_5.addWidget(self.cb_airspeed_unit)
        self.gridLayout.addLayout(self.horizontalLayout_5, 4, 1, 1, 1)
        self.line = QtWidgets.QFrame(AdvancedSpringDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 5, 0, 1, 2)
        self.frame = QtWidgets.QFrame(AdvancedSpringDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(300, 300))
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.lab_x_mastergain = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lab_x_mastergain.sizePolicy().hasHeightForWidth())
        self.lab_x_mastergain.setSizePolicy(sizePolicy)
        self.lab_x_mastergain.setObjectName("lab_x_mastergain")
        self.gridLayout_6.addWidget(self.lab_x_mastergain, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout_6.addWidget(self.label_5, 0, 1, 1, 1)
        self.sl_x_mastergain = QtWidgets.QSlider(self.frame)
        self.sl_x_mastergain.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sl_x_mastergain.sizePolicy().hasHeightForWidth())
        self.sl_x_mastergain.setSizePolicy(sizePolicy)
        self.sl_x_mastergain.setMinimumSize(QtCore.QSize(0, 0))
        self.sl_x_mastergain.setMaximum(100)
        self.sl_x_mastergain.setPageStep(1)
        self.sl_x_mastergain.setOrientation(QtCore.Qt.Horizontal)
        self.sl_x_mastergain.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl_x_mastergain.setTickInterval(5)
        self.sl_x_mastergain.setObjectName("sl_x_mastergain")
        self.gridLayout_6.addWidget(self.sl_x_mastergain, 1, 0, 1, 1)
        self.cb_x_smoothcurve = Toggle(self.frame)
        self.cb_x_smoothcurve.setText("")
        self.cb_x_smoothcurve.setObjectName("cb_x_smoothcurve")
        self.gridLayout_6.addWidget(self.cb_x_smoothcurve, 1, 1, 1, 1)
        self.pb_x_reset = QtWidgets.QPushButton(self.frame)
        self.pb_x_reset.setObjectName("pb_x_reset")
        self.gridLayout_6.addWidget(self.pb_x_reset, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_6)
        self.line_2 = QtWidgets.QFrame(self.frame)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_2.addWidget(self.line_2)
        self.curve_x = SpringCurveWidget(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.curve_x.sizePolicy().hasHeightForWidth())
        self.curve_x.setSizePolicy(sizePolicy)
        self.curve_x.setMinimumSize(QtCore.QSize(300, 200))
        self.curve_x.setStyleSheet("")
        self.curve_x.setObjectName("curve_x")
        self.verticalLayout_2.addWidget(self.curve_x)
        self.gridLayout.addWidget(self.frame, 1, 1, 1, 1)
        self.frame_2 = QtWidgets.QFrame(AdvancedSpringDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(300, 300))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.lab_y_mastergain = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lab_y_mastergain.sizePolicy().hasHeightForWidth())
        self.lab_y_mastergain.setSizePolicy(sizePolicy)
        self.lab_y_mastergain.setObjectName("lab_y_mastergain")
        self.gridLayout_4.addWidget(self.lab_y_mastergain, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 0, 1, 1, 1)
        self.sl_y_mastergain = QtWidgets.QSlider(self.frame_2)
        self.sl_y_mastergain.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sl_y_mastergain.sizePolicy().hasHeightForWidth())
        self.sl_y_mastergain.setSizePolicy(sizePolicy)
        self.sl_y_mastergain.setMinimumSize(QtCore.QSize(0, 0))
        self.sl_y_mastergain.setMaximum(100)
        self.sl_y_mastergain.setPageStep(1)
        self.sl_y_mastergain.setOrientation(QtCore.Qt.Horizontal)
        self.sl_y_mastergain.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl_y_mastergain.setTickInterval(5)
        self.sl_y_mastergain.setObjectName("sl_y_mastergain")
        self.gridLayout_4.addWidget(self.sl_y_mastergain, 1, 0, 1, 1)
        self.cb_y_smoothcurve = Toggle(self.frame_2)
        self.cb_y_smoothcurve.setText("")
        self.cb_y_smoothcurve.setObjectName("cb_y_smoothcurve")
        self.gridLayout_4.addWidget(self.cb_y_smoothcurve, 1, 1, 1, 1)
        self.pb_y_reset = QtWidgets.QPushButton(self.frame_2)
        self.pb_y_reset.setObjectName("pb_y_reset")
        self.gridLayout_4.addWidget(self.pb_y_reset, 1, 2, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_4)
        self.line_3 = QtWidgets.QFrame(self.frame_2)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_3.addWidget(self.line_3)
        self.curve_y = SpringCurveWidget(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.curve_y.sizePolicy().hasHeightForWidth())
        self.curve_y.setSizePolicy(sizePolicy)
        self.curve_y.setMinimumSize(QtCore.QSize(300, 200))
        self.curve_y.setStyleSheet("")
        self.curve_y.setObjectName("curve_y")
        self.verticalLayout_3.addWidget(self.curve_y)
        self.gridLayout.addWidget(self.frame_2, 3, 1, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout.addLayout(self.horizontalLayout_4, 7, 1, 1, 1)
        self.lab_y = QtWidgets.QLabel(AdvancedSpringDialog)
        font = QtGui.QFont()
        font.setFamily("Artifakt Element Heavy")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.lab_y.setFont(font)
        self.lab_y.setObjectName("lab_y")
        self.gridLayout.addWidget(self.lab_y, 3, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.lab_x = QtWidgets.QLabel(AdvancedSpringDialog)
        font = QtGui.QFont()
        font.setFamily("Artifakt Element Heavy")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.lab_x.setFont(font)
        self.lab_x.setObjectName("lab_x")
        self.gridLayout.addWidget(self.lab_x, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pb_cancel = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_cancel.setObjectName("pb_cancel")
        self.horizontalLayout_3.addWidget(self.pb_cancel)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.pb_revert = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_revert.setObjectName("pb_revert")
        self.horizontalLayout_3.addWidget(self.pb_revert)
        self.pb_save = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_save.setObjectName("pb_save")
        self.horizontalLayout_3.addWidget(self.pb_save)
        self.pb_saveclose = QtWidgets.QPushButton(AdvancedSpringDialog)
        self.pb_saveclose.setObjectName("pb_saveclose")
        self.horizontalLayout_3.addWidget(self.pb_saveclose)
        self.gridLayout.addLayout(self.horizontalLayout_3, 6, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(AdvancedSpringDialog)
        QtCore.QMetaObject.connectSlotsByName(AdvancedSpringDialog)

    def retranslateUi(self, AdvancedSpringDialog):
        _translate = QtCore.QCoreApplication.translate
        AdvancedSpringDialog.setWindowTitle(_translate("AdvancedSpringDialog", "Advanced Spring"))
        self.pb_copy_down.setText(_translate("AdvancedSpringDialog", "dn"))
        self.pb_copy_up.setText(_translate("AdvancedSpringDialog", "up"))
        self.tog_live_view.setText(_translate("AdvancedSpringDialog", "Live View"))
        self.label_2.setText(_translate("AdvancedSpringDialog", "Airspeed Range:"))
        self.pb_airspeed_neg_hundred.setText(_translate("AdvancedSpringDialog", "LL"))
        self.pb_airspeed_neg_ten.setText(_translate("AdvancedSpringDialog", "L"))
        self.pb_airspeed_manual.setText(_translate("AdvancedSpringDialog", "Manual"))
        self.pb_airspeed_pos_ten.setText(_translate("AdvancedSpringDialog", "R"))
        self.pb_airspeed_pos_hundred.setText(_translate("AdvancedSpringDialog", "RR"))
        self.label.setText(_translate("AdvancedSpringDialog", "Airspeed Unit (IAS):"))
        self.lab_x_mastergain.setText(_translate("AdvancedSpringDialog", "Axis Master Gain:"))
        self.label_5.setText(_translate("AdvancedSpringDialog", "Enable Smooth Curve:"))
        self.pb_x_reset.setText(_translate("AdvancedSpringDialog", "  Reset  "))
        self.lab_y_mastergain.setText(_translate("AdvancedSpringDialog", "Axis Master Gain:"))
        self.label_3.setText(_translate("AdvancedSpringDialog", "Enable Smooth Curve:"))
        self.pb_y_reset.setText(_translate("AdvancedSpringDialog", "  Reset  "))
        self.lab_y.setText(_translate("AdvancedSpringDialog", "<html><head/><body><p><span style=\" color:#ab37c8;\">Y</span></p></body></html>"))
        self.lab_x.setText(_translate("AdvancedSpringDialog", "<html><head/><body><p><span style=\" color:#ab37c8;\">X</span></p></body></html>"))
        self.pb_cancel.setText(_translate("AdvancedSpringDialog", "Cancel"))
        self.pb_revert.setText(_translate("AdvancedSpringDialog", "Revert"))
        self.pb_save.setText(_translate("AdvancedSpringDialog", "Save"))
        self.pb_saveclose.setText(_translate("AdvancedSpringDialog", "Save && Close"))
from telemffb.custom_widgets import LabeledToggle, SpringCurveWidget, Toggle
