import zmq
import hashlib
import os
import json


context = zmq.Context()
socket = context.socket(zmq.REQ)                # REQ because I going to request
socket.connect("tcp://127.0.0.1:3000")
print("<option> File")
print("submit pathFile")
print("download File")
print("add hash")
sizeBuf = 1024*1024*1  # 10MB
Files = {}

# This is to submit file to server
def submit(path):
    # Creo el hash con el cual va a quedar en el servidor
    os.stat(path).st_size
    with open(path, 'rb') as f :
        sha1 = hashlib.sha1()
        while True:
            data = f.read(sizeBuf)
            if not data :
                break
            sha1.update(data)
    # Save NameFile with your respect hash 
    Files[os.path.basename(path)] = sha1.hexdigest()
    with open("datos.json", "w") as f:
        json.dump(Files, f)
    # Submit File in the server
    name = sha1.hexdigest().encode()                            # File's hash
    socket.send_multipart([b"create", name])                    # Create File In server
    ans = socket.recv()
    if b"false" == ans:
        with open(path, 'rb') as f :
            lsend = [b'assignServers', str(os.stat(path).st_size).encode(), name]
            while True:
                sha2 = hashlib.sha1()
                data = f.read(sizeBuf)
                if not data :
                    break
                sha2.update(data)
                lsend.append(sha2.hexdigest().encode())
    socket.send_multipart(lsend)
    fileServers = socket.recv_json()
    dirSockets = {}
    index = 0
    # load parts files to servers
    for x in fileServers['file']:
        if not x[1] in dirSockets:
            dirSockets[x[1]] = context.socket(zmq.REQ)
            dirSockets[x[1]].connect("tcp://" + x[1])
        dirSockets[x[1]].send_multipart([b"create", x[0].encode()])
        if dirSockets[x[1]].recv() == b"false" :
            with open(path, 'rb') as f :
                f.seek(index)
                data = f.read(sizeBuf)
                dirSockets[x[1]].send_multipart([b"submit", x[0].encode(), data])
        index += sizeBuf
            

# This for Download Files
def download(name):
    with open(name, "wb") as f:
        pos = 0
        while True :
            socket.send_multipart([b"download", Files[name].encode(), str(pos).encode()])
            ans = socket.recv()
            if b"Finish" == ans:
                print("Done")
                break
            f.write(ans)
            pos += sizeBuf

# This is for share 
def add(value):
    print("Escribe el nombre del archivo con extension")
    nombre = input()
    Files[nombre] = value
    with open("datos.json", "w") as f:
        json.dump(Files, f)

switcher = { "submit" : submit, "download" : download, "add" : add}

# create file JSON for save information
with open("datos.json", "a+") as f:
    f.seek(0)
    data = f.read(1)
    if not data:
        f.write("{}")

# load insformation
with open("datos.json") as myFiles:
    Files = json.load(myFiles)

# Run program
while True:
    valor = input().split()
    if len(valor) != 2:
        print("No Esta Bien Escrito")
    else:
        if valor[0] in switcher:
            switcher[valor[0]](valor[1])
        else :
            print("esta mal escrito")