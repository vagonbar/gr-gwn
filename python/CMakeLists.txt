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

########################################################################
# Include python install macros
########################################################################
include(GrPython)
if(NOT PYTHONINTERP_FOUND)
    return()
endif()

########################################################################
# Install python sources
########################################################################
GR_PYTHON_INSTALL(
    FILES
    __init__.py
    gwnblock.py
    hier_rx_psk.py
    hier_tx_psk.py
    ev_to_pdu.py
    pdu_to_ev.py
    event_sink.py
    timer_source.py
    ieee80211_framer.py
    ieee80211_deframer.py
    virtual_channel.py
    data_source.py
    stop_wait_ack.py
    stop_wait_send.py
    l1_framer.py
    l1_deframer.py
    probe_medium.py
    sel_rep.py
    ack_rep.py
    CSMA_FSM.py
    event_constructor.py
    event_guider.py
    event_guider.py
    ack_rx.py DESTINATION ${GR_PYTHON_DIR}/gwn
)

########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

set(GR_TEST_TARGET_DEPS gnuradio-gwn)
set(GR_TEST_PYTHON_DIRS ${CMAKE_BINARY_DIR}/swig)
GR_ADD_TEST(qa_hier_rx_psk ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_hier_rx_psk.py)
GR_ADD_TEST(qa_hier_tx_psk ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_hier_tx_psk.py)
GR_ADD_TEST(qa_ev_to_pdu ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ev_to_pdu.py)
GR_ADD_TEST(qa_pdu_to_ev ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_pdu_to_ev.py)
GR_ADD_TEST(qa_event_sink ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_event_sink.py)
GR_ADD_TEST(qa_timer_source ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_timer_source.py)
GR_ADD_TEST(qa_ieee80211_framer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ieee80211_framer.py)
GR_ADD_TEST(qa_ieee80211_deframer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ieee80211_deframer.py)
GR_ADD_TEST(qa_virtual_channel ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_virtual_channel.py)
GR_ADD_TEST(qa_data_source ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_data_source.py)
GR_ADD_TEST(qa_stop_wait_ack ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_stop_wait_ack.py)
GR_ADD_TEST(qa_stop_wait_send ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_stop_wait_send.py)
GR_ADD_TEST(qa_l1_framer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_l1_framer.py)
GR_ADD_TEST(qa_l1_deframer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_l1_deframer.py)
GR_ADD_TEST(qa_probe_medium ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_probe_medium.py)
GR_ADD_TEST(qa_sel_rep ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_sel_rep.py)
GR_ADD_TEST(qa_ack_rep ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ack_rep.py)
GR_ADD_TEST(qa_CSMA_FSM ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_CSMA_FSM.py)
GR_ADD_TEST(qa_event_constructor ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_event_constructor.py)
GR_ADD_TEST(qa_event_guider ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_event_guider.py)
GR_ADD_TEST(qa_event_guider ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_event_guider.py)
GR_ADD_TEST(qa_ack_rx ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ack_rx.py)
