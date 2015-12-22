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

import pmt

import gwnutils
from gwnblock import gwnblock


def test1():
    payload = 20*'a' + 20*'b' + 20*'c'
    _samp_per_sym = 3
    _bits_per_sym = 2
    _preamble = gwnutils.default_preamble
    _access_code = gwnutils.default_access_code
    _pad_for_usrp = True
    _whitener_offset = False

    pkt = gwnutils.make_packet(payload,
        _samp_per_sym,
        _bits_per_sym,
        _preamble,
        _access_code,
        _pad_for_usrp,
        _whitener_offset)
    print 'type(pkt) :', type(pkt)
    #print "pkt in hex =", gwnutils.string_to_hex_list(pkt)
    msg = gr.message_from_string(pkt)
    #print "msg = ", msg
    return pkt


if __name__ == "__main__":
    msg_pmt = test1()

    meta = pmt.to_python(pmt.car(msg_pmt))
    content = pmt.cdr(msg_pmt)

    # converts received u8 vector into string of chars 0 and 1
    msg_str = "".join([str(x) for x in pmt.u8vector_elements(content)])
    # converts 1s and 0s  string into a packed binary string
    lschars, pad = conv_1_0_string_to_packed_binary_string(msg_str)
    print 'lschars =', lschars
    print 'pad =', pad
    # unmakes packet, checks CRC
    ok, payload = unmake_packet(lschars)
    
    print 'ok =', ok
    print 'payload =', payload

