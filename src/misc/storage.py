import asyncio

clients = dict()
banned_users = set()
channels = dict()

reload_event = asyncio.Event()

events_lock = asyncio.Lock()
user_events = {}
server_events = asyncio.Queue()
channel_events = {}
