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

'''Reception with ACK for Selective Repeat.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events 
import random
import time
import sys

class ack_rep(gwnblock):

    '''Reception with ACK .

    Receives an Event on its Event input port, if it has the expected seq_nr, sends the same item
    on corresponding output port sending an ACK signal on other output port. 
    If the event received is not the expected one, the event is saved in a reception window until 
    the missing events arrive. Once the window has the expected event, all the events in the
    reception window are sent in order.
    If an event arrives that indicates a missing event, sends a NAK signal with missing event's seq_nr.

    @param ack_nickname: nickname of ACK event. Has to match with processing ARQ block's name of expected Ack Event.
    @param nak_nickname: nickname of NAK event. Has to match with processing ARQ block's name of expected Nak Event.
    @param win_tam: reception window's size.
    '''

    def __init__(self, ack_nickname = 'DataOut', nak_nickname = 'DataIn', win_tam=5, debug=False):
        
        gwnblock.__init__(self, name='ack_rep', number_in=1, number_out=2, number_timers=0, number_timeouts=0)

        self.debug = debug
        self.ack_nickname = ack_nickname
        self.nak_nickname = nak_nickname
        self.aux_sink = 0           #seq_nr of the last event correctly received and sent
        self.win_tam = win_tam      #reception window's size

        self.buffer = []            #reception window
        self.bool = []              #to keep track of NACKs and ACKs sent
        self.NAKexpected = False    #flag to indicate if a NAK has already been sent
        
        #initialize reception window and bool list
        j = 0
        for j in range(win_tam):
            self.buffer.append(None) 
            self.bool.append(False)

        return

    def process_data(self, ev):

        # DataData event arrives 
        if (ev.nickname == 'DataData'):
            #if it is the expected event
            if ev.ev_dc['seq_nr'] == self.aux_sink+1:
                self.write_out(ev, port_nr=0)
                self.aux_sink = ev.ev_dc['seq_nr']

                #send events in reception window if in order
                i=0
                while (i<self.win_tam) and (self.buffer[0]!=None): 
                    ev_aux = self.buffer.pop(0)
                    self.write_out(ev_aux, port_nr=0)
                    self.aux_sink = ev_aux.ev_dc['seq_nr']
                    self.buffer.append(None)
                    self.bool.pop(0)
                    self.bool.append(False)
                    i = i+1

                #if next event to be expected hasn't arrived, rotate in buffer
                self.buffer.pop(0)
                self.buffer.append(None)
                self.bool.pop(0)
                self.bool.append(False)
                self.NAKexpected = False

                #prints seq_number of events sent to sink
                if self.debug:
                    dbg_msg = '   Sending events to sink from ' + str(ev.ev_dc['seq_nr']) + ' to ' + str(self.aux_sink)
                    mutex_prt(dbg_msg)
	        
                #create ack event
	            ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
	            self.write_out(ack, port_nr=1)
                if self.debug:
                    dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
                    mutex_prt(dbg_msg)

            #if it is an event that belongs to reception window but not the expected one
            elif (ev.ev_dc['seq_nr'] > (self.aux_sink+1)) and (ev.ev_dc['seq_nr'] <= (self.aux_sink+1+self.win_tam)) and (ev!=self.buffer[ev.ev_dc['seq_nr']-(self.aux_sink+2)]):
                if self.debug:
                    dbg_msg = ' Event ' + str(ev.ev_dc['seq_nr']) + ' is in reception window  // Last event arrived to sink is ' + str(self.aux_sink)
                    mutex_prt(dbg_msg)

                #save in reception window (buffer)
                pos = (ev.ev_dc['seq_nr']-(self.aux_sink+2)) #se puede agregar condicion en "elif" para ver si ya esta en el buffer, aunque no parece cambiar demasiado
                self.bool[pos] = True
                self.buffer[pos] = ev
                ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
                self.write_out(ack, port_nr=1)
                if self.debug:
                    dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
                    mutex_prt(dbg_msg)

                #send NAK of the expected event
                if self.NAKexpected == False:
                    nr = ev.ev_dc['seq_nr']-pos-1
                    nak = api_events.mkevent(self.nak_nickname, {'seq_nr': nr})
                    self.write_out(nak, port_nr=1)
                    if self.debug:
                        dbg_msg = '   Sending NAK corresponding to event number ' + str(nak.ev_dc['seq_nr'])
                        mutex_prt(dbg_msg)
                    self.NAKexpected = True
                
                #send NAK, unless it was sent before
                for i in range(pos):
                    if self.bool[i] == True:
                        pass
                    elif self.bool[i] == False:
                        nr = self.aux_sink+2+i
                        nak = api_events.mkevent(self.nak_nickname, {'seq_nr': nr})
                        self.write_out(nak, port_nr=1)
                        self.bool[i] = True
                        if self.debug:
                            dbg_msg = '   Sending NAK corresponding to event number ' + str(nak.ev_dc['seq_nr'])
                            mutex_prt(dbg_msg)

            #if event has been sent already, resend ACK backwards only.
            elif (ev.ev_dc['seq_nr']<=self.aux_sink) or (ev.ev_dc['seq_nr']!=self.buffer[ev.ev_dc['seq_nr']-(self.aux_sink+2)].ev_dc['seq_nr']):
                if self.debug:
                    dbg_msg = '   Data ' + str(ev.ev_dc['seq_nr']) + ' repeated, resending ACK to Source.'
                    mutex_prt(dbg_msg)
                ack = api_events.mkevent(self.ack_nickname, {'seq_nr' : ev.ev_dc['seq_nr']})
                self.write_out(ack, port_nr=1)

            else:
                pass
        else:
            pass

        return





