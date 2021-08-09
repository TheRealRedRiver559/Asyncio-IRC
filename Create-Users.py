import hashlib
import os
import mysql.connector as mysql
from rich.panel import Panel
from rich import print

db_name = ''
db_pass = ''

with mysql.connect(
    host = 'localhost',
    user = 'root',
    password = db_pass,
    database = db_name,
) as conn:

    cursor = conn.cursor()
    #users
    cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER AUTO_INCREMENT PRIMARY KEY, user_name VARCHAR(20) UNIQUE, user_hash VARBINARY(85), user_salt VARBINARY(85), role_id INT)")
    #roles
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (id INTEGER AUTO_INCREMENT PRIMARY KEY, role_id INTEGER UNIQUE, role_name VARCHAR(20) UNIQUE)")

def create_user():
    username = str(input('Username : ')).lower()
    password = str(input('Password : '))
    try:
        access_level = int(input('Access Level: 1-inf : '))
        if access_level <= 0:
            print('Cannot be below 0 or 0.')
            return
    except ValueError:
        print('Only integers allowed!')
        return

    salt = os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000)

    try:
        with mysql.connect(
        host = 'localhost',
        user = 'root',
        password = db_pass,
        database = db_name,
        ) as conn:
            cursor = conn.cursor()
            add_info = "INSERT INTO users (user_name, user_hash, user_salt, role_id) VALUES (%s, %s, %s, %s)"
            info = (username, hashed_password, salt, access_level)

            cursor.execute(add_info, info)
            conn.commit()
        print(f'User: {username} Created')
    except Exception as e:
        print(e)
        print('Username already taken! Returning to menu...')
        return

def login_test():
    username = str(input('Username : ')).lower()
    password = str(input('Password : '))

    with mysql.connect(
    host = 'localhost',
    user = 'root',
    password = db_pass,
    database = db_name,
    ) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT user_name, user_hash, user_salt FROM users')
        user_data = cursor.fetchall()
    for user in user_data:
        if username in user[0]:
            hash, salt = bytes(user[1]), bytes(user[2]) #converts the string hash and salt from the db to a byte for the new hash
        else:
            pass
    try:
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000)
        if new_hash == hash:
            print('Logged In!')
        else:
            print('Password or Username is incorret!')
    except UnboundLocalError: #Checks if the username is being assigned nothing (no user)
            print('Password or Username is incorret!')

def menu():
    print(Panel("Help\nLogin\nCreate\nExit", title="[cyan]Commands",expand=False))
    #print('| Help | Login | Create | Exit |')
menu()
while True:
    options = str(input('Command : '))
    if options.lower() == 'help':
        menu()
    elif options.lower() == 'create':
        create_user()
    elif options.lower() == 'login':
        login_test()
    elif options.lower() == 'exit':
        exit()
    else:
      print('Command not found!\n These are the avialable commands.')
      menu()
