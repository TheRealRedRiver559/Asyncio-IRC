from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_chatwindow(object):
    def setupUi(self, chatwindow):
        chatwindow.setObjectName("chatwindow")
        chatwindow.resize(1120, 670)
        chatwindow.setAutoFillBackground(False)
        chatwindow.setStyleSheet("QGroupBox {\n"
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
"    background-color: #2e2c2c;\n"
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
"    background-color: #1f1f1f;\n"
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
"#dateslist, #usernamelist, #messageslist, #onlineuserslist, #channelslist, #suggestionlist {\n"
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
"#line, #toptitlelb, #bottomlb, #messagedivider, #clearbutton, #sendbutton, #leavebutton, #frame, #helpbutton, #settingsbutton {\n"
"   background-color: rgb(30, 30, 30);\n"
"}\n"
"\n"
"#frame2, #inputbox {\n"
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
"QListWidget{\n"
"color: rgb(0, 173, 13);\n"
"border: 0px;\n"
"}\n"
"\n"
"QFrame {\n"
"   border-color: rgb(127, 127, 127);\n"
"}\n"
"\n"
"#ServerTable {\n"
"border-color:#2e2c2c;\n"
"}\n"
"\n"
"#suggestionlist {\n"
"border: 1px solid #2e2c2c;\n"
"}\n"
"\n"
"QLabel {\n"
"   color: #f0f0f0;\n"
"}\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(chatwindow)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.usernamelb = QtWidgets.QLabel(self.centralwidget)
        self.usernamelb.setGeometry(QtCore.QRect(0, 620, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.usernamelb.setFont(font)
        self.usernamelb.setObjectName("usernamelb")
        self.usernamelist = QtWidgets.QListWidget(self.centralwidget)
        self.usernamelist.setGeometry(QtCore.QRect(150, 20, 121, 581))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.usernamelist.setFont(font)
        self.usernamelist.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.usernamelist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.usernamelist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.usernamelist.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.usernamelist.setUniformItemSizes(False)
        self.usernamelist.setObjectName("usernamelist")
        self.messageslist = QtWidgets.QListWidget(self.centralwidget)
        self.messageslist.setGeometry(QtCore.QRect(280, 20, 701, 581))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.messageslist.setFont(font)
        self.messageslist.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.messageslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.messageslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.messageslist.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.messageslist.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.messageslist.setAlternatingRowColors(False)
        self.messageslist.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.messageslist.setProperty("isWrapping", False)
        self.messageslist.setResizeMode(QtWidgets.QListView.ResizeMode.Fixed)
        self.messageslist.setLayoutMode(QtWidgets.QListView.LayoutMode.Batched)
        self.messageslist.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.messageslist.setUniformItemSizes(False)
        self.messageslist.setWordWrap(True)
        self.messageslist.setSelectionRectVisible(False)
        self.messageslist.setObjectName("messageslist")
        self.onlineuserslist = QtWidgets.QListWidget(self.centralwidget)
        self.onlineuserslist.setGeometry(QtCore.QRect(980, 20, 141, 371))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.onlineuserslist.setFont(font)
        self.onlineuserslist.setAutoFillBackground(False)
        self.onlineuserslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.onlineuserslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.onlineuserslist.setUniformItemSizes(True)
        self.onlineuserslist.setObjectName("onlineuserslist")
        self.slashlist = QtWidgets.QListWidget(self.centralwidget)
        self.slashlist.setGeometry(QtCore.QRect(255, 18, 21, 581))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.slashlist.setFont(font)
        self.slashlist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.slashlist.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.slashlist.setObjectName("slashlist")
        self.messagedivider = QtWidgets.QFrame(self.centralwidget)
        self.messagedivider.setGeometry(QtCore.QRect(260, 10, 16, 591))
        self.messagedivider.setAutoFillBackground(False)
        self.messagedivider.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.messagedivider.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.messagedivider.setObjectName("messagedivider")
        self.inputbox = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.inputbox.setGeometry(QtCore.QRect(110, 620, 871, 41))
        self.inputbox.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CursorShape.IBeamCursor))
        self.inputbox.setFocusPolicy(QtCore.Qt.FocusPolicy.WheelFocus)
        self.inputbox.setBackgroundVisible(False)
        self.inputbox.setObjectName("inputbox")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(980, 20, 3, 580))
        self.line.setAutoFillBackground(False)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.toptitlelb = QtWidgets.QLabel(self.centralwidget)
        self.toptitlelb.setGeometry(QtCore.QRect(0, 0, 981, 21))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.toptitlelb.setFont(font)
        self.toptitlelb.setAutoFillBackground(False)
        self.toptitlelb.setScaledContents(True)
        self.toptitlelb.setObjectName("toptitlelb")
        self.bottomlb = QtWidgets.QLabel(self.centralwidget)
        self.bottomlb.setGeometry(QtCore.QRect(0, 596, 1121, 20))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.bottomlb.setFont(font)
        self.bottomlb.setAutoFillBackground(False)
        self.bottomlb.setObjectName("bottomlb")
        self.frame2 = QtWidgets.QFrame(self.centralwidget)
        self.frame2.setGeometry(QtCore.QRect(0, 610, 1131, 61))
        self.frame2.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame2.setObjectName("frame2")
        self.clearbutton = QtWidgets.QToolButton(self.frame2)
        self.clearbutton.setGeometry(QtCore.QRect(1060, 10, 51, 21))
        self.clearbutton.setObjectName("clearbutton")
        self.sendbutton = QtWidgets.QToolButton(self.frame2)
        self.sendbutton.setGeometry(QtCore.QRect(990, 10, 61, 21))
        self.sendbutton.setAutoFillBackground(False)
        self.sendbutton.setObjectName("sendbutton")
        self.sendbutton.raise_()
        self.clearbutton.raise_()
        self.leavebutton = QtWidgets.QToolButton(self.centralwidget)
        self.leavebutton.setGeometry(QtCore.QRect(910, 0, 71, 21))
        self.leavebutton.setObjectName("leavebutton")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(259, 19, 31, 581))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.helpbutton = QtWidgets.QToolButton(self.centralwidget)
        self.helpbutton.setGeometry(QtCore.QRect(860, 0, 51, 21))
        self.helpbutton.setObjectName("helpbutton")
        self.settingsbutton = QtWidgets.QToolButton(self.centralwidget)
        self.settingsbutton.setGeometry(QtCore.QRect(790, 0, 71, 21))
        self.settingsbutton.setObjectName("settingsbutton")
        self.dateslist = QtWidgets.QListWidget(self.centralwidget)
        self.dateslist.setGeometry(QtCore.QRect(0, 20, 151, 581))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.dateslist.setFont(font)
        self.dateslist.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.dateslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dateslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dateslist.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.dateslist.setUniformItemSizes(False)
        self.dateslist.setObjectName("dateslist")
        self.channelslist = QtWidgets.QListWidget(self.centralwidget)
        self.channelslist.setGeometry(QtCore.QRect(980, 410, 141, 191))
        font = QtGui.QFont()
        font.setFamily("Chakra Petch")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.channelslist.setFont(font)
        self.channelslist.setAutoFillBackground(False)
        self.channelslist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.channelslist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channelslist.setUniformItemSizes(True)
        self.channelslist.setObjectName("channelslist")
        self.userslabel = QtWidgets.QLabel(self.centralwidget)
        self.userslabel.setGeometry(QtCore.QRect(980, 0, 141, 20))
        self.userslabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.userslabel.setObjectName("userslabel")
        self.channelslabel = QtWidgets.QLabel(self.centralwidget)
        self.channelslabel.setGeometry(QtCore.QRect(976, 392, 151, 21))
        self.channelslabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.channelslabel.setObjectName("channelslabel")
        self.frame3 = QtWidgets.QFrame(self.centralwidget)
        self.frame3.setGeometry(QtCore.QRect(979, 0, 151, 601))
        self.frame3.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame3.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame3.setObjectName("frame3")
        self.suggestionlist = QtWidgets.QListWidget(self.centralwidget)
        self.suggestionlist.setGeometry(QtCore.QRect(110, 602, 256, 20))
        self.suggestionlist.setMovement(QtWidgets.QListView.Movement.Static)
        self.suggestionlist.setFlow(QtWidgets.QListView.Flow.TopToBottom)
        self.suggestionlist.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.suggestionlist.setLayoutMode(QtWidgets.QListView.LayoutMode.SinglePass)
        self.suggestionlist.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.suggestionlist.setObjectName("suggestionlist")
        self.suggestionlist.raise_()
        self.frame3.raise_()
        self.channelslabel.raise_()
        self.channelslist.raise_()
        self.dateslist.raise_()
        self.frame.raise_()
        self.frame2.raise_()
        self.usernamelb.raise_()
        self.onlineuserslist.raise_()
        self.slashlist.raise_()
        self.messagedivider.raise_()
        self.inputbox.raise_()
        self.line.raise_()
        self.usernamelist.raise_()
        self.messageslist.raise_()
        self.toptitlelb.raise_()
        self.bottomlb.raise_()
        self.leavebutton.raise_()
        self.helpbutton.raise_()
        self.settingsbutton.raise_()
        self.userslabel.raise_()
        chatwindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(chatwindow)
        QtCore.QMetaObject.connectSlotsByName(chatwindow)

    def retranslateUi(self, chatwindow):
        _translate = QtCore.QCoreApplication.translate
        chatwindow.setWindowTitle(_translate("chatwindow", "TCP Chat Server"))
        self.usernamelb.setText(_translate("chatwindow", "<html><head/><body><p align=\"right\"><br/></p></body></html>"))
        self.inputbox.setPlainText(_translate("chatwindow", "Enter Message"))
        self.inputbox.setPlaceholderText(_translate("chatwindow", "Enter Message"))
        self.toptitlelb.setText(_translate("chatwindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">[ TCP CHAT ] [ Channel: </span><span style=\" color:#319be6;\">Main</span><span style=\" color:#15ada8;\">] [ ] [ </span><span style=\" color:#00ad0d;\">Users: </span><span style=\" color:#1dada8;\">1 </span><span style=\" color:#15ada8;\">]</span></p></body></html>"))
        self.bottomlb.setText(_translate("chatwindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">[ </span><span style=\" color:#319be6;\">07/09/2023 12:24 AM</span><span style=\" color:#00ad0d;\"> ] [ IRC ] [ LATENCY: </span><span style=\" color:#319be6;\">1.008</span><span style=\" color:#00ad0d;\">MS] [ </span><span style=\" color:#319be6;\">TCP</span><span style=\" color:#00ad0d;\"> ] [SSL: </span><span style=\" color:#319be6;\">True </span><span style=\" color:#00ad0d;\">]</span></p></body></html>"))
        self.clearbutton.setText(_translate("chatwindow", "Clear"))
        self.sendbutton.setText(_translate("chatwindow", "Send"))
        self.leavebutton.setText(_translate("chatwindow", "Leave"))
        self.helpbutton.setText(_translate("chatwindow", "Help"))
        self.settingsbutton.setText(_translate("chatwindow", "Settings"))
        self.userslabel.setText(_translate("chatwindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">Online Users</span></p></body></html>"))
        self.channelslabel.setText(_translate("chatwindow", "<html><head/><body><p><span style=\" color:#00ad0d;\">Channels</span></p></body></html>"))
        self.suggestionlist.setSortingEnabled(False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    chatwindow = QtWidgets.QMainWindow()
    ui = Ui_chatwindow()
    ui.setupUi(chatwindow)
    chatwindow.show()
    sys.exit(app.exec())
