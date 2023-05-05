# TCP-Chat-Server
This TCP chat server is an ongoing project and really just a nice learning experience for me and an intro into networking. I plan on adding tons of features in the fute and re-writing all of the code to make it run asynchrously and with much more security of course. This was just a small project at first but branched out as one of my main ones and I really enjoy working on this. Any help or advice to make this any better is always appreciated!

For SSL go to the Async Branch

# Setup

This version includes Certifacites. You will need to either find one or sign one yourself. I reccomend just signing one yourself and sending it to both machine or placing it in 1 file, since this isnt secure anyways really. 

You can start a client or server first, they will both wait for the other to go online to actually make a valid connection. 
Commands have been removed due to me re working them so they can be updated live or switched off whenever if something breaks. Sort of like Git's thing. 
I will add a version without SSL soon. 

A GUI is also being made for the Client program that is using a library called "CustomTkinter" It should be done in about 1-2 months. 

# Todo and Future
To Add
- [ ] Original Commands
- [x] Login System with password
- [x] Color Checks for usernames 
- [x] Re-write using Asnyio and better more documented code.
- [x] More commands and a new system to send data across networks. (SSL / TSL)
- [ ] An SQL database for hashed + salted logins.
To Fix

- [x] Better performance with multiple users (Async will help a lot)
- [x] Connections being interupted
- [x] Color checks and meta data in messages

Some current bugs are as follows -
- Rich library responding to user messages making it so they can color and add whatever they want to their usernames (I may keep this but intergrate into a feature such as a command or something for permenant colors)

I plan on adding tons of new stuff and cool features so any suggestions are awesome! This is by no means a secure server or anything like that, i just made it for fun and practice. Im sure there are multiple vulnerabilities and issues so i advise not using this for anything serious.
Enjoy!
