# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
install(FILES
    gwn_hier_rx_psk.xml
    gwn_hier_tx_psk.xml
    gwn_ev_to_pdu.xml
    gwn_pdu_to_ev.xml
    gwn_event_sink.xml
    gwn_timer_source.xml
    gwn_msg_to_event.xml
    gwn_if_psk_rx.xml
    gwn_if_psk_tx.xml
    gwn_ieee80211_framer.xml
    gwn_ieee80211_deframer.xml
    gwn_virtual_channel.xml
    gwn_data_source.xml
    gwn_stop_wait_ack.xml
    gwn_stop_wait_send.xml
    gwn_ev_psk_encode.xml
    gwn_ev_psk_decode.xml
    gwn_l2_framer.xml
    gwn_l2_deframer.xml DESTINATION share/gnuradio/grc/blocks
)
