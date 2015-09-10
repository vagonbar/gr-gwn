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

'''
An IEEE 802.11 deframer, converts frame to Event.
'''

import numpy
from gnuradio import gr
import pmt

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests

import sys
import utils.framers.ieee80211.api_frmevs as api_frmevs
import utils.framers.ieee80211.api_frames as api_frames


class ieee80211_deframer(gwnblock):
    '''Generates an Event object from a PDU.

   Receives a PDU, generates an Event object from it, outputs Event object on output port.
    @param blkname: block name.
    @param blkid: block identifier. 
    '''

    def __init__(self, blkname='ieee80211_deframer', blkid='id_ieee80211_deframer'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=0, number_out=1, number_timers=0)

        self.debug = False  # please set from outside for debug print

        # register input port for PDUs and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)
        return


    def handle_pdu_msg(self, msg_pmt):
        # code taken from chat_blocks in GNURadio tutorial 5
        # Collect metadata, convert to Python format:
        meta = pmt.to_python(pmt.car(msg_pmt))
        # Collect message, convert to Python format:
        msg = pmt.cdr(msg_pmt)
        # Make sure it's a u8vector
        if not pmt.is_u8vector(msg):
            mutex_prt("[ERROR] Received invalid message type.\n")
            return
        # Convert to string:
        msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
        if self.debug:
            if meta is not None:
                mutex_prt ("[METADATA]: " + meta)
            mutex_prt ("[CONTENTS]: " + msg_str )

        # create Event object from frame, pass on to process_data
        try:
            frm_obj = api_frames.objfrompkt(msg_str)
            ev = api_frmevs.frmtoev(frm_obj)
        except:
            mutex_prt("Error trying to create Event from frame\n")
            return

        self.process_data(ev)
        return


    def process_data(self, ev):
        '''Send event through output port.
        '''
        self.write_out(ev)
        return

