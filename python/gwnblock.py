#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
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

'''GWN block with message inputs, message outputs and timers; inherits from gr.basic_block.
'''

#import numpy
from gnuradio import gr

import pmt
import time
import pickle



import threading
lock_obj = threading.Lock()


import sys

# by now, requires adjustment of PYTHONPAHT to work!
from gwnevents import api_events as api_events 



### support classes and functions for gwnblock
#from libgwnblock import GWNTimer, GWNOutPort, GWNInPort, mutex_prt

def mutex_prt(msg):
    '''Mutually exclusive printing.
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

        Attritubes and functions relative to a message port attached to a block.
        @param block: block to which this instance is attached.
        @param port: port in block to which messages will be posted.
        @param port_nr: port number, an index in list of ports in block.
        '''
        self.block = block
        self.port = port
        self.port_nr = port_nr
        #mutex_prt ("GWNPort built, " + port_nr)
        return

    def __str__(self):
        return  '  port %s index %d in block %s' % \
            (self.port, self.port_nr, self.block.blkname)
        return


class GWNInPort(GWNPort):
    '''Input GWN Port.
    '''

    def handle_msg(self, msg_pmt):
        '''Regenerates event from PMT, passes event to process_data.'''
        msg_ls = pmt.to_python(msg_pmt)[1]
        blkname, blkid, port, port_nr, ev_str = msg_ls[-1]
        ev = pickle.loads(ev_str)
        #ss = '  --- handle_msg, blkname {0}, blkid {1}, port {2}, port nr {3}'.\
        #    format(msg_ls[0], msg_ls[1], msg_ls[2], msg_ls[3])
        #ss = ss + '\n  ' + ev.__str__() + '\n'
        #mutex_prt(ss)
        #lock_obj.acquire()  # BLOCKS! # mutually exclusive event handling
        self.block.process_data(ev)    # handle event to process function
        #lock_obj.release()            # release lock
        return



class GWNOutPort(GWNPort):
    '''Output GWN Port.
    '''

    def post_message(self, ev):
        '''Converts Event to string, makes PMT message, posts on block port.
        
        Message is a list which contains the serialized (string) Event, block name, block id, and block port on which message is posted'''
        ev_str = pickle.dumps(ev)
        msg_ls = [self.block.blkname, self.block.blkid, self.port, 
            self.port_nr, ev_str]
        pmt_msg = pmt.cons(pmt.PMT_NIL, 
            pmt.pmt_to_python.python_to_pmt(msg_ls) )
        pmt_port = pmt.intern(self.port)
        self.block.message_port_pub(pmt_port, pmt.cons(pmt.PMT_NIL, 
            pmt_msg))
#        self.block.to_basic_block()._post(pmt_port, pmt_msg)
        return



class GWNTimer(GWNPort, threading.Thread):
    '''A timer class to add inside timers to GWN blocks.

    Objects of this class can attached to a gwnblock to act as internal timers. An object of this class sends messages to the block to which it is attached, at regular intervals. A timer object sends a message for an specified number of times, then a final second message to indicate the first series has exhausted.
    '''
    def __init__(self, block, port, port_nr, interrupt=True, interval=1, \
            retry=1, nickname1='TimerTOR1', nickname2='TimerTOR2', add_info=None):
        '''Constructor.

        @param interrupt: if True, timer is interrupted, i.e. does not send any messages.
        @param interval: time between messages to send.
        @param retry: how many times to send message 1, then send message 2 once.
        @param nickname1: message to send at regular intervals for retry times.
        @param nickname2: message to send when retries have exhausted.
        @param add_info: additional information for this timer.
        '''
        GWNPort.__init__(self, block, port, port_nr)
        threading.Thread.__init__(self)

        #self.block = block
        #self.port = port
        #self.port_nr = port_nr
        self.interrupt = interrupt
        self.interval = interval
        self.retry = retry
        self.nickname1 = nickname1
        self.nickname2 = nickname2
        self.add_info = add_info

        self.counter = 0
        self.exit_flag = False   # ir True, ends timer
        #mutex_prt ("Timer built, retry:" + str(self.retry))
        return


    def set_interrupt(self, interrupt):
        '''Interrupts generation of timer messages.'''
        self.interrupt = interrupt


    def stop(self):
        '''Stops timer thread.'''
        #ss = '  ...stopping timer %d in block %s' % 
        #    (self.port_nr, self.block.blkname)
        # mutex_prt(ss)
        self.exit_flag = True
        return


    def run(self):
        '''Runs timer thread.'''
        while not self.exit_flag:               # timer not stopped
            #mutex_prt("In timer, counter" + str(self.counter))
            if not self.interrupt:              # timer not interrupted
                self.counter = 0
                while self.counter <= self.retry and not self.exit_flag: 
                    # sends messages until count reaches number of retries
                    self.counter = self.counter + 1
                    if not self.interrupt:
                        # test repetition required, things may have changed!
                        self.post_message(self.nickname1)
                    else:
                        break
                    time.sleep(self.interval)   # waits interval
                if not self.interrupt and not self.exit_flag:
                    # test repetition required, things may have changed!
                    if self.nickname2 is not None:
                        self.post_message(self.nickname2)
                    self.interrupt = True
            #else:
            #    time.sleep(0.01)
        return

    ### handle and post message functions
    
    def post_message(self, nickname):
        '''Posts timer event and timer metadata on block port.'''
        #ss = 'in post message, port:', self.port, ', blkid:', self.block.blkid,
        #    ', time:', time.time()
        #mutex_prt(ss)
        evtimer = api_events.mkevent(nickname)   # create timer event
        ev_str = pickle.dumps(evtimer)
        msg_ls = [self.block.blkname, self.block.blkid, self.port, 
            self.port_nr, ev_str]
        pmt_msg = pmt.cons(pmt.PMT_NIL, 
            pmt.pmt_to_python.python_to_pmt(msg_ls) )
        pmt_port = pmt.intern(self.port)
        self.block.to_basic_block()._post(pmt_port, pmt_msg)
        return


    def handle_msg(self, msg_pmt):
        '''Timer message handler, regenerates event, passes to process_data.'''
        msg_ls = pmt.to_python(msg_pmt)[1]
        ev = pickle.loads(msg_ls[-1])
        #ss = '  --- handle_msg, blkname {0}, blkid {1}, port {2}, port nr {3}'.\
        #    format(msg_ls[0], msg_ls[1], msg_ls[2], msg_ls[3])
        #ss = ss + '\n  ' + ev.__str__() + '\n'
        #mutex_prt(ss)
        #lock_obj.acquire()  # BLOCKS!  # mutually exclusive event handling
        self.block.process_data(ev)   # handle event to process function
        #lock_obj.release()            # release lock
        return


    def __str__(self):
        return  '  timer %s index %d in block %s' % \
            (self.port, self.port_nr, self.block.blkname)
        return 

