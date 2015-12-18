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

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests

import pickle                           # to serialize event
import pmt                              # for PDUs
import gwnutils                         # for PSK packing



class ev_psk_decode(gwnblock):
    '''Demodulates PDU from PSK into an event or message.

    Receives a PDU, decodes from PSK, rebuilds event and writes on output port.
    @param blkname: block name.
    @param blkid: block identifier.
    @param out_type: type of output, may be "event" or "message"
    @param debug: if True, shows details of process; default False.
    '''
    def __init__(self, blkname='ev_psk_encode', blkid='id_ev_pdk_encode', \
            debug=False):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=0, number_out=1, number_timers=0)

        self.out_type = 'event' #out_type
        self.debug = debug
        self.debug = True

        # register input port for PDUS and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)


    def handle_pdu_msg(self, msg_pmt):
        '''Extracts string from PDU.
        '''
        meta = pmt.to_python(pmt.car(msg_pmt))
        content = pmt.cdr(msg_pmt)

        # converts received u8 vector into string of chars 0 and 1
        msg_str = "".join([str(x) for x in pmt.u8vector_elements(content)])
        # converts 1s and 0s  string into a packed binary string
        lschars, pad = gwnutils.conv_1_0_string_to_packed_binary_string(msg_str)
        # unmakes packet, checks CRC
        ok, rec_str = gwnutils.unmake_packet(lschars)

        #print "rec pkt =", string_to_hex_list(rec_str)
        #print "rec len pkt =", len(string_to_hex_list(rec_str))
        #print "rec pkt =", repr(rec_str)
        #print "rec len pkt =", len(rec_str)

        if self.debug:
            msg_dbg = '[CRC ok] : ' + str(ok) + '\n'
            msg_dbg += '[Rec str] : ' + repr(rec_str) + '\n'
            msg_dbg += '[Rec str len] : ' + str(len(rec_str)) + '\n'
            mutex_prt(msg_dbg)

        if ok:
            if self.out_type is 'event':
                try:
                    ev = pickle.loads(rec_str)
                    ev = rec_str
                except:
                    print '    Error on unpickle to event'
                    return
            else:
                ev = rec_str
            self.process_data(ev)
        else:
            mutex_prt('   Invalid CRC, discarding packet')

        return


    def process_data(self, ev):
        '''Send event through output port.
        '''
        self.write_out(ev)
        return

