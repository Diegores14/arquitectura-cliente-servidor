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
sizeBuf = 1024*1024*10  # 10MB
Files = {}

# This is to submit file to server
def submit(path):
    # Creo el hash con el cual va a quedar en el servidor
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
            while True:
                data = f.read(sizeBuf)
                if not data :
                    break
                socket.send_multipart([b'submit', name, data])      # Send Data
                #print(data)
                ans = socket.recv()                                 # The server forever Reply "OK"
    print(sha1.hexdigest())

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