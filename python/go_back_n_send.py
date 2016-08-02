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

'''An ARQ Go Back N sender.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events   # to create ACK event
import pmt                              # for messages and PDUs

from utils.fsm.gwnfsm import FSM, ExceptionFSM


###
### FSM code
###

### Actions

def send(fsm, event, block):
    '''Sends event received.
    '''
    if block.debug:
        mutex_prt('    SEND event, seq nr: {0} and awaited ack is thus: {1}'.format(event.ev_dc['seq_nr'], fsm.wait))
    block.win.append(event)                  # store in sender's win for eventual resend
    i=0
    while block.loob[i]==True and i<block.win_len:
        i = i+1
    block.win[len(block.win)-1].ev_dc['ack'] = fsm.wait     # waited ack
    block.timeouts[i].start(block.timeout, ev_dc = event.ev_dc)
    block.dic_timeouts[event.ev_dc['seq_nr']] = i
    block.loob[i] = True
    if block.debug:
        mutex_prt(' Empezo timeout: {0}' . format(len(block.win)-1))
    block.write_out(block.win[len(block.win)-1])
    return 


def sendfrombuffer(fsm, event, block):
    '''Sends event from buffer, first in list.
    '''
    if len(block.ls_buffer) > 0:
        ack_ok(fsm, event, block)
        event = block.ls_buffer.pop(0)   # get first from list
        if block.debug:
            mutex_prt('    TO SEND, from buffer, seq nr: {0}'.\
                format(event.ev_dc['seq_nr']))
        send(fsm, event, block)
    else:
        mutex_prt('FSM send ERROR: no event to send')
    return


def resend(fsm, event, block):
    '''Resends event not acknowledged.
    '''
    # Beware! event to resend is fsm.ev_sent, not event in arguments --> Now events to resend are all in win
    #fsm.print_state(show=['transition', 'action'])
    fsm.nr_retries = fsm.nr_retries + 1     # check if this is still valid
    if block.debug:
        mutex_prt('    RESEND events from win, from seq nr: {0} to {1}, retries: {2}'.\
            format(block.win[0].ev_dc['seq_nr'], block.win[len(block.win)-1].ev_dc['seq_nr'], fsm.nr_retries))
    for i in range(len(block.win)):
        block.timeouts[i].cancel()    # in case it is still active
        block.loob[i] = False
    for i in range(len(block.win)):
        if block.debug:
            mutex_prt('    RESEND event, seq nr: {0} and awaited ack is thus: {1}'.\
            format(block.win[i].ev_dc['seq_nr'], fsm.wait))
        j=0
        while block.loob[j]==True and j<block.win_len:
            j = j+1
        #block.win[len(block.win)-1].ev_dc['ack'] = fsm.wait     # waited ack
        block.timeouts[j].start(block.timeout, ev_dc = event.ev_dc)
        block.dic_timeouts[block.win[i].ev_dc['seq_nr']] = j
        block.loob[j] = True
        if block.debug:
            mutex_prt(' Empezo timeout: {0}' . format(j))
        block.write_out(block.win[i])
    return


def push(fsm, ev, block):
    '''Pushes event into buffer.
    '''
    if block.buffer_len == -1 or len(block.ls_buffer) < block.buffer_len:
        block.ls_buffer.append(ev)    # add to end of list
    else:
        raise ExceptionFSM('Buffer length exceeded')
    #block.ls_buffer.append(ev)    # add to end of list
    if block.debug:
        mutex_prt('    FSM PUSH, len buffer: ' + str(len(block.ls_buffer)) + \
            'max buffer: ' + str(block.buffer_len))
    return


def ack_ok(fsm, event, block):
    '''ACK was correct, cancel timer, reset retries.
    '''
    if block.debug:
        mutex_prt('    ENTRE AL ACK_OK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!          =|:)     !!!!!!!!!!!!!')
    block.win.pop(0)
    fsm.nr_retries = 0     #  check nr_retries
    aux = block.dic_timeouts[event.ev_dc['ack']]
    block.timeouts[aux].cancel()
    block.loob[aux] = False
    if block.debug:
        mutex_prt(' Cancelo timeout: {0}' . format(aux))
    fsm.wait = fsm.wait+1
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

def go_back_n_send_fsm(blk):
    '''The ARQ Stop and Wait FSM.

    @param blk: reference to the block to which this FSM is attached.
    '''
    f = FSM ('Idle') # 
    f.debug = False
    f.wait = 1                    #chequear si este estado inicial es escalable (1er seq_nr tiene mas sentido)
    f.nr_retries = 0
#    f.win = [] #entiendo que es block.win , ya que debe ser una variable global

    # transitions
    f.set_default_transition (fn_error, 'Idle')

    #f.add_transition_any ('Idle', None, 'Idle')
    #f.add_transition_any ('WaitAck', None, 'WaitAck')

    # 1
    f.add_transition('DataData', 'Idle', send, 'WaitAck', \
        None)
    # 2
    f.add_transition('CtrlACK', 'WaitAck', ack_ok, 'Idle', \
        ['self.wait == event.ev_dc["ack"]'])  # ack is ack waited for
        #'len(block.win) == 0'])       # no event in win
    # 3
    f.add_transition ('CtrlACK', 'WaitAck', sendfrombuffer, 'WaitAck', \
        ['self.wait == event.ev_dc["ack"]',  # ack is ack waited for
        'len(block.ls_buffer) > 0'])         # event in buffer
    # 4
    f.add_transition ('CtrlACK', 'WaitAck', None, 'WaitAck', \
        ['self.wait != event.ev_dc["ack"]'])  # ack is NOT ack waited for
    # 5 
    f.add_transition ('EventTimer', 'WaitAck', resend, 'WaitAck', \
        ['self.nr_retries <= block.max_retries'])    # retries left
    # 6
    f.add_transition ('EventTimer', 'WaitAck', stop, 'Stop', \
        ['self.nr_retries > block.max_retries'])     # retries exceeded
    # 7
    f.add_transition ('DataData', 'WaitAck', send, 'WaitAck', \
        ['len(block.win) < block.win_len'])  # buffer ok
    # 8
    f.add_transition ('DataData', 'WaitAck', push, 'WaitAck', \
        ['len(block.ls_buffer) < block.buffer_len', 'len(block.win)>=block.win_len'])  # buffer ok
    # 9
    f.add_transition ('DataData', 'WaitAck', stop, 'Stop', \
        ['len(block.ls_buffer) >= block.buffer_len'])  # buffer max exceed

    # 10
    f.add_transition_any ('Stop', stop, 'Stop')
    # 11
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

class go_back_n_send(gwnblock):
    '''An ARQ Stop and wait event sender.

    Receives an event, starts a timeout, writes this event on output port 1, and waits for an ACK to the message sent. On receiving the appropriate ACK, sends next message. On timeout, resends the unacknowledged message. Received messages are buffered in a FIFO list.
    @param blkname: block name.
    @param blkid: block identifier.
    @param ack_nickname: the nickname of the acknowledge event waited for.
    @param max_retries: number of times to resend event if ACK not received.
    @param tout_nickname: the nickname of the timer event waited for.
    @param timeout: the timeout in seconds.
    @param buffer_len: the buffer capacity, i.e. the maximum length of the list; default is 0, which means no limit.
    '''

    def __init__(self, blkname='go_back_n_send',
            ack_nickname='CtrlACK', max_retries=3, timeout=1.0, \
            buffer_len=1000, win_len=500, debug=False):

        # invocation of ancestor constructor
        gwnblock.__init__(self, name=blkname, 
            number_in=1, number_out=1, number_timeouts=win_len)

        self.a = 0
        self.ack_nickname = ack_nickname
        self.max_retries = max_retries
        self.timeout = timeout
        self.buffer_len = buffer_len
        self.win_len = win_len
        self.win = []
        self.dic_timeouts = {}
        self.loob = []

        j = 0   #inicio loob
        for j in range(win_len):
            self.loob.append(False)

        self.ls_buffer = []     # length must be checked in process
        #self.debug = False      # please set from outside for debug print
        self.debug = debug

        self.fsm = go_back_n_send_fsm(self)
        return


    def process_data(self, ev, port, port_nr):
        '''Writes event, waits for ACK, retransmits.

        The received event is passed on to the process function of the FSM; actions in the FSM are provided with the received event and a reference to the present block, so that they can access this block's attributes and functions, in particular the write_out function to send events.
        @param ev: a received Event object.
        '''
        if self.debug:
            dbg_msg = '--- {0}, received ev: {1}, with dic: {2}'. \
                format(self.name(), ev.nickname, ev.ev_dc)
            # only for Data Events:
            #dbg_msg = '--- {0}, received ev: {1}, seq nr: {2}'. \
            #    format(self.blkname, ev.nickname, ev.ev_dc['seq_nr'])
            mutex_prt(dbg_msg)
        # handle event to FSM process functions
        self.fsm.process(ev.nickname, event=ev, block=self)
        return



