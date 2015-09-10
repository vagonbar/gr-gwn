#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
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

'''
A message sender, sends messages produced by timers.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # block specific, for this block
import time                             # block specific, for this block



class msg_sender_m(gwnblock):
    '''A test block, sends messages produced by 2 timers, one set by user.
    
    A test block which produces events based on two timers. Timer on port 0 can be set by the user, the other is internal and produces a fixed number of predefined timer events.
    @param blkname: block name.
    @param blkid: block identifier.
    @param interrupt: if True, timer does not generate events.
    @param interval: time betweeen events.
    @param retry: how many events to produce.
    @param nickname1: event nickname of event to produce on each interval.
    @param nickname2: event nickname of event to produce when retry has exhausted.
    '''

    def __init__(self, blkname, blkid, 
            interrupt=False, interval=2.0, retry=3, 
            nickname1='TimerTOR1', nickname2='TimerTOR2'):
        gwnblock.__init__(self, blkname, blkid, 
            number_in=0, number_out=2, number_timers=2)

        self.debug = False  # please set from outside for debug print
        
        self.time_init = time.time()    
        self.set_timer(0, interrupt=interrupt, interval=interval, retry=retry, 
            nickname1=nickname1, nickname2=nickname2)
        self.set_timer(1, interrupt=False, interval=1.0, retry=1, 
            nickname1='TimerTOC', nickname2='TimerTOH')
        self.start_timers()

        return


    def elapsed_time(self):
        '''Time elapsed since construction of block.
        '''
        return time.time() - self.time_init


    def process_data(self, ev):
        '''Sends timer events produced by the internal timers.'''
        if self.debug:
            ss = '--- send {0}, ev nickname {1}, time {2:4.1f}'.\
                format(self.blkname, ev.nickname, self.elapsed_time() )
            mutex_prt(ss)
        #self.write_out(ev)    # write on all output ports

        ev.frmpkt = 'Timer_Event_framepacket'
        # write on different output ports according to timer events
        if 'TOH' in ev.nickname or 'TOC' in ev.nickname:    # internal timer
            #print '--- ev.nickname:', ev.nickname, 'en puerto', 1
            self.write_out(ev, port_nr=1)
        else:                                               # user timer
            #print '--- ev.nickname:', ev.nickname, 'en puerto', 0
            self.write_out(ev, port_nr=0)
        return



