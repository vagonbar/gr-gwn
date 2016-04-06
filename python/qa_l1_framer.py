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
from l1_framer import l1_framer

from data_source import data_source
from event_sink import event_sink
import time
from gwnblock import mutex_prt



class qa_l1_framer (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def test_l1_framer (self):
        '''Data source to l2_framer to l1_framer to event sink, whole event.
        '''

        blk_src = data_source(retry=3, interval=1.0, \
            payload='L1 Framer QA test, payload in event')
        #blk_dst = event_sink(debug=True)
        blk_l1_frm = l1_framer(debug=True)
        blk_dbg = blocks.message_debug()
        self.tb.msg_connect(blk_src, blk_src.ports_out[0].port, 
                            blk_l1_frm, blk_l1_frm.ports_in[0].port)
        self.tb.msg_connect(blk_l1_frm, 'pdu', 
                            blk_dbg, 'print_pdu')

        self.tb.start()
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()
        
        secs = 5
        print '--- sender, timer started, waiting %d seconds\n' % (secs,)
        time.sleep(secs)
        
        blk_src.stop_timers()
        print '\n--- sender, timers stopped'
        #time.sleep(2)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'



    def test_l2_framer (self):
        '''Data source to l2_framer to l1_framer to event sink, on payload.
        '''

        blk_src = data_source(retry=3, interval=1.0, \
            payload='L1 Framer QA test, payload only')
        #blk_dst = event_sink(debug=True)
        blk_l1_frm = l1_framer(in_type='payload', debug=True)
        blk_dbg = blocks.message_debug()
        self.tb.msg_connect(blk_src, blk_src.ports_out[0].port, 
                            blk_l1_frm, blk_l1_frm.ports_in[0].port)
        self.tb.msg_connect(blk_l1_frm, 'pdu', 
                            blk_dbg, 'print_pdu')

        self.tb.start()
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()
        
        secs = 5
        print '--- sender, timer started, waiting %d seconds\n' % (secs,)
        time.sleep(secs)
        
        blk_src.stop_timers()
        print '\n--- sender, timers stopped'
        #time.sleep(2)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'


if __name__ == '__main__':
    gr_unittest.run(qa_l1_framer, "qa_l1_framer.xml")
