import zmq

context = zmq.Context()
socket = context.socket(zmq.REP) # REP because is Reply
socket.bind("tcp://*:3000")

print("Server ON")