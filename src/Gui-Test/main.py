from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox
from PySide6 import QtWidgets, QtNetwork, QtGui, QtCore
from PySide6.QtWidgets import QFileDialog

from Connect.ConnectWindow_ui import Ui_ConnectWindow
from Login.LoginWindow_ui import Ui_LoginWindow
from Chat.ChatWindow_ui import Ui_ChatWindow
from Settings.settings_ui import  Ui_SettingsForm
import json
import sys
import time
import datetime


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
    
dark_theme = load_theme("Themes\dark.qss")
light_theme = load_theme("Themes\light.qss")
yami_theme = load_theme("Themes\yami.qss")


class SettingsWindow(QtWidgets.QDialog):
    current_theme = "Light"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui: QtWidgets.QMainWindow = Ui_SettingsForm()
        self.ui.setupUi(self)

class ConnectWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ConnectWindow()
        self.ui.setupUi(self)

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

class ChatWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ChatWindow()
        self.ui.setupUi(self)

class Status:
    LOGGED_IN = "LOGGED_IN"
    PERMIT = "PERMIT"

class Message:
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    INFO = "INFO"
    ERROR = "ERROR"
    CHAT = "CHAT"
    PRIVATE = "PRIVATE"
    STATUS = "STATUS"
    PUBLIC = "PUBLIC"
    ACK = "ACK"
    LOGIN = "LOGIN"
    SYN = "SYN"

    def __init__(self, sender, message, message_type, time, post_flag=False):
        self.sender = sender
        self.message = message
        self.message_type = message_type
        self.time = time
        self.post_flag = post_flag

    def to_dict(self):
        return {
            'sender': self.sender,
            'message': self.message,
            'message_type': self.message_type,
            'time': self.time,
            'post_flag': self.post_flag
        }

    @staticmethod
    def from_dict(data):
        return Message(
            sender=data.get('sender'),
            message=data.get('message'),
            message_type=data.get('message_type'),
            time=data.get('time'),
            post_flag=data.get('post_flag', False)
        )

class Client:
    def __init__(self):
        self.host = None
        self.port = None
        self.username = None

        self.current_channel = 'Main'
        self.logged_in = False


