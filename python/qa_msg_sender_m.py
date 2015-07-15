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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from msg_sender_m import msg_sender_m
import time
from gwnblock import mutex_prt


class qa_msg_sender_m (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def test_with_message_debug(self):
        '''Message Sender to Message Debug.
        '''
        ### blocks Timer Source --> Message Debug
        blk_snd = msg_sender_m('MessageSender', 'blk001', retry=2)
        blk_snd.debug = True
        blk_dbg = blocks.message_debug()
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_dbg, 'print')
        #self.tb.msg_connect(blk_snd, blk_snd.ports_out[1].port, 
        #                    blk_dbg, 'print')
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



if __name__ == '__main__':
    gr_unittest.run(qa_msg_sender_m, "qa_msg_sender_m.xml")
