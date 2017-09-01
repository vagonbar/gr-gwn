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

'''An ARQ Stop and Wait sender with a CSMA/CA implementation.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events   # to create ACK event
import pmt                              # for messages and PDUs
import random
import math

from utils.fsm.gwnfsm import FSM, ExceptionFSM


###
### FSM code
###

### Actions

def send(fsm, event, block):
    '''Sends event received.
    '''
    if block.debug:
        mutex_prt('    SEND event, seq nr: {0}'.format(event.ev_dc['seq_nr']))
    block.ls_buffer.append(event)
    # not needed
    #    fsm.ev_sent = event                    # store for eventual resend
    #event.ev_dc['ack'] = fsm.wait    # waited ack 
    block.timeouts[0].start(block.timeout)
    fsm.wait=event.ev_dc['seq_nr']
    block.write_out(event, port_nr=0)
    # make a count event to send to upper process in order to measure QoS
    count = api_events.mkevent('DataData', payload='Try!')
    block.write_out(count, port_nr=1)
    return 

def sendfrombuffer(fsm, event, block):
    '''Sends event from buffer, first in list.
    '''
    ack_ok(fsm, event, block)
    if len(block.ls_buffer) > 0:
        event = block.ls_buffer[0]   # get first from list
        if block.debug:
            mutex_prt('    TO SEND, from buffer, seq nr: {0}'.\
                format(event.ev_dc['seq_nr']))
        #fsm.ev_sent = event                    # store for eventual resend
        #event.ev_dc['ack'] = fsm.wait    # waited ack 
        block.timeouts[0].start(block.timeout)
        fsm.wait=event.ev_dc['seq_nr']
        block.write_out(event, port_nr=0)
        count = api_events.mkevent('DataData', payload='Try!')
        block.write_out(count, port_nr=1)
    else:
        mutex_prt('FSM send ERROR: no event to send')
    return



def sendfrombackoff(fsm, event, block):
    '''Sends event from backoff state, first in list.
    '''
    if len(block.ls_buffer) > 0:
        event = block.ls_buffer[0]   # get first from list
        if block.debug:
            mutex_prt('    TO SEND, from backoff, seq nr: {0}'.\
                format(event.ev_dc['seq_nr']))
        #fsm.ev_sent = event                    # store for eventual resend
        #event.ev_dc['ack'] = fsm.wait    # waited ack 
        block.timeouts[0].start(block.timeout)
        fsm.wait=event.ev_dc['seq_nr']
        block.write_out(event, port_nr=0)
        # make a count event to send to upper process in order to measure QoS
        count = api_events.mkevent('DataData', payload='Try!')
        block.write_out(count, port_nr=1)
    else:
        mutex_prt('FSM send ERROR: no event to send')
    return


def resend(fsm, event, block):
    '''Resends event not acknowledged.
    '''
    # Beware! event to resend is fsm.ev_sent, not event in arguments
    #fsm.print_state(show=['transition', 'action'])
    block.timeouts[0].cancel()    # in case it is still active
    fsm.nr_retries = fsm.nr_retries + 1
    block.slots_backoff=block.slots_backoff*2
    event=block.ls_buffer[0]
    if block.debug:
        mutex_prt('    RESEND event, seq nr: {0}, retries: {1}'.\
            format(event.ev_dc['seq_nr'], fsm.nr_retries))
    #event.ev_dc['ack'] = fsm.wait    # waited ack 
    block.timeouts[0].start(block.timeout)
    fsm.wait=event.ev_dc['seq_nr']
    block.write_out(event, port_nr=0)
    # make a count event to send to upper process in order to measure QoS
    count = api_events.mkevent('DataData', payload='Try!')
    block.write_out(count, port_nr=1)
    return


def push(fsm, event, block):
    '''Pushes event into buffer.
    '''
    if block.buffer_len == -1 or len(block.ls_buffer) < block.buffer_len:
        block.ls_buffer.append(event)    # add to end of list
    else:
        raise ExceptionFSM('Buffer length exceeded')
    #block.ls_buffer.append(ev)    # add to end of list
    if block.debug:
        mutex_prt('    FSM PUSH, len buffer: ' + str(len(block.ls_buffer)) + \
            ' max buffer: ' + str(block.buffer_len))
    return


def ack_ok(fsm, event, block):
    '''ACK was correct, cancel timer, reset retries.
    '''
    block.timeouts[0].cancel()
    block.ls_buffer.pop(0)
    fsm.nr_retries = 0
    block.slots_backoff = 1
    # make a success event to send to upper process in order to measure QoS
    success = api_events.mkevent('DataData', payload='Success!')
    block.write_out(success, port_nr=1)
    # cambiamos lo siguiente por la comprobacion del ack.seq_nr
    '''if fsm.wait == event.ev_dc['ack']:
        fsm.wait = 'ack0'
    else:
        fsm.wait = 'ack1' '''
    #fsm.wait=fsm.wait+1
    return


def stop(fsm, event, block):
    '''Retries in sending of buffer exceeded, stop sending.
    '''
    if block.debug:
        mutex_prt('    FSM, send retries or buffer exceeded')
        mutex_prt('      max buffer length: ' + str(block.buffer_len) + \
            ', buffer length: ' + str(len(block.ls_buffer)))
        mutex_prt('      max retries: ' + str(block.max_retries) + \
            ' retries: ' + str(fsm.nr_retries))
        fsm.print_state(show=['transition', 'action'])
    # genero un dato que avise al proceso superior que estoy en el estado Stop
    stop = api_events.mkevent('DataData', payload='Stop!')
    block.write_out(stop, port_nr=1)
    #raise ExceptionFSM('Send retries, exceeded')
    return


def hold(fsm, event, block):
    '''Starts random timer for backoff state.
    '''
    #block.slots_backoff=1
    #x=random.randint(1, block.slots_backoff)
    fsm.nr_retries+=1
    if event.nickname=='DataData':
        push(fsm, event, block)
    block.timeouts[1].start(block.timeout_backoff)#*x)
    #mutex_prt('-* *-*-*-   estoy en hold ----------')
    return


def rehold(fsm, event, block):
    '''Restarts random timer for backoff state, changes the number of possible slots.
    '''
    fsm.nr_retries+=1
    block.slots_backoff=block.slots_backoff*2
    x=random.randint(1, block.slots_backoff)
    mutex_prt('El x vale: {0}'.format(x))
    block.timeouts[1].cancel()   # chequear si es necesario
    block.timeouts[1].start(block.timeout_backoff*x)
    return


def hold_ack(fsm, event, block):
    '''ACK was correct, cancel timer, reset retries.
    Buffer isn't empty, channel is busy, holds in backoff state.
    '''
    ack_ok(fsm, event, block)
    if len(block.ls_buffer) > 0:
        event = block.ls_buffer[0]   # get first from list
        block.timeouts[1].start(block.timeout_backoff)
        fsm.nr_retries+=1
        if block.debug:
            mutex_prt('    TO SEND, from buffer, seq nr: {0}'.\
                format(event.ev_dc['seq_nr']))
    else:
        mutex_prt('FSM send ERROR: no event to send')
    return


def fn_error(fsm, event, block):
    mutex_prt('fn_error --> {0}'.format(event.nickname))
    fsm.print_state(show=['transition', 'action'])
    raise ExceptionFSM('fn_error, error in transition')
    return


### Conditions
# funcions must return True or False
# conditions expressed as strings are accepted, i.e. 'a == b'

def med_free_true(fsm, event, block):
    '''Transmits or discards event according to signal strength.

    Obtains signal power level signal; if less than threshold transmits, else discards event.
    @param ev: an Event object.
    '''
    channel = False
    signal_strength = block.get_level()
    true_signal_strength = math.sqrt(signal_strength)

    msg = ">>> Probe Medium: transmit threshold {0}, signal strength {1}".\
        format(block.transmit_threshold, true_signal_strength)
    if block.debug:
        mutex_prt(msg)

    if true_signal_strength < block.transmit_threshold:
        channel=True
    return channel


# como solo preguntamos si el canal esta libre, y asumimos que si la respuesta es falsa, esta ocupado,
# ya no tiene sentido tener dos versiones, una preguntando libre y otra ocupado

# def med_free_true(fsm, event, block):
#     return med_free(fsm, event, block)

# def med_free_false(fsm, event, block):
#     return not med_free(fsm, event, block)

#def med_free(fsm, event, block):
#    return fsm.states[block.pos]


### the FSM

def csma_fsm(blk):
    '''The ARQ Stop and Wait FSM.

    @param blk: reference to the block to which this FSM is attached.
    '''
    f = FSM ('Idle') # 
    f.debug = blk.fsm_debug #
    # para cada dato que mando: f.wait=event.ev_dc['seq_nr']
    f.wait = 0
    f.nr_retries = 0

    #f.states=[True, True]+[True]*1000 #

    # transitions
    f.set_default_transition (fn_error, 'Idle')

    #f.add_transition_any ('Idle', None, 'Idle')
    #f.add_transition_any ('WaitAck', None, 'WaitAck')


    # 1
    f.add_transition('DataData', 'Idle', send, 'WaitAck', \
        med_free_true)   # channel free

    # 2
    f.add_transition('CtrlACK', 'WaitAck', ack_ok, 'Idle', \
        ['self.wait==event.ev_dc["seq_nr"]',  # ack is ack waited for
        'len(block.ls_buffer) == 1'] )       # no event in buffer

    # 3
    f.add_transition ('CtrlACK', 'WaitAck', sendfrombuffer, 'WaitAck', \
        ['self.wait==event.ev_dc["seq_nr"]',  # ack is ack waited for
        'len(block.ls_buffer) > 1',          # event in buffer
        med_free_true])              # channel free

    # 4
    f.add_transition ('CtrlACK', 'WaitAck', None, 'WaitAck', \
        ['self.wait<>event.ev_dc["seq_nr"]'])  # ack is NOT ack waited for

    # 5 
    f.add_transition ('EventTimer', 'WaitAck', resend, 'WaitAck', \
        ['self.nr_retries < block.max_retries',   # retries left
        med_free_true])                    #channel free

    # 7
    f.add_transition('EventTimer', 'WaitAck', rehold, 'BackOff', \
        'self.nr_retries < block.max_retries')   # se reemplaza med_free_false, asumiendo que es el complemento

    # 6
    f.add_transition ('EventTimer', 'WaitAck', stop, 'Stop', \
        ['self.nr_retries >= block.max_retries'])     # retries exceeded

    # 8
    f.add_transition ('DataData', 'WaitAck', push, 'WaitAck', \
        ['len(block.ls_buffer) < block.buffer_len'])  # buffer ok

    # 9
    f.add_transition ('DataData', 'WaitAck', stop, 'Stop', \
        ['len(block.ls_buffer) >= block.buffer_len'])  # buffer max exceed

    # 10
    f.add_transition('DataData', 'Idle', hold, 'BackOff')   # channel busy # se saco med_free_false

    # 11
    f.add_transition('CtrlACK', 'WaitAck', hold_ack, 'BackOff', \
        ['self.wait==event.ev_dc["seq_nr"]', 'len(block.ls_buffer) > 1'])   # channel not free # se saca med_free_false, 

    # 12
    f.add_transition('EventTimer', 'BackOff', sendfrombackoff, 'WaitAck', \
        med_free_true) # revisar que es el timeout del BackOff

    # 13
    f.add_transition('EventTimer', 'BackOff', rehold, 'BackOff', \
        'self.nr_retries < block.max_retries') # revisar que es el timeout del BackOff
        # retiramos esta condicion para que no reitere consulta de canal: med_free_false, 

    # 14
    f.add_transition('EventTimer', 'BackOff', stop, 'Stop', \
        'self.nr_retries >= block.max_retries')     # retries exceeded # revisar que es el timeout del BackOff
    	#retiramos esta condicion: , med_free_false

    # 15
    f.add_transition('DataData', 'BackOff', push, 'BackOff', \
        ['len(block.ls_buffer) < block.buffer_len'])  # buffer ok

    # 16
    f.add_transition('DataData', 'BackOff', stop, 'Stop', \
        ['len(block.ls_buffer) >= block.buffer_len'])  # buffer max exceed

    # 17 
    f.add_transition_any ('Stop', stop, 'Stop')

    # 18
    f.add_transition_any ('Idle', None, 'Idle')

   

    #if blk.debug:
    #    print "--- FSM created, show state"
    #    f.print_state(show='state')

    return f


###
### block class code
###

class CSMA_FSM(gwnblock):
    '''An ARQ Stop and wait event sender with a CSMA/CA implementation.

    Receives an event, starts a timeout, writes this event on output port 1, and waits for an ACK to the message sent. On receiving the appropriate ACK, sends next message. On timeout, resends the unacknowledged message. Received messages are buffered in a FIFO list.
    @param ack_nickname: the nickname of the acknowledge event waited for.
    @param max_retries: number of times to resend event if ACK not received.
    @param tout_nickname: the nickname of the timer event waited for.
    @param timeout: the timeout in seconds.
    @param tout_backoff: the nickname of the backoff timer event waited for.
    @param slots_backoff: the backoff time slots in seconds.
    @param buffer_len: the buffer capacity, i.e. the maximum length of the list; default is 0, which means no limit.
    '''

    def __init__(self, ack_nickname='CtrlACK', max_retries=3, \
            tout_nickname='EventTimer', timeout=1.0, \
            tout_backoff='TimerTOH', timeout_backoff = 0.01, \
            buffer_len=1000, transmit_threshold=1.0, fsm_debug=False, debug=False):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name='CSMA_FSM', \
            number_in=1, number_out=2, number_timeouts=2)

        self.ack_nickname = ack_nickname
        self.max_retries = max_retries
        self.tout_nickname = tout_nickname
        self.timeout = timeout
        self.tout_backoff = tout_backoff   #Timeout event
        self.timeout_backoff = timeout_backoff    #Timeout default time
        self.slots_backoff = 1
        self.buffer_len = buffer_len
        self.ls_buffer = []     # length must be checked in process
        #self.debug = False      # please set from outside for debug print
        self.fsm_debug = fsm_debug
        self.debug = debug

        #self.signal_strength
        self.transmit_threshold = transmit_threshold
        self.get_level = None   # reference to function in external block

        self.fsm = csma_fsm(self)

        #not needed no more: self.pos = -1

        return

    # for probing the medium
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
        '''Writes event, waits for ACK, retransmits.

        The received event is passed on to the process function of the FSM; actions in the FSM are provided with the received event and a reference to the present block, so that they can access this block's attributes and functions, in particular the write_out function to send events.
        @param ev: a received Event object.
        '''
        #not needed no more: self.pos+=1

        if self.debug:
            dbg_msg = '--- {0}, received ev: {1}'. \
                format(self.name(), ev.nickname)
            # only for Data Events:
            #dbg_msg = '--- {0}, received ev: {1}, seq nr: {2}'. \
            #    format(self.name(), ev.nickname, ev.ev_dc['seq_nr'])
            mutex_prt(dbg_msg)
        # handle event to FSM process functions
        self.fsm.process(ev.nickname, event=ev, block=self)
        return

