import sqlite3
import os
path = os.getcwd()
conn = sqlite3.connect(fr'{path}\ServerStorage.db')

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT -- Assuming passwords are hashed
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS BannedUsersChannel (
    ban_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for the ban record
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    ban_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of when the ban was issued
    ban_duration REAL,  -- Duration of the ban in days, NULL for permanent bans
    ban_reason TEXT,  -- Optional field to describe the reason for the ban
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_name TEXT NOT NULL UNIQUE,
    password TEXT, -- NULL if no password is set
    is_private INTEGER NOT NULL DEFAULT 0, -- 0 for public, 1 for private
    is_visible INTEGER NOT NULL DEFAULT 1 -- 1 for public, 0 for private
);""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS UserChannelPermissions (
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    permission_level INTEGER NOT NULL,
    PRIMARY KEY (user_id, channel_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER,
    sender_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_type TEXT NOT NULL,
    message TEXT NOT NULL,
    additional_info TEXT  -- Optional, for storing any extra information
);""")
conn.commit()