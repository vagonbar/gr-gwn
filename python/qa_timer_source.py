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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from timer_source import timer_source
from event_sink import event_sink
import time
from gwnblock import mutex_prt



class qa_timer_source (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_with_message_debug(self):
        '''Timer Source to Message Debug.
        '''
        ### blocks Timer Source --> Message Debug
        blk_snd = timer_source(retry=2, debug=True)
        blk_dbg = blocks.message_debug()
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_dbg, 'print')
        #self.tb.run()  # for flowgraphs that will stop on its own!
        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()

        secs = 5
        print '--- sender, timer started, waiting %d seconds\n' % (secs,)
        time.sleep(secs)
        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return

    def test_interrupt(self):
        '''Timer Source to Event Sink with interruption.
        '''
        blk_snd = timer_source(retry=10, interval=1.0)
        blk_snd.timers[0].debug = True     # print debug on timer
        blk_snk = event_sink()
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_snk, blk_snk.ports_in[0].port)
        #self.tb.run()  # for flowgraphs that will stop on its own!
        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()

        time.sleep(4)
        print '\n--- set interrupt to True, sleep 4 secs'
        blk_snd.timers[0].set_interrupt(True)
        time.sleep(4)
        print '\n--- set interrupt to False, sleep 6 secs'
        blk_snd.timers[0].set_interrupt(False)
        time.sleep(6)
        print '\n--- timer reset, retry 3, sleep 7 secs'
        blk_snd.timers[0].reset(retry=3)      # reset timer, adjust retry
        time.sleep(7)

        print '\n--- stop timers'    ### blocks in next statement!!!
        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        time.sleep(2)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return

if __name__ == '__main__':
    gr_unittest.run(qa_timer_source, "qa_timer_source.xml")
