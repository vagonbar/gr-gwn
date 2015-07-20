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
import pmt

import gwnutils as packet_utils
from gwnblock import gwnblock
from gwnblock import mutex_prt          # for tests

#from gwnutils import conv_packed_binary_string_to_1_0_string
from gwnutils import conv_1_0_string_to_packed_binary_string
from gwnutils import unmake_packet


class if_psk_rx(gwnblock):
    '''PSK receiver interface, for testing.
    '''
    def __init__(self, blkname="gwn_if_psk_tx", blkid='0'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=0, number_out=0, number_timers=0)

        self.debug = True

        # register input port for PDUS and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))


    def handle_pdu_msg(self, msg_pmt):
        meta = pmt.to_python(pmt.car(msg_pmt))
        content = pmt.cdr(msg_pmt)
        if self.debug:
            if meta is not None:
                mutex_prt('[PMT metadata]: ' + meta)
            else:
                #mutex_prt('[PMT metadata]: None')
                pass
        #mutex_prt('[PMT message]; '  + content)
        #print pmt.to_python(content)
        msg_str = "".join([str(x) for x in pmt.u8vector_elements(content)])
        #lschars = [(x) for x in pmt.u8vector_elements(content)]
        lschars, pad = conv_1_0_string_to_packed_binary_string(msg_str)
        #print lschars
        #print "El Tipo:", type(msg_str)
        #print msg_str
        #print lschars
        ok, payload = unmake_packet(lschars)
        print ok
        print payload        
        #print [x for x in pmt.u8vector_elements(content)]    

        #to_string = content.to_string()
        #mutex_prt('[to_string]; '  + to_string)
        #msg_send = pmt.cons(pmt.PMT_NIL, content)
        #self.write_out(msg_send)
        if ok:
            self.message_port_pub( pmt.intern('pdu'), 
                pmt.cons(pmt.PMT_NIL, payload) )
        else:
            mutex_prt('Invalid CRC, discarding packet')

        return

    def process_data(self, msg_pmt):
        pass

