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
An IEEE 802.11 framer, converts Event object to frame.
'''

import numpy
from gnuradio import gr
import pmt

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests

import sys
import utils.framers.ieee80211.api_frmevs as api_frmevs


class ieee80211_framer(gwnblock):
    '''Generates IEEE 802.11 frame from event.

    Receives an Event object on input port, generates an IEEE 802.11 frame from it, ouputs frame as a PDU on output port.
    @param blkname: block name.
    @param blkid: block identifier.
    '''
    def __init__(self, blkname='ieee80211_framer', blkid='id_ieee80211_framer'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=0, number_timers=0)

        self.debug = False  # please set from outside for debug print

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))
        return

    def process_data(self, ev):
        '''Receives an event, packs into a frame, loads in event attribute.
        '''
        #ev.frmpkt = '***ieee80211framer:_the_packed_frame***'
        frmobj = api_frmevs.evtofrm(ev)
        send_str = frmobj.mkpkt()
        # Create an empty PMT (contains only spaces):
        send_pmt = pmt.make_u8vector(len(send_str), ord(' '))
        # Copy all characters to the u8vector:
        for i in range(len(send_str)):
            pmt.u8vector_set(send_pmt, i, ord(send_str[i]))
        if self.debug:
            mutex_prt('[Event]\n' + ev.__str__() )
            mutex_prt('[frame]\n' + send_str)
            mutex_prt('[PMT message]')
            mutex_prt(send_pmt)
        # Send the message:
        self.message_port_pub( pmt.intern('pdu'), 
            pmt.cons(pmt.PMT_NIL, send_pmt) )

        return

