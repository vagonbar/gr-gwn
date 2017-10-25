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

'''GWN block with message inputs, message outputs and timers.

The GWN block is an extension of the GNU Radio gr.basic_block; it inherits from gr.basic_block.
'''

#import numpy
from gnuradio import gr

import pmt
import time
import pickle

import threading
lock_obj = threading.Lock()

import sys

# requires adjustment of PYTHONPAHT to libgwn
#   export PYTHONPATH=$PYTHONPATH:<path_to>/gr-gwn/libgwn
from gwnevents import api_events as api_events 


### support classes and functions for gwnblock
#from libgwnblock import GWNTimer, GWNOutPort, GWNInPort, mutex_prt


def pdu_to_msg(pdu, debug=False):
    '''Extracts message from PDU.

    @param pdu: a PDU.
    @param debug: print additional information, default False.
    @return: (metadata, contents).
    '''
    # code taken from chat_blocks in GNURadio tutorial 5
    # collect metadata, convert to Python format:
    meta = pmt.to_python(pmt.car(pdu))
    # collect message, convert to Python format:
    msg = pmt.cdr(pdu)
    # make sure it's a u8vector
    if not pmt.is_u8vector(msg):
        print "[ERROR] Received invalid message type.\n"
        return ('', '')
    # convert to string:
    msg_str = "".join([chr(x) for x in pmt.u8vector_elements(msg)])
    if debug:
        if meta is not None:
            mutex_prt ("[METADATA]: " + meta)
        mutex_prt ("[CONTENTS]: " + msg_str )
    return (meta, msg_str)

def msg_to_pdu(msg, debug=False):
    '''Inserts message into a PDU.

    @param msg: a string to insert as content of the PDU.
    @param debug: print additional information, default False.
    @return: a PDU, a pair (metadata, content) in PMT data types; metadata is None.
    '''
    # create an empty PMT (contains only spaces):
    send_pmt = pmt.make_u8vector(len(msg), ord(' '))
    # copy all characters to the u8vector:
    for i in range(len(msg)):
        pmt.u8vector_set(send_pmt, i, ord(msg[i]))
    if debug:
        mutex_prt('[PMT message]')
        mutex_prt(send_pmt)
    pdu = pmt.cons(pmt.PMT_NIL, send_pmt) 
    return pdu


def mutex_prt(msg):
    '''Mutually exclusive printing.

    @param msg: string to print.
    '''
    lock_obj.acquire()
    print msg
    lock_obj.release()
    return



class GWNPort():
    '''A class for GNU Radio message ports.
    '''
    def __init__(self, block, port, port_nr):
        '''Constructor.

        Attributes and functions relative to a message port attached to a block. Ports need to know the block to which they are attached, and the port in block on whith they receive or send messages.
        @param block: block reference to which this instance is attached.
        @param port: tag of port to which messages will be posted.
        @param port_nr: port number, an index in list of ports in block.
        '''
        self.block = block
        self.port = port
        self.port_nr = port_nr
        return

    def __str__(self):
        return  '  port %s index %d in block id %d' % \
            (self.port, self.port_nr, id(self.block))
        return



class GWNInPort(GWNPort):
    '''Input GWN Port.
    '''

    def handle_msg(self, msg_pmt):
        '''Regenerates event from PMT, passes event to process_data.

        Regenerated event is passed to process function in block to which this message input port is attached. 
        @param msg_pmt: the PMT message received.'''
        msg_ls = pmt.to_python(msg_pmt)[1]
        ev_str = msg_ls[1]
        #print "In port serialized ev", ev_str
        ev = pickle.loads(ev_str)
        self.block.process_data(ev)  # pass to process function in block
        return



class GWNOutPort(GWNPort):
    '''Output GWN Port.
    '''

    def post_message(self, ev):
        '''Converts Event to string, makes PMT message, posts on block port.
        
        The PMT message is sent through a message port of the block to which this output port is attached.
        @param ev: an Event object. 
        '''
        ev_str = pickle.dumps(ev)
        #print "Out port serialized ev", ev_str
        pmt_msg = pmt.cons(pmt.PMT_NIL, 
            pmt.pmt_to_python.python_to_pmt(ev_str))
        pmt_port = pmt.intern(self.port)
        self.block.message_port_pub(pmt_port, pmt.cons(pmt.PMT_NIL, 
            pmt_msg))
        #self.block.to_basic_block()._post(pmt_port, pmt_msg)
        return



