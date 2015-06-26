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

import numpy
from gnuradio import gr

import gwnutils as packet_utils
from gwnblock import gwnblock


class gwn_if_psk_tx(gwnblock):
    """
    docstring for block gwn_if_psk_tx
    """
    def __init__(self):
        gwnblock.__init__(self, blkname="gwn_if_psk_tx", blkid='0', 
            number_in=1, number_out=1, number_timers=0)

        self._samp_per_sym = 5
        self._bits_per_sym = 2
        self._preamble = packet_utils.default_preamble
        self._access_code = packet_utils.default_access_code
        self._pad_for_usrp = True
        self._whitener_offset = False
        return


    def process_data(self, ev):
        payload = ev.frmpkt
        pkt = packet_utils.make_packet(payload,
            self._samp_per_sym,
            self._bits_per_sym,
            self._preamble,
            self._access_code,
            self._pad_for_usrp,
            self._whitener_offset)
            #print "pkt =", string_to_hex_list(pkt)
            #msg = gr.message_from_string(pkt)
        self.write_out(pkt)


if __name__ == "__main__":

    import time
    from gnuradio.blocks import message_debug
    
    from msg_sender_m import msg_sender_m
    from msg_receiver_m import msg_receiver_m

    tb = gr.top_block()
    blk_snd = msg_sender_m('SendTimerEvs', 'blk001')
    blk_ifz = gwn_if_psk_tx()
    #blk_rec = msg_receiver_m('Receiver', 'blk002')
    blk_msg_dbg = message_debug()

    tb.msg_connect(blk_snd, blk_snd.ports_out[0].port, 
                   blk_ifz, blk_ifz.ports_in[0].port)
    #tb.msg_connect(blk_ifz, blk_ifz.ports_out[0].port, 
    #               blk_rec, blk_rec.ports_in[0].port)
    tb.msg_connect(blk_ifz, blk_ifz.ports_out[0].port, 
                   blk_msg_dbg, 'print')
    tb.start()
    print tb.msg_edge_list()

    blk_snd.set_timer(1, interrupt=False, interval=1, retry=3, 
        nickname1='TimerTOC', nickname2='TimerTOH')

    time.sleep(5)
    blk_snd.stop_timers()
    
    tb.stop()
    tb.wait()

