# TCP-Chat-Server  (Non SSL)
This TCP chat server is an ongoing project and really just a nice learning experience for me and an intro into networking. I plan on adding tons of features in the fute and re-writing all of the code to make it run asynchrously and with much more security of course. This was just a small project at first but branched out as one of my main ones and I really enjoy working on this. Any help or advice to make this any better is always appreciated!

# Setup
Make sure the 'Server.py' file is running before trying to connect to it. It will not let clients connect without it.
Once the server is running you can connect clients to the server.

# Todo and Future
To Add
- [ ] Original Commands
- [ ] Login System with password
- [x] Color Checks for usernames 
- [x] Re-write using Asnyio and better more documented code.
- [ ] More commands and a new system to send data across networks. (SSL / TSL)
- [ ] An SQL database for hashed + salted logins.
To Fix

- [x] Better performance with multiple users (Async will help a lot)
- [x] Connections being interupted
- [x] Color checks and meta data in messages

Some current bugs are as follows -
- Rich library responding to user messages making it so they can color and add whatever they want to their usernames (I may keep this but intergrate into a feature such as a command or something for permenant colors)

I plan on adding tons of new stuff and cool features so any suggestions are awesome! This is by no means a secure server or anything like that, i just made it for fun and practice. Im sure there are multiple vulnerabilities and issues so i advise not using this for anything serious.
Enjoy!
