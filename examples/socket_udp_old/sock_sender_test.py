# sock_sender_test.py : test for sock_sender.grc

import socket
HOST = '127.0.0.1'
PORT = 50008
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
while True:
	data, addr = s.recvfrom(1024)
	print "SERVER, received message:", data
