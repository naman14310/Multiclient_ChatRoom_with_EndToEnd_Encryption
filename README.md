# Lab Assignment 1 : An end to end messaging system

A multiclient chat application in which message can be sent to an individual or a group with end to end encryption. 

## Files present in the folder

1. server.py
2. client.py
3. load_balancer.py
4. userData.txt, groups.txt, uroll.txt, UIPort.txt
5. class_diagram.pdf

## How to run ?

`python server.py <PORT>`

`python load_balancer.py`

`python client.py <IP:PORT>`

## Assumptions 

1. We used file handling for storing user data permanently at the server side.

2. Load balancer will take care of servers and allot server (with less load) to clients.

3. For sending messages to multiple users or groups, write their names in comma seperated format without any space. (Eg : user1,user2,grp1,grp2)

4. We assumed that unique Roll no. and usernames will be provided.

5. In CREATE_USER command, inputs should be given in this format : `CREATE_USER <username> <password> <rollno>`
  
6. For sending normal messages, use this command : `SEND <username(s) or group(s)> <message>`
  
7. For sending files, use this command : `SEND <username(s) or group(s)> FILE <filepath>`
  
8. Shared files will be saved in the current working directory with name `username_filename`.
