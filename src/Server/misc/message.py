from __future__ import annotations
import time

class MessageType:
    CHAT = "CHAT" # For sending general chat messages
    SERVER = "SERVER" # Server and system messages
    AUTH = "AUTH" # Authentication messages for logging in and registration messages
    ERROR = "ERROR" #  main type for all error messages
    INFO = "INFO" # Info type for storage and so on
    STATUS = "STATUS" #status message for access
    CONN = "CONN"
    COMMAND = "COMMAND"

class MessageSubType:
    REQUEST = "REQUEST" #Requests data
    RESPONSE = "RESPONSE" # Response to a request
    CLOSE = "CLOSE_CONN" # closes connection
    LOGIN = "LOGIN" # login  flag
    REGISTER = "REGISTER" # register flag
    ACK = "ACK" # ack flag
    SYN = "SYN" # syn flag
    CHANNEL_LEAVE = "CHANNEL_LEAVE" #channel leave response
    CHANNEL_JOIN = "CHANNEL_JOIN" # channel join response
    CHANNEL_CREATE = "CHANNEL_CREATE" # channel create response
    CLEAR = "CLEAR" # clear response 
    CONN_ERROR = "CONNECTION_ERROR" # connection error
    CHANNEL_LIST = "CHANNEL_LIST" # list of channels for client updates
    USER_LIST = "USER_LIST" #list of clients for the client updates
    PUBLIC = "PUBLIC" # used for CLI client messaging and formatting
    PRIVATE = "PRIVATE" # used for CLI client messaging and formatting
    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_ACCESS = "INVALID_ACCESS"
    DISABLED = "DISABLED"
    GENERAL = "GENERAL"
    TEST_MESSAGE = "TEST_MESSAGE"
    BROADCAST = "BROADCAST"
    COMMAND_RESPONSE = "COMMAND_REPONSE"
    SLASH_COMMANDS = "SLASH_COMMANDS"
    COMMAND_ERROR = "COMMAND_ERROR"
    BANNED = "BANNED"
    KICKED = "KICKED"
    UNBANNED = "UNBANNED"
    MESSAGE_LENGTH = "MESSAGE_LENGTH"
    USERNAME_LENGTH = "USERNAME_LENGTH"
    CONNECT_DATA = "CONNECT_DATA"
    INVALID_FORMAT = "INVALID_FORMAT"
    FAILED_LOGIN = "FAILED_LOGIN"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    PERMIT = "PERMIT"
    DENY = "DENY"
    PASSED_LOGIN = "PASSED_LOGIN"
    PREFIX_CHANGE = "PREFIX_CHANGE"
    CLEAR = "CLEAR"
    HISTORY = "HISTORY" # History message telling the client history data is coming.

class Message:
    def __init__(self, sender: str, message: str, main_type: str, sub_type: str, _time=None) -> None:
        self.sender = sender
        self.message = message
        self.main_type = main_type
        self.sub_type = sub_type
        self.time = time.time()

    async def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "message": self.message,
            "main_type": self.main_type,
            "sub_type": self.sub_type,
            "time": self.time,
        }

    @staticmethod
    async def from_dict(data) -> Message:
        return Message(
            sender=data.get("sender"),
            message=data.get("message"),
            main_type=data.get("main_type"),
            sub_type=data.get("sub_type"),
            _time=data.get("time"),
        )
