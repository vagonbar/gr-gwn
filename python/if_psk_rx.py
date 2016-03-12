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

import numpy
from gnuradio import gr
import pmt

import gwnutils as packet_utils
from gwnblock import gwnblock
from gwnblock import mutex_prt          # for tests

#from gwnutils import conv_packed_binary_string_to_1_0_string
from gwnutils import conv_1_0_string_to_packed_binary_string
from gwnutils import unmake_packet


class if_psk_rx(gwnblock):
    '''PSK receiver interface.

    Receives a PDU, extracts content, rebuilds into string and outputs content as a string message (not a PDU).
    '''
    def __init__(self, blkname="gwn_if_psk_tx", blkid='0'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=0, number_out=0, number_timers=0)

        self.debug = False

        # register input port for PDUS and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('msg'))


    def handle_pdu_msg(self, msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        content = pmt.cdr(msg_pmt)
        if self.debug:
            if meta is not None:
                mutex_prt('[PMT metadata]: ' + meta)
            else:
                #mutex_prt('[PMT metadata]: None')
                pass
            mutex_prt('[PMT message]:')
            mutex_prt(pmt.to_python(content))
        # converts received u8 vector into string of chars 0 and 1
        msg_str = "".join([str(x) for x in pmt.u8vector_elements(content)])
        # converts 1s and 0s  string into a packed binary string
        lschars, pad = conv_1_0_string_to_packed_binary_string(msg_str)
        # unmakes packet, checks CRC
        ok, payload = unmake_packet(lschars)
        if self.debug:
            mutex_prt('if_psk_rx, CRC ok: ' + str(ok))
            mutex_prt(payload)
            mutex_prt('if_psk_rx payload type: ' + str(type(payload)))
        if ok:
            # sends payload as a list of one member
            send_pmt = pmt.pmt_to_python.python_to_pmt( [payload] )
            self.message_port_pub( pmt.intern('msg'), 
                pmt.cons(pmt.PMT_NIL, send_pmt) )
        else:
            mutex_prt('Invalid CRC, discarding packet')

        return

    def process_data(self, msg_pmt):
        pass

