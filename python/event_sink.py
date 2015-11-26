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

'''An Event sink block; receives and prints event information.
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
    @param blkname: block name.
    @param blkid: block identifier.
    '''

    def __init__(self, blkname='EventSink', blkid='event_sink_id'):
        gwnblock.__init__(self, blkname=blkname, blkid=blkid,
            number_in=1, number_out=0, number_timers=0)

        self.debug = False  # please set from outside for debug print

        return


    def process_data(self, ev, port, port_nr):
        '''Receives events, prints.
        '''
        dbg_msg = '--- {0}, received ev: {1}'.\
            format(self.blkname, ev.nickname)
        if ev.ev_dc.has_key('seq_nr'):
            dbg_msg += ', seq nr: {0}'.format(ev.ev_dc['seq_nr'])
        if ev.payload:
            dbg_msg += '\n    payload: {0}'.format(ev.payload)
        mutex_prt(dbg_msg)
        if self.debug:
            mutex_prt(ev)

        return

