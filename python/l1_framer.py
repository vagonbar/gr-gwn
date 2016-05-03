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

'''Adds prefix and postfix fields for L1 framing.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import msg_to_pdu
from gwnblock import mutex_prt          # for tests

import pickle                           # to serialize event
import pmt                              # for PDUs
import gwnutils                         # for packing



class l1_framer(gwnblock):
    '''Adds prefix and postfix fields for L1 framing.

    Receives an Event object on input; adds access code, length, CRC32 for L1 framing; outputs a PDU (Protocol Data Unit). Framing may be done on the event previously serialized, on the payload, or on a received PMT message; parameter in_type selects the action. 
    @param in_type: type of input, may be "event", "payload", or "message".
    @param debug: if True, shows details of process; default False.
    '''

    def __init__(self, in_type='event', debug=False):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='l1_framer', \
            number_in=1, number_out=1, number_timers=0)

        self.in_type = in_type
        self.debug = debug

        # values for encoding
        self._samp_per_sym = 5
        self._bits_per_sym = 2
        self._preamble = gwnutils.default_preamble
        self._access_code = gwnutils.default_access_code
        self._pad_for_usrp = True
        self._whitener_offset = False

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))

        return


    def process_data(self, ev):
        '''Adds framing fields, creates PDU, writes on output.
        '''

        # create string to send
        if self.in_type is 'event':
            send_str = pickle.dumps(ev)    # serializes Event object
        elif self.in_type is 'payload':
            send_str = ev.payload          # payload goes as such
        elif self.in_type is 'message':
            send_str = ev                  # ev is a PMT message

        if self.debug:
            msg_dbg = '--- L1 framer, id {0}\n'.format(id(self),)
            msg_dbg += '[Send str] : ' + repr(send_str) + '\n'
            msg_dbg += '[Send str len] : ' + str(len(send_str)) + '\n'
            mutex_prt(msg_dbg)

        # frame packet
        send_pkt = gwnutils.make_packet(send_str,
            self._samp_per_sym,
            self._bits_per_sym,
            self._preamble,
            self._access_code,
            self._pad_for_usrp,
            self._whitener_offset)

        pdu = msg_to_pdu(send_pkt, debug=self.debug)
        self.message_port_pub( pmt.intern('pdu'), pdu)

        return

