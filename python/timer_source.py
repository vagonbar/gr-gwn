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
A timer Event source, sends events produced by an internal timer.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt 
import time


class timer_source(gwnblock):
    '''Timer events source, sends Events produced by an internal timer.
    
    Timer events source block, produces Timer Event objects based on an internal timer set by the user.
    @param blkname: block name.
    @param blkid: block identifier.
    @param interrupt: if set to True, timer does not generate events.
    @param interval: time betweeen successive events.
    @param retry: how many events to produce.
    @param nickname1: event nickname of event to produce on each interval.
    @param nickname2: event nickname of event to produce when retry has exhausted.
    '''
    def __init__(self,  blkname='timer_source', blkid='timer_source', 
            interrupt=False, interval=1.0, retry=5, 
            nickname1='TimerTOR1', nickname2='TimerTOR2'):
        gwnblock.__init__(self, blkname, blkid,
            number_in=0, number_out=1, number_timers=1)

        self.debug = False  # please set from outside for debug print
        self.counter = 1

        self.time_init = time.time()    
        self.set_timer(0, interrupt=interrupt, interval=interval, retry=retry, 
            nickname1=nickname1, nickname2=nickname2)
        self.start_timers()

        return


    def elapsed_time(self):
        '''Time elapsed since construction of block.
        '''
        return time.time() - self.time_init


    def process_data(self, ev):
        '''Sends timer events produced by the internal timer.'''
	# set event duration, required for deframing. TODO: see if correct
        ev.ev_dc['duration'] = 0
        if self.debug:
            ss = '--- send {0}, ev nickname {1}, time {2:4.1f}'.\
                format(self.blkname, ev.nickname, self.elapsed_time() )
            mutex_prt(ss)
        ev.frmpkt = 'Timer Event ' + str(self.counter)  # load frame packet
        self.counter += 1
        self.write_out(ev, port_nr=0)

        return


