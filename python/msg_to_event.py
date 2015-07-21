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
#import time                             # for tests
from gwnevents import api_events as api_events    # to create events
#import pickle
import pmt


class msg_to_event(gwnblock):
    '''Receives a message, creates a Data Event from it.

    Warning: received item is a "messsage", but not a "PDU": received message contents is a string, while content in PDUs must be a vector.
    @param blkname: block name.
    @param blkid: block identifier.
    '''
    def __init__(self, blkname='msg_to_event', blkid='msg_to_event'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid,
            number_in=0, number_out=1, number_timers=0)

        self.debug = True

        # register input port for messages and set function handler
        self.message_port_register_in(pmt.intern('msg'))
        self.set_msg_handler(pmt.intern('msg'), self.handle_msg)
        return


    def handle_msg(self, msg_pmt):
        '''Receive message, extract contents, create event.
        '''
        # code taken from chat_blocks in GNURadio tutorial 5
        # Collect metadata, convert to Python format:
        meta = pmt.to_python(pmt.car(msg_pmt))
        # Collect message, convert to Python format:
        msg_pmt = pmt.cdr(msg_pmt)
        msg_ls = pmt.to_python(msg_pmt)
        msg = msg_ls[-1]
        msg_str = msg
        if self.debug:
            if meta is not None:
                mutex_prt ("[METADATA]: " + meta)
            mutex_prt ("[CONTENTS]: " + msg_str )
        # creste DataData event with msg_str as frmpkt, pass on to process_data
        evdata = api_events.mkevent('DataData')   # create event
        evdata.frmpkt = msg_str
        self.process_data(evdata)
        return


    def process_data(self, ev):
        '''Send event through output port.
        '''
        self.write_out(ev)
        return


