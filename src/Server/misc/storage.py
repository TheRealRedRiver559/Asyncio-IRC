import asyncio

# Crazy storage system 
clients = dict()
banned_users = set()
channels = dict()
commands = dict()
prefix = "//"
killed_commands = set()
reload_event = asyncio.Event()

message_queue = asyncio.Queue()
events_lock = asyncio.Lock()
user_events = dict()
server_events = asyncio.Queue()
channel_events = dict()