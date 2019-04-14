import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ) # REQ because I going to request
socket.connect("tcp://127.0.0.1:3000")
print("Client ON")