class GWNTimeout(GWNPort):
    '''A timer class to implement timeouts inside GWN blocks.

    Objects of this class can be attached to a gwnblock to act as internal timeouts. An object of this class sends a messages to the block to which it is attached once the specified time has elapsed. A timeout object can be interrupted before its action starts, i.e. before it sends its message.
    '''

    def __init__(self, block, port, port_nr, timeout=1.0, ev_dc={}):
        '''Constructor.

        @param block: block reference to which this instance is attached.
        @param port: tag of port to which messages will be posted.
        @param port_nr: port number, an index in list of ports in block.
        @param timeout: timeout in seconds.
        @param ev_dc: additional information for event to send on timeout.
        '''
        GWNPort.__init__(self, block, port, port_nr)

        self.block = block
        self.port = port
        self.port_nr = port_nr
        self.timeout = timeout
        self.ev_dc = dict()
        self.ev_dc.update(ev_dc)

        self.nickname = 'EventTimer'    # default Event type to generate
        self.debug = False
        self.timer = None

        if self.debug:
            mutex_prt ("    GWNTimeout BUILT, timeout=" + str(self.timeout))
        return


    def start(self, timeout=None, nickname='EventTimer', ev_dc={}):
        '''Starts timer, lives until timeout.

        @param timeout: a timeout value in seconds.
	@param nickname: Event nickname to generate.
        @param ev_dc: additional information for event to send.
        '''
	self.nickname = nickname
        if timeout:
            self.timeout = timeout
        self.ev_dc.update(ev_dc)    # adds or modifies existing ev_dc
        self.timer = threading.Timer(self.timeout, self.post_message)
        self.timer.start()
        if self.debug:
            msg_dbg = '    Block '+self.block.name() + ': ' + self.port + '\n'
            msg_dbg += '    GWNTimeout STARTED, timeout=' + \
                str(self.timeout) + ', event ' + self.nickname
            msg_dbg = msg_dbg + '\n    ev_dc: ' + str(self.ev_dc) + '\n'
            mutex_prt(msg_dbg)
        return


    def cancel(self):
        '''Stops timer if action has not started.'''
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            msg_dbg = '    GWNTimeout CANCEL done'
        else:
            msg_dbg = '    GWNTimeout timer thread does not exist.'
        if self.debug:
            mutex_prt(msg_dbg)
        self.timer = None    # last reference, garbage collector will act
        # del(self.timer)    # not necessary if self.timeout set to None
        return


    def post_message(self):
        '''Creates Timer Event and posts it on block port.'''
        evtimeout = api_events.mkevent(self.nickname)   # create timer event
        evtimeout.ev_dc = self.ev_dc     # assign add info to event
        # serialize, prepare and send event through block timer port
        ev_str = pickle.dumps(evtimeout)
        msg_ls = [self.port, self.port_nr, ev_str]
        pmt_msg = pmt.cons(pmt.PMT_NIL, 
            pmt.pmt_to_python.python_to_pmt(msg_ls) )
        pmt_port = pmt.intern(self.port)
        self.block.to_basic_block()._post(pmt_port, pmt.cons(pmt.PMT_NIL, 
            pmt_msg) )
        #self.block.to_basic_block()._post(pmt_port, pmt_msg)
        if self.debug:
            msg_dbg = '    GWN Timeout TIMEOUT REACHED, generated EVENT:\n'
            msg_dbg += evtimeout.__str__()
            mutex_prt(msg_dbg)
        # del(self.timer)      # not necessary if self.timeout set to None
        self.timer = None    # last reference, garbage collector will act
        return


    def handle_msg(self, msg_pmt):
        '''Timer message handler, regenerates event, passes to process_data.

        @param msg_pmt: the received PMT message.
        '''
        msg_ls = pmt.to_python(msg_pmt)[1]
        port, port_nr, ev_str = msg_ls[1]
        ev = pickle.loads(ev_str)
        self.block.process_data(ev)    # pass to process function
        return


    def __str__(self):
        return  '   GWNTimeout %s index %d in block id %d' % \
            (self.port, self.port_nr, id(self.block))
        return 



