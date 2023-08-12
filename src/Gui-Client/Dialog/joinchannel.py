
from PySide6 import QtCore, QtGui, QtWidgets


class JoinChannelWindow(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(175, 161)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.joinchannelbutton = QtWidgets.QPushButton(Dialog)
        self.joinchannelbutton.setObjectName("joinchannelbutton")
        self.gridLayout.addWidget(self.joinchannelbutton, 4, 0, 1, 1)
        self.channeljoinpassword = QtWidgets.QLineEdit(Dialog)
        self.channeljoinpassword.setObjectName("channeljoinpassword")
        self.gridLayout.addWidget(self.channeljoinpassword, 2, 0, 1, 1)
        self.channelnamelabel = QtWidgets.QLabel(Dialog)
        self.channelnamelabel.setObjectName("channelnamelabel")
        self.gridLayout.addWidget(self.channelnamelabel, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.joinchannelbutton.setText(_translate("Dialog", "Join"))
        self.channeljoinpassword.setPlaceholderText(_translate("Dialog", "Password"))
        self.channelnamelabel.setText(_translate("Dialog", "Join Channel: "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = JoinChannelWindow()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
