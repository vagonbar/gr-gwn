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
import random
from gnuradio import gr

# GWN imports
from gwnblock import gwnblock           # for all GWN blocks
from gwnevents import api_events as api_events
from gwnblock import mutex_prt          # for tests


class event_constructor(gwnblock):
    """
    docstring for block event_constructor
    """
    def __init__(self, src_address='', Destination=False, seq_nr=1, dst_address='', debug=False):
        gwnblock.__init__(self, name="event_constructor", \
            number_in=1, number_out=2, number_timers=0)
        
        self.ev_dc={}
        self.src_address=src_address
        # Destination=True if you wish to manually select a single destination and sequence number
        self.Destination=Destination
        self.dst_address=dst_address
        self.seq_nr=seq_nr
        self.debug=debug
        self.dic_dst={}
        # capaz esta bueno setear este valor por afuera!
        self.MAX_SEQ = 65000

        return


    def detection(self, ev):
        i=0
        destino=str()
        data=ev.payload
        while(data[i]<>' ' and i<len(data)):
            destino+=data[i]
            i+=1
        return destino


    def process_data(self, ev):

        '''
        @param ev: an Event object.
        falta ver aca que quiero tocar realmente, si todos tienen que ser DataData
        ademas falta ver aca si me interesa cambiar los seq_nr y si pueden llegar a confundirse conversaciones
        '''

        if self.Destination:
            ev_data = api_events.mkevent(ev.nickname, \
                ev_dc=self.ev_dc, payload=ev.payload)
            ev_data.src_address = self.src_address
            ev_data.dst_address = self.dst_address
            ev_data.ev_dc['seq_nr'] = self.seq_nr
            if self.debug:
                dbg_msg = 'Asigno al dato el numero de secuencia: ' + str(self.seq_nr) + ' y lo envío a ' + str(self.dst_address)
                mutex_prt(dbg_msg)
            self.seq_nr += 1

        else:
            # detecto el destino en el payload
            # si el destino ya esta en una lista, asigno el numero de secuencia siguiente
            # si el destino no esta, agrego a la lista, y asigno un numero de secuencia aleatorio
            dst = self.detection(ev)
            if (dst in self.dic_dst):
                ev_data = api_events.mkevent(ev.nickname, \
                    ev_dc=self.ev_dc, payload=ev.payload)
                ev_data.src_address = self.src_address
                ev_data.dst_address = dst
                self.dic_dst[dst] += 1
                seq_nr=self.dic_dst[dst]
                ev_data.ev_dc['seq_nr'] = seq_nr
                if self.debug:
                    dbg_msg = 'Detecte el destino, el numero de secuencia que asigno es: ' + str(seq_nr) + ' y lo envío a ' + str(dst)
                    mutex_prt(dbg_msg)

            else:
                seq_nr = random.randrange(self.MAX_SEQ)
                self.dic_dst[dst] = seq_nr
                ev_data = api_events.mkevent(ev.nickname, \
                    ev_dc=self.ev_dc, payload=ev.payload)
                ev_data.src_address = self.src_address
                ev_data.dst_address = dst
                ev_data.ev_dc['seq_nr'] = seq_nr
                if self.debug:
                    dbg_msg = 'Nuevo destino, el numero de secuencia que asigno es: ' + str(seq_nr) + ' y lo envío a ' + str(dst)
                    mutex_prt(dbg_msg)

        self.write_out(ev_data)

        return


