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
A Data Event source, sends data events at regular intervals.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnevents import api_events as api_events
from gwnblock import mutex_prt 
import time


class data_source(gwnblock):
    '''Data events source, sends Data Events at regular intervals.
    
    Data events source block, produces DataComm Event objects based on an internal timer set by the user.
    @param interrupt: if set to True, timer does not generate events.
    @param interval: time betweeen successive events.
    @param retry: how many events to produce.
    @param payload: user data to be carried from source to destination.
    @param ev_dc: additional information for event to send.
    @param debug: print additional information; default False.
    '''
    def __init__(self, interrupt=False, interval=1.0, retry=5,
            src_addr='', dst_addr='', payload='', ev_dc={}, debug=False ): 

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='data_source', \
            number_in=0, number_out=1, number_timers=1)

        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.ev_dc = ev_dc
        self.payload = payload
        self.debug = debug
        self.nr_sent =0 

        self.nickname = 'DataData'
        self.ev_dc['interval'] = interval
        self.ev_dc['retry'] = retry
        self.set_timer(0, interrupt=interrupt, interval=interval, retry=retry, 
            ev_dc_1={'name':'retry'}, ev_dc_2={'name':'final'})
        self.start_timers()

        return


    def process_data(self, ev):
        '''Sends data events produced by the internal timer.

        @param ev: an Event object.
        '''
        if ev.ev_dc['name'] == 'final':    # nothing done
            return
        self.nr_sent += 1
        if self.nr_sent == 1:        # first event
            self.ev_dc['time_init'] = time.time()
        ev_data = api_events.mkevent(self.nickname, \
            ev_dc=self.ev_dc, payload=self.payload)
        ev_data.src_addr = self.src_addr
        ev_data.dst_addr = self.dst_addr
        ev_data.ev_dc['seq_nr'] = self.nr_sent
        ev_data.ev_dc['time_now'] = time.time()
        if self.debug:
            dbg_msg = '--- Data Source, id {0}, seq_nr: {1}, nr_sent: {2}'.\
                format(id(self), str(self.nr_sent), str(self.nr_sent))
            dbg_msg += '\n    time_init: {0}, time_now: {1}, time elapsed: {2}'.\
                format(ev_data.ev_dc['time_init'], ev_data.ev_dc['time_now'], \
                ev_data.ev_dc['time_now']-ev_data.ev_dc['time_init'])
            dbg_msg += '\n' + ev_data.__str__()
            mutex_prt(dbg_msg)
        self.write_out(ev_data, port_nr=0)

        return

