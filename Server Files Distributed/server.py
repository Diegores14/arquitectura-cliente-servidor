import zmq
import os

# Datos iniciales
IP = "127.0.0.1"                                    # IP Del Servidor 1
Port = "6008"                                       # Puerto por el cual va a escuchar
sizePart = 1024*1024*10                             # 10MB
capServer = str(1024*1024*1024*10)                  # 10 GB de espacio dentro del servidor
context = zmq.Context()                             # creacion del Contexto
socketReq = context.socket(zmq.REQ)                 # REQ because I going to request
socket = context.socket(zmq.REP)                    # REP because is Reply
socket.bind("tcp://" + IP + ":" + Port)             # Escuchamos por la IP y puerto definidos anteriormente.

# Se Crea una estructura Trie para poder saber que hash a sido guardado en el servidor
class trie:
    def __init__(self):
        self.m = {}
    
    def insert(self, s, idx=0) :
        if idx < len(s) :
            if not s[idx] in self.m :
                self.m[s[idx]] = trie()
            self.m[s[idx]].insert(s, idx+1)
    
    def search(self, s, idx=0) :
        if idx == len(s) :
            return True
        if not s[idx] in self.m:
            return False
        return self.m[s[idx]].search(s, idx+1)

def create(name) :
    name = name[1].decode()
    if database.search(name):
        socket.send(b"true")
    else :
        database.insert(name)
        with open(name, "a") as f:
            pass
        socket.send(b"false")

def submit(data) :
    name = data[1].decode()
    with open(name, "ab") as f:
        f.write(data[2])
    socket.send(b"OK")

def download(data) :
    name = data[1].decode()
    with open(name, "rb") as f:
        f.seek( int( data[2].decode() ) )
        data = f.read(sizePart)
        if not data:
            socket.send(b"Finish")
        else :
            socket.send(data)
    print("download")

switcher = {"create": create, "submit" : submit, "download": download}
database = trie()
print("Server ON")

# Voy agregarme en el Proxy
socketReq.connect("tcp://127.0.0.1:3000")                  # Me conecto al proxy
aux = IP+":"+Port
socketReq.send_multipart([b"addServer", aux.encode(), capServer.encode()])
ans = socketReq.recv()

while True :
    operation = socket.recv_multipart()
    operation[0] = operation[0].decode()
    print(operation[0])
    switcher[operation[0]](operation)