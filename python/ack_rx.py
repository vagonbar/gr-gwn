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

'''Reception with ACK.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events 
import random
import time
import sys

class ack_rx(gwnblock):

	'''Reception with ACK .

	Receives an Event on its Event input port, outputs the same item on corresponding output port sending an ACK signal on other output port.
	@param ack_nickname: ACK nickname.
	'''

	def __init__(self, ack_nickname='CtrlACK', debug=False):
		
		gwnblock.__init__(self, name='ack_rx', number_in=1, number_out=2, number_timers=0)

		self.debug = debug
		self.ack_nickname = ack_nickname
		# not needed no more:
		#self.aux_sink = 0  #auxiliary variable to keep track of the last seq_nr received

		# tengo que hacer un diccionario que guarde un numero de ack por cada origen!
		self.dic_src = {}

		return

	def process_data(self, ev):

		''' Receives an event, writes it on output and sends ack
		'''

		if (ev.src_address in self.dic_src):
			aux = self.dic_src[ev.src_address]
			mutex_prt('Destino reconocido!, tenia: ' + str(aux) + ' llego: ' + str(ev.ev_dc['seq_nr']))

			# if event has already been sent, resend ACK backwards only. Checks only if the last data is repeated.
			if ev.nickname == 'DataData' and ev.ev_dc['seq_nr'] == aux:
				mutex_prt('en el caso en que el ev es repetido')
				if self.debug:
					dbg_msg = '   Data ' + str(ev.ev_dc['seq_nr']) + ' repeated, resending ACK to Source.'
					mutex_prt(dbg_msg)
				# making an ack event
				ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
				# envío a la dirección de origen del dato desde mi dirección
				ack.src_address = ev.dst_address
				ack.dst_address = ev.src_address
				self.write_out(ack, port_nr=1)

			# if event is new, pass it forward and send ACK backwards.
			if ev.nickname == 'DataData' and ev.ev_dc['seq_nr'] == aux+1:
				mutex_prt('en el caso en que el ev es nuevo')
				self.write_out(ev, port_nr=0)
				# making an ack event
				ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
				# envío a la dirección de origen del dato desde mi dirección
				ack.src_address = ev.dst_address
				ack.dst_address = ev.src_address
				self.dic_src[ev.src_address] = ev.ev_dc['seq_nr']
				self.write_out(ack, port_nr=1) 
				if self.debug:
					dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
					mutex_prt(dbg_msg)

			# if event is very different than expected: may have changed seq_nr because of reset
			if ev.nickname == 'DataData' and ev.ev_dc['seq_nr'] <> aux and ev.ev_dc['seq_nr'] <> aux + 1:
				mutex_prt('en el caso en que reseteo seq_nr pero es dest conocido')
				self.write_out(ev, port_nr=0)
				# making an ack event
				ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
				# envío a la dirección de origen del dato desde mi dirección
				ack.src_address = ev.dst_address
				ack.dst_address = ev.src_address
				self.dic_src[ev.src_address] = ev.ev_dc['seq_nr']
				self.write_out(ack, port_nr=1) 
				if self.debug:
					dbg_msg = '   Sending ACK corresponding to event number ' + str(ev.ev_dc['seq_nr'])
					mutex_prt(dbg_msg)

		else:
			mutex_prt('en el caso en que el destino es nuevo')
			self.write_out(ev, port_nr=0)
			# agrego al diccionario el destino con su respectivo numero de secuencia
			self.dic_src[ev.src_address]=ev.ev_dc['seq_nr']
			ack = api_events.mkevent(self.ack_nickname, {'seq_nr': ev.ev_dc['seq_nr']})
			# envío a la dirección de origen del dato desde mi dirección
			ack.src_address = ev.dst_address
			ack.dst_address = ev.src_address
			self.write_out(ack, port_nr=1)
			if self.debug:
				dbg_msg = '   Sending ACK corresponding to dst_address:seq_nr ' + str(ev.dst_address) + ':' + str(ev.ev_dc['seq_nr'])
				mutex_prt(dbg_msg)

		return