# TCP-Chat-Server
This TCP chat server is an ongoing project and really just a nice learning experience for me and an intro into networking. I plan on adding tons of features in the fute and re-writing all of the code to make it run asynchrously and with much more security of course. This was just a small project at first but branched out as one of my main ones and I really enjoy working on this. Any help or advice to make this any better is always appreciated!

For non-SSL go to the Async Branch

# Setup

Be sure to install the Requirments and that you have all the required dependicies installed.

Start the Server.py file either on some sort computer, workstation or server. Depending on your network you ay have to port forward or open up certain parts of your network for this to work. If you have an ordinary home router with no configs, you just need to set the ip address to whatever host you use. Set the IP of the hosting device on the Server.py and the Client.py. 
After these steps you can either start the Server or Client, the client will keep trying to connect if the server is down so it doens really matter. 
SSL is optional, you will have to self sign certs if you would like to do that until I port this to WebSockets so its automatic. 

The client will ask for a username and password to login, these values do NOT matter since this is a proof of concept type of project. 
Most settings and options are configurable in the Server.py and Commands.py file such as message logging, and more. 
You can add commnads very easily due to the simple decorator system I have in place. 

A GUI is also being made for the Client program that is using a library called "CustomTkinter" It should be done in about 1-2 months. 

# Command Usage
Commands are stored in the Commands.py file. Here you can edit command functionality easily and change whatever you want. There is a Temp.py file acting as a intermdiary for the Commands and Server file. This file stores some client information and general data sets. Kind of like a local mini data base. 

Command Usage is pretty simple. The defualt prefix is a double forward slash: //. The commands and arguments are as follow :
<> = Required, () = optional

help   ->  returns a useful list of available commands and their usages.
create-channel <channel name>  ->   Creates a channel with the specified name.
join-channel <channel name>   ->  Joins specified channel.
}leave-channel  ->  leaves the current channel you are in. 
delete-channel <channel name>   ->  Deletes the specified channel name if it exists.
users  ->  returns a list of all online users in the server.
user-count     ->  returns a numeric amount of users online.
banned-users   ->  returns a list of all banned-users.
broadcast <message>    ->  broadcasts a message as the server.
ban <username> (reason)    ->  bans a user with an optional reason.
unban <username> ->    unbans a specified user.
disable-command <command name>     ->  diables the specified command.
enable-command <command name>  ->  enables the specified command."""


# Todo and Future Roadmap
GUI, private messaging, file transfering, compression

# Todo and Future
To Add
- [x] Commands
- [x] Login System with password
- [x] Color Checks for usernames 
- [x] Re-write using Asnyio and better more documented code.
- [x] More commands and a new system to send data across networks. (SSL / TSL)
- [ ] An SQL database for hashed + salted logins.
- [ ] GUI for clients
- [ ] Server clustering for load balancing and to create larger networks.
- [ ] Private Channels
- [ ] Message control features for server side (Allows complex functions and commands that can recieve input and responses)

To Fix
- [x] Better performance with multiple users (Async will help a lot)
- [x] Connections being interupted
- [x] Color checks and meta data in messages
- [ ] Any erros still missing that havent been updated...
Some current bugs are as follows -
- Basic disconect exceptions that have not been covered yet. 
- Changing Networks when connected will void that connected username.
  
I plan on adding tons of new stuff and cool features so any suggestions are awesome! This is by no means a secure server or anything like that, i just made it for fun and practice. Im sure there are multiple vulnerabilities and issues so i advise not using this for anything serious.
Enjoy!


# Examples or images
[image-7](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/6b9ec54d-2600-4f8f-a9ec-5c51e41558d7)
  
![image-8](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/8460739d-17d7-4ff9-b333-d977a07d3e4a)
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/e4103b6e-90ef-4f5f-bbb3-cd3d69b4f935)