class GWNTimer(GWNPort, threading.Thread):
    '''A timer class to add inside timers to GWN blocks.

    Objects of this class can attached to a gwnblock to act as internal timers. An object of this class sends messages to the block to which it is attached, at regular intervals. It sends a message for an specified number of times, then a final second message to indicate the first series has exhausted.
    '''

    def __init__(self, block, port, port_nr, interrupt=True, interval=1.0, \
            retry=1, ev_dc_1={}, ev_dc_2={}):
        '''Constructor.

        @param block: block reference to which this instance is attached.
        @param port: tag of port to which messages will be posted.
        @param port_nr: port number, an index in list of ports in block.
        @param interrupt: if True, timer is interrupted, i.e. does not send any messages.
        @param interval: time between messages to send.
        @param retry: how many times to send message 1, then send message 2 once.
        @param ev_dc_1: additional information for event to send at regular intervals for retry times (as message 1).
        @param ev_dc_2: additional information for event to send when retries have exhausted (as message 2).
        '''
        GWNPort.__init__(self, block, port, port_nr)
        threading.Thread.__init__(self)

        self.block = block
        self.port = port
        self.port_nr = port_nr
        self.interrupt = interrupt
        self.interval = float(interval)
        self.retry = retry
        self.ev_dc_1 = dict()
        self.ev_dc_1.update(ev_dc_1)
        self.ev_dc_2 = dict()
        self.ev_dc_2.update(ev_dc_2)

        self.nickname = 'EventTimer'    # the event to generate
        self.counter = 0
        self.exit_flag = False  # if True, ends timer
        self.debug = False      # please set from outside for debug print
        if self.debug:
            mutex_prt ("    GWNTimer built, retry:" + str(self.retry))
        return


    def set_interrupt(self, interrupt):
        '''Interrupts generation of timer messages.

        @param interrupt: if True, timer is interrupted, i.e. does not send any messages.
        '''
        #lock_obj.acquire()
        self.interrupt = interrupt
        #lock_obj.release()
        if self.debug:
            msg_dbg = '    GWNTimer, interrupt set to ' + str(interrupt)
            mutex_prt(msg_dbg)


    def stop(self):
        '''Stops timer thread... or intends to.

        There is no clear way to stop a thread in Python. Here, interrupt is set to True; no messages will be sent, but thread remains alive.'''
        if self.debug:
            msg_dbg = '    GWNTimer STOP, stopping timer %d in block id %d' % \
               (self.port_nr, id(self.block))
            mutex_prt(msg_dbg)
        self.exit_flag = True   # no clear action on this flag
        self.interrupt = True
        return


    def reset(self, retry=None):
        '''Resets counter to 0, starts timing again.

        Sets interrupt to False and starts timing again, from 0 count.
        @param retry: new retry value, optional; default None to keep former value.
        '''
        if retry:
            self.retry = retry
        self.counter = 0
        self.set_interrupt(False)
        if self.debug:
            msg_dbg = '    GWNTimer RESET, counter=0, '
            if retry and self.debug:
                msg_dbg += 'new retry value ' +  str(retry)
            elif self.debug:
                msg_dbg += 'retry value left in ' + str(self.retry)
            mutex_prt(msg_dbg)
        return


    def run(self):
        '''Runs timer thread, uses time.sleep.'''
        if not self.exit_flag:               # timer not stopped
            self.counter = 0
            ## post timer messages
            while self.counter < self.retry and not self.exit_flag: 
                # sends messages until count reaches number of retries
                self.counter = self.counter + 1
                if self.debug:
                    mutex_prt("    GWNTimer, counter" + str(self.counter))
                if not self.interrupt:
                    self.post_message(final=False)   # regular messages
                else:            # interrupted, does not send but counts
                    pass         # no message sent
                time.sleep(self.interval)   # waits interval
            ## post final message
            if not self.interrupt and not self.exit_flag:
                # test repetition required, things may have changed!
                self.post_message(final=True)        # final message
                self.interrupt = True
        #else:
        #    raise Exception    # seems only way to stop thread
        return

    
    def post_message(self, final):
        '''Creates Timer Event and posts it on block timer port.

        @param final: if False, send message with ev_dc_1; if True, send last message with ev_dc_2.
        '''
        evtimer = api_events.mkevent(self.nickname)   # create timer event
        if final:
            evtimer.ev_dc = self.ev_dc_2
        else:
            evtimer.ev_dc = self.ev_dc_1
        evtimer.ev_dc['port'] = self.port
        # serialize, prepare and send event through block timer port
        ev_str = pickle.dumps(evtimer)
        msg_ls = [self.port, self.port_nr, ev_str]
        pmt_msg = pmt.cons(pmt.PMT_NIL, 
            pmt.pmt_to_python.python_to_pmt(msg_ls) )
        pmt_port = pmt.intern(self.port)
        self.block.to_basic_block()._post(pmt_port, pmt.cons(pmt.PMT_NIL, 
            pmt_msg) )
        return


    def handle_msg(self, msg_pmt):
        '''Timer message handler, regenerates event, passes to process_data.

        @param msg_pmt: the received PMT message.'''
        msg_ls = pmt.to_python(msg_pmt)[1]
        port, port_nr, ev_str = msg_ls[1]
        ev = pickle.loads(ev_str)
        self.block.process_data(ev)     # pass to block process function
        return


    def __str__(self):
        return  'GWNTimer %s index %d in block id %d' % \
            (self.port, self.port_nr, id(self.block))
        return 



