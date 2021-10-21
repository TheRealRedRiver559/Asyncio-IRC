import json
import os.path
from json import JSONDecodeError

def create_user():
    if not os.path.exists("Tcp Server\\users.json"):
        with open("Tcp Server\\users.json", "w"):
            pass
    username = str(input('Username : ')).lower()
    password = str(input('Password : '))
    try:
        access_level = int(input('Access Level: 1-5 : '))
        if access_level <= 0:
            print('Must be above 0')
            return
        elif access_level > 5:
            access_level = 5
            print(access_level)
    except ValueError:
        print('Only integers allowed...')
        return

    with open('Tcp Server\\users.json', 'r') as f:
        try:
            data = json.load(f)
            data[username] = {"role_id": access_level, "password": password}
        except JSONDecodeError:
            data = {username:{"role_id": access_level, "password": password}}
    with open('Tcp Server\\users.json', 'w') as f:
        json.dump(data, f)
        print('User created')

create_user()