###



class gwnblock(gr.basic_block):
    '''The GWN basic block.
    '''
    def __init__(self, blkname, blkid, number_in=0, number_out=0, \
            number_timers=0):
        gr.basic_block.__init__(self,
            name='gwnblock',
            in_sig=[],   #[<+numpy.float+>],
            out_sig=[])  #[<+numpy.float+>])

        self.blkname = blkname
        self.blkid = blkid
        self.ports_in = []
        self.ports_out = []
        self.timers = []
        self.finished = False

        self.set_timer_size(number_timers)  # timer input ports
        self.set_in_size(number_in)         # message input ports
        self.set_out_size(number_out)       # message output ports

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
            mutex_prt(myport)           # for debug
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
            mutex_prt(myport)           # for debug
            pmt_out_port = pmt.intern(out_port)
            self.message_port_register_out(pmt_out_port)
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
            mutex_prt(mytimer)           # for debug
            pmt_timer_port = pmt.intern(timer_port)
            self.message_port_register_in(pmt_timer_port)
            self.set_msg_handler(pmt_timer_port, mytimer.handle_msg)
            #mytimer.start()  # done from outside
        return


    def set_timer(self, index, interrupt=True, interval=1, retry=1, \
            nickname1="nick1", nickname2="nick2", add_info=None):
        '''Sets timer values.

        @param index: the timer index position.
        @param interrupt: if True interrupts timer event generation until set to False.
        @param interval: the time between two successive timer events.
        @param retry: the number of events to be generated; once this number is reached, the timer is interrupted until interrupt is set to False.
        @param nickname1: the nickname of the event to be generated after each interval.
        @param nickname2: the nickname of the event to be generated once reached the retry number.
        @param add_info: additional info.
        ''' 
        mytimer = self.timers[index]
        mytimer.interval = interval
        mytimer.retry = retry
        mytimer.nickname1 = nickname1
        mytimer.nickname2 = nickname2 
        mytimer.add_info = add_info
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


    def write_out(self, ev, port_nr=None):
        '''Sends an event converted to PMT on an output port.

        @param ev: an Event object.
        @param port_nr: the output por number, an index of the output ports list. If not given, write out on all ports.
        '''
        #'''ev_str = pickle.dumps(ev)
        #msg_ls = [self.block.blkname, self.block.blkid, self.port_out, 
        #    self.port_nr, ev_str]
        #pmt_msg = pmt.cons(pmt.PMT_NIL, 
        #    pmt.pmt_to_python.python_to_pmt(msg_ls) )'''
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
        '''To be overwritten by descendent block.
        
        Receives Event object, processes, produces event(s).
        '''
        pass #mutex_prt(ev)
        return
        

    # other functiones
    def __str__(self):
        ss = 'gwnblock {0}, id: {1}; {2} ports_in, {3} ports_out, {4} timers'. \
            format(self.blkname, self.blkid, len(self.ports_in), 
                len(self.ports_out), len(self.timers) )
        return ss





if __name__ == "__main__":
    print "Run test on msg_receiver_.py"
    print "   python msg_receiver_.py"

"""

    ### test timers and messages

    tb = gr.top_block()
    blk = gwnblock('blk001', 'FirsBlck', number_timers=2, number_in=1,
        number_out=1)

    #tb.nicknameconnect(blk, 'nicknameout', blk, 'timer0')
    tb.msg_connect(blk, blk.ports_out[0], blk, blk.ports_in[0])
    
    tb.start()

    blk.set_timer(0, interrupt=False, interval=2, retry=3, 
        nickname1='tic-0', nickname2='TAC-0')
    blk.set_timer(1, interrupt=False, interval=1, retry=8, 
        nickname1='tic-1', nickname2='TAC-1')

    print '  --- timers started'
    blk.start_timers()

    #blk.send(0, 5)
    time.sleep(12)
    #msg_pmt = pmt.intern('  ...message from outside')
    #nicknamevec = pmt.cons(pmt.PMT_NIL, msg_pmt)
    #blk.to_basic_block()._post(pmt.intern('timer0'), nicknamevec)
    blk.timers[0].interrupt=False   # reset after retry exhausted
    time.sleep(9)

    #blk.timers[0].stop()
    #blk.timers[1].stop()
    blk.stop_timers()
    print '  --- timers stopped'

    tb.stop()
    tb.wait()
"""
