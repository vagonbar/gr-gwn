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

import numpy
from gnuradio import gr


'''An ARQ selective repeat sender.
'''

import numpy
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
from gwnevents import api_events as api_events   # to create ACK event
import pmt                              # for messages and PDUs

from utils.fsm.gwnfsm import FSM, ExceptionFSM


###
### FSM code
###

### Actions

def send(fsm, event, block):
	'''Sends event received.
	'''
	block.win.append(event)
	block.write_out(event, port_nr=0)
	i = 0
	while block.loob[i]==True and i<block.win_len:
		i = i+1
	block.timeouts[i].start(timeout=block.timeout, ev_dc=event.ev_dc)
	block.dic[event.ev_dc['seq_nr']] = i
	block.loob[i]=True
	return 


def sendfrombuffer(fsm, event, block):
	'''Sends event from buffer, first in list.
	'''
	dato = block.buffer.pop(0)
	send(fsm, dato, block)
	return


def resend(fsm, event, block):
	'''Resends event not acknowledged.
	'''
	if event.nickname == 'EventTimer':
		#for seq_nr, numtime in block.dic.iteritems():
		#	if numtime == int(block.dic[seq_nr]):
		#		block.var_aux = seq_nr
		#		block.loob[numtime] = False
		del block.dic[event.ev_dc['seq_nr']]
		i=0
		while i<len(block.win) and int(block.win[i].ev_dc['seq_nr'])!=int(event.ev_dc['seq_nr']):
			i = i+1
		dato_r = block.win[i]
		dbg_msg = '  Timeout expired, resending event ' + str(dato_r.ev_dc['seq_nr'])
		mutex(dbg_msg)
		block.write_out(dato_r, port_nr=0)
		i=0
		while i<len(block.loob)and block.loob[i]==True:
			i=i+1
		block.timeouts[i].start(timeout=block.timeout, ev_dc=dato_r.ev_dc)
		block.dic[dato_r.ev_dc['seq_nr']] = i
		block.loob[i] = True
	else:
		auxdos = int(block.dic[event.ev_dc['seq_nr']])
		block.timeouts[auxdos].cancel()
		block.loob[auxdos]=False
		del block.dic[event.ev_dc['seq_nr']]
		dbg_msg = ' NAK arrived, resending event '+str(event.ev_dc['seq_nr'])
		mutex_prt(dbg_msg)
		i=0
		while i<len(block.win) and int(block.win[i].ev_dc['seq_nr'])!=int(event.ev_dc['seq_nr']):
			i = i + 1
		dato_r = block.win[i]
		if block.debug:
			dbg_msg = '\n / / NAK arrived! Message ' + str(dato_r.ev_dc['seq_nr']) + ' appears to be lost, resending from Sel_Rep ' + str(dato_r.nickname)
			mutex_prt(dbg_msg)
		block.write_out(dato_r, port_nr=0)
		i=0
		while i<len(block.loob) and block.loob[i]==True:
			i = i+1
		block.timeouts[i].start(timeout=block.timeout, ev_dc=dato_r.ev_dc)
		block.dic[event.dato_r['seq_nr']] = i
		block.loob[i] = True
    
	return


def push(fsm, event, block):
	'''Pushes event into buffer.
	'''
	if len(block.buffer)<block.buff_len:
		block.buffer.append(event)
		if block.debug:
			dbg_msg = '    Window is full, event saved in buffer'
			mutex_prt(dbg_msg)
	return


def ack_ok(fsm, event, block):
	'''ACK was correct, cancel timer, reset retries.
	'''
	if event.ev_dc['seq_nr'] in block.dic.keys():
		aux = block.dic[event.ev_dc['seq_nr']]
		block.timeouts[aux].cancel()
		block.loob[aux] = False
		del block.dic[event.ev_dc['seq_nr']]
		i=0
		while i<len(block.win) and block.win[i].ev_dc['seq_nr']!=event.ev_dc['seq_nr']:
			i=i+1
		dato_r = block.win.pop(i)
		if block.debug:
			msg = '   ACK correctly received from message ' + str(event.ev_dc['seq_nr']) + ', type ' + str(dato_r.nickname) + '\n'
			mutex_prt(msg)
	if block.buffer!=[]:
	   sendfrombuffer(fsm, event, block)
	return


def stop(fsm, event, block):
	'''Retries in sending of buffer exceeded, stop sending.
	'''
	if block.debug:
		mutex_prt('    FSM, send retries or buffer exceeded')
		mutex_prt('      max buffer length: ' + str(block.buffer_len) + \
			', buffer length: ' + str(len(block.ls_buffer)))
		mutex_prt('      max retries: ' + str(block.max_retries) + \
			' retries: ' + str(fsm.nr_retries))
		fsm.print_state(show=['transition', 'action'])
	#raise ExceptionFSM('Send retries, exceeded')
	return


