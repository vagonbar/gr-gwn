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
Probe shared transmission medium to detect if busy.
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

    This block receives an event and outputs it only if the instant signal strength is lower than the transmit threshold, else event is discarded.
    The instant signal strength is obtained through invocation of a function in another block, such as function level() in GNU Radio block Probe Avg Mag^2 (probe average magnitude squared).
    In GRC, this block parameters Block ID, Function Name, and Funcion Args must be initialized to refer to the external block identifier, the function name, and optionally the function args. These parameters are defined in the XML file for this block.
    @ivar get_level: a reference to a function in an external block.
    '''
    def __init__(self, transmit_threshold=1.0, debug=False):
        '''Constructor.

        @param transmit_threshold: the signal power under which transmission happens, i.e. event is transferred to output if signal_strength value is lower than this value.
        @param debug: print additional information; default False.
        '''
        gwnblock.__init__(self, name="probe_medium", 
            number_in=1, number_out=1, number_timers=0)
        self.transmit_threshold = transmit_threshold
        self.debug = debug
        self.get_level = None   # reference to function in external block
        return


    def set_get_level(self, get_level):
        '''Sets function to interrogate signal level in other block.

        @param get_level: a reference to a function in an external block.
        '''        
        self.get_level = get_level
        if self.debug: 
            mutex_prt("Probe medium, function level() set, " + \
                str(type(self.get_level)))
        return


    def process_data(self, ev):
        '''Transmits or discards event according to signal strength.

        Obtains signal power level signal; if less than threshold transmits, else discards event.
        @param ev: an Event object.
        '''

        self.signal_strength = self.get_level()

        msg = ">>> Probe Medium: transmit threshold {0}, signal strength {1}".\
            format(self.transmit_threshold, self.signal_strength)
        if self.debug:
            mutex_prt(msg)

        if self.signal_strength < self.transmit_threshold:
            ev.payload += msg
            self.write_out(ev, port_nr=0)
        return


