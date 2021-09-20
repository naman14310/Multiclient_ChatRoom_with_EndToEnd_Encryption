import socket
import random
import hashlib
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from _thread import *
import sys

#------------------------------------------- GLOBAL VARIABLES ---------------------------------------------------#

host = '127.0.0.1'
port = 2222
loginStatus = False
sport = ""
userName = ""
rollno = ""
BLOCK_SIZE = 32
p=1000000007
g=2

#----------------------------------------------------------------------------------------------------------------#

def generate_public_key(roll):
    t1=random.randint(0,999)
    a = roll + str(t1)
    a = int(a)
    #print(a)

    pka1=hashlib.sha256(str(a).encode())
    #print(int(pka1.hexdigest(),16))
    pka=int(pka1.hexdigest(),16)

    public_a=pow(g,pka,p) 
    #print(public_a)
    return public_a, pka 

#----------------------------------------------------------------------------------------------------------------#

def generate_shared_key(key1, key2):
    shared_key_1 = pow(key1, key2, p)
    #print(shared_key_1)
    return shared_key_1

#----------------------------------------------------------------------------------------------------------------#

def DES_encrypt(key, plaintext, isFile):
    key = str(key)
    if(len(key)<15):
        key=key+'0'*(15-len(key)) 
    key=key.encode()
    #print("" + len(key))
    while(len(key)!=24):
        key+=b"\0"
    key=DES3.adjust_key_parity(key)
    cipher = DES3.new(key,DES3.MODE_ECB)
    if isFile:
        msg = cipher.encrypt(pad(plaintext, BLOCK_SIZE))
        return msg
    else:
        msg = cipher.encrypt(pad(plaintext.encode(), BLOCK_SIZE))
        return msg

#----------------------------------------------------------------------------------------------------------------#

def DES_decrypt(key, msg):
    key = str(key)
    if(len(key)<15):
        key=key+'0'*(15-len(key)) 
    key=key.encode()
    while(len(key)!=24):
        key+=b"\0"
    key=DES3.adjust_key_parity(key)
    cipher = DES3.new(key,DES3.MODE_ECB)
    plaintext= cipher.decrypt(msg)
    return plaintext

#----------------------------------------------------------------------------------------------------------------#

def process_query(ClientSocket, cmd):
    tokens = cmd.split(" ")
    keyword = tokens[0]
    
    if keyword == "LOGIN":
        if loginStatus:
            return "Server :\>  User already logged in"
        else:
            resp = send(ClientSocket, cmd)
            global userName, rollno
            userName = cmd.split(" ")[1]
            return resp

    elif keyword == "CREATE_USER":
        resp = send(ClientSocket, cmd)
        rollno = cmd.split(" ")[3]
        return resp

    else:
        if loginStatus:
            resp = send(ClientSocket, cmd)
            return resp
        else:
            return "Server :\> Please login first"

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

    #-------------------- ENCRYPTION--------------------#

    pubkey, pk = generate_public_key(rollno)
    pubkey = str(pubkey)
    pk = str(pk)

    ClientSocket2 = socket.socket()
    ClientSocket2.connect((ip, int(port)))

    ClientSocket2.sendall(str.encode(pubkey))
    rkey = ClientSocket2.recv(1024*1024*1024).decode()

    rkey = int(rkey)
    pk = int(pk)
    sharedKey = generate_shared_key(rkey, pk)

    msg = header.encode() + content
    msg = DES_encrypt(sharedKey, msg, True)

    ClientSocket2.sendall(msg)
    ClientSocket2.close()

#----------------------------------------------------------------------------------------------------------------#

def send_file_to_group(iplist, filePath):
    for iport in iplist:
        ip, port = iport.split(":")
        if port==sport:
            continue
        send_file_data(iport, filePath)

#----------------------------------------------------------------------------------------------------------------#

def init_communication(resp):
    tkns = resp[4:].split("||")
    iplist = tkns[:-1]
    #print(iplist)
    file_info = tkns[-1].split(" ")
    #print(file_info)
    if file_info[0].lower().replace(" ", "") == "file":
        if(len(iplist)>1):
            send_file_to_group(iplist, file_info[1])
            return "File Successfully transferred."
        send_file_data(iplist[0], file_info[1])
        return "File Successfully transferred."

    for iport in iplist:
        ip, port = iport.split(":")
        msg = userName + " :\> " + tkns[-1]
        if port==sport:
            continue
        
        #-------------------- ENCRYPTION--------------------#

        pubkey, pk = generate_public_key(rollno)
        pubkey = str(pubkey)
        pk = str(pk)

        ClientSocket2 = socket.socket()
        ClientSocket2.connect((ip, int(port)))

        ClientSocket2.sendall(str.encode(pubkey))
        rkey = ClientSocket2.recv(1024*1024*1024).decode()

        rkey = int(rkey)
        pk = int(pk)
        sharedKey = generate_shared_key(rkey, pk)

        msg = DES_encrypt(sharedKey, msg, False)

        ClientSocket2.sendall(msg)
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
    ServerSocket = socket.socket()
    ServerSocket.bind((IP, PORT))
    ServerSocket.listen(5)

    while True:

        Client, address = ServerSocket.accept()

        rkey = Client.recv(1024).decode()
        pubkey, pk = generate_public_key(rollno)
        pubkey = str(pubkey)
        Client.sendall(str.encode(pubkey))

        rkey = int(rkey)
        pk = int(pk)
        sharedKey = generate_shared_key(rkey, pk)

        data = Client.recv(1024*1024*1024, socket.MSG_WAITALL)

        data = DES_decrypt(sharedKey, data)

        data1 = data.split(b'\n\n')

        if(len(data1)>1):
            headers, body = data.split(b'\n\n', 1)
            fname = userName + "_" + headers.decode('utf-8')
            with open(fname, "wb") as f:
                temp = f.write(body)
            print("File " + fname + " received successfully.\n")

        else:
            msg = data.decode('utf-8')
            print(msg)
            print()

    ServerSocket.close()

#----------------------------------------------------------------------------------------------------------------#

def main():
    print()
    print("---------------------> WELCOME TO MESSENGER <---------------------")
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
