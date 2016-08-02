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

'''Reception with ACK.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events 
import random
import time
import sys

class go_back_n_ack(gwnblock):
    """Reception with ACK .

    Receives an Event on its Event input port, outputs the same item on corresponding output port sending an ACK signal on other output port.
    @param blkname: block name.
    @param blkid: block identifier.
    """
    def __init__(self, blkname='ack_rx', ack_nickname='CtrlACK', debug=False):
        
        gwnblock.__init__(self, name=blkname, number_in=1, number_out=2, number_timers=0)

        self.debug = False
        self.ack_nickname=ack_nickname
        self.aux_sink = 0
        self.aux_source = 0

        return


    def process_data(self, event):
        ''' Receives an event, writes it on output and sends ack
        '''

        # if event's been sent already, resend ACK backwards only.
        if ev.nickname == 'DataData' and ev.ev_dc['seq_nr']<=int(float(self.aux_sink)):
           if self.debug:
              dbg_msg = '   Data ' + str(ev.ev_dc['seq_nr']) + ' repeated, resending ACK to Source.'
              mutex_prt(dbg_msg)
           ack = api_events.mkevent(self.ack_nickname)
           ack.ev_dc['ack'] = ev.ev_dc['ack']
           self.write_out(ack, port_nr=1)

        # if event is new, pass it forward and send ACK backwards.
        if ev.nickname == 'DataData' and ev.ev_dc['seq_nr'] == int(float(self.aux_sink)+1):
           self.write_out(ev, port_nr=0)
	         # making an ack event
           ack = api_events.mkevent(self.ack_nickname)
           ack.ev_dc['ack'] = ev.ev_dc['ack']
           self.aux_sink = int(ev.ev_dc['seq_nr'])
           self.write_out(ack, port_nr=1) 
           if self.debug:
              dbg_msg = '   Sending ACK corresponding to event number ' + str(ack.ev_dc['ack'])
              mutex_prt(dbg_msg)

        return