class gwnblock(gr.basic_block):
    '''The GWN basic block, from which all GWN blocks inherit.

    '''
    def __init__(self, name='', number_in=0, number_out=0, \
            number_timers=0, number_timeouts=0):
        '''The GWN basic block constructor.

        The GWN basic block implements facilites used by all GWN blocks. A descendent of this class may call this constructor to fix the number of ports, timers and timeouts.
        @param name: a name for this block.
        @param number_in: number of input ports.
        @param number_out: number of output ports.
        @param number_timers: number of internal timers.
        @param number_timeouts: number of internal timeouts.
        '''
        # invocation of GR basic block constructor
        gr.basic_block.__init__(self,
            name=name, in_sig=[], out_sig=[])  

        self.ports_in = []
        self.ports_out = []
        self.timeouts = []
        self.timers = []
        self.finished = False
        self.debug = False

        self.set_timeout_size(number_timeouts)  # timeout input ports
        self.set_timer_size(number_timers)      # timer input ports
        self.set_in_size(number_in)             # message input ports
        self.set_out_size(number_out)           # message output ports

        return


    ### GNU Radio functions for gr.basic_block
    # they must be here for compatibility, even if no stream is present

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        output_items[0][:] = input_items[0]
        consume(0, len(input_items[0]))
        #self.consume_each(len(input_items[0]))
        return len(output_items[0])

    ###


    ### input and output message functions

    def set_in_size(self, number_in):
        '''Creates a list of input message connections.

        @param number_in: the number of input message connections.
        '''
        for i in xrange(0, number_in):
            in_port = 'in' + str(i)
            myport = GWNInPort(self, in_port, i)
            self.ports_in.append(myport)
            if self.debug:
                mutex_prt(myport)
            pmt_in_port = pmt.intern(in_port)
            self.message_port_register_in(pmt_in_port)
            self.set_msg_handler(pmt_in_port, myport.handle_msg)
        return


    def set_out_size(self, number_out):
        '''Creates a list of output message connections.

        @param number_out: the number of output message connections.
        '''
        for i in xrange(0, number_out):
            out_port = 'out' + str(i)
            myport = GWNOutPort(self, out_port, i)
            self.ports_out.append(myport)
            if self.debug:
                mutex_prt(myport)
            pmt_out_port = pmt.intern(out_port)
            self.message_port_register_out(pmt_out_port)
        return


    ### timeout functions

    def set_timeout_size(self, number_timeouts):
        '''Creates a list of timeout objects, assigns to block.

        Creates a list of timeout objects with default values.
        @param number_timeouts: the number of timeouts to create.
        '''
        for i in xrange(0, number_timeouts):
            timeout_port = 'timeout' + str(i)
            mytimeout = GWNTimeout(self, timeout_port, i)
            self.timeouts.append(mytimeout)
            if self.debug:
                mutex_prt(mytimeout)           # for debug
            pmt_timeout_port = pmt.intern(timeout_port)
            self.message_port_register_in(pmt_timeout_port)
            self.set_msg_handler(pmt_timeout_port, mytimeout.handle_msg)
        return


    ### timer functions

    def set_timer_size(self, number_timers):
        '''Creates a list of inside timer objects, assigns to block.

        Creates a list of inside timer objects with default values; timer characteristics can be set later with function set_timer().
        @param number_timers: the number of timers to create.
        '''
        for i in xrange(0, number_timers):
            timer_port = 'timer' + str(i)
            mytimer = GWNTimer(self, timer_port, i)
            self.timers.append(mytimer)
            if self.debug:
                mutex_prt(mytimer)
            pmt_timer_port = pmt.intern(timer_port)
            self.message_port_register_in(pmt_timer_port)
            self.set_msg_handler(pmt_timer_port, mytimer.handle_msg)
            #mytimer.start()  # done from outside
        return


    def set_timer(self, index, interrupt=True, interval=1, retry=1, \
            ev_dc_1={}, ev_dc_2={}):
        '''Sets timer values.

        @param index: the timer index position.
        @param interrupt: if True interrupts timer event generation until set to False.
        @param interval: the time between two successive timer events.
        @param retry: the number of events to be generated; once this number is reached, the timer is interrupted until interrupt is set to False.
        @param ev_dc_1: additional information for event to send at regular intervals for retry times. Adds to existing dictionary.
        @param ev_dc_2: additional information for event to send when retries have exhausted. Adds to existing dictionary.
        ''' 
        mytimer = self.timers[index]
        mytimer.interval = float(interval)
        mytimer.retry = retry
        mytimer.ev_dc_1.update(ev_dc_1)
        mytimer.ev_dc_2.update(ev_dc_2)
        mytimer.interrupt = interrupt
        return


    def start_timers(self):
        '''Starts timers attached to this block.'''
        for timer in self.timers:
            timer.start()
        for timer in self.timers:
            #timer.join()     # does not finish...
            pass
        return

        
    def stop_timers(self):
        '''Stops timers attached to this block.'''
        for timer in self.timers:
            timer.stop()
        for timeout in self.timeouts:
            timeout.cancel()


    def write_out(self, ev, port_nr=None):
        '''Sends an event converted to PMT on an output port.

        @param ev: an Event object.
        @param port_nr: the output por number, an index of the output ports list. If not given, write out on all ports.
        '''
        if port_nr is None:        # output message in all ports
            for outport in self.ports_out:
                lock_obj.acquire()
                outport.post_message(ev)
                lock_obj.release()                
        else:
            lock_obj.acquire()
            self.ports_out[port_nr].post_message(ev)
            lock_obj.release()
        return


    def handle_msg(self):
        pass 


    def process_data(self, ev):
        ''' Receives Event, processes, produces output event(s).
        
        To be overwritten by descendent block.
        @param ev: the event received, to process.
        '''
        if self.debug:
            mutex_prt(ev)
        else:
            pass
        return
        

    # other functiones
    def __str__(self):
        ss = 'gwnblock id {0}, name {4}, ports_in {1}, ports_out {2}, timers {3}'. \
            format( id(self), len(self.ports_in), 
                len(self.ports_out), len(self.timers), self.name() )
        return ss



if __name__ == "__main__":

    print "Run tests qa_timer_source.py, qa_event_sink.py"
