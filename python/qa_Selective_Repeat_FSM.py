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
from Selective_Repeat_FSM import Selective_Repeat_FSM

from ACK_Rep_FSM import ACK_Rep_FSM
from virtual_channel import virtual_channel

from event_sink import event_sink
from data_source import data_source
from delay_ev import delay_ev
from gwnblock import mutex_prt
import time

class qa_Selective_Repeat_FSM (gr_unittest.TestCase):

	def setUp (self):
		self.tb = gr.top_block ()

	def tearDown (self):
		self.tb = None

	def test_Sel_Rep (self):
		blk_snd = data_source(interrupt=False, interval=1.0, retry=5)
		blk_sel = Selective_Repeat_FSM()
		blk_sel.debug=True
		blk_vchan = virtual_channel(0.2)
		blk_vchan.debug = True
		blk_ack = ACK_Rep_FSM()
		blk_ack.debug = True 		# to see when the msg is sent
		blk_snk1 = event_sink()
		blk_vchanAck = virtual_channel(0.2)
		blk_vchanAck.debug = True
		blk_del = delay_ev(delay_add=0, delay_min=0)
		blk_del.debug = True


		self.tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, blk_sel,         
										 blk_sel.ports_in[0].port)		#connect data source to buff_and_snd block
		self.tb.msg_connect(blk_sel, blk_sel.ports_out[0].port, blk_vchan, 
										 blk_vchan.ports_in[0].port)		#connect buffer_and_snd block to virtual channel
		self.tb.msg_connect(blk_vchan, blk_vchan.ports_out[0].port, blk_ack, 
										 blk_ack.ports_in[0].port)		#connect virtual channel to ack block
		self.tb.msg_connect(blk_ack, blk_ack.ports_out[0].port, blk_snk1, 
										 blk_snk1.ports_in[0].port)		#connect ack block output to event sink
		self.tb.msg_connect(blk_ack, blk_ack.ports_out[1].port, blk_vchanAck, 
										 blk_vchanAck.ports_in[0].port)		#connect the other ack block output to virtual channel
		self.tb.msg_connect(blk_vchanAck, blk_vchanAck.ports_out[0].port, blk_del, 
										 blk_del.ports_in[0].port)  		#connect virtual channel output to delay block
		self.tb.msg_connect(blk_del, blk_del.ports_out[0].port, blk_sel,
										 blk_sel.ports_in[1].port)		#connect delay output to buffer and send
		self.tb.start()
		mutex_prt(self.tb.msg_edge_list())

		secs = 15
		print '--- sender, timer started, waiting %d seconds\n' % (secs,)
		time.sleep(secs)

		blk_snd.stop_timers()
		print '\n--- sender, timers stopped'
		
		self.tb.stop()
		self.tb.wait()
		print '\n--- top block stopped'

		return

if __name__ == '__main__':
	gr_unittest.run(qa_Selective_Repeat_FSM, "qa_Selective_Repeat_FSM.xml")
