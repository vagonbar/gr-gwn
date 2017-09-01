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

'''An ARQ Selective Repeat sender.
'''

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
import math
import time
import pmt  


class sel_rep(gwnblock):

    '''Saves events in buffer and sends a window of them, as it receives the corresponding ACKs it keeps sending events.

    @param ack_nickname: ack event's nickname.
    @param buff_tam: buffer's size.
    @param win_tam: window's size.
    @param time_out: expiration time for ack receipt.
    '''

    def __init__(self, ack_nickname='DataOut', buff_tam=10, win_tam=5, time_out=1, debug=False):
        
        gwnblock.__init__(self, name='sel_rep', number_in=2, number_out=1, number_timers=0, number_timeouts=win_tam)

        self.debug = debug           # please set from outside     
        self.buffer = []
        self.win = []
        self.ack_nickname = ack_nickname
        self.timeout = time_out
        self.buff_tam = buff_tam
        self.var_aux = 0
        self.win_tam = win_tam
        self.a = 0

        
        self.loob = []     #boolean list used to see timeouts available
        j = 0
        for j in range(win_tam):
            self.loob.append(False)     #at the beginning, all timeouts are available

        #create a dictionary to save seq_nr:timeout_nr
        self.dic = {}

        return


    def process_data(self, ev):

        ''' Process data.

        Receives an event, saves it in window, unless it is full,
        in which case saves in buffer. If the latter is full, the event
        is discarded. Writes events from the window on output and
        starts a timeout for each of them, when ack received, it clears 
        the corresponding entry in the window, printing an appropiate
        messagge. If a timeout expires, it resends the corresponding
        event, starting another timeout. If a NAK is received, the event
        is resent starting a timeout.
        '''

        #empty window
        if (ev.nickname == 'DataData' and self.win == []):
            self.win.append(ev)
            self.write_out(ev, port_nr=0)
            if self.debug:
                dbg_msg = '   Win empty, event: ' + str(ev.ev_dc['seq_nr']) + ', type ' + str(ev.nickname) + ' arrived to Sel_Rep. Sending event, saving in Win and starting timeout!'
                mutex_prt(dbg_msg)
            #search for an available timeout
            i=0
            while self.loob[i]==True and i<self.win_tam:
                i = i+1
            self.timeouts[i].start(self.timeout, ev_dc = ev.ev_dc)
            self.dic[ev.ev_dc['seq_nr']] = i
            self.loob[i] = True
            
        #send and save event in win unless it is full
        elif (ev.nickname == 'DataData'and len(self.win)<self.win_tam):
            self.win.append(ev)
            self.write_out(ev, port_nr=0)
            if self.debug:
                dbg_msg = '   Event ' + str(ev.ev_dc['seq_nr']) + ', type ' + str(ev.nickname) + ' arrived to Sel_Rep. Sending event, saving in Win and starting timeout!'
                mutex_prt(dbg_msg)
            self.write_out(ev, port_nr=0)
            i=0
            while self.loob[i]==True and i<self.win_tam:
                i = i+1
            self.timeouts[i].start(self.timeout, ev_dc = ev.ev_dc)
            self.dic[ev.ev_dc['seq_nr']] = i
            self.loob[i] = True

        #if win is full
        elif (ev.nickname=='DataData' and len(self.win)>=self.win_tam):
            #if buffer is not full
            if len(self.buffer)<self.buff_tam:
                self.buffer.append(ev)
                if self.debug:
                    dbg_msg = '   Window is full, event saved on buffer ' +str(ev.ev_dc['seq_nr']) + ', type ' + str(ev.nickname)
                    mutex_prt(dbg_msg)
            #if buffer is full
            elif len(self.buffer)>=self.buff_tam:
                if self.debug:
                    dbg_msg = '   Buffer is full, event discarded ' +str(ev.ev_dc['seq_nr']) + ', type ' + str(ev.nickname)
                    mutex_prt(dbg_msg)

        #when timeout is reached, resend the lost event
        elif (len(self.win)!=0) and (ev.nickname == 'EventTimer'):
            #get the timeout index from the dictionary dic
            auxdos = int(self.dic[ev.ev_dc['seq_nr']])
            #set that timeout as available
            self.loob[auxdos]=False
            #delete the correspondence in the dictionary
            del self.dic[ev.ev_dc['seq_nr']]
            #search for the event lost in win
            i=0
            while i<len(self.win) and int(self.win[i].ev_dc['seq_nr'])!=ev.ev_dc['seq_nr']:
                i = i + 1
            dato_r = self.win[i]
            if self.debug:
                dbg_msg = '\n / / Message ' + str(dato_r.ev_dc['seq_nr']) + ' lost, resending from Sel_Rep ' + str(dato_r.nickname) + ' \ \ '
                mutex_prt(dbg_msg)
            self.write_out(dato_r, port_nr=0)
            #search for an available timeout
            i=0
            while i<len(self.loob) and self.loob[i]==True:
                i = i+1
            self.timeouts[i].start(self.timeout, ev_dc = dato_r.ev_dc)
            self.dic[ev.ev_dc['seq_nr']] = i
            self.loob[i] = True

        #when NAK arrives, resend the missing event
        elif (len(self.win)>0) and (ev.nickname == 'DataIn'):
            #get the timeout index from the dictionary dic
            auxdos = int(self.dic[ev.ev_dc['seq_nr']])
            self.timeouts[auxdos].cancel()
            #set that timeout as available
            self.loob[auxdos]=False
            del self.dic[ev.ev_dc['seq_nr']]
            #search for the event lost in win
            i=0
            while i<len(self.win) and int(self.win[i].ev_dc['seq_nr'])!=int(ev.ev_dc['seq_nr']):
                i = i + 1
            dato_r = self.win[i]
            if self.debug:
                dbg_msg = '\n / / NAK arrived! Message ' + str(dato_r.ev_dc['seq_nr']) + ' appears to be lost, resending from Sel_Rep ' + str(dato_r.nickname)
                mutex_prt(dbg_msg)
            self.write_out(dato_r, port_nr=0)
            #search for an available timeout
            i=0
            while i<len(self.loob) and self.loob[i]==True:
                i = i+1
            self.timeouts[i].start(self.timeout, ev_dc = dato_r.ev_dc)
            self.dic[ev.ev_dc['seq_nr']] = i
            self.loob[i] = True

	    #ack received: cancel timeout and send events in win
        elif (ev.nickname == self.ack_nickname) and (len(self.win)>0):
            #check if the ack received corresponds to one of the events sent 
            if ev.ev_dc['seq_nr'] in self.dic.keys(): 
                #get the corresponding timeout index and cancel it
                aux = self.dic[ev.ev_dc['seq_nr']]
                self.timeouts[aux].cancel()
                self.loob[aux]=False
                del self.dic[ev.ev_dc['seq_nr']]
                #search for the corresponding event and take it out of the win
                i=0
                while i<len(self.win) and self.win[i].ev_dc['seq_nr']!=ev.ev_dc['seq_nr']:
                    i = i + 1
                dato_r = self.win.pop(i)
                if self.debug:
                    msg = '   ACK correctly received from message ' + str(ev.ev_dc['seq_nr']) + ', type ' + str(dato_r.nickname) + '\n'
                    mutex_prt(msg)
                #buffer not empty
                if self.buffer!=[]:
                    dato = self.buffer.pop(0)
                    self.win.append(dato)
                    if self.debug:
                        dbg_msg = '   Sending event '+ str(dato.ev_dc['seq_nr']) + ' from Win, type ' + str(dato.nickname)
                        mutex_prt(dbg_msg)
                    #search for an available timeout and send the event
                    i=0
                    while i<len(self.loob) and self.loob[i]==True:
                        i = i+1
                    self.timeouts[i].start(self.timeout, ev_dc = dato.ev_dc)
                    self.dic[dato.ev_dc['seq_nr']] = i
                    self.loob[i] = True
                    self.write_out(dato, port_nr=0)
            else:
                if self.debug:
                    msg = '   ACK already received from message ' + str(ev.ev_dc['seq_nr']) + '\n'
                    mutex_prt(msg)

        return



