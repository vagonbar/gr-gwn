#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # 
# # Copyright 2015
# #   Instituto de Ingenieria Electrica, Facultad de Ingenieria,
# #   Universidad de la Republica, Uruguay.
# # 
# # This is free software; you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation; either version 3, or (at your option)
# # any later version.
# # 
# # This software is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# # 
# # You should have received a copy of the GNU General Public License
# # along with this software; see the file COPYING.  If not, write to
# # the Free Software Foundation, Inc., 51 Franklin Street,
# # Boston, MA 02110-1301, USA.
# #
# 

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from ev_to_pdu import ev_to_pdu
from timer_source import timer_source
import time
from gwnblock import mutex_prt


class qa_ev_to_pdu (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def test_with_timer_source (self):
        '''Timer Source to Event To PDU to Message Debug.
        '''
        
        ### blocks Timer Source --> Event To PDU --> Message Debug
        blk_snd = timer_source('TimerEvSource', 'blk001', retry=2)
        blk_snd.debug = True  # to enable timer source print
        blk_ev2pdu = ev_to_pdu('EvToPDU', 'blk002')
        blk_dbg = blocks.message_debug()

        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
            blk_ev2pdu, blk_ev2pdu.ports_in[0].port )
        self.tb.msg_connect(blk_ev2pdu, 'pdu', 
                            blk_dbg, 'print')
        #self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
        #                    blk_dbg, 'print')

        #self.tb.run()  # for flowgraphs that will stop on its own!
        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump(

        secs = 5
        print '--- sender, timer started, waiting %d seconds\n' % (secs,)
        time.sleep(secs)

        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        
        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'
        
        return


if __name__ == '__main__':
    gr_unittest.run(qa_ev_to_pdu, "qa_ev_to_pdu.xml")
