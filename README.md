# TCP-Chat-Server

## New Update Coming Soon!
# Status Update #
Update is taking longer than expected, I wanted to devolop a new GUI using Textual or some other framework, but It has proven to be more difficult than I originally thought. I will continue working with the normal terminal GUI, and also the PySide6 GUI alongside it. 

- Adding lots of new commands with complex-like features. (Clear, custom-input, and more)
- Adding private messaging (finally) and the addition of private channels that can be password protected and privately viewed.
- Implementing SQL Light for a much better, and faster data design structure. This will allow the user permissions and channels to be used to their full extent in the coming updates.
- SSL or some other private security for data.
- More optimizations and an easier-to-make command systems
- Will be fixing the Command line Client to accommodate more features and support new changes.


## Introduction
TCP-Chat-Server is a Python-based chat server designed to facilitate real-time communication over a network. This project offers a proof-of-concept implementation with various features, including customizable commands, channel management, private channels, and more. While primarily developed for fun and practice, it showcases the potential for building more advanced chat systems.

## Setup and Usage
- Dependencies: Ensure you have the required dependencies installed by checking the Requirements.txt file.
- Configuration: Open the Server.py and Client.py files to set the IP address of the hosting device. SSL (Secure Sockets Layer) is optional and can be configured by generating self-signed certificates for secure communication. (It is off by defualt on the server side)
- Starting the Server: Run the Server.py file on your chosen device. For some network configurations, port forwarding might be necessary to allow incoming connections.
- Client Login: The client prompts for a username and password for login, although they have no purpose in the program besides displaying information, they will be of use in a public version.
- Channel Management: The server supports creating, joining, leaving, and deleting channels. Channels allow users to organize and interact in distinct conversation spaces. There are public and private channels that can be created by adding a password argument to create-channel
- Customizable Commands: The chat system has a simple yet extensible command system. New commands can be easily added by modifying the Commands.py file, with the possibility of more complex functionality.
- Message Broadcasting: The server enables broadcasting messages to all connected clients to either all channels and their users, or all users in a channel
- User Management: Obtain lists of online users, user counts, banned users, and permissions.

## Showcase and Images
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/3ef6d58b-c7da-46ff-9c37-bc90662d265a)
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/f5641986-9837-49f9-bfd1-53ce6ff964c4)
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/6422c391-018c-4da7-88c2-6c3801c2bee0)
There is a CLI version, but in this branch, it has not been updated yet.
The server has features such as a settings window, a connect and login page, and many more useful features. This is still in development, but I am adding more every week. Recently I have been working on a context menu for users and channel to make it easier to add, message, and join channels or users.

## Command Usage
The default commands are structured as follows:

- `help`: Display a list of available commands and their usages.
- `channel`:Display a list of public or available channels to join
- `create-channel <channel name> (password)`: Create a new channel with the specified name.
- `join-channel <channel name> (password)`: Join a specified channel.
- `leave-channel`: Leave the current channel.
- `delete-channel <channel name>`: Delete an existing channel.
- `users`: List all online users.
- `user-count`: Display the count of online users.
- `banned-users`: List banned users.
- `broadcast <message>`: Send a message to all users.
- `ban <username> (reason)`: Ban a user with an optional reason.
- `unban <username>`: Unban a previously banned user.
- `disable-command <command name>`: Disable a specified command.
- `enable-command <command name>`: Enable a previously disabled command.
- `set-prefix <new prefix>`: Set a custom prefix for command invocation.
- `set-perm <user> <new permission level>`: Modify permissions for specific users or roles.
- `command-history`: Display a history of recently executed commands and their arguments.
- `input-test`: Test input functionality of server response event.
- `test`:Displays a test message as a proof of concept command.
- 
# Recent Updates
- None

# Plans and things I want to implement
- Channels will now have thier own permission sets. This is sort of like discords channel system with roles and what not.
- Named permission levels. At the moment the server only allows numeric roles. However, I plan to add some sort of naming scheme you can implement per channel.
- Client that will show the command arguments and description when typing instead of just the name.
- Update the CLI client with tables using rich, curses, colorama, or something similiar. 
  
## Known Issues
While efforts have been made to ensure stability, some issues have been identified and are being addressed:
- Server overloads when lots of clients join and spam messages. Due to not having a send / receive queue.
- No interval or rate limiting of messages. Will add one for the server, and a custom interval for each channel. 
- Improved performance is being sought for scenarios involving multiple users still.
- Performance issue involving the servers active client data structure. Need to add locks and find a way to not use .copy() since its slow. 
- Continuously resolving any unidentified errors.

# Note
TCP-Chat-Server is an ongoing project, and user suggestions and contributions are welcomed. Please be aware that this system is not intended for secure or critical applications due to potential vulnerabilities and limitations at the moment.
