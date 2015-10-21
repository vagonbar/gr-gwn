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
from stop_wait_ack import stop_wait_ack

from event_sink import event_sink
from data_source import data_source
import time
from gwnblock import mutex_prt


class qa_stop_wait_ack (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_stop_wait_ack (self):

        '''Event and Ack to different Event Sink blocks.
        '''
        ### block Data Source --> Stop and Wait ACK
        blk_snd = data_source('DataData', 'blk001', retry=3, interval=1.0)
        blk_ack = stop_wait_ack('StopAndWaitACK', 'blk002')
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_ack, blk_ack.ports_in[0].port)

        ### block Stop and Wait ACK --> Event Sink 1, Event Sink 2
        blk_snk_ev = event_sink()
        blk_snk_ack = event_sink()
        #blk_snk.debug = True
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[0].port, 
                            blk_snk_ev, blk_snk_ev.ports_in[0].port)
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[1].port, 
                            blk_snk_ack, blk_snk_ack.ports_in[0].port)
        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()

        time.sleep(5)

        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        time.sleep(2)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return

if __name__ == '__main__':
    gr_unittest.run(qa_stop_wait_ack, "qa_stop_wait_ack.xml")
