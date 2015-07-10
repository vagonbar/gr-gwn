#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # 
# # Copyright 2015
# #   Instituto de Ingenieria Electrica, Facultad de Ingenieria,
# #   Universidad de la Republica, Uruguay.
# # 
# # This is free software; you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation; either version 3, or (at your option)
# # any later version.
# # 
# # This software is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# # 
# # You should have received a copy of the GNU General Public License
# # along with this software; see the file COPYING.  If not, write to
# # the Free Software Foundation, Inc., 51 Franklin Street,
# # Boston, MA 02110-1301, USA.
# #
# 

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
import time                             # for tests

import pickle
import pmt


class ev_to_pdu(gwnblock):
    '''Converts an Event object to PDU.

    Receives an Event object on input port, produces a PDU (Process Data Unit) on its output port.
    '''
    def __init__(self, blkname='ev_to_pdu', blkid='id_ev_to_pdu'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=0, number_timers=0)

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))

        return


    def process_data(self, ev):
        '''Receives an Event, converts to PDU, writes on output.
        '''
        send_str = pickle.dumps(ev)    # serializes Event object
        #send_str = '10101010'
        # Create an empty PMT (contains only spaces):
        send_pmt = pmt.make_u8vector(len(send_str), ord(' '))
        # Copy all characters to the u8vector:
        for i in range(len(send_str)):
            pmt.u8vector_set(send_pmt, i, ord(send_str[i]))
        # Send the message:
        print send_pmt
        self.message_port_pub(pmt.intern('pdu'), pmt.cons(pmt.PMT_NIL, send_pmt))

        return




