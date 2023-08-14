# TCP-Chat-Server

## Introduction
TCP-Chat-Server is a Python-based chat server designed to facilitate real-time communication over a network. This project offers a proof-of-concept implementation with various features, including customizable commands, channel management, private channels, and more. While primarily developed for fun and practice, it showcases the potential for building more advanced chat systems.

## Setup and Usage
- Dependencies: Ensure you have the required dependencies installed by checking the Requirements.txt file.
- Configuration: Open the Server.py and Client.py files to set the IP address of the hosting device. SSL (Secure Sockets Layer) is optional and can be configured by generating self-signed certificates for secure communication.
- Starting the Server: Run the Server.py file on your chosen device. For some network configurations, port forwarding might be necessary to allow incoming connections.
- Client Login: The client prompts for a username and password for login, although they are not essential for the proof-of-concept nature of the project.
- Channel Management: The server supports creating, joining, leaving, and deleting channels. Channels allow users to organize and interact in distinct conversation spaces.
- Customizable Commands: The chat system boasts a simple yet extensible command system. New commands can be easily added by modifying the Commands.py file, with the possibility of more complex functionality.
- Private Channels: Private channels provide a secure space for specific users to engage in confidential conversations.
- Message Broadcasting: The server enables broadcasting messages to all connected clients.
- User Management: Obtain lists of online users, user counts, and banned users.

## Showcase and Images
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/3ef6d58b-c7da-46ff-9c37-bc90662d265a)
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/f5641986-9837-49f9-bfd1-53ce6ff964c4)
![image](https://github.com/TheRealRedRiver559/Asyncio-TCP/assets/80642468/6422c391-018c-4da7-88c2-6c3801c2bee0)



<div style="display: flex;">
  <img src="https://github.com/TheRealRedRiver559/Asyncio-TCP/blob/master/assets/80642468/3ef6d58b-c7da-46ff-9c37-bc90662d265a.png" alt="Image 1" style="width: 33%; padding: 5px;">
  <img src="https://github.com/TheRealRedRiver559/Asyncio-TCP/blob/master/assets/80642468/f5641986-9837-49f9-bfd1-53ce6ff964c4.png" alt="Image 2" style="width: 33%; padding: 5px;">
  <img src="https://github.com/TheRealRedRiver559/Asyncio-TCP/blob/master/assets/80642468/6422c391-018c-4da7-88c2-6c3801c2bee0.png" alt="Image 3" style="width: 33%; padding: 5px;">
</div>

## Command Usage
The defualt commands are structured as follows:

- help: Display a list of available commands and their usages.
- create-channel <channel name>: Create a new channel with the specified name.
- join-channel <channel name>: Join a specified channel.
- leave-channel: Leave the current channel.
- delete-channel <channel name>: Delete an existing channel.
- users: List all online users.
- user-count: Display the count of online users.
- banned-users: List banned users.
- broadcast <message>: Send a message to all users.
- ban <username> (reason): Ban a user with an optional reason.
- unban <username>: Unban a previously banned user.
- disable-command <command name>: Disable a specified command.
- enable-command <command name>: Enable a previously disabled command.
# Recent Updates
- Added private and password-protected channels.
- New updates relating the GUI. It now features auto suggestions.
- Added a ping system to handle unresponsive clients.
- Incorporation of type hints and documentation to enhance code clarity.
### Future updates and improvements include:
- Implementing SSL/TLS for enhanced security during data transmission.
- Incorporating an SQL database for secure hashed and salted logins.
- Finishing the GUI
- Adding a public server that anyone can join!
## Known Issues
While efforts have been made to ensure stability, some issues have been identified and are being addressed:
- Server crashes when trying to access and change data storage
- Improved performance is being sought for scenarios involving multiple users.
- Addressing intermittent connection interruptions.
- Further refining color checks and metadata in messages.
- Continuously resolving any unidentified errors.

# Note
TCP-Chat-Server is an ongoing project, and user suggestions and contributions are welcomed. Please be aware that this system is not intended for secure or critical applications due to potential vulnerabilities and limitations.

Enjoy the experience of exploring and contributing to this evolving chat server project!
