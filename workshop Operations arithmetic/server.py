import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:3000")

print("Server ON")

while True :
    op, num1, num2 = socket.recv_multipart()   # is a operation block and recive various message
    op = op.decode()
    print("Received request: ", op)
    answer = 0
    if op == "add":
        answer = int(num1) + int(num2)
    if op == "sub":
        answer = int(num1) - int(num2)
    if op == "mul":
        answer = int(num1) * int(num2)
    if op == "divide":
        if int(num2) == 0:
            answer = error
        else :
            answer = int(num1) / int(num2)
    socket.send(str(answer).encode("utf-8"))
