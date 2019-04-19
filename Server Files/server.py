import zmq
import os

sizePart = 1024*1024*1024*10  # 10MB
context = zmq.Context()
socket = context.socket(zmq.REP) # REP because is Reply
socket.bind("tcp://*:3000")


def create(name) :
    name = name[1].decode()
    with open(name, "a") as f:
        pass
    os.remove(name)
    with open(name, "a") as f:
        pass
    socket.send(b"OK")

def submit(data) :
    name = data[1].decode()
    with open(name, "ab") as f:
        f.write(data[2])
    socket.send(b"OK")

def download(name) :
    name = name[1].decode()
    with open(name, "rb") as f:
        while True:
            data = f.read(sizePart)
            if not data:
                socket.send(b"Finish")
                break
            socket.send(data)
            socket.recv()

switcher = {"create": create, "submit" : submit, "download": download}

print("Server ON")

while True :
    operation = socket.recv_multipart()
    operation[0] = operation[0].decode()
    print(operation[0])
    switcher[operation[0]](operation)