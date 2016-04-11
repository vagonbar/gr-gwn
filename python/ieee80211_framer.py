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
from gwnevents import api_events as api_events

import utils.framers.ieee80211.api_frmevs as api_frmevs
import utils.framers.ieee80211.api_frames as api_frames
import utils.framers.ieee80211.frames as frames


class ieee80211_framer(gwnblock):
    '''Generates IEEE 802.11 frame from event.

    Receives an Event object on input port, generates an IEEE 802.11 frame from it, ouputs frame as a PDU on output port. From the event received, an IEEE 802.11 compatible Event object is created. Objects of the IEEE 802.11 compatible class can be converted into an IEEE 802.11 Frame object, which allows for the construction of an IEEE 802.11 frame. Fields of frame are extracted from fields source and destination addresses, the ev_dc dictionary of field names and values, and the payload.
    @param nickname: nickname of an IEEE 802.11 compatible Event object.
    '''
    def __init__(self, nickname='DataData'):
        gwnblock.__init__(self, name='ieee80211_framer', 
            number_in=1, number_out=0, number_timers=0)

        self.nickname = nickname
        self.debug = False  # please set from outside for debug print

        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))
        return


    def process_data(self, ev):
        '''Receives an event, packs into a frame, outputs as a PDU.
        '''

        # create an IEEE 802.11 compatible Event
        new_ev = api_events.mkevent(self.nickname, \
            ev_dc=ev.ev_dc, payload=ev.payload)
        # load addresses in 6 byte format
        new_ev.ev_dc['src_addr'] = frames.addrmac2pkt(ev.src_addr)
        new_ev.ev_dc['dst_addr'] = frames.addrmac2pkt(ev.dst_addr) 

        # convert event into a Frame object, make packet to transmit
        frmobj = api_frmevs.evtofrm(new_ev, fr_dc_fldvals=new_ev.ev_dc)
        send_str = api_frames.pktfromobj(frmobj)

        # create an empty PMT (contains only spaces):
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

