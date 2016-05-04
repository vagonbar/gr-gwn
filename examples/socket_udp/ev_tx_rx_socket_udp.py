#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Channel with Events
# Description: Events from source to sink
# Generated: Wed May  4 13:30:21 2016
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late

from gnuradio import blocks
from gnuradio import channels
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import gwn
import gwnutils

class ev_tx_rx_socket_udp(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Channel with Events")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 100000
        self.access_code = access_code = gwnutils.default_access_code

        ##################################################
        # Blocks
        ##################################################
        self.gwn_pdu_to_ev_0 = gwn.pdu_to_ev('payload')
        self.gwn_l1_framer_0 = gwn.l1_framer('event', False)
        self.gwn_l1_deframer_0 = gwn.l1_deframer('event', False)
        self.gwn_hier_tx_psk_0 = gwn.hier_tx_psk(0.35,  5 ,  2 , ([-1-1j, 1-1j, 1+1j, -1+1j]),  7 ,  0.4 )
        self.gwn_hier_rx_psk_0 = gwn.hier_rx_psk( 2*3.14/100 ,  3.14/1600 ,  2*3.14/100 ,  32 ,  7 , digital.constellation_calcdist([-1-1j, 1-1j, 1+1j, -1+1j], [], 4, 1).base(),  5 , 0.35,  2 , 0.1, 0.1, 1.0, 1.0, 0.1, 0)
        self.gwn_ev_to_pdu_0 = gwn.ev_to_pdu('payload')
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts(access_code,
          1, "correlate")
        self.channels_channel_model_0 = channels.channel_model(
        	noise_voltage=0.0,
        	frequency_offset=0.0,
        	epsilon=1.0,
        	taps=(1.0, ),
        	noise_seed=0,
        	block_tags=False
        )
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, "correlate")
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_CLIENT", '127.0.0.1', "50008", 10000, False)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("UDP_SERVER", '127.0.0.1', "50007", 10000, False)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, "packet_len")

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.gwn_pdu_to_ev_0, 'pdu'))    
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.gwn_l1_deframer_0, 'pdu'))    
        self.msg_connect((self.gwn_ev_to_pdu_0, 'pdu'), (self.blocks_socket_pdu_0_0, 'pdus'))    
        self.msg_connect((self.gwn_l1_deframer_0, 'out0'), (self.gwn_ev_to_pdu_0, 'in0'))    
        self.msg_connect((self.gwn_l1_framer_0, 'pdu'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))    
        self.msg_connect((self.gwn_pdu_to_ev_0, 'out0'), (self.gwn_l1_framer_0, 'in0'))    
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.gwn_hier_tx_psk_0, 0))    
        self.connect((self.channels_channel_model_0, 0), (self.gwn_hier_rx_psk_0, 0))    
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))    
        self.connect((self.gwn_hier_rx_psk_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))    
        self.connect((self.gwn_hier_tx_psk_0, 0), (self.channels_channel_model_0, 0))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_access_code(self):
        return self.access_code

    def set_access_code(self, access_code):
        self.access_code = access_code

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = ev_tx_rx_socket_udp()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()
