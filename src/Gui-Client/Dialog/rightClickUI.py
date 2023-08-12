
from PySide6 import QtCore, QtGui, QtWidgets


class Right_Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(133, 233)
        Dialog.setAcceptDrops(False)
        Dialog.setWindowOpacity(0.3)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(Dialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.listWidget.setFont(font)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Right_Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
