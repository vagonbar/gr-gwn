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
A Data Event source, sends data events produced by an internal timer.
'''
import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt 
import time


class data_source(gwnblock):
    '''Data events source, sends Data Events at regular intervals.
    
    Data events source block, produces DataComm Event objects at regular intervals. Number of events produced and interval are set by the user.
    @param blkname: block name.
    @param blkid: block identifier.
    @param interrupt: if set to True, timer does not generate events.
    @param interval: time betweeen successive events.
    @param retry: how many events to produce.
    @param nickname: event nickname of event to produce on each interval.
    @param ev_dc: dictionary of other data info.
    @param payload: data to be carried from source to destination.
    '''
    def __init__(self,  blkname='data_source', blkid='data_source_id', 
            interrupt=False, interval=1.0, retry=5,
            nickname='DataData', ev_dc={}, payload=''):

        # invocation of ancestor constructor
        gwnblock.__init__(self, blkname, blkid,
            number_in=0, number_out=1, number_timers=1)

        self.blkname = blkname
        self.blkidid = blkid
        self.interrupt = interrupt
        self.interval = interval
        self.retry = retry
        self.nickname = nickname
        self.ev_dc = ev_dc
        self.payload = payload

        self.debug = False  # please set from outside for debug print
        self.counter = 1

        self.time_init = time.time()    
        self.set_timer(0, interrupt=interrupt, interval=interval, retry=retry, 
            nickname1=nickname, nickname2='')
        self.start_timers()

        return


    def process_data(self, ev, port, port_nr):
        '''Sends data events produced by the internal timer.

        @param ev: an Event object.
        '''
        #ev.payload = 'Data Event ' + str(self.counter)  # event payload
        if self.debug:
            ss = '--- {0}, send ev: {1}, counter: {2}'.\
                format(self.blkname, ev.nickname, str(self.counter))
            mutex_prt(ss)
            #ev.payload = 'Data Event ' + str(self.counter)  # load payoad
        ev.ev_dc = self.ev_dc
        ev.ev_dc['seq_nr'] = self.counter
        self.counter += 1
        self.write_out(ev, port_nr=0)

        return
