#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# socket_server.py: a socket server to use in tests
# use this app to test socket_client.grc

import socket
import time
import sys

from argparse import ArgumentParser


# create options for command line
parser = ArgumentParser()
parser.add_argument('-H', '--host', dest='host', type=str, 
    default='127.0.0.1', help='name or IP of host')
parser.add_argument('-p', '--port', dest='port', type=int, 
    default=50007, help='port number')
parser.add_argument('-P', '--protocol', dest='protocol', type=str,
    default='udp', help='protocol, may be udp or tcp')
parser.add_argument('-n', '--number', dest='nr_to_send', type=int,
    default=10, help='number of messages to send')

args = parser.parse_args()
print 'socket_clent args:', args

if args.protocol == 'udp':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
elif args.protocol == 'tcp':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port))

for i in range(0, args.nr_to_send):
    s.sendto('CLIENT, sending message ' + str(i), (args.host, args.port) )
    time.sleep(1)
s.close()


