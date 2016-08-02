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
import random                           # for probability loss
import pmt                              # for messages and PDUs


class delay_ev(gwnblock):
    '''A delay event, outputs items with delay time if choosen.

    Receives an Event on its Event input port, outputs the same item on corresponding output port with a delay time.
    @param blkname: block name.
    @param blkid: block identifier.
    @param delay_add: added delay, float value.
    @param delay_min: minimum delay time.
    '''

    def __init__(self, delay_add=0., delay_min=0.):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='delay_ev', number_in=1, number_out=1, number_timers=0, number_timeouts=1)
        
        self.delay = 0.
        self.delay_add = delay_add
        self.delay_min = delay_min
        self.debug = False  # please set from outside for debug print
        self.buffer_dato = []
        return


    def process_data(self, ev, port, port_nr):
        '''Receives an Event, outputs with probability delay. Buffer holds events so to send them FIFO.

        @param ev: an Event object.
        '''
        if self.delay_add != 0. and self.delay_min != 0.:
            # first event to come, holds in buffer and sets delay time
            if ev.nickname!='TimerTOH' and len(self.buffer_dato)==0:
                self.buffer_dato.append(ev)
                rand_nr = random.random()
                self.delay = self.delay_min + rand_nr*self.delay_add
                self.timeouts[0].start(self.delay, 'TimerTOH')
    
            # saves event in buffer
            elif ev.nickname!='TimerTOH' and len(self.buffer_dato)!=0:
                self.buffer_dato.append(ev)
    
            # when timeout arrives sends the first event in line, restarts timeout
            elif len(self.buffer_dato)!=0 and (ev.nickname=='TimerTOH'):
                dato = self.buffer_dato.pop(0)
                self.write_out(dato)
                if self.debug:
                    dbg_msg = '____ ACK from event number ' + str(dato.ev_dc['seq_nr']) + ' is sent with a delay of ' + str(self.delay) + ' ____' # can be used in both ways (sending Data or receiving ACKs)
                    mutex_prt(dbg_msg)
                if len(self.buffer_dato)!=0:
                    rand_nr = random.random()
                    self.delay = self.delay_min + rand_nr*self.delay_add
                    self.timeouts[0].start(self.delay, 'TimerTOH')
        else:
            self.write_out(ev)
            if self.debug:
                dbg_msg = '   Envio de evento ' + str(ev.ev_dc['seq_nr']) + ' sin delay!    '
                mutex_prt(dbg_msg)

        return


