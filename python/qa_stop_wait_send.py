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
from stop_wait_send import stop_wait_send
from stop_wait_ack import stop_wait_ack
from virtual_channel import virtual_channel

from event_sink import event_sink
from data_source import data_source
from gwnblock import mutex_prt

import time

class qa_stop_wait_send (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def notest_ack (self):
        '''Send and receive ACK.
        '''
        ### block Data Source --> Stop and Wait Send
        blk_snd = data_source('DataData', 'blk001', retry=3, interval=1.0)
        blk_snd.debug = True
        blk_arq_send = stop_wait_send('StopAndWaitSend', 'blk002')
        blk_arq_send.debug = True   # prints complete Event
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_arq_send, blk_arq_send.ports_in[0].port)

        ### block Stop and Wait ACK <--> Stop and Wait ACK
        blk_ack = stop_wait_ack('StopAndWaitACK', 'blk003')
        blk_ack.debug = True
        self.tb.msg_connect(blk_arq_send, blk_arq_send.ports_out[0].port, 
                            blk_ack, blk_ack.ports_in[0].port)
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[1].port, 
                            blk_arq_send, blk_arq_send.ports_in[0].port)

        ### block Stop and Wait ACK --> Event Sink
        blk_snk_ev = event_sink('EventSink', 'blk004')
        #blk_snk_ev.debug = True    # print complete Event
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[0].port, 
                            blk_snk_ev, blk_snk_ev.ports_in[0].port)

        #self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
        #                    blk_snk_ev, blk_snk_ev.ports_in[0].port)

        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()

        time.sleep(4)

        print "Block Stop and Wait Send, buffer:", blk_arq_send.ls_buffer

        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        time.sleep(1)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return

    def notest_retry (self):
        '''Send, timeout, retry, no ACK.
        '''
        ### block Data Source --> Stop and Wait Send
        blk_snd = data_source('DataData', 'blk001', retry=5, interval=1.0)
        blk_snd.debug = True
        blk_arq_send = stop_wait_send('StopAndWaitSend', 'blk002', \
            timeout=0.5, retries=2)
        blk_arq_send.debug = False   # prints complete Event
        blk_arq_send.fsm.debug = True
        self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                            blk_arq_send, blk_arq_send.ports_in[0].port)

        ### block Stop and Wait Send --> Event Sink
        blk_snk_ev = event_sink('EventSink', 'blk004')
        #blk_snk_ev.debug = True    # print complete Event
        self.tb.msg_connect(blk_arq_send, blk_arq_send.ports_out[0].port, 
                            blk_snk_ev, blk_snk_ev.ports_in[0].port)

        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()
        time.sleep(4)
        print "Block Stop and Wait Send, buffer:", blk_arq_send.ls_buffer
        blk_snd.stop_timers()
        print '\n--- sender, timers stopped'
        time.sleep(1)
        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return


    def test_with_loss (self):
        '''Send over virtual channel.
        '''
        ### block Data Source --> Stop and Wait Send
        blk_src = data_source('DataData', 'blk001', retry=6, interval=1.0)
        blk_src.debug = True
        blk_arq_send = stop_wait_send('StopAndWaitSend', 'blk002', timeout=1.5)
        blk_arq_send.debug = False #True   # prints complete Event
        blk_arq_send.fsm.debug = True
        blk_arq_send.timeouts[0].debug = True
        self.tb.msg_connect(blk_src, blk_src.ports_out[0].port, 
                            blk_arq_send, blk_arq_send.ports_in[0].port)

        ### block Stop and Wait Send --> Virtual Channel
        blk_vch = virtual_channel('VirtualChannel', 'blk003', prob_loss=0.0)
        blk_vch.debug = True
        self.tb.msg_connect(blk_arq_send, blk_arq_send.ports_out[0].port, 
                            blk_vch, blk_vch.ports_in[0].port)

        ### block Virtual Channel --> Stop and Wait ACK
        blk_ack = stop_wait_ack('StopAndWaitACK', 'blk004')
        blk_ack.debug = True
        self.tb.msg_connect(blk_vch, blk_vch.ports_out[0].port, 
                            blk_ack, blk_ack.ports_in[0].port)
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[1].port, 
                            blk_arq_send, blk_arq_send.ports_in[0].port)


        ### block Virtual Channel --> Event Sink
        blk_snk_ev = event_sink('EventSink', 'blk005')
        #blk_snk_ev.debug = True    # print complete Event
        self.tb.msg_connect(blk_ack, blk_ack.ports_out[0].port, 
                            blk_snk_ev, blk_snk_ev.ports_in[0].port)

        #self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
        #                    blk_snk_ev, blk_snk_ev.ports_in[0].port)

        self.tb.start() 
        mutex_prt(self.tb.msg_edge_list())
        #print tb.dump()

        time.sleep(9)

        blk_snd.stop_timers()
        print "Block Stop and Wait Send, buffer:", blk_arq_send.ls_buffer
        blk_arq_send.stop_timers()
        print '\n--- sender, timers stopped'
        time.sleep(1)

        self.tb.stop()
        self.tb.wait()
        print '\n--- top block stopped'

        return


if __name__ == '__main__':
    gr_unittest.run(qa_stop_wait_send, "qa_stop_wait_send.xml")
