from PySide6.QtWidgets import QMessageBox
from PySide6 import QtWidgets, QtNetwork, QtGui, QtCore
from PySide6.QtWidgets import QFileDialog
from Connect.ConnectWindow_ui import Ui_ConnectWindow
from Login.LoginWindow_ui import Ui_LoginWindow
from Chat.ChatWindow_ui import Ui_ChatWindow
from Settings.settings_ui import Ui_SettingsForm
from Dialog.rightClickUI import Right_Ui_Dialog
from Dialog.createchannel import CreatChannelWindow
from Dialog.joinchannel import JoinChannelWindow
import json
import time
import datetime
import csv
from pathlib import Path
import os

# Opens a link
def open_link(link):
    url = QtCore.QUrl(link)
    QtGui.QDesktopServices.openUrl(url)

# Loads a theme file given the file location
def load_theme(theme_file):
    file = QtCore.QFile(theme_file)
    if not file.open(
        QtCore.QFile.OpenModeFlag.ReadOnly | QtCore.QFile.OpenModeFlag.Text
    ):
        return ""
    stream = QtCore.QTextStream(file)
    theme = stream.readAll()
    file.close()
    return theme

# Brings up a popup error message
def show_error_message(message, parent=None):
    error_dialog = QMessageBox(parent=parent)
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("Error")
    error_dialog.setText(message)
    error_dialog.exec()

# Also like an error message but shows a more formal message
def show_message(message, title="Connection"):
    info_dialog = QMessageBox()
    info_dialog.setIcon(QMessageBox.Icon.Information)
    info_dialog.setWindowTitle(title)
    info_dialog.setText(message)
    info_dialog.exec()

script_dir = Path(os.path.dirname(os.path.abspath(__file__)))

# Construct paths to the theme files relative to the script directory
themes_dir = script_dir / "Themes"
dark_theme_path = themes_dir / "dark.qss"
light_theme_path = themes_dir / "light.qss"
yami_theme_path = themes_dir / "yami.qss"

# Now load the themes
dark_theme = load_theme(dark_theme_path)
light_theme = load_theme(light_theme_path)
yami_theme = load_theme(yami_theme_path)

# Using an override to check for a shift + enter on the input (multiple lines)
class PlainTextEdit(QtWidgets.QPlainTextEdit):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            # Perform the desired action
            print("Enter key pressed!")
        else:
            # Call the base class implementation for other key events
            super().keyPressEvent(event)

# Settings window constructor, may be remove so its easier to code. Not sure why I did this
class SettingsWindow(QtWidgets.QDialog):
    current_theme = "Light"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui: QtWidgets.QDialog = Ui_SettingsForm()
        self.ui.setupUi(self)

# Same for all of these class constructors
# I did this so I could share data easily across all widgets
class ConnectWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ConnectWindow()
        self.ui.setupUi(self)

    def clear_page(self):
        self.ui.ServerTable.clearContents()
        self.ui.hostnameText.clear()
        self.ui.PortText.clear()
        self.ui.ServerNameText.clear()


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

    def clear_page(self):
        self.ui.usernameText.clear()
        self.ui.passwordText.clear()


class ChatWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ChatWindow()
        self.ui.setupUi(self)
        self.ui.suggestionlist = QtWidgets.QListWidget(self)
        self.ui.suggestionlist.lower()

    def clear_page(self):
        self.ui.usernamelist.clear()
        self.ui.dateslist.clear()
        self.ui.inputbox.clear()
        self.ui.onlineuserslist.clear()
        self.ui.messageslist.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.ui.suggestionlist.move(self.ui.inputbox.x(),self.ui.messageslist.height())

# Status messages WIP        
class Status:
    LOGGED_IN = "LOGGED_IN"
    PERMIT = "PERMIT"

