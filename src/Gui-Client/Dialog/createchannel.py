
from PySide6 import QtCore, QtGui, QtWidgets


class CreatChannelWindow(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(202, 157)
        Dialog.setStyleSheet("QGroupBox {\n"
"    border: 1px solid #2e2c2c;\n"
"    margin-top: 5ex;\n"
"   /* leave space at the top for the title */\n"
"}\n"
"#miscgroupBox {\n"
"    margin-top: 0ex;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top left;\n"
"   /* position at the top center */\n"
"    padding: 5px;\n"
"}\n"
"QPushButton {\n"
"    background-color:grey;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color:grey;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #1f1f1f;\n"
"}\n"
"QHeaderView::section {\n"
"    background-color: #1f1f1f;\n"
"    border: 1px solid #333333;\n"
"    color: #f0f0f0;\n"
"}\n"
"QWidget {\n"
"    background-color: black;\n"
"    color: #f0f0f0;\n"
"}\n"
"QLineEdit {\n"
"    color: #f0f0f0;\n"
"    border: 1px solid #2e2c2c;\n"
"}\n"
"QTableWidget {\n"
"    background-color: #1f1f1f;\n"
"    color: #f0f0f0;\n"
"    gridline-color: #555454;\n"
"    border: 1px solid #333030;\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color:#2e2c2c;\n"
"}\n"
"QToolButton {\n"
"    background-color: #2e2c2c;\n"
"    color: #f0f0f0;\n"
"}\n"
"QRadioButton {\n"
"    color: #f0f0f0;\n"
"    border: none;\n"
"}\n"
"QToolButton:hover {\n"
"    background-color: #1f1f1f;\n"
"}\n"
"\n"
"#dateslist, #usernamelist, #messageslist, #onlineuserslist, #channelslist {\n"
"   background-color: rgb(0, 0, 0);\n"
"}\n"
"\n"
"#username_list {\n"
"color: #319be6;\n"
"}\n"
"\n"
"#usernamelb {\n"
"background-color: black;\n"
"}\n"
"\n"
"\n"
"#toptitlelb, #bottomlb, #messagedivider, #clearbutton, #sendbutton, #leavebutton, #frame, #helpbutton, #settingsbutton {\n"
"   background-color: rgb(30, 30, 30);\n"
"}\n"
"\n"
"#frame, #inputbox {\n"
"background-color: rgb(0,0, 0);\n"
"}\n"
"\n"
"#usernamelist, #usernamelb {\n"
"   color: #319be6;\n"
"   border: 0px;\n"
"   text-align: \'right\';\n"
"}\n"
"\n"
"\n"
"QPlainTextEdit{    \n"
"   color: rgb(0, 173, 13);\n"
"   border: 0px;\n"
"   outline: none;\n"
"}\n"
"\n"
"#sendbutton, #clearbutton, #leavebutton, #settingsbutton, #helpbutton {\n"
"color: green;\n"
"}\n"
"\n"
"#sendbutton:hover {\n"
"    background-color: #2e2c2c;\n"
"}\n"
"\n"
"QListWidget{\n"
"color: rgb(0, 173, 13);\n"
"border: 0px;\n"
"}\n"
"\n"
"#ServerTable {\n"
"border-color:#2e2c2c;\n"
"}\n"
"\n"
"QLabel {\n"
"   color: #f0f0f0;\n"
"}\n"
"\n"
"#usernamelist {\n"
"border-right: 1px solid #1f1f1f;;\n"
"}\n"
"\n"
"#userslabel, #channelslabel {\n"
"border: 1px solid #1f1f1f;\n"
"}\n"
"\n"
"#messageslist, #channelslabel, #channelslist, #onlineuserslist{\n"
"border-left: 1px solid #1f1f1f;\n"
"border-right: 1px solid #1f1f1f;\n"
"}\n"
"\n"
"")
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.createchannelbutton = QtWidgets.QPushButton(Dialog)
        self.createchannelbutton.setObjectName("createchannelbutton")
        self.gridLayout.addWidget(self.createchannelbutton, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 3, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.channelname = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.channelname.sizePolicy().hasHeightForWidth())
        self.channelname.setSizePolicy(sizePolicy)
        self.channelname.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.channelname.setObjectName("channelname")
        self.verticalLayout.addWidget(self.channelname)
        self.channelpassword = QtWidgets.QLineEdit(Dialog)
        self.channelpassword.setEnabled(True)
        self.channelpassword.setObjectName("channelpassword")
        self.verticalLayout.addWidget(self.channelpassword)
        self.privateradio = QtWidgets.QRadioButton(Dialog)
        self.privateradio.setObjectName("privateradio")
        self.verticalLayout.addWidget(self.privateradio)
        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 4)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.createchannelbutton.setText(_translate("Dialog", "Create Channel"))
        self.channelname.setPlaceholderText(_translate("Dialog", "Channel Name"))
        self.channelpassword.setPlaceholderText(_translate("Dialog", "Password"))
        self.privateradio.setText(_translate("Dialog", "Private Channel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = CreatChannelWindow()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