def fn_error(fsm, event, block):
	fsm.print_state(show=['transition', 'action'])
	raise ExceptionFSM('fn_error, error in transition')
	return



### Conditions
# funcions must return True or False
# conditions expressed as strings are accepted, i.e. 'a == b'


### the FSM

def Sel_Repeat_FSM(blk):
	'''The ARQ Stop and Wait FSM.

	@param blk: reference to the block to which this FSM is attached.
	'''
	f = FSM ('Idle') # 
	f.debug = False
	f.wait = 1                    #chequear si este estado inicial es escalable (1er seq_nr tiene mas sentido)
	f.nr_retries = 0

	# transitions
	f.set_default_transition (fn_error, 'Idle')

	#f.add_transition_any ('Idle', None, 'Idle')
	#f.add_transition_any ('WaitAck', None, 'WaitAck')

	# 1
	f.add_transition('DataData', 'Idle', send, 'WaitAck', \
		None) #first event of the window
	# 2
	f.add_transition('DataOut', 'WaitAck', ack_ok, 'Idle', \
		['len(block.win)==1'])  #ack of the only event of the window received
	# 3
	f.add_transition ('DataOut', 'WaitAck', ack_ok, 'WaitAck')         # event in buffer
	#4 
	f.add_transition('DataIn','WaitAck', resend, 'WaitAck')#nak received, resend event
	# 5 
	f.add_transition ('EventTimer', 'WaitAck', resend, 'WaitAck', \
		['self.nr_retries <= block.max_retries'])    # retries left
	# 6
	f.add_transition ('EventTimer', 'WaitAck', stop, 'Stop', \
		['self.nr_retries > block.max_retries'])     # retries exceeded'''
	# 7
	f.add_transition ('DataData', 'WaitAck', send, 'WaitAck', \
		['len(block.win) < block.win_len'])  # buffer ok
	# 8
	f.add_transition ('DataData', 'WaitAck', push, 'WaitAck', \
		['len(block.buffer) < block.buffer_len', 'len(block.win)>=block.win_len'])  # buffer ok
	# 9
	f.add_transition ('DataData', 'WaitAck', stop, 'Stop', \
		['len(block.ls_buffer) >= block.buffer_len'])  # buffer max exceed

	# 10
	f.add_transition_any ('Stop', stop, 'Stop')
	# 11
	f.add_transition_any ('Idle', None, 'Idle')


	if blk.debug:
		print "--- FSM created, show state"
		f.print_state(show='state')

	return f


###
### block class code
###

class Selective_Repeat_FSM(gwnblock):
	'''An ARQ Stop and wait event sender.

	Receives an event, starts a timeout, writes this event on output port 1, and waits for an ACK to the message sent. On receiving the appropriate ACK, sends next message. On timeout, resends the unacknowledged message. Received messages are buffered in a FIFO list.
	@param blkname: block name.
	@param blkid: block identifier.
	@param ack_nickname: the nickname of the acknowledge event waited for.
	@param max_retries: number of times to resend event if ACK not received.
	@param tout_nickname: the nickname of the timer event waited for.
	@param timeout: the timeout in seconds.
	@param buffer_len: the buffer capacity, i.e. the maximum length of the list; default is 0, which means no limit.
	'''

	def __init__(self, ack_nickname='CtrlACK', \
			max_retries=3, timeout=1.0, \
			buffer_len=1000, win_len=500, debug=False):

		# invocation of ancestor constructor
		gwnblock.__init__(self, name='Selective_Repeat_FSM', number_in=2, number_out=1, number_timeouts=win_len)


		self.a = 0
		self.ack_nickname = ack_nickname
		self.max_retries = 3
		self.timeout = timeout
		self.buffer_len = buffer_len
		self.win_len = win_len
		self.var_aux = 0
		self.win = []
		self.buffer = []
		self.dic = {}  # dictionary used to relate timeout with event
		self.loob = []

		j = 0   #inicio loob
		for j in range(win_len):
			self.loob.append(False)

		self.ls_buffer = []     # length must be checked in process
		#self.debug = False      # please set from outside for debug print
		self.debug = debug

		self.fsm = Sel_Repeat_FSM(self)
		return


	def process_data(self, ev):
		'''Writes event, waits for ACK, retransmits.

		The received event is passed on to the process function of the FSM; actions in the FSM are provided with the received event and a reference to the present block, so that they can access this block's attributes and functions, in particular the write_out function to send events.
		@param ev: a received Event object.
		'''
		if self.debug:
			dbg_msg = '--- {0}, received ev: {1}, with dic: {2}'. \
				format(self.name(), ev.nickname, ev.ev_dc)
			# only for Data Events:
			#dbg_msg = '--- {0}, received ev: {1}, seq nr: {2}'. \
			#    format(self.blkname, ev.nickname, ev.ev_dc['seq_nr'])
			mutex_prt(dbg_msg)
		# handle event to FSM process functions
		self.fsm.process(ev.nickname, event=ev, block=self)
		return
