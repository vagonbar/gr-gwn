#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Jul 15 12:31:19 2015
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import gwn

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################
        self.gwn_timer_source_0 = gwn.timer_source("", "", False, 1.0, 3, "TimerTOR1", "TimerTOR2")
        self.gwn_pdu_to_ev_0 = gwn.pdu_to_ev("", "")
        self.gwn_event_sink_0 = gwn.event_sink("", "")
        self.gwn_ev_to_pdu_0 = gwn.ev_to_pdu("", "")
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, "packet_len")
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, "packet_len")
        self.blocks_copy_0 = blocks.copy(gr.sizeof_char*1)
        self.blocks_copy_0.set_enabled(True)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.gwn_pdu_to_ev_0, 'pdu'))    
        self.msg_connect((self.gwn_ev_to_pdu_0, 'pdu'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))    
        self.msg_connect((self.gwn_pdu_to_ev_0, 'out0'), (self.gwn_event_sink_0, 'in0'))    
        self.msg_connect((self.gwn_timer_source_0, 'out0'), (self.gwn_ev_to_pdu_0, 'in0'))    
        self.connect((self.blocks_copy_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))    
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_copy_0, 0))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

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
