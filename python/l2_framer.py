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

'''Creates a frame packet from event or event payolad.
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


class l2_framer(gwnblock):
    ''' Creates a frame packet from event or event payload.

    Serializes a received event and saves it in frame packet field in the event. Optionally, takes only the payload and saves it in the frame packet field. Event must be a communications event; other kinds are not packed, just repeated on output as such.
    @param pack: type of packing; if 'event', serializes event into frmpkt field of output event; if 'payload' puts payload in frmpkt field of output event. An unrecognized type of packing does nothing, no event output.
    '''

    def __init__(self, pack='event'):
        gwnblock.__init__(self, name="l2_framer", number_in=1, \
            number_out=1, number_timers=0)

        self.pack = pack


    def process_data(self, ev):
        '''Receives event, packs, loads frmpkt.
        '''
        if ev.__class__ is gwnevent.EventComm:
            if self.pack == 'event':
               ev.frmpkt = pickle.dumps(ev)
            elif self.pack == 'payload':
                self.frmpkt = ev.payload
            else:
                return    # not recognized pack action, just copy on output
            self.write_out(ev, port_nr=0)
        else:
            pass  # not a data comm event, ignore
        return