# Message class just for formatting
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
    COMMAND = "COMMAND"
    CHANNEL_LEAVE = "CHANNEL_LEAVE"
    CHANNEL_JOIN = "CHANNEL_LEAVE"
    CHANNEL_CREATE = "CHANNEL_LEAVE"

    def __init__(self, sender, message, message_type, time, post_flag=False):
        self.sender = sender
        self.message = message
        self.message_type = message_type
        self.time = time
        self.post_flag = post_flag

    def to_dict(self):
        return {
            "sender": self.sender,
            "message": self.message,
            "message_type": self.message_type,
            "time": self.time,
            "post_flag": self.post_flag,
        }

    @staticmethod
    def from_dict(data):
        return Message(
            sender=data.get("sender"),
            message=data.get("message"),
            message_type=data.get("message_type"),
            time=data.get("time"),
            post_flag=data.get("post_flag", False),
        )

# This client class holds important information such as current channel and more
class Client:
    def __init__(self):
        self.host = None
        self.port = None
        self.username = None

        self.current_channel = "Main"
        self.logged_in = False


class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui: QtWidgets.QDialog = Right_Ui_Dialog()
        self.ui.setupUi(self)

# This main class holds all instances and main methods
class Main:
    def __init__(self):
        self.tcp_socket = None # Socket
        self.selected_row = None # This is for the connection window and joining
        self.current_theme = "Dark"

        self.username_max = 8 # This will be changed by the server if sent
        self.message_max = 200 # This will also be changed possibly
        self.username = None
        self.connected = True
        self.current_window = None #Not used at the moment
        self.logged_in = False
        self.users_list = [] #This list gets updated by the server

        self.client = Client()
        self.ssl_path = "/path/to/ssl/key/file.pem" # SLL is disabled at the moment
        self.ping = None
        self.current_channel = None
        self.ssl_active = False # Leave this off and dont press the radio button as the server does not use SSL right now
        monospaced_font = QtGui.QFont("Iosevka", 10)

        # Settings Window
        self.settings_window = SettingsWindow()
        self.settings_window.ui.themeComboBox.currentIndexChanged.connect(self.handle_theme_change)
        self.settings_window.ui.saveSettingsButton.clicked.connect(self.save_settings)
        self.settings_window.ui.cancelSettingsButton.clicked.connect(self.cancel_settings)
        self.settings_window.finished.connect(self.cancel_settings)
        self.settings_window.ui.certPath.setText(self.ssl_path)

        # Connect Window
        self.connect_window = ConnectWindow()
        self.connect_window.ui.SettingsButton.clicked.connect(self.settings_popup)
        self.connect_window.ui.SettingsButton.click
        self.connect_window.ui.HelpButton.clicked.connect(self.help_button_pressed)
        self.connect_window.ui.ImportButton.clicked.connect(self.open_import_dialog)
        self.connect_window.ui.ExportButton.clicked.connect(self.open_export_dialog)
        self.connect_window.ui.ConnectButton.clicked.connect(self.connect)
        self.connect_window.ui.CancelConnectButton.clicked.connect(self.close_connection)
        self.connect_window.ui.AddServerButton.clicked.connect(self.add_server)
        self.connect_window.ui.LoadServerButton.clicked.connect(self.load_server)
        self.connect_window.ui.DeleteServerButton.clicked.connect(self.delete_server)
        self.connect_window.ui.ServerTable.cellClicked.connect(self.cell_clicked)

        # Login Window
        self.login_window = LoginWindow()
        self.login_window.ui.settingsButton.clicked.connect(self.settings_popup)
        self.login_window.ui.helpButton.clicked.connect(self.help_button_pressed)
        self.login_window.ui.signInButton.clicked.connect(self.login)

        # Chat Window
        self.chat_window: QtWidgets.QMainWindow = ChatWindow()
        self.chat_window.ui.leavebutton.clicked.connect(self.leave_chat)
        self.chat_window.ui.settingsbutton.clicked.connect(self.settings_popup)
        self.chat_window.ui.helpbutton.clicked.connect(self.help_button_pressed)
        self.chat_window.ui.sendbutton.clicked.connect(self.send_button_pressed)
        self.chat_window.ui.clearbutton.clicked.connect(self.clear_input_pressed)
        self.chat_window.ui.inputbox.keyPressEvent = self.chat_key_press
        self.chat_window.ui.messageslist.setFont(monospaced_font)
        self.chat_window.ui.dateslist.setFont(monospaced_font)
        self.chat_window.ui.usernamelist.setFont(monospaced_font)
        self.chat_window.ui.onlineuserslist.setFont(monospaced_font)
        self.chat_window.ui.inputbox.setFont(monospaced_font)
        self.chat_window.ui.suggestionlist.currentItemChanged.connect(self.suggestion_click)
        self.chat_window.ui.onlineuserslist.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_window.ui.channelslist.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_window.ui.onlineuserslist.customContextMenuRequested.connect(self.show_user_context)
        self.chat_window.ui.channelslist.customContextMenuRequested.connect(self.show_channel_conetex)
        self.chat_lines = 0
        self.dateslist = self.chat_window.ui.dateslist
        self.usernamelist = self.chat_window.ui.usernamelist
        self.messageslist = self.chat_window.ui.messageslist
        self.users_online_list = self.chat_window.ui.onlineuserslist
        self.dateslist.verticalScrollBar().valueChanged.connect(self.usernamelist.verticalScrollBar().setValue)
        self.dateslist.verticalScrollBar().valueChanged.connect(self.messageslist.verticalScrollBar().setValue)
        self.usernamelist.verticalScrollBar().valueChanged.connect(self.dateslist.verticalScrollBar().setValue)
        self.usernamelist.verticalScrollBar().valueChanged.connect(self.messageslist.verticalScrollBar().setValue)
        self.messageslist.verticalScrollBar().valueChanged.connect(
        self.dateslist.verticalScrollBar().setValue)
        self.messageslist.verticalScrollBar().valueChanged.connect(
        self.usernamelist.verticalScrollBar().setValue)
        self.chat_animation_timer = QtCore.QTimer(self.chat_window)
        self.chat_animation_timer.timeout.connect(self.update_chat_animation)
        self.chat_animation_timer.start(1000)
        self.handle_theme_change("Dark")
        self.settings_window.ui.themeComboBox.setCurrentIndex(1)

        self.Ui_dialog = Ui_Dialog()
        self.prefix = "//"
        self.slash_commands = None
        self.suggestion_clicked = False

    def show_user_context(self, point): # When you right click on a user WIP (not working fully)
        item = self.chat_window.ui.onlineuserslist.itemAt(point)
        menu = QtWidgets.QMenu(self.chat_window)
        if item is not None:
            add_user_label = QtWidgets.QLabel("Add user", self.chat_window)
            add_user_action = QtWidgets.QWidgetAction(self.chat_window)
            add_user_action.setDefaultWidget(add_user_label)
            add_user_action.triggered.connect(self.join_channel)

            message_user_label = QtWidgets.QLabel("Message User", self.chat_window)
            message_user_action = QtWidgets.QWidgetAction(self.chat_window)
            message_user_action.setDefaultWidget(message_user_label)
            message_user_action.triggered.connect(self.join_channel)
            
            menu.addActions([add_user_action, message_user_action])
        menu.raise_()
        menu.exec(QtGui.QCursor.pos())

    def show_channel_conetex(self, point): # When you right click on a channel WIP (not working fully)
        item = self.chat_window.ui.channelslist.itemAt(point)
        menu = QtWidgets.QMenu(self.chat_window)
        self.channel_to_join = item
        self.channel_to_leave = item
        if item is not None:
            join_channel_label = QtWidgets.QLabel("Join Channel", self.chat_window)
            join_channel_action = QtWidgets.QWidgetAction(self.chat_window)
            join_channel_action.setDefaultWidget(join_channel_label)
            join_channel_action.triggered.connect(self.join_channel_event)
            menu.addAction(join_channel_action)

            leave_channel_label = QtWidgets.QLabel("Leave Channel", self.chat_window)
            leave_channel_action = QtWidgets.QWidgetAction(self.chat_window)
            leave_channel_action.setDefaultWidget(leave_channel_label)
            leave_channel_action.triggered.connect(self.leave_channel_event)
            menu.addAction(leave_channel_action)
        create_channel_label = QtWidgets.QLabel("Create Channel", self.chat_window)
        create_channel_action = QtWidgets.QWidgetAction(self.chat_window)
        create_channel_action.setDefaultWidget(create_channel_label)
        create_channel_action.triggered.connect(self.create_channel_event)
        menu.addAction(create_channel_action)
        menu.exec(QtGui.QCursor.pos())
    
    #WIP
    def join_channel_event(self, event):
        channel = self.channel_to_join.text()
        if self.client.current_channel == channel:
            pass
    
    #WIP
    def leave_channel_event(self, event):
        print('left')
    #WIP
    def create_channel_event(self, event):
        print('left')
        
    # When you click on a suggestion inside the suggestion box it will paste the text
    def suggestion_click(self, item):
        if self.suggestion_clicked:
            return
        text = item.text()
        self.chat_window.ui.inputbox.setPlainText(text)
        self.chat_window.ui.suggestionlist.clearSelection()

        cursor = self.chat_window.ui.inputbox.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.chat_window.ui.inputbox.setFocus()
        self.chat_window.ui.inputbox.setTextCursor(cursor)
        self.chat_window.ui.suggestionlist.lower()
        self.suggestion_clicked = True

    # Whenever a key is pressed this will check and see if there is a slash command
    def update_auto_complete(self):
        self.slash_commands = ['help', 'ban', 'test', 'test2']
        self.prefix = '//'
        cursor = self.chat_window.ui.inputbox.textCursor()
        if self.suggestion_clicked:
            self.chat_window.ui.suggestionlist.clear()
            self.suggestion_clicked = False
            return
        self.chat_window.ui.suggestionlist.lower()
        self.chat_window.ui.suggestionlist.clear()

        text = self.chat_window.ui.inputbox.toPlainText()
        if len(text) < 1 or not text:
            return

        if text.startswith(self.prefix):
            text = text.removeprefix(self.prefix)

            suggestions_list = []
            for command in self.slash_commands:
                if command.startswith(text):
                    suggestion = (
                        self.prefix + command
                        if not command.startswith(self.prefix)
                        else command
                    )
                    suggestion_item = QtWidgets.QListWidgetItem(suggestion)
                    suggestions_list.append(suggestion)
                    self.chat_window.ui.suggestionlist.addItem(suggestion_item)

            if suggestions_list:
                item_height = self.chat_window.ui.suggestionlist.sizeHintForRow(0)
                item_count = self.chat_window.ui.suggestionlist.count()
                height = (item_count * item_height) + 5
                self.chat_window.ui.suggestionlist.setFixedHeight(height)
                self.chat_window.ui.suggestionlist.move(self.chat_window.ui.inputbox.x(), self.chat_window.ui.messageslist.height()-height+20)
                self.chat_window.ui.suggestionlist.raise_()

    def chat_key_press(self, event: QtGui.QKeyEvent):
        modifiers = event.modifiers()
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            if modifiers:
                QtWidgets.QPlainTextEdit.keyPressEvent(
                    self.chat_window.ui.inputbox, event
                )
            else:
                self.send_button_pressed()
        else:
            QtWidgets.QPlainTextEdit.keyPressEvent(self.chat_window.ui.inputbox, event)
            self.update_auto_complete()

    def clear_input_pressed(self):
        self.chat_window.ui.inputbox.clear()

    def send_button_pressed(self):
        text = self.chat_window.ui.inputbox.toPlainText()
        if len(text) > self.message_max:
            show_message(f"Message is too long, must be within {self.message_max} characters")
            return
        if text != "":
            message = Message(
                sender=self.username,
                message=text,
                message_type="CHAT",
                time=time.time(),
                post_flag=True,
            )

            self.send_message(message)
            self.chat_window.ui.suggestionlist.lower()
            self.chat_window.ui.inputbox.clear()

    # This is for updating all incoming messages such as dates list and more (Buggy after using large texts, math is off i think)
    def update_chat(self, message: Message):
        if len(message.message) < 1:
            return

        messages_list: QtWidgets.QListWidget = self.chat_window.ui.messageslist
        times_list: QtWidgets.QListWidget = self.chat_window.ui.dateslist
        usernames_list: QtWidgets.QListWidget = self.chat_window.ui.usernamelist

        list_lines = 0
        widget_length = 98
        lines = message.message.split("\n")
        for element in reversed(lines):
            if element.strip() == "":
                lines.pop()
            else:
                break

        for line in lines:
            list_lines += len(line) // widget_length

        message.message = "\n".join(lines)
        line_count = len(lines)

        new_message = list(message.message)
        for i in range(1, list_lines + 1):
            new_message.insert(i * widget_length - 1, " ")
        message_data = "".join(new_message)

        line_count += list_lines

        username = message.sender
        unix_time = message.time
        date_time = datetime.datetime.fromtimestamp(int(float(unix_time))).strftime("%m/%d/%Y %#I:%M:%S %p")

        username_item = QtWidgets.QListWidgetItem(username + ((line_count - 1) * "\n"))
        time_item = QtWidgets.QListWidgetItem(date_time + ((line_count - 1) * "\n"))
        message_item = QtWidgets.QListWidgetItem(message_data)
        times_list.addItem(time_item)
        usernames_list.addItem(username_item)
        messages_list.addItem(message_item)

        # Scroll to the bottom

        if (
            self.chat_window.ui.messageslist.verticalScrollBar().value()
            == self.chat_window.ui.messageslist.verticalScrollBar().maximum()
        ):
            self.chat_window.ui.messageslist.scrollToBottom()
            self.chat_window.ui.dateslist.scrollToBottom()
            self.chat_window.ui.usernamelist.scrollToBottom()
        else:
            pass

    # Takes in ANY message with a time header and calculates ping. Does not update page
    def update_ping(self, message: Message):
        server_time = message.time
        time_now = time.time()
        delta_time = round(time_now - server_time)
        self.ping = delta_time

    # This updates the time animation and clock for the chat server. And any other animations someone may want to add
    def update_chat_animation(self):
        unix_time = time.time()
        date_time = datetime.datetime.fromtimestamp(int(float(unix_time))).strftime(
            "%m/%d/%Y %#I:%M:%S %p"
        )
        self.chat_window.ui.bottomlb.setText(
            f"<html><head/><body><p><span style='color:#00ad0d;'>[ </\
                                             span><span style='color:#319be6;'>{date_time}</\
                                             span><span style='color:#00ad0d;'> ] [ IRC ] [ LATENCY: </\
                                             span><span style='color:#319be6;'>{self.ping}</\
                                             span><span style='color:#00ad0d;'>MS] [ </\
                                             span><span style='color:#319be6;'>TCP</\
                                             span><span style='color:#00ad0d;'> ] [SSL: </\
                                             span><span style='color:#319be6;'>{self.ssl_active} </\
                                             span><span style='color:#00ad0d;'>]</\
                                             span></p></body></html>"
        )

        self.chat_window.ui.toptitlelb.setText(
            f"<html><head/\
                                               ><body><p><span style='color:#00ad0d;'>[ TCP CHAT ] [ Channel: </\
                                               span><span style='color:#319be6;'>{self.current_channel}</\
                                               span><span style='color:#15ada8;'>] [ ] [ </\
                                               span><span style='color:#00ad0d;'>Users: </span><span style='color:#1dada8;'>{len(self.users_list)} </\
                                               span><span style='color:#15ada8;'>]</\
                                               span></p></body></html>"
        )

    
    def leave_chat(self):
        self.chat_window.close()
        self.chat_window.clear_page()
        self.connect_window.show()
        self.close_connection()

    def handle_import_export(self, action):
        if action == "Import":
            self.connect_window.ui.ImportButton.setText("Import")
        elif action == "Export":
            self.connect_window.ui.ImportButton.setText("Export")

    def settings_popup(self):
        self.settings_window.show()

    def help_button_pressed(self):
        open_link("https://github.com/TheRealRedRiver559/Asyncio-TCP")

    def open_import_dialog(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.connect_window, "Import File", "", "All Files (*);;Text Files (*.txt)")
        if file:
            self.import_servers(file)

    def import_servers(self, file_path):
        self.connect_window.clear_page()
        current_row = 0
        with open(file_path, newline="") as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            for row in reader:
                if any(row):
                    for index, col in enumerate(row):
                        item = QtWidgets.QTableWidgetItem(col)
                        self.connect_window.ui.ServerTable.setItem(
                            current_row, index, item
                        )
                    current_row += 1

        self.selected_row = None

    def open_export_dialog(self):
        file, _ = QFileDialog.getSaveFileName(
            self.connect_window, "Export File", "", "All Files (*);;Text Files (*.txt)"
        )
        if file:
            self.export_servers(file)

    def export_servers(self, file_path):
        with open(file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            for row in range(self.connect_window.ui.ServerTable.rowCount()):
                row_data = []
                for column in range(self.connect_window.ui.ServerTable.columnCount()):
                    item = self.connect_window.ui.ServerTable.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                writer.writerow(row_data)

    def handle_theme_change(self, theme):
        theme = self.settings_window.ui.themeComboBox.currentText()
        if theme == "Light":
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

                if row == self.connect_window.ui.ServerTable.rowCount() - 1:
                    self.connect_window.ui.ServerTable.setRowCount(row + 2)
                return

    def load_server(self):
        if self.selected_row is not None:
            values = [
                self.connect_window.ui.ServerTable.item(self.selected_row, col)
                for col in range(3)
            ]
            if all(values):
                self.connect_window.ui.ServerNameText.setText(values[0].text())
                self.connect_window.ui.hostnameText.setText(values[1].text())
                self.connect_window.ui.PortText.setText(values[2].text())

    def delete_server(self):
        if self.selected_row is not None:
            self.connect_window.ui.ServerTable.removeRow(self.selected_row)
            self.connect_window.ui.ServerTable.insertRow(
                self.connect_window.ui.ServerTable.rowCount() - 1
            )
            self.selected_row = None
            self.connect_window.ui.ServerTable.clearSelection()

    def connect(self):
        hostname = self.connect_window.ui.hostnameText.text()
        port = self.connect_window.ui.PortText.text()

        if self.selected_row is not None:
            hostname_item = self.connect_window.ui.ServerTable.item(
                self.selected_row, 1
            )
            port_item = self.connect_window.ui.ServerTable.item(self.selected_row, 2)

            if hostname_item and port_item:
                hostname = hostname_item.text()
                port = port_item.text()

        if hostname == "" or port == "":
            # selective error
            if not hostname and not port:
                show_error_message("No values present.")
            elif not hostname and port:
                show_error_message("Hostname is missing.")
            else:
                show_error_message("Port is missing.")
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
            self.tcp_socket.setPrivateKey(
                QtNetwork.QSslKey(self.ssl_path, QtNetwork.QSsl.KeyAlgorithm.Rsa)
            )
            self.tcp_socket.setLocalCertificate(
                QtNetwork.QSslCertificate(self.ssl_path)
            )
            self.tcp_socket.sslErrors.connect(self.handle_ssl_errors)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHostEncrypted(hostname, port)
            self.ssl_active = True
        else:
            self.tcp_socket = QtNetwork.QTcpSocket()
            self.tcp_socket.connected.connect(self.handle_connected)
            self.tcp_socket.readyRead.connect(self.handle_ready_read)
            self.tcp_socket.errorOccurred.connect(self.handle_error)
            self.tcp_socket.connectToHost(hostname, port)
            self.ssl_active = False

        # Disable Connect button while connecting
        self.connect_window.ui.ConnectButton.setEnabled(False)

    def handle_connected(self):
        self.connected = True
        self.connect_window.close()
        self.login_window.show()

    def close_connection(self):
        if self.tcp_socket:
            self.tcp_socket.abort()
            self.connect_window.ui.ConnectButton.setEnabled(True)
        self.logged_in = False

    def handle_connection_timeout(self):
        show_error_message("Connection timeout")
        self.connect_window.ui.ConnectButton.setEnabled(True)

    def update_users(self, user_list):
        self.chat_window.ui.onlineuserslist.clear()
        self.users_list = user_list
        for user in user_list:
            user_item = QtWidgets.QListWidgetItem(user)
            self.chat_window.ui.onlineuserslist.addItem(user_item)

    def update_channels(self, channels_list):
        self.chat_window.ui.channelslist.clear()
        for channel in channels_list:
            channel_item = QtWidgets.QListWidgetItem(channel)
            self.chat_window.ui.channelslist.addItem(channel_item)

    def clear_chat_window(self):
        self.chat_window.ui.messageslist.clear()
        self.chat_window.ui.usernamelist.clear()
        self.chat_window.ui.dateslist.clear()

    def handle_ready_read(self):
        # Handle data received from the server
        while self.tcp_socket.canReadLine():
            message: Message = self.receive_data()
            self.update_ping(message)
            if message:
                message_type = message.message_type
                message_data = message.message
                if message_type == Message.REQUEST:
                    pass
                elif message_type == Message.RESPONSE:
                    pass
                elif message_type == Message.INFO:
                    if isinstance(message_data, dict):
                        keys = message_data.keys()
                        if "username_length" in keys and "message_length" in keys:
                            self.username_max = message_data["username_length"]
                            self.message_max = message_data["message_length"]
                        if "help" in keys:
                            message.message = message_data["help"]
                            self.update_chat(message)
                        if "users" in keys:
                            user_list = message_data["users"]
                            self.update_users(user_list)
                        if "channels" in keys:
                            channels_list = message_data["channels"]
                            self.update_channels(channels_list)
                        if "prefix" in keys:
                            self.prefix = message_data["prefix"]
                        if "slash_commands" in keys:
                            self.slash_commands = message_data["slash_commands"]
                    else:
                        self.update_chat(message)

                elif message_type == Message.ERROR:
                    pass
                elif message_type == Message.CHANNEL_JOIN:
                    self.clear_chat_window()
                    self.current_channel = message_data
                elif message_type == Message.CHANNEL_LEAVE:
                    self.clear_chat_window()
                    self.current_channel = message_data

                elif message_type == Message.CHAT:
                    self.update_chat(message)
                elif message_type == Message.PRIVATE:
                    self.update_chat(message)
                elif message_type == Message.STATUS:
                    if message_data == Status.PERMIT:
                        # self.update_chat(message)
                        if not self.logged_in:
                            self.logged_in = True
                            self.chat_window.show()
                            self.chat_window.ui.usernamelb.setText(
                                f'<html><head/><body><p align="right">[ {self.username} ]</p></body></html>'
                            )
                            self.login_window.close()
                            self.login_window.clear_page()

                elif message_type == Message.SYN:
                    message = Message(
                        sender=self.username,
                        message="Pong",
                        message_type=Message.ACK,
                        time=time.time(),
                    )
                    self.update_ping(message)
                    self.send_message(message)
                else:
                    pass

    def send_message(self, message: Message):
        message_dict = message.to_dict()
        json_data = json.dumps(message_dict).encode() + b"\n"
        self.tcp_socket.write(json_data)
        self.tcp_socket.flush()

    def login(self):
        self.username = self.login_window.ui.usernameText.text()
        self.password = self.login_window.ui.passwordText.text()
        if all((self.username, self.password)):
            message = Message(
                sender=None,
                message={"username": self.username, "password": self.password},
                message_type=Message.LOGIN,
                post_flag=True,
                time=time.time(),
            )
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
        if socket_error == QtNetwork.QSslSocket.SocketError.RemoteHostClosedError:
            self.close_connection()
            self.connect_window.show()
            self.chat_window.close()
            self.chat_window.clear_page()
            self.login_window.close()
            self.login_window.clear_page()
            show_error_message(f"Server disconnected.", parent=self.connect_window)
        elif socket_error == QtNetwork.QSslSocket.SocketError.ConnectionRefusedError:
            show_error_message(
                f"Could not connect to host.", parent=self.connect_window
            )
            self.connect_window.ui.ConnectButton.setEnabled(True)
        else:
            show_error_message(f"socket error detected\n{socket_error}")

    def handle_ssl_errors(self, errors):
        for error in errors:
            print("SSL error:", error.errorString())


app = QtWidgets.QApplication([])
main = Main()
main.connect_window.show()
app.exec()
