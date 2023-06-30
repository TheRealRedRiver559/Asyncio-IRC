from PyQt6.QtWidgets import QApplication
from ui_file import Ui_MainWindow
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6 import QtWidgets, QtNetwork, QtGui, QtCore
from settings_ui import  Ui_SettingsForm
from PyQt6.QtWidgets import QFileDialog
import sys

def open_link(link):
    url = QtCore.QUrl(link)
    QtGui.QDesktopServices.openUrl(url)

def load_theme(theme_file):
    file = QtCore.QFile(theme_file)
    if not file.open(QtCore.QFile.OpenModeFlag.ReadOnly | QtCore.QFile.OpenModeFlag.Text):
        return ""
    stream = QtCore.QTextStream(file)
    theme = stream.readAll()
    file.close()
    return theme

def show_error_message(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("Error")
    error_dialog.setText(message)
    error_dialog.exec()

def show_message(message, title="Connection"):
    info_dialog = QMessageBox()
    info_dialog.setIcon(QMessageBox.Icon.Information)
    info_dialog.setWindowTitle(title)
    info_dialog.setText(message)
    info_dialog.exec()

dark_theme = load_theme("Themes/dark.qss")
light_theme = load_theme("Themes/light.qss")
yami_theme = load_theme("Themes/yami.qss")

class SettingsPopupWindow(QtWidgets.QDialog):
    theme_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsForm()
        self.ui.setupUi(self)

        self.ui.themeComboBox.currentIndexChanged.connect(self.handle_theme_change)
        
    def handle_theme_change(self, index):
        theme = self.ui.themeComboBox.itemText(index)
        self.theme_changed.emit(theme)



class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.tcp_socket = None
        self.selected_row = None

        #Settings / Help
        self.ui.SettingButton.clicked.connect(self.settings_popup)
        self.ui.HelpButton.clicked.connect(self.help_button_pressed)

        #Import / Export
        self.ui.ImportButton.clicked.connect(self.open_import_dialog)
        self.ui.ExportButton.clicked.connect(self.open_export_dialog)

        #Connecting to server
        self.ui.ConnectButton.clicked.connect(self.connect)
        self.ui.CancelConnectButton.clicked.connect(self.close_connection)

        #Adding, Loading, and deleting servers
        self.ui.AddServerButton.clicked.connect(self.add_server)
        self.ui.LoadServerButton.clicked.connect(self.load_server)
        self.ui.DeleteServerButton.clicked.connect(self.delete_server)
        self.ui.ServerTable.cellClicked.connect(self.cell_clicked)

    def handle_import_export(self, action):
        if action == 'Import':
            self.ui.ImportButton.setText('Import')
        elif action == 'Export':
            self.ui.ImportButton.setText('Export')
    
    def settings_popup(self):
        settings_window = SettingsPopupWindow(self)
        settings_window.theme_changed.connect(self.handle_theme_change)
        settings_window.show()

    def help_button_pressed(self):
        open_link("https://github.com/TheRealRedRiver559/Asyncio-TCP")


    def open_import_dialog(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import File", "", "All Files (*);;Text Files (*.txt)")
        if file:
            print("Selected file for import:", file)

    def open_export_dialog(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export File", "", "All Files (*);;Text Files (*.txt)")
        if file:
            print("Selected file for export:", file)

    @QtCore.pyqtSlot(str)
    def handle_theme_change(self, theme):
        if theme == 'Light':
            self.setStyleSheet(light_theme)
        elif theme == "Dark":
            self.setStyleSheet(dark_theme)
        elif theme == "Yami":
            self.setStyleSheet(yami_theme)

    def change_page(self, page_index):
        self.ui.stackedWidget.setCurrentIndex(page_index)

    def cell_clicked(self, row, column):
        self.selected_row = row

    def add_server(self):
        servername = self.ui.ServerNameText.text()
        hostname = self.ui.hostnameText.text()
        port = self.ui.PortText.text()

        item_0 = QtWidgets.QTableWidgetItem(servername)
        item_1 = QtWidgets.QTableWidgetItem(hostname)
        item_2 = QtWidgets.QTableWidgetItem(port)
        
        if all(value != "" for value in (servername, hostname, port)):
            for row in range(self.ui.ServerTable.rowCount()):
                name = self.ui.ServerTable.item(row, 0)
                if name is None:
                    continue
                name = name.text()
                if name == servername:
                    self.ui.ServerTable.setItem(row, 1, item_1)
                    self.ui.ServerTable.setItem(row, 2, item_2)
                    self.ui.ServerTable.selectRow(row)
                    self.selected_row = row
                    return
        else:
            show_error_message("All values must be filled to add a server")
            return
        
        for row in range(self.ui.ServerTable.rowCount()):
            name = self.ui.ServerTable.item(row, 0)
            if name is None:
                self.ui.ServerTable.setItem(row, 0, item_0)
                self.ui.ServerTable.setItem(row, 1, item_1)
                self.ui.ServerTable.setItem(row, 2, item_2)
                self.ui.ServerTable.selectRow(row)
                self.selected_row = row
                return
         
    def load_server(self):
        if self.selected_row is not None:
            values = [self.ui.ServerTable.item(self.selected_row, col) for col in range(3)]
            if all(values):
                self.ui.ServerNameText.setText(values[0].text())
                self.ui.hostnameText.setText(values[1].text())
                self.ui.PortText.setText(values[2].text())
    
    def delete_server(self):
        if self.selected_row is not None:
            self.ui.ServerTable.removeRow(self.selected_row)
            self.ui.ServerTable.insertRow(self.ui.ServerTable.rowCount()-1)
            self.selected_row = None
            self.ui.ServerTable.clearSelection()
                
    def connect(self):
        if self.selected_row is None:
            hostname = self.ui.hostnameText.text()
            port = self.ui.PortText.text()
            if hostname != "" and port != "":
                pass
            else:
                show_error_message('No values present')
                return   
        else:
            hostname_item = self.ui.ServerTable.item(self.selected_row, 1)
            port_item = self.ui.ServerTable.item(self.selected_row, 2)

            if hostname_item is not None and port_item is not None:
                hostname = hostname_item.text()
                port = port_item.text()
            else:
                show_error_message('No values present')
                return
            

        try:
            port = int(port)
        except ValueError:
            show_error_message("Port number must be a number")
            return
        if port > 65535 or port <= 0:
            show_error_message("Port must be between 0 - 65535")
            return
        
        use_ssl = self.ui.SSLButton.isChecked()

        if use_ssl:
            self.tcp_socket = QtNetwork.QSslSocket(self)
            self.tcp_socket.connected.connect(self.handle_connected)
            self.tcp_socket.setPrivateKey(QtNetwork.QSslKey('/path/to/ssl/key/file.pem', QtNetwork.QSsl.KeyAlgorithm.Rsa))
            self.tcp_socket.setLocalCertificate(QtNetwork.QSslCertificate('/path/to/ssl/cert/file.pem'))
            self.tcp_socket.sslErrors.connect(self.handle_ssl_errors)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHostEncrypted(hostname, port)
        else:
            self.tcp_socket = QtNetwork.QTcpSocket(self)
            self.tcp_socket.connected.connect(self.handle_connected)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHost(hostname, port)
        
        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.setInterval(5000)  # Timeout after 5 seconds
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.handle_connection_timeout)
        self.timeout_timer.start()

        # Disable Connect button while connecting
        self.ui.ConnectButton.setEnabled(False)

    def handle_connected(self):
        self.change_page(1)
        print('Connected')
    
    def close_connection(self):
        if self.tcp_socket:
            self.tcp_socket.abort()
            self.timeout_timer.stop()
            self.ui.ConnectButton.setEnabled(True)
    
    def handle_connection_timeout(self):
        print('Connection timeout')
        show_error_message('Connection timeout')
        self.ui.ConnectButton.setEnabled(True)

    def disconnect_from_server(self):
        if self.tcp_socket.state() == QtNetwork.QAbstractSocket.SocketState.ConnectedState:
            self.tcp_socket.disconnectFromHost()

    def handle_ready_read(self):
        # Handle data received from the server
        if self.tcp_socket is not None and self.tcp_socket.bytesAvailable() > 0:
            data = self.tcp_socket.readLine()
            # Process the received data
            print(data)

    def handle_error(self, socket_error):
        # Handle socket error
        pass

    def handle_ssl_errors(self, errors):
        for error in errors:
            print("SSL error:", error.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
