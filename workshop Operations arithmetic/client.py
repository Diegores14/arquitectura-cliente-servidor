import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ) # REQ because I going to request
socket.connect("tcp://127.0.0.1:3000")
print("Client ON")
msj = [ b"sub", b"15", b"4"] 
#msj = "sum,5,5"
#msj = {"operacion":"suma", "a1":10, "a2":20}
socket.send_multipart(msj)

res = socket.recv()
print("Your answer is ", res.decode('utf-8'))