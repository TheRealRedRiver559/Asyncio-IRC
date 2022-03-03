# TCP-Chat-Server
This TCP chat server is an ongoing project and really just a nice learning experience for me and an intro into networking. I plan on adding tons of features in the fute and re-writing all of the code to make it run asynchrously and with much more security of course. This was just a small project at first but branched out as one of my main ones and I really enjoy working on this. Any help or advice to make this any better is always appreciated!

# General Information
Defualt Command Prefix =  '//'

Commands and their permissions can be handled in the function decorators located in the 'Server.py' file.
Role permissions and Users can be created in the 'Create Users.py' file.
Uses 'Rich' Library for coloring prompts, and messages / names.
Commands can easily be added using the @command decorator with functions.
Access levels are the way role hierachys work, the higher the access level the more permissions and power. You can change functions and commands to have required access roles as well.

# Setup
Make sure the 'Server.py' file is running before trying to connect to it. It will not let clients connect without it.
Once the server is running you can connect clients to the server.
To create a new user go to the 'Create-Users.py' file and make a username, password, and an access level.

# Commands
These are the current commands :
  Users
  Banned-users
  Connections
  Ban
  Unban
  Help.

All commands have custom descriptions explaining what it does and some examples on how to use it.
Most of the commands have either 1 or more arguments required.
Dynamic prefix for the descriptions allowing it to be changed easily.

# Todo and Future
To Add
- [ ] Re-write using Asnyio and better more documented code.
- [ ] More commands and a new system to send data across networks.
- [ ] An SQL database for hashed + salted logins.

To Fix

- [ ] Better performance with multiple users (Async will help a lot)
- [ ] Connections being interupted
- [ ] Color checks and meta data in messages

Some current bugs are as follows -
- Rich library responding to user messages making it so they can color and add whatever they want to their usernames (I may keep this but intergrate into a feature such as a command or something for permenant colors)
- When checking the name of a user to the name of a user with a very similiar name, it can cause color swaps since I am using  the '.startsWith()' method. So re-write code structure to allow passing of message length and username length for exact checks.


I plan on adding tons of new stuff and cool features so any suggestions are awesome! This is by no means a secure server or anything like that, i just made it for fun and practice. Im sure there are multiple vulnerabilities and issues so i advise not using this for anything serious.
Enjoy!
