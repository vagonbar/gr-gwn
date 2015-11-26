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

'''An ARQ Stop and wait ACK sender.
'''
import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events   # to create ACK event
import pmt                              # for messages and PDUs


class stop_wait_ack(gwnblock):
    '''An ARQ Stop and wait ACK sender.

    Receives an event, writes this event on output port 1, generates an ACK event, writes it out on output port 2.
    @param blkname: block name.
    @param blkid: block identifier.
    '''

    def __init__(self, blkname='stop_wait_ack', blkid='id_stop_wait_ack',
            ack_nickname='CtrlACK', debug=False):

        # invocation of ancestor constructor
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=2, number_timers=0)

        self.ack_nickname = ack_nickname
        self.ack = 'ack0'
        self.debug = debug

        return


    def process_data(self, ev, port, port_nr):
        '''Writes event and ACK on output ports.

        @param ev: an Event object.
        '''
        if self.debug:
            dbg_msg = '--- {0} received ev: {1}, seq nr: {2}'. \
                format(self.blkname, ev.nickname, ev.ev_dc['seq_nr'])
            dbg_msg += '\n    event ack:{0}, waited ack: {1}'. \
                format(ev.ev_dc['ack'], self.ack)
            if ev.payload:
                dbg_msg += '\n    payload: ' + ev.payload
            mutex_prt(dbg_msg)
        if True:        # test for some condition, i.e. CRC OK 
            if self.ack == ev.ev_dc['ack']:    # new packet
                ev_ack = api_events.mkevent(self.ack_nickname)
                #ev_ack.payload = ev.payload + self.ack
                ev_ack.ev_dc['ack'] = ev.ev_dc['ack']
                #self.write_out(ev)		# write event on all outputs
                self.write_out(ev, port_nr=0)		# write event on output
                self.write_out(ev_ack, port_nr=1)   # write ACK event on output
                # revert ACK sequence number
                if self.ack == 'ack1':
                    self.ack = 'ack0'
                else:
                    self.ack = 'ack1'
            else:                        # repeated event
                if self.debug:
                    msg_dbg = '    REPEATED, event ack: {0}, waited ack: {1}'.\
                        format(ev.ev_dc['ack'], self.ack)
                mutex_prt(msg_dbg)
        else:
            pass
        return