class Main:
    def __init__(self):

        self.tcp_socket = None
        self.selected_row = None
        self.current_theme = "Light"

        self.username_max = None
        self.message_max = None
        self.username = None
        self.connected = True
        self.current_window = None
        self.logged_in = False
        
        self.client = Client()

        #Settings Window
        self.settings_window = SettingsWindow()
        self.settings_window.ui.themeComboBox.currentIndexChanged.connect(self.handle_theme_change)
        self.settings_window.ui.saveSettingsButton.clicked.connect(self.save_settings)
        self.settings_window.ui.cancelSettingsButton.clicked.connect(self.cancel_settings)
        self.settings_window.finished.connect(self.cancel_settings)

        #Connect Window
        self.connect_window = ConnectWindow()
        self.connect_window.ui.SettingsButton.clicked.connect(self.settings_popup)
        self.connect_window.ui.HelpButton.clicked.connect(self.help_button_pressed)
        self.connect_window.ui.ImportButton.clicked.connect(self.open_import_dialog)
        self.connect_window.ui.ExportButton.clicked.connect(self.open_export_dialog)
        self.connect_window.ui.ConnectButton.clicked.connect(self.connect)
        self.connect_window.ui.CancelConnectButton.clicked.connect(self.close_connection)
        self.connect_window.ui.AddServerButton.clicked.connect(self.add_server)
        self.connect_window.ui.LoadServerButton.clicked.connect(self.load_server)
        self.connect_window.ui.DeleteServerButton.clicked.connect(self.delete_server)
        self.connect_window.ui.ServerTable.cellClicked.connect(self.cell_clicked)

        #Login Window
        self.login_window = LoginWindow()
        self.login_window.ui.settingsButton.clicked.connect(self.settings_popup)
        self.login_window.ui.helpButton.clicked.connect(self.help_button_pressed)
        self.login_window.ui.signInButton.clicked.connect(self.login)

        #Chat Window
        self.chat_window: QtWidgets.QMainWindow = ChatWindow()
        self.chat_window.ui.leaveButton.clicked.connect(self.leave_chat)
        self.chat_window.ui.settingsButton.clicked.connect(self.settings_popup)
        self.chat_window.ui.helpButton.clicked.connect(self.help_button_pressed)
        self.chat_window.ui.sendButton.clicked.connect(self.send_button_pressed)

        monospaced_font = QtGui.QFont("Courier New", 10)
        self.chat_window.ui.chatText.setFont(monospaced_font)
        self.chat_lines = 23
        self.current_lines = 0
        
    def send_button_pressed(self):

        text = self.chat_window.ui.textInput.toPlainText()
        if text != "":
            message = Message(sender=self.username, message=text, message_type='CHAT', time=time.time(), post_flag=True)
            #self.update_chat(message)
            self.send_message(message)
            
            self.chat_window.ui.textInput.clear()
        
    
    def update_chat(self, message: Message):
        current_text = self.chat_window.ui.chatText.toPlainText()

        username = message.sender
        text = message.message
        unix_time = message.time
        date_time = datetime.datetime.fromtimestamp(int(float(unix_time))).strftime("%m/%d/%Y %#I:%M %p")

        data_format = f'{date_time:<18} {username:<12} | {message.message}'

        if current_text:
            # Add a new line and insert the user data
            self.chat_window.ui.chatText.append('')
            self.chat_window.ui.chatText.insertPlainText(data_format)
        else:
            self.chat_window.ui.chatText.append(data_format)

        # Scroll to the bottom
        self.chat_window.ui.chatText.verticalScrollBar().setValue(self.chat_window.ui.chatText.verticalScrollBar().maximum())

    def leave_chat(self):
        self.chat_window.close()
        self.connect_window.show()
        self.close_connection()

    def handle_import_export(self, action):
        if action == 'Import':
            self.connect_window.ui.ImportButton.setText('Import')
        elif action == 'Export':
            self.connect_window.ui.ImportButton.setText('Export')
    
    def settings_popup(self):
        self.settings_window.show()

    def help_button_pressed(self):
        open_link("https://github.com/TheRealRedRiver559/Asyncio-TCP")

    def open_import_dialog(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self.connect_window, "Import File", "", "All Files (*);;Text Files (*.txt)")
        if file:
            print("Selected file for import:", file)

    def open_export_dialog(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self.connect_window, "Export File", "", "All Files (*);;Text Files (*.txt)")
        if file:
            print("Selected file for export:", file)

    def handle_theme_change(self, theme):
        theme = self.settings_window.ui.themeComboBox.currentText()
        if theme == 'Light':
            self.connect_window.setStyleSheet(light_theme)
            self.login_window.setStyleSheet(light_theme)
            self.settings_window.setStyleSheet(light_theme)
            self.chat_window.setStyleSheet(light_theme)
        elif theme == "Dark":
            self.connect_window.setStyleSheet(dark_theme)
            self.login_window.setStyleSheet(dark_theme)
            self.settings_window.setStyleSheet(dark_theme)
            self.chat_window.setStyleSheet(dark_theme)
        elif theme == "Yami":
            self.connect_window.setStyleSheet(yami_theme)
            self.login_window.setStyleSheet(yami_theme)
            self.settings_window.setStyleSheet(yami_theme)
            self.chat_window.setStyleSheet(yami_theme)

    def save_settings(self):
        theme = self.settings_window.ui.themeComboBox.currentText()
        self.current_theme = theme
        self.settings_window.close()

    def cancel_settings(self):
        initial_theme = self.current_theme
        theme = self.settings_window.ui.themeComboBox.currentText()
        
        if theme == initial_theme:
            self.handle_theme_change(theme)
        else:
            index = self.settings_window.ui.themeComboBox.findText(initial_theme)
            if index != -1:
                self.settings_window.ui.themeComboBox.setCurrentIndex(index)
                self.handle_theme_change(initial_theme)

        self.settings_window.close()

    def cell_clicked(self, row, column):
        self.selected_row = row

    def add_server(self):
        servername = self.connect_window.ui.ServerNameText.text()
        hostname = self.connect_window.ui.hostnameText.text()
        port = self.connect_window.ui.PortText.text()

        item_0 = QtWidgets.QTableWidgetItem(servername)
        item_1 = QtWidgets.QTableWidgetItem(hostname)
        item_2 = QtWidgets.QTableWidgetItem(port)
        
        if all(value != "" for value in (servername, hostname, port)):
            for row in range(self.connect_window.ui.ServerTable.rowCount()):
                name = self.connect_window.ui.ServerTable.item(row, 0)
                if name is None:
                    continue
                name = name.text()
                if name == servername:
                    self.connect_window.ui.ServerTable.setItem(row, 1, item_1)
                    self.connect_window.ui.ServerTable.setItem(row, 2, item_2)
                    self.connect_window.ui.ServerTable.selectRow(row)
                    self.selected_row = row
                    return
        else:
            show_error_message("All values must be filled to add a server")
            return
        
        for row in range(self.connect_window.ui.ServerTable.rowCount()):
            name = self.connect_window.ui.ServerTable.item(row, 0)
            if name is None:
                self.connect_window.ui.ServerTable.setItem(row, 0, item_0)
                self.connect_window.ui.ServerTable.setItem(row, 1, item_1)
                self.connect_window.ui.ServerTable.setItem(row, 2, item_2)
                self.connect_window.ui.ServerTable.selectRow(row)
                self.selected_row = row

                if row == self.connect_window.ui.ServerTable.rowCount()-1:
                    self.connect_window.ui.ServerTable.setRowCount(row + 2)
                return
         
    def load_server(self):
        if self.selected_row is not None:
            values = [self.connect_window.ui.ServerTable.item(self.selected_row, col) for col in range(3)]
            if all(values):
                self.connect_window.ui.ServerNameText.setText(values[0].text())
                self.connect_window.ui.hostnameText.setText(values[1].text())
                self.connect_window.ui.PortText.setText(values[2].text())
    
    def delete_server(self):
        if self.selected_row is not None:
            self.connect_window.ui.ServerTable.removeRow(self.selected_row)
            self.connect_window.ui.ServerTable.insertRow(self.connect_window.ui.ServerTable.rowCount()-1)
            self.selected_row = None
            self.connect_window.ui.ServerTable.clearSelection()
                
    def connect(self):

        hostname_item = self.connect_window.ui.ServerTable.item(self.selected_row, 1)
        port_item = self.connect_window.ui.ServerTable.item(self.selected_row, 2)

        if hostname_item is None or port_item == None:
            hostname = self.connect_window.ui.hostnameText.text()
            port = self.connect_window.ui.PortText.text()
            if hostname != "" and port != "":
                pass
            else:
                show_error_message('No values present')
                return   
        else:
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
        
        use_ssl = self.connect_window.ui.SSLButton.isChecked()

        if use_ssl:
            self.tcp_socket = QtNetwork.QSslSocket()
            self.tcp_socket.connected.connect(self.handle_connected)
            self.tcp_socket.setPrivateKey(QtNetwork.QSslKey('/path/to/ssl/key/file.pem', QtNetwork.QSsl.KeyAlgorithm.Rsa))
            self.tcp_socket.setLocalCertificate(QtNetwork.QSslCertificate('/path/to/ssl/cert/file.pem'))
            self.tcp_socket.sslErrors.connect(self.handle_ssl_errors)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHostEncrypted(hostname, port)
        else:
            self.tcp_socket = QtNetwork.QTcpSocket()
            self.tcp_socket.connected.connect(self.handle_connected)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHost(hostname, port)
        
        self.timeout_timer = QtCore.QTimer(self.connect_window)
        self.timeout_timer.setInterval(5000)  # Timeout after 5 seconds
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.handle_connection_timeout)
        self.timeout_timer.start()

        # Disable Connect button while connecting
        self.connect_window.ui.ConnectButton.setEnabled(False)

    def handle_connected(self):
        self.connected = True
        self.timeout_timer.stop()
        self.connect_window.close()
        self.login_window.show()
    
    def close_connection(self):
        if self.tcp_socket:
            self.tcp_socket.abort()
            self.timeout_timer.stop()
            self.connect_window.ui.ConnectButton.setEnabled(True)
        self.logged_in = False
    
    def handle_connection_timeout(self):
        show_error_message('Connection timeout')
        self.connect_window.ui.ConnectButton.setEnabled(True)

    def disconnect_from_server(self):
        if self.tcp_socket.state() == QtNetwork.QAbstractSocket.SocketState.ConnectedState:
            self.tcp_socket.disconnectFromHost()
            self.logged_in = False

    def handle_ready_read(self):
        # Handle data received from the server
        while self.tcp_socket.canReadLine():
            message : Message = self.receive_data()
            print(message)
            if message:
                message_type = message.message_type
                message_data = message.message
                if message_type == Message.REQUEST:
                    print(message_data)
                elif message_type == Message.RESPONSE:
                    print(message_data)
                elif message_type == Message.INFO:
                    self.update_chat(message)
                elif message_type == Message.ERROR:
                    print(message_data)
                elif message_type == Message.CHAT:
                    self.update_chat(message)
                elif message_type == Message.PRIVATE:
                    self.update_chat(message)
                elif message_type == Message.STATUS:
                    if message_data == Status.PERMIT:
                        self.update_chat(message)
                        if not self.logged_in:
                            self.logged_in = True
                            self.chat_window.show()
                            self.login_window.close()

                elif message_type == Message.SYN:
                    message = Message(sender=self.username, message="Pong", message_type=Message.ACK, time=time.time())
                    self.send_message(message)
                else:
                    pass
                
    def send_message(self, message: Message):
        print(message.message)
        message_dict = message.to_dict()
        json_data = json.dumps(message_dict).encode() + b"\n"
        self.tcp_socket.write(json_data)
        self.tcp_socket.flush()

    def login(self):
        self.username = self.login_window.ui.usernameText.text()
        self.password = self.login_window.ui.passwordText.text()
        if all((self.username, self.password)):
            message = Message(sender=None, message={'username':self.username, 'password':self.password},message_type=Message.LOGIN, post_flag=True, time=time.time())
            self.send_message(message)
            
    def receive_data(self):
        try:
            data = self.tcp_socket.readLine()
            if data:
                data = data.data().decode().strip()
                message = Message.from_dict(json.loads(data))
                return message
        except QtNetwork.QAbstractSocket.RemoteHostClosedError:
            show_error_message("Connection closed by the server")
            if self.connected:
                self.leave()
        except json.JSONDecodeError:
            show_error_message("Received data is not valid JSON")
        return None

    def handle_error(self, socket_error):
        # Handle socket error
        show_error_message('socket error detected')
        print(socket_error)
        pass

    def handle_ssl_errors(self, errors):
        for error in errors:
            print("SSL error:", error.errorString())


app = QtWidgets.QApplication([])
main = Main()
main.chat_window.show()
app.exec()
