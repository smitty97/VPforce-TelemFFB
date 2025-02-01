# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'launcherwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LauncherWindow(object):
    def setupUi(self, LauncherWindow):
        LauncherWindow.setObjectName("LauncherWindow")
        LauncherWindow.resize(236, 253)
        LauncherWindow.setMinimumSize(QtCore.QSize(236, 253))
        LauncherWindow.setMaximumSize(QtCore.QSize(236, 253))
        self.centralwidget = QtWidgets.QWidget(LauncherWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logowidget = QtWidgets.QWidget(self.centralwidget)
        self.logowidget.setMinimumSize(QtCore.QSize(218, 82))
        self.logowidget.setMaximumSize(QtCore.QSize(218, 82))
        self.logowidget.setObjectName("logowidget")
        self.image_label = QtWidgets.QLabel(self.logowidget)
        self.image_label.setGeometry(QtCore.QRect(0, 0, 218, 82))
        self.image_label.setMinimumSize(QtCore.QSize(218, 82))
        self.image_label.setText("")
        self.image_label.setPixmap(QtGui.QPixmap("image/vpforcelogo.png"))
        self.image_label.setObjectName("image_label")
        self.verticalLayout.addWidget(self.logowidget)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)

        self.tb_joystick = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_joystick.setObjectName("tb_joystick")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tb_joystick)
        self.cb_pedals = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_pedals.setObjectName("cb_pedals")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.cb_pedals)
        self.tb_pedals = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_pedals.setObjectName("tb_pedals")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.tb_pedals)

        self.cb_collective = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_collective.setObjectName("cb_collective")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.cb_collective)
        self.tb_collective = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_collective.setObjectName("tb_collective")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tb_collective)

        self.cb_trimwheel = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_trimwheel.setObjectName("cb_trimwheel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.cb_trimwheel)
        self.tb_trimwheel = QtWidgets.QLineEdit(self.centralwidget)
        self.tb_trimwheel.setObjectName("tb_trimwheel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tb_trimwheel)

        self.verticalLayout.addLayout(self.formLayout_2)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.cb_autolaunch = QtWidgets.QCheckBox(self.centralwidget)
        self.cb_autolaunch.setObjectName("cb_autolaunch")
        self.verticalLayout.addWidget(self.cb_autolaunch)
        self.b_launch = QtWidgets.QPushButton(self.centralwidget)
        self.b_launch.setObjectName("b_launch")
        self.verticalLayout.addWidget(self.b_launch)
        LauncherWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LauncherWindow)
        QtCore.QMetaObject.connectSlotsByName(LauncherWindow)

    def retranslateUi(self, LauncherWindow):
        _translate = QtCore.QCoreApplication.translate
        LauncherWindow.setWindowTitle(_translate("LauncherWindow", "TelemFFB MultiLauncher"))
        self.label.setText(_translate("LauncherWindow", "     Joystick"))
        self.tb_joystick.setText(_translate("LauncherWindow", "2055"))
        self.cb_pedals.setText(_translate("LauncherWindow", "Pedals"))
        self.cb_collective.setText(_translate("LauncherWindow", "Collective"))
        self.label_2.setText(_translate("LauncherWindow", "Enter the USB address (default: 2055)"))
        self.cb_autolaunch.setText(_translate("LauncherWindow", "Launch when opened"))
        self.b_launch.setText(_translate("LauncherWindow", "Launch"))
