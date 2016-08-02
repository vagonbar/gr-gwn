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

'''Reception with ACK for Selective Repeat, using FSM.
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


from utils.fsm.gwnfsm import FSM, ExceptionFSM


###
### FSM code
###

### Actions

def send_ack(fsm, ev, block):
    '''Sends ack for event received. If there are events in order, pass them to event_sink
    '''

    block.write_out(ev, port_nr=0)
    block.aux_sink = ev.ev_dc['seq_nr']
    i=0
    while (i<block.win_tam) and (block.buffer[0]!=None): # sends events in reception window if in order
        ev_aux = block.buffer.pop(0)
        block.write_out(ev_aux, port_nr=0)
        block.aux_sink = ev_aux.ev_dc['seq_nr']
        block.buffer.append(None)
        block.bool.pop(0)
        block.bool.append(False)
        i = i+1
    # if next event to be expected hasn't arrived, rotate in buffer
    block.buffer.pop(0)
    block.buffer.append(None)
    block.bool.pop(0)
    block.bool.append(False)
    block.NAKexpected = False
    # prints seq_number of events sent to sink
    if block.debug:
        dbg_msg = '   Sending events to sink from ' + str(ev.ev_dc['seq_nr']) + ' to ' + str(block.aux_sink)
        mutex_prt(dbg_msg)
    # making an ack event
    ack = api_events.mkevent('DataOut', {'seq_nr': ev.ev_dc['seq_nr']})
    block.write_out(ack, port_nr=1)
    if block.debug:
        dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
        mutex_prt(dbg_msg)
    return

def store_win(fsm, ev, block):
    '''An event arrives that belongs to reception window, sends ack and stores.
    Sends Nak of previously expected events.
    '''

    if block.debug:
        dbg_msg = ' Event ' + str(ev.ev_dc['seq_nr']) + ' is in reception window  // Last event arrived to sink is ' + str(block.aux_sink)
        mutex_prt(dbg_msg)
    # save in buffer
    pos = (ev.ev_dc['seq_nr']-(block.aux_sink+2)) #se puede agregar condicion en "elif" para ver si ya esta en el buffer, aunque no parece cambiar demasiado
    block.bool[pos] = True
    block.buffer[pos] = ev
    ack = api_events.mkevent('DataOut', {'seq_nr': ev.ev_dc['seq_nr']})
    block.write_out(ack, port_nr=1)
    if block.debug:
        dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
        mutex_prt(dbg_msg)
    # sends NAK of the expected event
    if block.NAKexpected == False:
        pay = ev.ev_dc['seq_nr']-pos-1
        nak = api_events.mkevent('DataIn', {'seq_nr': pay})
        block.write_out(nak, port_nr=1)
        if block.debug:
            dbg_msg = '   Sending NAK corresponding to event number ' + str(nak.ev_dc['seq_nr'])
            mutex_prt(dbg_msg)
        block.NAKexpected = True
    # sends NAK, unless it was sent before
    for i in range(pos):
        if block.bool[i] == True:
            pass
        elif block.bool[i] == False:
            pay = block.aux_sink+2+i
            nak = api_events.mkevent('DataIn', {'seq_nr': pay})
            block.write_out(nak, port_nr=1)
            block.bool[i] = True
            if block.debug:
                dbg_msg = '   Sending NAK corresponding to event number ' + str(nak.ev_dc['seq_nr'])
                mutex_prt(dbg_msg)
    return


def old_ack(fsm, ev, block):
    '''Resends ack not acknowledged.
    '''
    if block.debug:
        dbg_msg = '   Data ' + str(ev.ev_dc['seq_nr']) + ' repeated, resending ACK to Source.'
        mutex_prt(dbg_msg)
    ack = api_events.mkevent('DataOut', {'seq_nr' : ev.ev_dc['seq_nr']})
    block.write_out(ack, port_nr=1)
    return

def stop(fsm, ev, block):
    '''Retries in sending of buffer exceeded, stop sending.
    '''
    if block.debug:
        mutex_prt('    FSM, send retries or buffer exceeded')
        mutex_prt('      max buffer length: ' + str(block.buffer_len) + \
            ', buffer length: ' + str(len(block.ls_buffer)))
        mutex_prt('      max retries: ' + str(block.max_retries) + \
            ' retries: ' + str(fsm.nr_retries))
        fsm.print_state(show=['transition', 'action'])
    #raise ExceptionFSM('Send retries, exceeded')
    return


def fn_error(fsm, event, block):
    fsm.print_state(show=['transition', 'action'])
    raise ExceptionFSM('fn_error, error in transition')
    return



### Conditions
# funcions must return True or False
# conditions expressed as strings are accepted, i.e. 'a == b'


### the FSM

def ack_rep_fsm(blk):
    '''The ARQ Stop and Wait FSM.

    @param blk: reference to the block to which this FSM is attached.
    '''
    f = FSM ('Idle') # 
    f.debug = False

    # transitions
    f.set_default_transition (fn_error, 'Idle')

    #f.add_transition_any ('Idle', None, 'WaitEv')
    #f.add_transition_any ('WaitAck', None, 'WaitAck')

    # 0
    # event is waited to be passed to ev_sink in order
    f.add_transition('DataData', 'Idle', send_ack, 'WaitEv', \
        ['event.ev_dc["seq_nr"] == block.aux_sink+1'])

    # 1
    # event is waited to be passed to ev_sink in order
    f.add_transition('DataData', 'WaitEv', send_ack, 'WaitEv', \
        ['event.ev_dc["seq_nr"] == block.aux_sink+1'])

    # 2
    # ev is not ev waited for, sends ack and stores in reception window
    f.add_transition('DataData', 'WaitEv', store_win, 'WaitEv', \
        ['event.ev_dc["seq_nr"] > (block.aux_sink+1)',
        'event.ev_dc["seq_nr"] <= (block.aux_sink+1+block.win_tam)',
        'event!=block.buffer[event.ev_dc["seq_nr"]-(block.aux_sink+2)]'])

    # 3
    # event is repeated, 1st case
    f.add_transition ('DataData', 'WaitEv', old_ack, 'WaitEv', \
        ['event.ev_dc["seq_nr"]<=block.aux_sink'])

    # 4
    # event is repeated, 2nd case
    f.add_transition ('DataData', 'WaitEv', old_ack, 'WaitEv', \
        ['event.ev_dc["seq_nr"]!=block.buffer[event.ev_dc["seq_nr"]-(block.aux_sink+2)].ev_dc["seq_nr"]'])


    # 11
    f.add_transition_any ('Stop', stop, 'Stop')
    # 12
    f.add_transition_any ('Idle', None, 'Idle')

    #f.add_transition_list (['nak', 'ack0', 'tout'], \
    #                    'WaitAck', resend, 'WaitAck', wait1)

    if blk.debug:
        print "--- FSM created, show state"
        f.print_state(show='state')

    return f


###
### block class code
###

class ACK_Rep_FSM(gwnblock):
    """Reception with ACK .

    Receives an Event on its Event input port, outputs the same item on corresponding output port sending an ACK signal on other output port.
    @param blkname: block name.
    @param blkid: block identifier.
    @param win_tam: reception window's size.
    """
    def __init__(self, win_tam=5):
        
        gwnblock.__init__(self, name='ACK_Rep_FSM', number_in=1, number_out=2, number_timers=0, number_timeouts=0)

        self.debug = True
        self.aux_source = 0 #no parece ser necesario
        self.win_tam = win_tam #cantidad de lugares de la ventana de recepción
        self.aux_sink = 0 #param de payload de ultimo evento que paso

        # genero los vectores buffer y bool
        self.buffer = []   #ventana de recepción
        self.bool = []     #para registro de NAKs y ACKs enviados
        self.NAKexpected = False #para NAK de esperado
        j = 0
        for j in range(win_tam):
            self.buffer.append(None)
            self.bool.append(False)

        self.fsm = ack_rep_fsm(self)

        return


    def process_data(self, ev):
        ''' Receives an event, writes it on output and sends ack
        '''

        if self.debug:
            dbg_msg = '--- {0}, received ev: {1}, with dic: {2}'. \
                format(self.blkname, ev.nickname, ev.ev_dc)
            # only for Data Events:
            #dbg_msg = '--- {0}, received ev: {1}, seq nr: {2}'. \
            #    format(self.blkname, ev.nickname, ev.ev_dc['seq_nr'])
            mutex_prt(dbg_msg)
        # handle event to FSM process functions
        self.fsm.process(ev.nickname, event=ev, block=self)

        return




