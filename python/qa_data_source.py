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
from data_source import data_source


from event_sink import event_sink
import time
from gwnblock import mutex_prt


class qa_data_source (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def test_data_source(self):
        '''Data Source to Event Sink.
        '''
        ### blocks Timer Source --> Message Debug
        blk_snd = data_source('DataData', 'blk001', retry=3, interval=1.0)
        #blk_snd.timers[0].debug = True     # print debug on timer
        blk_snk = event_sink()
        #blk_snk.debug = True
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_snk, blk_snk.ports_in[0].port)
        #self.tb.run()  # for flowgraphs that will stop on its own!
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
    gr_unittest.run(qa_data_source, "qa_data_source.xml")
