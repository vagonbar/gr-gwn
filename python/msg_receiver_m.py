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

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # block specific, for this block
import time                             # block specific, for this block



class msg_receiver_m(gwnblock):
    '''A test block, receives messages; one input, no outputs, no timers.
    '''
    def __init__(self, blkname, blkid):
        gwnblock.__init__(self, blkid, blkname, 
            number_in=1, number_out=0, number_timers=0)
        return


    def process_data(self, ev):
        '''Receives events, prints.
        '''
        ss = '  --- blkname {0}, blkid {1}, event:'.\
            format(self.blkname, self.blkid)
        ss = ss +   ' ' + ev.nickname
        #ss = ss + '\n  ' + ev.__str__() + '\n'
        mutex_prt(ss)
        return



###
### Tests
###

def test_1():
    '''Tests timers, block with timers sends to receive block.
    '''
    tb = gr.top_block()
    blk_snd = msg_sender_m('blk001', 'SendTimerEvs')
    blk_rec1 = msg_receiver_m('blk002', 'Receiver ONE')
    blk_rec2 = msg_receiver_m('blk003', 'Receiver TWO')

    tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, blk_rec1, blk_rec1.ports_in[0].port)
    tb.msg_connect(blk_snd, blk_snd.ports_out[1].port, blk_rec2, blk_rec2.ports_in[0].port)

    tb.start()
    #print tb.dump()
    print tb.msg_edge_list()

    # set timers, may be done inside block
    blk_snd.set_timer(0, interrupt=False, interval=2, retry=3, 
        nickname1='TimerTOR1', nickname2='TimerTOR2')
    blk_snd.set_timer(1, interrupt=False, interval=1, retry=8, 
        nickname1='TimerTOC', nickname2='TimerTOH')

    print '--- sender, timers started\n'
    #blk_snd.start_timers()
    time.sleep(12)

    print '\n--- sender, timer 0 reset after retry exhausted\n'
    blk_snd.timers[0].interrupt=False   # reset after retry exhausted
    time.sleep(10)

    blk_snd.stop_timers()
    print '\n--- sender, timers stopped'

    tb.stop()
    tb.wait()



if __name__ == "__main__":

    import time
    from msg_sender_m import msg_sender_m
    test_1()


