#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  Copyright 2015
#    Instituto de Ingenieria Electrica, Facultad de Ingenieria,
#    Universidad de la Republica, Uruguay.
#  
#  This is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3, or (at your option)
#  any later version.
#  
#  This software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this software; see the file COPYING.  If not, write to
#  the Free Software Foundation, Inc., 51 Franklin Street,
#  Boston, MA 02110-1301, USA.
# 
# 

'''
Converts an Event object or string to PDU.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnblock import msg_to_pdu
import time                             # for tests

import pickle
import pmt


class ev_to_pdu(gwnblock):
    '''Converts an Event object or string to PDU.

    Receives an Event object on input port, produces a PDU (Protocol Data Unit) on its output port.
    @param in_type: type of input, may be "event", "payload", "message". If "event", the received event is serialized and stored as the content of the PDU. If "payload", the event's payload is stored as the content of the PDU. If "message", the received string is stored as the content of the PDU.
    '''
    def __init__(self, in_type='event'):
        gwnblock.__init__(self, name='ev_to_pdu', 
            number_in=1, number_out=0, number_timers=0)

        self.in_type = in_type
        self.debug = False

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))
        return


    def process_data(self, ev):
        '''Receives an Event, converts to PDU, writes on output.
        '''
        if self.in_type is 'event':
            send_str = pickle.dumps(ev)    # serializes Event object
        elif self.in_type is 'payload':
            send_str = ev.payload
        elif self.in_type is 'message':
            send_str = ev

        pdu = msg_to_pdu(send_str, debug=self.debug)
        self.message_port_pub( pmt.intern('pdu'), pdu)

        return




