#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# socket_client.py: a socket client to use in tests
# use this app to test socket_server.grc

import sys
import socket

from argparse import ArgumentParser


# create options for command line
parser = ArgumentParser(description='Socket server, sends messages.')
parser.add_argument('-H', '--host', dest='host', type=str, 
    default='127.0.0.1', help='name or IP of host')
parser.add_argument('-p', '--port', dest='port', type=int, 
    default=50007, help='port number')
parser.add_argument('-P', '--protocol', dest='protocol', type=str,
    default='udp', help="protocol, may be udp or tcp")
parser.add_argument('-n', '--number', dest='nr_to_receive', type=int,
    default=-1, 
    help="number of messages to receive; if -1 receive until Ctrl-C")

args = parser.parse_args()
print 'socket_server args:', args

number = args.nr_to_receive

if args.protocol == 'udp':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((args.host, args.port))
elif args.protocol == 'tcp':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args.host, args.port))
    s.listen(1)
    conn, addr = s.accept()
    print 'SERVER, connected by', addr
else:
    print "Protocol not supported:", args.protocol
    sys.exit()

while number > 0 or args.nr_to_receive == -1:
    try:
        if args.protocol == 'udp':
            data, addr = s.recvfrom(1024)
        elif args.protocol == 'tcp':
            data = conn.recv(1024)
        if data:
            print "SERVER, received message:", data
    except KeyboardInterrupt:
        s.close()
        sys.exit()
    number -= 1

