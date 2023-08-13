from PySide6 import QtCore, QtGui, QtWidgets


class Ui_ChatWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1125, 695)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet("QGroupBox {\n"
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
"    background-color: #1f1f1f;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color:red;\n"
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
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.clearbutton = QtWidgets.QPushButton(self.frame)
        self.clearbutton.setObjectName("clearbutton")
        self.gridLayout_7.addWidget(self.clearbutton, 2, 4, 1, 1)
        self.sendbutton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sendbutton.sizePolicy().hasHeightForWidth())
        self.sendbutton.setSizePolicy(sizePolicy)
        self.sendbutton.setAutoFillBackground(False)
        self.sendbutton.setObjectName("sendbutton")
        self.gridLayout_7.addWidget(self.sendbutton, 0, 4, 2, 1)
        self.inputbox = QtWidgets.QPlainTextEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(7)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputbox.sizePolicy().hasHeightForWidth())
        self.inputbox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.inputbox.setFont(font)
        self.inputbox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.inputbox.setPlainText("")
        self.inputbox.setObjectName("inputbox")
        self.gridLayout_7.addWidget(self.inputbox, 0, 2, 3, 1)
        self.usernamelb = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.usernamelb.sizePolicy().hasHeightForWidth())
        self.usernamelb.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(True)
        self.usernamelb.setFont(font)
        self.usernamelb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.usernamelb.setObjectName("usernamelb")
        self.gridLayout_7.addWidget(self.usernamelb, 0, 1, 2, 1)
        self.gridLayout_5.addWidget(self.frame, 3, 0, 2, 1)
        self.bottomlb = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bottomlb.sizePolicy().hasHeightForWidth())
        self.bottomlb.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.bottomlb.setFont(font)
        self.bottomlb.setAutoFillBackground(False)
        self.bottomlb.setObjectName("bottomlb")
        self.gridLayout_5.addWidget(self.bottomlb, 0, 0, 3, 1)
        self.gridLayout.addLayout(self.gridLayout_5, 2, 0, 2, 8)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toptitlelb = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toptitlelb.sizePolicy().hasHeightForWidth())
        self.toptitlelb.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.toptitlelb.setFont(font)
        self.toptitlelb.setAutoFillBackground(False)
        self.toptitlelb.setScaledContents(True)
        self.toptitlelb.setObjectName("toptitlelb")
        self.horizontalLayout.addWidget(self.toptitlelb)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.settingsbutton = QtWidgets.QToolButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingsbutton.sizePolicy().hasHeightForWidth())
        self.settingsbutton.setSizePolicy(sizePolicy)
        self.settingsbutton.setObjectName("settingsbutton")
        self.horizontalLayout_3.addWidget(self.settingsbutton)
        self.leavebutton = QtWidgets.QToolButton(self.centralwidget)
        self.leavebutton.setObjectName("leavebutton")
        self.horizontalLayout_3.addWidget(self.leavebutton)
        self.helpbutton = QtWidgets.QToolButton(self.centralwidget)
        self.helpbutton.setObjectName("helpbutton")
        self.horizontalLayout_3.addWidget(self.helpbutton)
        self.horizontalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.setStretch(0, 4)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 7)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.messageslist = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.messageslist.sizePolicy().hasHeightForWidth())
        self.messageslist.setSizePolicy(sizePolicy)
        self.messageslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.messageslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messageslist.setObjectName("messageslist")
        item = QtWidgets.QListWidgetItem()
        self.messageslist.addItem(item)
        self.horizontalLayout_11.addWidget(self.messageslist)
        self.horizontalLayout_11.setStretch(0, 1)
        self.gridLayout.addLayout(self.horizontalLayout_11, 1, 2, 1, 5)
        self.userslabel = QtWidgets.QLabel(self.centralwidget)
        self.userslabel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.userslabel.sizePolicy().hasHeightForWidth())
        self.userslabel.setSizePolicy(sizePolicy)
        self.userslabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.userslabel.setObjectName("userslabel")
        self.gridLayout.addWidget(self.userslabel, 0, 7, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_5.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.dateslist = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateslist.sizePolicy().hasHeightForWidth())
        self.dateslist.setSizePolicy(sizePolicy)
        self.dateslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dateslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dateslist.setObjectName("dateslist")
        item = QtWidgets.QListWidgetItem()
        self.dateslist.addItem(item)
        self.horizontalLayout_5.addWidget(self.dateslist)
        self.usernamelist = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.usernamelist.sizePolicy().hasHeightForWidth())
        self.usernamelist.setSizePolicy(sizePolicy)
        self.usernamelist.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.usernamelist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.usernamelist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.usernamelist.setObjectName("usernamelist")
        item = QtWidgets.QListWidgetItem()
        self.usernamelist.addItem(item)
        self.horizontalLayout_5.addWidget(self.usernamelist)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 0, 1, 2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.onlineuserslist = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.onlineuserslist.sizePolicy().hasHeightForWidth())
        self.onlineuserslist.setSizePolicy(sizePolicy)
        self.onlineuserslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.onlineuserslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.onlineuserslist.setObjectName("onlineuserslist")
        item = QtWidgets.QListWidgetItem()
        self.onlineuserslist.addItem(item)
        self.verticalLayout_3.addWidget(self.onlineuserslist)
        self.channelslabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.channelslabel.sizePolicy().hasHeightForWidth())
        self.channelslabel.setSizePolicy(sizePolicy)
        self.channelslabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.channelslabel.setObjectName("channelslabel")
        self.verticalLayout_3.addWidget(self.channelslabel)
        self.channelslist = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.channelslist.sizePolicy().hasHeightForWidth())
        self.channelslist.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        self.channelslist.setFont(font)
        self.channelslist.setAutoFillBackground(False)
        self.channelslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channelslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channelslist.setUniformItemSizes(True)
        self.channelslist.setObjectName("channelslist")
        item = QtWidgets.QListWidgetItem()
        self.channelslist.addItem(item)
        self.verticalLayout_3.addWidget(self.channelslist)
        self.verticalLayout_3.setStretch(0, 1)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 7, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.clearbutton.setText(_translate("MainWindow", "Clear"))
        self.sendbutton.setText(_translate("MainWindow", "Send"))
        self.inputbox.setPlaceholderText(_translate("MainWindow", "Enter a message"))
        self.usernamelb.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" color:#33aa44;\">[ RedRiver559 ]</span></p></body></html>"))
        self.bottomlb.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">[ </span><span style=\" color:#319be6;\">07/09/2023 12:24 AM</span><span style=\" color:#00ad0d;\"> ] [ IRC ] [ LATENCY: </span><span style=\" color:#319be6;\">1.008</span><span style=\" color:#00ad0d;\">MS] [ </span><span style=\" color:#319be6;\">TCP</span><span style=\" color:#00ad0d;\"> ] [SSL: </span><span style=\" color:#319be6;\">True </span><span style=\" color:#00ad0d;\">]</span></p></body></html>"))
        self.toptitlelb.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">[ TCP CHAT ] [ Channel: </span><span style=\" color:#319be6;\">Main</span><span style=\" color:#15ada8;\">] [ ] [ </span><span style=\" color:#00ad0d;\">Users: </span><span style=\" color:#1dada8;\">1 </span><span style=\" color:#15ada8;\">]</span></p></body></html>"))
        self.settingsbutton.setText(_translate("MainWindow", "Settings"))
        self.leavebutton.setText(_translate("MainWindow", "Leave"))
        self.helpbutton.setText(_translate("MainWindow", "Help"))
        __sortingEnabled = self.messageslist.isSortingEnabled()
        self.messageslist.setSortingEnabled(False)
        item = self.messageslist.item(0)
        item.setText(_translate("MainWindow", "Test Message"))
        self.messageslist.setSortingEnabled(__sortingEnabled)
        self.userslabel.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">Online Users</span></p></body></html>"))
        __sortingEnabled = self.dateslist.isSortingEnabled()
        self.dateslist.setSortingEnabled(False)
        item = self.dateslist.item(0)
        item.setText(_translate("MainWindow", "08/11/2023 01:54:43 PM"))
        self.dateslist.setSortingEnabled(__sortingEnabled)
        __sortingEnabled = self.usernamelist.isSortingEnabled()
        self.usernamelist.setSortingEnabled(False)
        item = self.usernamelist.item(0)
        item.setText(_translate("MainWindow", "RedRiver559"))
        self.usernamelist.setSortingEnabled(__sortingEnabled)
        __sortingEnabled = self.onlineuserslist.isSortingEnabled()
        self.onlineuserslist.setSortingEnabled(False)
        item = self.onlineuserslist.item(0)
        item.setText(_translate("MainWindow", "RedRiver559"))
        self.onlineuserslist.setSortingEnabled(__sortingEnabled)
        self.channelslabel.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">Channels</span></p></body></html>"))
        __sortingEnabled = self.channelslist.isSortingEnabled()
        self.channelslist.setSortingEnabled(False)
        item = self.channelslist.item(0)
        item.setText(_translate("MainWindow", "Main"))
        self.channelslist.setSortingEnabled(__sortingEnabled)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_ChatWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
