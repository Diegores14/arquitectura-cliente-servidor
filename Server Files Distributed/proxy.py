import zmq
import os
import random
import json


# El segmentTree es una Estructura De Datos la cual me permite hacer Queries en Rangos en O(log(n)).
# La creación del SegmentTree tiene una complejidad de O(4*n).
# En este caso el segmentTree lo vamos a utilizar para encontrar el k-th servidor que voy a distribuir,
# sin incluir los que ya he distribuido. pues para que quede un poco más claro, el segment Tree es el 
# que me va a generar la probalidad uniforme para escoger entre k servidores con un random.
class segmentTree:
    def __init__(self, tam):
        self.tam = tam
        self.st = [0] * (4 * tam)
        self.build(1, 0, self.tam)

    def build(self, p, L, R):
        if L == R :
            self.st[p] = 1
        else :
            mid = (L + R)>>1
            left = p<<1
            self.build(left, L, mid)
            self.build(left+1, mid+1, R)
            self.st[p] = self.st[left] + self.st[left+1]

    def update(self, p, L, R, i):
        if L <= i and i <= R:
            if L == R :
                self.st[p] = 0
            else :
                mid = (L + R)>>1
                left = p<<1
                self.update(left, L, mid, i)
                self.update(left+1, mid+1, R, i)
                self.st[p] = self.st[left] + self.st[left+1]

    def query(self, p, L, R, i):
        if L == R :
            return L
        mid = (L + R)>>1
        left = p<<1
        if self.st[left] < i:
            return self.query(left+1, mid+1, R, i - self.st[left])
        else :
            return self.query(left, L, mid, i)
        

# trie es para saber de forma rapida si el hash de todo el archivo ya fue distribuido.
class trie:
    def __init__(self):
        self.m = {}
        self.isfinish = False
    
    def insert(self, s, idx=0) :
        if idx < len(s) :
            if not s[idx] in self.m :
                self.m[s[idx]] = trie()
            self.m[s[idx]].insert(s, idx+1)
        else :
            self.isfinish = True
    
    def search(self, s, idx=0) :
        if idx == len(s) :
            return self.isfinish
        if not s[idx] in self.m:
            return False
        return self.m[s[idx]].search(s, idx+1)

class Proxy:
    def __init__(self):
        self.IP = "127.0.0.1"                            # IP Del Proxy
        self.Port = "3000"                               # Puerto por el cual va a escuchar
        self.tam = 1005                                  # El tam es para definir la cantidad de servidores limite.
        self.cant = 0                                    # Es la cantidad de serividores disponibles.
        self.cantRand = 0                                # CantRand está variable me va a servir para hacer la distribucion con probabilidad Uniforme.
        self.cantLimit = 1024*1024*10                    # 10MB es la cantidad limite de cada parte del archivo.
        self.context = zmq.Context()                     # La creación del contexto.
        self.socket = self.context.socket(zmq.REP)            # REP because is Reply.
        self.socket.bind("tcp://" + self.IP + ":" + self.Port)     # Escuchamos por la IP y puerto definidos anteriormente.
        self.servers = [("", 0)] * self.tam                    # Lista de los servidores
        self.database = trie()
        self.switcher = {"create": self.create, "assignServers" : self.assignServers, "addServer": self.addServer, "Download": self.download}
        self.st = segmentTree(self.tam)
        print("Proxy ON")
        while True :
            operation = self.socket.recv_multipart()
            operation[0] = operation[0].decode()
            print(operation[0])
            self.switcher[operation[0]](operation)

    # metodos Del Servidor donde se Añaden Servidores, se crea nuevos archivos, distribuir servidores

    def addServer(self, data):
        print("add Server")
        self.servers[self.cant] = (data[1].decode(), int(data[2].decode()))
        print(self.servers[self.cant])
        self.cant += 1
        self.cantRand += 1
        self.socket.send(b"OK")
        print(self.cant)

    def create(self, data):
        name = data[1].decode()
        if self.database.search(name):
            self.socket.send(b"true")
        else :
            self.database.insert(name)
            with open(name, "a") as f:
                pass
            self.socket.send(b"false")

    def assignServers(self, data):
        with open(data[2].decode(), "w") as f :
            fileHashServers = {}
            fileHashServers["size"] = int(data[1].decode())
            fileHashServers["file"] = []
            i = 3
            while i < len(data) :
                k = random.randrange(self.cantRand) + 1
                self.cantRand -= 1
                j = self.st.query(1, 0, self.tam, k)
                print("valor j-th ", j)
                self.st.update(1, 0, self.tam, j)
                fileHashServers["file"].append((data[i].decode(), self.servers[j][0]))
                if self.cantRand <= 0:
                    self.cantRand = self.cant
                    self.st.build(1, 0, self.tam)
                i += 1
            json.dump(fileHashServers, f)
        self.socket.send_json(fileHashServers)

    def download(self, data) :
        fileHashServers = {}
        with open(data[1].decode()) as f:
            fileHashServers = json.load(f)
        self.socket.send_json(fileHashServers)


ObjProxy = Proxy()


# Un while para que corra el programa de forma indefinida

