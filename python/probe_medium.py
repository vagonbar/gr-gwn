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
A block to probe the medium.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnevents import api_events as api_events
from gwnblock import mutex_prt 
import time


class probe_medium(gwnblock):
    '''Probe shared transmission medium to detect if busy.

        This block receives an event and outputs it only if the instant signal strength is lower than the transmit threshold. The instant signal strength is typically read from an external variable, such as the one produce by GNU Radio block Function Probe.
    '''
    def __init__(self, transmit_threshold=1.0, signal_strength=0.0, debug=False):
        '''Constructor.

        @param transmit_threshold: the signal power under which transmission happens.
        @param signal_strength: instant power value of the signal, read from external variable.
        @param debug: print additional information; default False.
        '''
        gwnblock.__init__(self, name="probe_medium", 
            number_in=1, number_out=1, number_timers=0)
        self.transmit_threshold = transmit_threshold
        self.signal_strength = signal_strength
        self.debug = debug
        return

    def set_signal_strength(self, signal_strength):
        '''Set signal strength, required in XML file to read external variable.
        '''
        self.signal_strength = signal_strength
        return

    def process_data(self, ev):
        msg = "--- Probe Medium: transmit threshold {0}, signal strength {1}".\
            format(self.transmit_threshold, self.signal_strength)
        if self.debug:
            mutex_prt(msg)
        if self.signal_strength < self.transmit_threshold:
            ev.payload += msg
            self.write_out(ev, port_nr=0)
        return


