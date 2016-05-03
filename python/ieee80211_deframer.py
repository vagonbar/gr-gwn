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
An IEEE 802.11 deframer, converts frame to Event objrct.
'''

import numpy
from gnuradio import gr
import pmt

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import pdu_to_msg
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events

import utils.framers.ieee80211.api_frmevs as api_frmevs
import utils.framers.ieee80211.api_frames as api_frames
import utils.framers.ieee80211.frames as frames


class ieee80211_deframer(gwnblock):
    '''Generates an Event object from a PDU with a frame.

   Receives a PDU, extracts an IEEE 802.11 frame, generates an Event object from it, outputs Event object on output port.
    '''

    def __init__(self):
        gwnblock.__init__(self, name='ieee802.11_deframer', \
            number_in=0, number_out=1, number_timers=0)

        self.debug = False  # please set from outside for debug print

        # register input port for PDUs and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu_msg)
        return


    def handle_pdu_msg(self, msg_pmt):
        if self.debug:
            msg_dbg = '--- IEEE 802.11 deframer, id {0}\n'.format(id(self), )
            mutex_prt(msg_dbg)
        meta, msg_str = pdu_to_msg(msg_pmt, debug=self.debug)

        # create Frame object from frame, pass on to process_data
        try:
            frm_obj = api_frames.objfrompkt(msg_str)
            ev = api_frmevs.frmtoev(frm_obj)
            ev.ev_dc['src_addr'] = frames.addrpkt2mac(ev.ev_dc['src_addr'])
            ev.ev_dc['dst_addr'] = frames.addrpkt2mac(ev.ev_dc['dst_addr'])
        except:
            msg_dbg = "Error trying to create Event from frame\n"
            if meta is not None:
                msg_dbg += "[METADATA]: " + meta + "\n"
            msg_dbg += "[CONTENTS]: " + msg_str + "\n"
            mutex_prt(msg_dbg)
            return

        self.process_data(ev)
        return


    def process_data(self, ev):
        '''Send event through output port.
        '''
        self.write_out(ev)
        return

