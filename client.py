import socket
from _thread import *
import sys

host = '127.0.0.1'
port = 2828
loginStatus = False
sport = ""
userName = ""

#----------------------------------------------------------------------------------------------------------------#

def process_query(ClientSocket, cmd):
    tokens = cmd.split(" ")
    keyword = tokens[0]
    
    if keyword == "LOGIN":
        if loginStatus:
            return "SERVER : User already logged in"
        else:
            resp = send(ClientSocket, cmd)
            global userName
            userName = cmd.split(" ")[1]
            return resp

    elif keyword == "CREATE_USER":
        resp = send(ClientSocket, cmd)
        return resp

    else:
        if loginStatus:
            resp = send(ClientSocket, cmd)
            return resp
        else:
            return "Please login first"

#----------------------------------------------------------------------------------------------------------------#

def getFileName(filePath):
    tkns = filePath.split("/")
    return tkns[-1]

#----------------------------------------------------------------------------------------------------------------#
#/home/ideapad/Videos/test.mp4
def send_file_data(iport, filePath):
    #print(filePath)
    header = getFileName(filePath) + "\n\n"
    fin = open(filePath, 'rb')
    content = fin.read()
    fin.close()

    ip, port = iport.split(":")

    if port==sport:
        return

    ClientSocket2 = socket.socket()
    ClientSocket2.connect((ip, int(port)))
    ClientSocket2.sendall(header.encode() + content)
    ClientSocket2.close()

#----------------------------------------------------------------------------------------------------------------#

def init_communication(resp):

    tkns = resp[4:].split("||")
    iplist = tkns[:-1]
    file_info = tkns[-1].split(" ")
    #print(file_info)
    if file_info[0].lower().replace(" ", "") == "file":
        send_file_data(iplist[0], file_info[1])
        return "File Successfully transferred."

    msg = userName + " :\> " + tkns[-1]


    for iport in iplist:
        ip, port = iport.split(":")

        if port==sport:
            continue

        ClientSocket2 = socket.socket()
        ClientSocket2.connect((ip, int(port)))
        ClientSocket2.sendall(str.encode(msg))
        ClientSocket2.close()
    
    resp = "<----- message sent ----->"
    return resp

#----------------------------------------------------------------------------------------------------------------#

def send(ClientSocket, cmd):
    ClientSocket.send(str.encode(cmd))
    Response = ClientSocket.recv(1024).decode('utf-8')
    if(Response[:2]=="IP"):
        Response = init_communication(Response)
        
    setLoginStatus(Response)
    return ("Server :\> " + Response)

#----------------------------------------------------------------------------------------------------------------#

def setLoginStatus(resp):
	if resp == "User login Successfully":
		global loginStatus
		loginStatus = True

#----------------------------------------------------------------------------------------------------------------#

def init_server(IP, PORT):

   # print("CLIENT _ SERVER THREAD")

    ServerSocket = socket.socket()
    ServerSocket.bind((IP, PORT))
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()

        data = Client.recv(1024*1024*1024, socket.MSG_WAITALL)

        data1 = data.split(b'\n\n')

        if(len(data1)>1):
            headers, body = data.split(b'\n\n', 1)
            fname = headers.decode('utf-8')
            with open(fname, "wb") as f:
                temp = f.write(body)
            print("File " + fname + " received successfully.")

        else:
            msg = data.decode('utf-8')
            print(msg)
            print()

    ServerSocket.close()

#----------------------------------------------------------------------------------------------------------------#

def main():
    print()
    print("----------> WELCOME TO MESSENGER <----------")
    print()
    print()
    ClientSocket = socket.socket()
    ClientSocket.connect((host, port))
    if len(sys.argv)!=2:
        print("Please enter correct no. of arguments")
        return
    
    iport = sys.argv[1]
    iportlist = iport.split(":")

    IP = iportlist[0]
    global sport
    PORT = int(iportlist[1])
    sport = str(PORT)
    start_new_thread(init_server, (IP, PORT))
    
    while True:
        cmd = input()
        cmd+= " " + iport
        resp = process_query(ClientSocket, cmd)
        print(resp)
        print()
    ClientSocket.close()

main()

