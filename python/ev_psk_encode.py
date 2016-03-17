#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015
#   Instituto de Ingenieria Electrica, Facultad de Ingenieria,
#   Universidad de la Republica, Uruguay.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 
# 

'''Encodes an event or message into a PDU for modulation.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
import time                             # for tests

import pickle                           # to serialize event
import pmt                              # for PDUs
import gwnutils                         # for packing


class ev_psk_encode(gwnblock):
    '''Encodes an event or message into a PDU for modulation.

    Receives an Event object on input port, serializes, adds fields for PSK modulation, produces a PDU (Protocol Data Unit) on its output port.
    @param blkname: block name.
    @param blkid: block identifier.
    @param in_type: type of input, may be "event" or "message".
    @param debug: if True, shows details of process; default False.
    '''
    def __init__(self, blkname='ev_psk_encode', blkid='id_ev_pdk_encode', \
            in_type='event', debug=False):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=0, number_timers=0)

        self.in_type = in_type
        self.debug = debug

        # values for PSK encoding
        self._samp_per_sym = 5
        self._bits_per_sym = 2
        self._preamble = gwnutils.default_preamble
        self._access_code = gwnutils.default_access_code
        self._pad_for_usrp = True
        self._whitener_offset = False

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))

        return


    def process_data(self, ev, port, port_nr):
        '''Receives Event or message, encodes, outputs as PDU.
        '''

        # create string to send
        if self.in_type is 'event':
            send_str = pickle.dumps(ev)    # serializes Event object
        elif self.in_type is 'message':
            send_str = ev

        #send_str = 20*'a' + 20*'b' + 20*'c' + 20*'d' + 20*'e' + 20*'f'


        if self.debug:
            msg_dbg = '[Send str] : ' + repr(send_str) + '\n'
            msg_dbg += '[Send str len] : ' + str(len(send_str)) + '\n'
            mutex_prt(msg_dbg)

        # encode packet
        send_pkt = gwnutils.make_packet(send_str,
            self._samp_per_sym,
            self._bits_per_sym,
            self._preamble,
            self._access_code,
            self._pad_for_usrp,
            self._whitener_offset)
        #print "send pkt =", repr(send_pkt)
        #print "send len pkt =", len(send_pkt)
        #print
        #msg = gr.message_from_string(pkt)

        # create PDU, send
        # create an empty PMT (contains only spaces):
        send_pmt = pmt.make_u8vector(len(send_pkt), ord(' '))
        # Copy all characters to the u8vector:
        for i in range(len(send_pkt)):
            pmt.u8vector_set(send_pmt, i, ord(send_pkt[i]))

        # Send the message:
        self.message_port_pub( pmt.intern('pdu'), 
            pmt.cons(pmt.PMT_NIL, send_pmt) )

        return


    
