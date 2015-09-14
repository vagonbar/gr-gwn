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

'''A virtual channel with probability loss.
'''

from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnblock import mutex_prt          # for tests
import random                           # for probability loss
import pmt                              # for messages and PDUs


class virtual_channel(gwnblock):
    '''A virtual channel, outputs items with probability loss.

    Receives an Event on its Event input port, outputs the same item on corresponding output port with a probability of loss.
    @param blkname: block name.
    @param blkid: block identifier.
    @param prob_loss: probability of loss, float value in [0,1].
    '''

    def __init__(self, blkname='virtual_chanel', blkid='id_virtual_channel', 
            prob_loss=0):

        # invocation of ancestor constructor
        gwnblock.__init__(self, blkname=blkname, blkid=blkid, 
            number_in=1, number_out=1, number_timers=0)

        self.prob_loss = prob_loss
        self.debug = False  # please set from outside for debug print

        # register input port for PDUS and set function handler
        self.message_port_register_in(pmt.intern('pdu'))
        self.set_msg_handler(pmt.intern('pdu'), self.handle_pdu)
        # register output port for PDUs
        self.message_port_register_out(pmt.intern('pdu'))

        return


    def process_data(self, ev):
        '''Receives an Event, outputs with probability loss.

        @param ev: an Event object.
        '''
        rand_nr = random.random()
        if self.debug:
            dbg_msg = '  prob_loss=' + str(self.prob_loss) + \
                '; rand_nr=' + str(rand_nr)
            mutex_prt(dbg_msg)
        if rand_nr <= self.prob_loss:
            pass					# no output
        else:
            self.write_out(ev)		# write event on output
        return


    def handle_pdu(self, msg_pmt):
        '''Receives a PDU, outputs with probability loss.

        @param msg_pmt: a PDU.
        '''
        rand_nr = random.random()
        if self.debug:
            dbg_msg = '  prob_loss=' + str(self.prob_loss) + \
                '; rand_nr=' + str(rand_nr)
            mutex_prt(dbg_msg)
        if rand_nr <= self.prob_loss:
            pass					# no output
        else:
            # send the message on PDU output port
            self.message_port_pub( pmt.intern('pdu'), msg_pmt)
        return


