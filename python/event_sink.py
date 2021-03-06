#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  Copyright 2015
#    Instituto de Ingenieria Electrica, Facultad de Ingenieria,
#    Universidad de la Republica, Uruguay.
#  
#  This is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3, or (at your option)
#  any later version.
#  
#  This software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this software; see the file COPYING.  If not, write to
#  the Free Software Foundation, Inc., 51 Franklin Street,
#  Boston, MA 02110-1301, USA.
# 
# 

'''
An Event sink block; receives and prints event information.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # block specific, for this block
import time                             # block specific, for this block


class event_sink(gwnblock):
    '''Event sink, receives and shows Event objects.

    Receives an Event object, shows it.
    @param debug: shows whole details of event received; default False.
    '''

    def __init__(self, debug=False):
        gwnblock.__init__(self, name='event_sink', \
            number_in=1, number_out=0, number_timers=0)
        self.debug = debug
        self.nr_rec = 0      # number events received
        return


    def process_data(self, ev): #, port, port_nr):
        '''Receives events, prints.

        @param ev: event received.
        '''
        self.nr_rec += 1
        if self.nr_rec == 1:
            self.time_init = time.time()
        dbg_msg = '--- Event Sink id {0}, received ev: {1}; total rec: {2}'.\
            format(str(id(self)), ev.nickname, str(self.nr_rec))
        if self.debug:
            time_now = time.time()
            dbg_msg += '\n    time_init: {0}, time_now: {1}, time elapsed: {2}'.\
                format(self.time_init, time_now, time_now-self.time_init)
            dbg_msg += "\n" + ev.__str__()
        mutex_prt(dbg_msg)

        return


        
