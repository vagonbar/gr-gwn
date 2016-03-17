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

'''Rebuilds event or payload from a frame packet.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
import time                             # for tests

import pickle                           # to serialize event
import pmt                              # for PDUs
import gwnutils                         # for packing
from gwnevents import gwnevent          # to check class of event



class l2_deframer(gwnblock):
    '''Rebuilds event or payload from a frame packet.

    Extracts string from payload, deserializes into a new event to ouput, or loads as payload in current event.
    @param pack: type of packing; if 'event', deserializes event from frmpkt field of input event; if 'payload' puts frmpkt as payload in current event. An unrecognized type of packing does nothing, no event output.
    '''
    def __init__(self, pack='event'):
        gwnblock.__init__(self, name="l2_deframer", number_in=1, \
            number_out=1, number_timers=0)

        self.pack = pack


    def process_data(self, ev):
        '''Receives event, extracts payload or event from frmpkt.
        '''
        if ev.__class__ is gwnevent.EventComm:
            if self.pack == 'event':
                n_ev = pickle.loads(ev.frmpkt) 
            elif self.pack == 'payload':
                n_ev = ev
                n_ev.payload = ev.frmpkt
            else:
                return    # not recognized pack action, just copy on output
            self.write_out(n_ev, port_nr=0)
        else:
            pass  # not a data comm event, ignore
        return

