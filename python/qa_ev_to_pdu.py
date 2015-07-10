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
from msg_sender_m import msg_sender_m
from msg_receiver_m import msg_receiver_m

import time

class qa_ev_to_pdu (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        #self.tb.run ()

        ### define blocks
        blk_snd = msg_sender_m('TimerEvSource', 'blk001',
            interrupt=False, interval=1, retry=5)
        blk_ev2pdu = ev_to_pdu('EvToPDU', 'blk002')
        #blk_rec = msg_receiver_m('Receiver ONE', 'blk003')
        blk_dbg = blocks.message_debug()

        ### connect blocks
        # a send - receive connection of messagese
        #self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
        #    blk_rec, blk_rec.ports_in[0].port )

        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
            blk_ev2pdu, blk_ev2pdu.ports_in[0].port )
        self.tb.msg_connect(blk_ev2pdu, 'pdu', 
            blk_dbg, 'print_pdu')

        # check data
        self.tb.start()

        time.sleep(10)
        blk_snd.stop_timers()
        self.tb.stop()
        self.tb.wait()

        return

if __name__ == '__main__':
    gr_unittest.run(qa_ev_to_pdu, "qa_ev_to_pdu.xml")
