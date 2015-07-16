#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Thu Jul 16 09:44:27 2015
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import gwn
import tutorial

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.QPSK = QPSK = digital.constellation_calcdist(([1+1j, -1+1j, 1-1j, -1-1j]), ([0, 1, 3, 2]), 4, 1).base()

        ##################################################
        # Blocks
        ##################################################
        self.tutorial_my_qpsk_demod_cb_0 = tutorial.my_qpsk_demod_cb(True)
        self.gwn_timer_source_0 = gwn.timer_source("", "", False, 1.0, 3, "TimerTOR1", "TimerTOR2")
        self.gwn_pdu_to_ev_0 = gwn.pdu_to_ev("", "")
        self.gwn_event_sink_0 = gwn.event_sink("Event Receiver", "evrec")
        self.gwn_ev_to_pdu_0 = gwn.ev_to_pdu("", "")
        self.digital_crc32_async_bb_1 = digital.crc32_async_bb(True)
        self.digital_crc32_async_bb_0 = digital.crc32_async_bb(False)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc((QPSK.points()), 1)
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, "tsb_tag")
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(2, 8, "tsb_tag", True, gr.GR_LSB_FIRST)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(8, 2, "tsb_tag", False, gr.GR_LSB_FIRST)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, "tsb_tag")

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.digital_crc32_async_bb_1, 'in'))    
        self.msg_connect((self.digital_crc32_async_bb_0, 'out'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))    
        self.msg_connect((self.digital_crc32_async_bb_1, 'out'), (self.gwn_pdu_to_ev_0, 'pdu'))    
        self.msg_connect((self.gwn_ev_to_pdu_0, 'pdu'), (self.digital_crc32_async_bb_0, 'in'))    
        self.msg_connect((self.gwn_pdu_to_ev_0, 'out0'), (self.gwn_event_sink_0, 'in0'))    
        self.msg_connect((self.gwn_timer_source_0, 'out0'), (self.gwn_ev_to_pdu_0, 'in0'))    
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_0, 0))    
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))    
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0, 0))    
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.tutorial_my_qpsk_demod_cb_0, 0))    
        self.connect((self.tutorial_my_qpsk_demod_cb_0, 0), (self.blocks_repack_bits_bb_1, 0))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_QPSK(self):
        return self.QPSK

    def set_QPSK(self, QPSK):
        self.QPSK = QPSK

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()
