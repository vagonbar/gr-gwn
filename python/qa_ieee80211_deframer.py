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
from ieee80211_framer import ieee80211_framer
from ieee80211_deframer import ieee80211_deframer

#from timer_source import timer_source
from data_source import data_source
from event_sink import event_sink
import time
from gwnblock import mutex_prt


class qa_ieee80211_deframer (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_deframer_1(self):
        '''Test deframer with Timer Source, IEEE802.11 Framer.
        '''

        # Data Source --> Framer
        blk_src = data_source(retry=2, \
            src_addr='aa:bb:cc:dd:ff:11', dst_addr='22:33:44:55:66:77', \
            payload='Test IEEE 802.11 deframer', \
            ev_dc={'duration':0, \
                'src_addr':'11:11:11:11:11:11', \
                'dst_addr':'22:22:22:22:22:22'} )
        blk_src.debug = False
        blk_frm = ieee80211_framer()
        self.tb.msg_connect(blk_src, blk_src.ports_out[0].port, 
                            blk_frm, blk_frm.ports_in[0].port)
        # Framer --> Deframer
        blk_dfrm = ieee80211_deframer()
        blk_dfrm.debug = True
        self.tb.msg_connect(blk_frm, 'pdu', 
                            blk_dfrm, 'pdu')
        # blocks Deframer --> Event Sink
        blk_evsink = event_sink(debug=True)
        self.tb.msg_connect(blk_dfrm, blk_dfrm.ports_out[0].port, 
                            blk_evsink, blk_evsink.ports_in[0].port)

        #self.tb.run()  # for flowgraphs that will stop on its own!
        self.tb.start()
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()
        
        secs = 5
        print '--- sender, timer started, waiting %d seconds\n' % (secs,)
        time.sleep(secs)
        
        blk_src.stop_timers()
        print '\n--- sender, timers stopped'

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'


if __name__ == '__main__':
    gr_unittest.run(qa_ieee80211_deframer, "qa_ieee80211_deframer.xml")
