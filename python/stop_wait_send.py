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

'''An ARQ Stop and Wait sender.
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
    fsm.ev_sent = event       # store for eventual resend
    fsm.ev_sent.payload += " FSM Waited ACK: " + fsm.wait
    block.timeouts[0].start(block.timeout, block.tout_nickname)
    block.write_out(fsm.ev_sent)
    return 


def sendfrombuffer(fsm, event, block):
    '''Sends event from buffer, first in list.
    '''
    if len(block.ls_buffer) > 0:
        event = block.ls_buffer.pop(0)   # get first from list
    else:
        #mutex_prt('FSM send ERROR: no event to send')
        return
    fsm.ev_sent = event       # store for eventual resend
    fsm.ev_sent.payload += " FSM Waited ACK: " + fsm.wait
    block.timeouts[0].start(block.timeout, block.tout_nickname)
    block.write_out(fsm.ev_sent)
    return 


def resend(fsm, event, block):
    '''Resends event not acknowledged.
    '''
    #fsm.print_state(show=['transition', 'action'])
    fsm.nr_retries = fsm.nr_retries + 1
    if fsm.debug:
        mutex_prt('    FSM RESEND, retries: ' + str(fsm.nr_retries))
    block.timeouts[0].cancel()    # in case it is still active
    block.timeouts[0].start(block.timeout, block.tout_nickname)
    block.write_out(fsm.ev_sent)
    return


def push(fsm, ev, block):
    '''Pushes event into buffer.
    '''
    if block.buffer_len == -1 or len(block.ls_buffer) < block.buffer_len:
        block.ls_buffer.append(ev)    # add to end of list
    else:
        raise ExceptionFSM('Buffer length exceeded')
    block.ls_buffer.append(ev)    # add to end of list
    if block.debug:
        mutex_prt('    FSM PUSH, len buffer: ' + str(len(block.ls_buffer)) + \
            'max buffer: ' + str(block.buffer_len))
    return


def ack_ok(fsm, ev, block):
    '''ACK is correct, cancel timer, reset retries.
    '''
    fsm.nr_retries = 0
    block.timeouts[0].cancel()
    if fsm.wait == 'ack1':
        fsm.wait = 'ack0'
    else:
        fsm.wait = 'ack1'
    return


def stop(fsm, ev, block):
    '''Retries in sending of buffer exceeded, stop sending.
    '''
    if fsm.debug:
        mutex_prt('    FSM, send retries or buffer exceeded')
        mutex_prt('      max buffer length: ' + str(block.buffer_len) + \
            ', buffer length: ' + str(len(block.ls_buffer)))
        mutex_prt('      max retries: ' + str(block.retries) + \
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

def stop_wait_send_fsm(blk):
    '''The ARQ Stop and Wait FSM.

    @param blk: reference to the block to which this FSM is attached.
    '''
    f = FSM ('Idle') # 
    f.debug = False
    f.wait = 'ack0'
    f.nr_retries = 0

    # transitions
    f.set_default_transition (fn_error, 'Idle')

    #f.add_transition_any ('Idle', None, 'Idle')
    #f.add_transition_any ('WaitAck', None, 'WaitAck')

    f.add_transition('DataData', 'Idle', send, 'WaitAck', \
        None)

    f.add_transition('CtrlACK', 'WaitAck', ack_ok, 'Idle', \
        ['self.wait in event.payload',  # ack is ack waited for
        'len(block.ls_buffer) == 0'] )  # no event in buffer

    f.add_transition ('CtrlACK', 'WaitAck', sendfrombuffer, 'WaitAck', \
        ['self.wait in event.payload',  # ack is ack waited for
        'len(block.ls_buffer) > 0'])    # event in buffer

    f.add_transition ('CtrlACK', 'WaitAck', None, 'WaitAck', \
        ['self.wait not in event.payload']) # ack is NOT ack waited for
 
    f.add_transition ('TimerACKTout', 'WaitAck', resend, 'WaitAck', \
        ['self.nr_retries <= block.retries'])    # retries left

    f.add_transition ('TimerACKTout', 'WaitAck', stop, 'Stop', \
        ['self.nr_retries > block.retries'])     # retries exceeded

    f.add_transition ('DataData', 'WaitAck', push, 'WaitAck', \
        ['len(block.ls_buffer) < block.buffer_len'])  # buffer ok

    f.add_transition ('DataData', 'WaitAck', stop, 'Stop', \
        ['len(block.ls_buffer) >= block.buffer_len'])  # buffer max exceed

    f.add_transition_any ('Stop', stop, 'Stop')
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

class stop_wait_send(gwnblock):
    '''An ARQ Stop and wait event sender.

    Receives an event, starts a timeout, writes this event on output port 1, and waits for an ACK to the message sent. On receiving the appropriate ACK, sends next message. On timeout, resends the unacknowledged message. Received messages are buffered in a FIFO list.
    @param blkname: block name.
    @param blkid: block identifier.
    @param ack_nickname: the nickname of the acknowledge event waited for.
    @param retries: number of times to resend event if ACK not received.
    @param tout_nickname: the nickname of the timer event waited for.
    @param timeout: the timeout in seconds.
    @param buffer_len: the buffer capacity, i.e. the maximum length of the list; default is 0, which means no limit.
    '''

    def __init__(self, blkname='stop_wait_send', blkid='id_stop_wait_send',
            ack_nickname='CtrlACK', retries=3, \
            tout_nickname='TimerACKTout', timeout=1.0, \
            buffer_len=1000):

        # invocation of ancestor constructor
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=1, number_timeouts=1)

        self.blkname = blkname
        self.blkid = blkid
        self.ack_nickname = ack_nickname
        self.retries = retries
        self.tout_nickname = tout_nickname
        self.timeout = timeout
        self.buffer_len = buffer_len
        self.ls_buffer = []     # length must be checked in process
        self.debug = False      # please set from outside for debug print

        self.fsm = stop_wait_send_fsm(self)
        return


    def process_data(self, ev):
        '''Writes event, waits for ACK, retransmits.

        The received event is passed on to the process function of the FSM; actions in the FSM are provided with the received event and a reference to the present block, so that they can access this block's attributes and functions, in particular the write_out function to send events.
        @param ev: a received Event object.
        '''
        if self.debug:
            dbg_msg = '--- {0}, received ev: {1}, payload: {2}'. \
                format(self.blkname, ev.nickname, ev.payload)
            mutex_prt(dbg_msg)
        # handle event to FSM process functions
        self.fsm.process(ev.nickname, event=ev, block=self)
        return

