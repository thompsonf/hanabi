import socket

HOST_dflt = "199.87.127.48"
PORT_dflt = 8888

HOST = input("Connect to which IP? (leave empty for default): ")
PORT = input("Connect to which port? (leave empty for default): ")

if not HOST:
	HOST = HOST_dflt
if PORT:
	PORT = int(PORT)
else:
	PORT = PORT_dflt

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected to", HOST, "on port", PORT)

while True:
	msgstr = s.recv(1024).decode()
	if msgstr == "":
		print("Disconnected from server")
		exit()
	print(msgstr)
	msglist = msgstr.split()
	#process the msg
	if msglist[-1].lower() == "move:" or msglist[-1].lower() == "name:" or msglist[-1].lower() == "players?" or msglist[-1] == "5:":
		reply = input()
		s.send(reply.encode())