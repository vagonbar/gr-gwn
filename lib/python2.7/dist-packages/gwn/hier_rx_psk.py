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

from gnuradio import gr
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio.filter import firdes
import math
DEBUG = 0


class hier_rx_psk(gr.hier_block2):
    """
    docstring for block hier_rx_psk
    """
    def __init__(self, bw_clock_sync=2*math.pi/100, bw_fll=math.pi/1600, bw_costas=2*math.pi/100, n_filts=32, len_sym_srrc=7, constellation=digital.constellation_calcdist([-1-1j, 1-1j, 1+1j, -1+1j], [], 4, 1).base(), samp_per_sym=5, alfa=0.35, bits_per_sym=2,agc_attack_rate=1e-1, agc_decay_rate=1e-2, agc_reference=1.0, agc_gain=1.0, alpha_probe=0.1, th_probe=0):
        gr.hier_block2.__init__(
            self, "Hier Rx",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.bw_clock_sync = bw_clock_sync
        self.bw_fll = bw_fll
        self.bw_costas = bw_costas
        self.n_filts = n_filts
        self.len_sym_srrc = len_sym_srrc
        self.constellation = constellation
        self.samp_per_sym = samp_per_sym
        self.alfa = alfa
        self.bits_per_sym = bits_per_sym
        self.alpha_probe = alpha_probe
        self.th_probe = th_probe

        ##################################################
        # Variables
        ##################################################
        self.filtro_srrc = filtro_srrc = firdes.root_raised_cosine(n_filts,samp_per_sym*n_filts,1.0,alfa,samp_per_sym*len_sym_srrc*n_filts)

        ##################################################
        # Blocks
        ##################################################
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_ccf(samp_per_sym, bw_clock_sync, (filtro_srrc), n_filts, 16, 5, 1)
        self.digital_fll_band_edge_cc_0 = digital.fll_band_edge_cc(samp_per_sym, alfa, len_sym_srrc*samp_per_sym, bw_fll)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2**bits_per_sym)
        self.digital_costas_loop_cc_0_0_0 = digital.costas_loop_cc(bw_costas, 2**bits_per_sym)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constellation)
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(bits_per_sym)
        self.analog_probe_avg_mag_sqrd_x_0 = analog.probe_avg_mag_sqrd_c(th_probe, alpha_probe)
        self.analog_agc2_xx_0 = analog.agc2_cc(agc_attack_rate, agc_decay_rate, agc_reference, agc_gain)
	self.analog_agc2_xx_0.set_max_gain(agc_gain)
	
	#self.analog_agc2_xx_0 = analog.agc2_cc(0.6e-2, 1e-3, 2, 15)
        #self.analog_agc2_xx_0.set_max_gain(15)

	if DEBUG:
		self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, "./file_rx_fin", False)
        	self.blocks_file_sink_0.set_unbuffered(True)	        
		self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_char*1, "./file_rx_out_diff", False)
        	self.blocks_file_sink_1.set_unbuffered(True)	
 		self.blocks_file_sink_2 = blocks.file_sink(gr.sizeof_gr_complex*1, "./file_rx_sym", False)
        	self.blocks_file_sink_2.set_unbuffered(True)
		self.blocks_file_sink_3 = blocks.file_sink(gr.sizeof_gr_complex*1, "./file_rx_input", False)
        	self.blocks_file_sink_3.set_unbuffered(True)

        ##################################################
        # Connections
        ##################################################
	#self.connect((self, 0), (self.digital_fll_band_edge_cc_0, 0))        
	self.connect((self.digital_diff_decoder_bb_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.analog_agc2_xx_0, 0), (self.digital_fll_band_edge_cc_0, 0))
        self.connect((self.digital_fll_band_edge_cc_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.digital_costas_loop_cc_0_0_0, 0))
        self.connect((self, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self, 0))
	if DEBUG:
		self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.blocks_file_sink_0, 0))
        	self.connect((self.digital_diff_decoder_bb_0, 0), (self.blocks_file_sink_1, 0))
		self.connect((self.digital_fll_band_edge_cc_0, 0), (self.blocks_file_sink_2, 0))
		self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.blocks_file_sink_3, 0))

        self.connect((self, 0), (self.analog_probe_avg_mag_sqrd_x_0, 0))


# QT sink close method reimplementation

    def get_bw_clock_sync(self):
        return self.bw_clock_sync

    def set_bw_clock_sync(self, bw_clock_sync):
        self.bw_clock_sync = bw_clock_sync
        self.digital_pfb_clock_sync_xxx_0.set_loop_bandwidth(self.bw_clock_sync)

    def get_bw_fll(self):
        return self.bw_fll

    def set_bw_fll(self, bw_fll):
        self.bw_fll = bw_fll
        self.digital_fll_band_edge_cc_0.set_loop_bandwidth(self.bw_fll)

    def get_bw_costas(self):
        return self.bw_costas

    def set_bw_costas(self, bw_costas):
        self.bw_costas = bw_costas
        self.digital_costas_loop_cc_0_0_0.set_loop_bandwidth(self.bw_costas)

    def get_n_filts(self):
        return self.n_filts

    def set_n_filts(self, n_filts):
        self.n_filts = n_filts
        self.set_filtro_srrc(firdes.root_raised_cosine(self.n_filts,self.samp_per_sym*self.n_filts,1.0,self.alfa,self.samp_per_sym*self.len_sym_srrc*self.n_filts))

    def get_len_sym_srrc(self):
        return self.len_sym_srrc

    def set_len_sym_srrc(self, len_sym_srrc):
        self.len_sym_srrc = len_sym_srrc
        self.set_filtro_srrc(firdes.root_raised_cosine(self.n_filts,self.samp_per_sym*self.n_filts,1.0,self.alfa,self.samp_per_sym*self.len_sym_srrc*self.n_filts))

    def get_constellation(self):
        return self.constellation

    def set_constellation(self, constellation):
        self.constellation = constellation

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_filtro_srrc(firdes.root_raised_cosine(self.n_filts,self.samp_per_sym*self.n_filts,1.0,self.alfa,self.samp_per_sym*self.len_sym_srrc*self.n_filts))

    def get_alfa(self):
        return self.alfa

    def set_alfa(self, alfa):
        self.alfa = alfa
        self.set_filtro_srrc(firdes.root_raised_cosine(self.n_filts,self.samp_per_sym*self.n_filts,1.0,self.alfa,self.samp_per_sym*self.len_sym_srrc*self.n_filts))

    def get_bits_per_sym(self):
        return self.bits_per_sym

    def set_bits_per_sym(self, bits_per_sym):
        self.bits_per_sym = bits_per_sym

    def get_alpha_probe(self):
        return self.alpha_probe

    def set_alpha_probe(self, alpha_probe):
        self.alpha_probe = alpha_probe
        self.analog_probe_avg_mag_sqrd_x_0.set_alpha(self.alpha_probe)

    def get_th_probe(self):
        return self.th_probe

    def set_th_probe(self, th_probe):
        self.th_probe = th_probe
        self.analog_probe_avg_mag_sqrd_x_0.set_threshold(self.th_probe)

    def get_filtro_srrc(self):
        return self.filtro_srrc

    def set_filtro_srrc(self, filtro_srrc):
        self.filtro_srrc = filtro_srrc
        self.digital_pfb_clock_sync_xxx_0.set_taps((self.filtro_srrc))


