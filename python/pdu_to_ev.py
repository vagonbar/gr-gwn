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

'''Converts a PDU into an Event object.
''' 

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnblock import pdu_to_msg
import time                             # for tests

import pickle
import pmt
from gwnevents import api_events as api_events



class pdu_to_ev(gwnblock):
    '''Converts a PDU into an Event object

    Receives a PDU message, deserializes content into an Event object, sends Event object on its output port.
    @param in_type: type of input, may be "event", "payload" or "message". If "event", PDU content is deserialized into an Event object. If "payload" or "message", a Data Event is built and PDU content is loaded into the payload attribute of this new event.
    '''
    def __init__(self, in_type='event'):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='pdu_to_ev',
            number_in=0, number_out=1, number_timers=0)

        self.out_nickname = 'DataData'   # event to load payload into
        self.in_type = in_type
        self.debug = False  # please set from outside for debug print
                
        # register input port for PDUS and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)
        return


    def handle_pdu_msg(self, pdu):
        meta, msg_str = pdu_to_msg(pdu, debug=self.debug)
        if self.in_type == 'event':
            # deserialize into Event object, pass on to process_data
            try:
                ev = pickle.loads(msg_str)
            except:
                print "pdu_to ev: Error on unpickle to event"
                return
        elif self.in_type == 'payload' or self.in_type == 'message':
            ev = api_events.mkevent(self.out_nickname, payload=msg_str)
        else:
            mutex_prt('    pdu_to_ev: Invalid in_data type: ' + self.n_type)
        self.process_data(ev)
        return


    def process_data(self, ev):
        '''Send event through output port.
        '''
        self.write_out(ev)
        return
        

