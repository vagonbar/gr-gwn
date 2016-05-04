# sock_receiver_test : test for sock_receiver.grc

import socket
import time

nr_to_send = 100

HOST = '127.0.0.1'
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(0,nr_to_send):
    s.sendto('SEND message ' + str(i), (HOST, PORT))
    time.sleep(1)
s.close()


