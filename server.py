import socket
import os
import sys
from _thread import *

IP = '127.0.0.1'
PORT = 2222

userData = {}
UIPort = {}
groups = {}
uroll = {}

#----------------------------------------------------------------------------------------------------------------#

def get_userName(iport):
    for entry in UIPort:
        if UIPort[entry]==iport:
            return entry

#----------------------------------------------------------------------------------------------------------------#

def printUIPort():
    for entry in UIPort.keys():
        print(entry + " " + UIPort[entry])
        print

#----------------------------------------------------------------------------------------------------------------#

def isUserExist(userID , password):
    if userID in userData:
        return True
    return False

#----------------------------------------------------------------------------------------------------------------#

def isRollExist(roll):
    for r in uroll:
        if uroll[r]==roll:
            return True
    return False

#----------------------------------------------------------------------------------------------------------------#

def create_user(userID, password, roll, iport):
    if isUserExist(userID, password) == False:
        userData[userID] = password
        if isRollExist(roll):
            return "This rollno already exist."
        uroll[userID] = roll
        return "User created successfully."
    else:
        return "User already existed"

#----------------------------------------------------------------------------------------------------------------#

def login(userID, pwd, iport):
    if userID in userData.keys():
        if userData[userID] == pwd:
            UIPort[userID] = iport
            return "User login Successfully"
        else:
            return "Invalid password"
    else:
        return "User doesn't exist"    

#----------------------------------------------------------------------------------------------------------------#

def create_group(gname, iport):
    userName = get_userName(iport)
    if gname in groups:
        return "Group already exist"
    else:
        ls = []
        ls.append(userName)
        groups[gname] = ls
        return "Group created successfully."

#----------------------------------------------------------------------------------------------------------------#

def join_group(gname, iport):
    userName = get_userName(iport)

    if gname not in groups:
        return "Group doesn't exist."
    else:
        if userName in groups[gname]:
            return "You are already a member."
        groups[gname].append(userName)
        return "Group joined successfully."

#----------------------------------------------------------------------------------------------------------------#

def list_groups():
    resp = ""
    if len(groups)==0:
        return "No groups present"

    for entry in groups:
        resp += entry + " | "

    resp = resp[:-3]
    return resp

#----------------------------------------------------------------------------------------------------------------#

# Assumption :--> g1,g2,g2

def getIPs(tokens):
    names = tokens[1].split(",");
    print("---------------------------")
    print(names)
    print("---------------------------")
    ips = "IP||"
    for name in names:
        
        if name in UIPort:
            ips += UIPort[name]+ "||"
        
        elif name in groups.keys():

            for users in groups[name]:
                uip = UIPort[users]
                ips += uip + "||"
        else:
            return "Invalid User name or Group name."
        print(ips)

    print("--------------------------------")
    return ips

#----------------------------------------------------------------------------------------------------------------#

def process_request(msg):
  #  print(msg) 
    tokens = msg.split(" ")
    iport = tokens[-1].replace(" ", "")
    tokens = tokens[:-1]
   # print(tokens)
    cmd = tokens[0]

    if(cmd=="CREATE_USER"):
        if len(tokens)!=4:
            return "Invalid Number of arguments."
        userId = tokens[1]
        pwd = tokens[2]
        roll = tokens[3]
        res = create_user(userId, pwd, roll, iport)
        return res

    if(cmd=="LOGIN"):
        if len(tokens)!=3:
            return "Invalid Number of arguments."        
        userId = tokens[1]
        pwd = tokens[2]
        res = login(userId, pwd, iport)
        return res

    if(cmd=="CREATE"):
        if len(tokens)!=2:
            return "Invalid Number of arguments."
        gname = tokens[1]
        res = create_group(gname, iport)
        return res

    if(cmd=="JOIN"):
        if len(tokens)!=2:
            return "Invalid Number of arguments."
        gname = tokens[1]
        res = join_group(gname, iport)
        return res

    if(cmd=="LIST"):
        if len(tokens)!=1:
            return "Invalid Number of arguments."
        res = list_groups()
        return res

    if(cmd=="SEND"):
        res = getIPs(tokens)
        msg = ""
        for i in range(2, len(tokens)):
            msg+=tokens[i] + " "
        res += msg
        return res

    if(cmd=="CHECK"):
        printUIPort()
        return "ALL TEST CASES PASS! WAHH BHAIMYA FUMLL CHECKUP BAZI"

    return "NO String Received.."
    
#----------------------------------------------------------------------------------------------------------------#

def threaded_client(connection):
    #connection.send(str.encode('Welcome to the Server\n'))
    while True:
        data = connection.recv(2048).decode('utf-8')
        resp = process_request(data)
        print(resp)
        if not data:
            break
        connection.sendall(str.encode(resp))
    connection.close()

#----------------------------------------------------------------------------------------------------------------#

def main():
    ServerSocket = socket.socket()
    ThreadCount = 0 

    ServerSocket.bind((IP, PORT))

    print('Listening..')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()

        start_new_thread(threaded_client, (Client,))
        
        ThreadCount += 1

    ServerSocket.close()

main()