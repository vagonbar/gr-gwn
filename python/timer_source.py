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
A timer Event source, sends Timer events at regular intervals.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt 
import time


class timer_source(gwnblock):
    '''Timer Event source, sends Timer events at regular intervals.
    
    Timer events source block, produces Timer Event objects based on an internal timer set by the user.
    @param interrupt: if set to True, timer does not generate events.
    @param interval: time betweeen successive events.
    @param retry: how many events to produce.
    @param ev_dc_1: additional information for event to send at regular intervals for retry times.
    @param ev_dc_2: additional information for event to send when retries have exhausted.
    @param debug: print additional information; default False.
    '''
    def __init__(self, interrupt=False, interval=1.0, retry=5, 
            debug=False, ev_dc_1={}, ev_dc_2={}):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='timer_source', \
            number_in=0, number_out=1, number_timers=1)

        self.debug = debug
        self.counter = 1

        self.time_init = time.time()    
        self.set_timer(0, interrupt=interrupt, interval=interval, retry=retry, 
            ev_dc_1=ev_dc_1, ev_dc_2=ev_dc_2)
        self.start_timers()

        return


    def elapsed_time(self):
        '''Time elapsed since construction of block.

        @return: time elapsed.
        '''
        return time.time() - self.time_init


    def process_data(self, ev):
        '''Sends timer events produced by the internal timer.

        @param ev: an Event object.
        '''
        ev.ev_dc['seq_nr'] = self.counter
        if self.debug:
            dbg_msg = '--- Timer Source, id {0}, time {1:4.1f}'.\
                format(str(id(self)), self.elapsed_time() )
            dbg_msg += '\n' + ev.__str__()
            mutex_prt(dbg_msg)
        self.write_out(ev, port_nr=0)
        self.counter += 1

        return


