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

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests


class event_guider(gwnblock):
    '''A Guider, outputs items in right port.

    Receives an Event on its Event input port, outputs the same item on corresponding output port for further treatment.
    @param type_1: event Data nickname.
    @param type_2: event Ack nickname.
    '''

    def __init__(self, type_1='DataData', type_2='CtrlACK', my_address='', debug=False):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='event_guider', \
            number_in=1, number_out=2, number_timers=0)
        self.type_1 = type_1
        self.type_2 = type_2
        self.my_address = my_address   # has to match address in Event_Constructor
        self.debug = debug          # please set from outside for debug print
        
        return
    
    def process_data(self, ev):

        '''
        @param ev: an Event object.
        '''

        if self.debug:
            dbg_msg = 'Llego el dato ' + str(ev.nickname) + ' dirigido a la dirección: ' + str(ev.dst_address)
            mutex_prt(dbg_msg)
        if ev.dst_address==self.my_address:
            if ev.nickname==self.type_1:
                self.write_out(ev, port_nr=0)
            elif ev.nickname==self.type_2:
                self.write_out(ev, port_nr=1)

        if self.my_address=='Broadcast':
            if ev.nickname==self.type_1:
                self.write_out(ev, port_nr=0)
            elif ev.nickname==self.type_2:
                self.write_out(ev, port_nr=1)

        return


