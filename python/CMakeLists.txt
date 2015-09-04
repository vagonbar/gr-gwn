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
    msg_sender_m.py
    msg_receiver_m.py
    gwnblock.py
    hier_rx_psk.py
    hier_tx_psk.py
    ev_to_pdu.py
    pdu_to_ev.py
    event_sink.py
    timer_source.py
    if_psk_rx.py
    msg_to_event.py
    if_psk_tx.py
    ieee80211_framer.py
    ieee80211_deframer.py DESTINATION ${GR_PYTHON_DIR}/gwn
)

########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

set(GR_TEST_TARGET_DEPS gnuradio-gwn)
set(GR_TEST_PYTHON_DIRS ${CMAKE_BINARY_DIR}/swig)
GR_ADD_TEST(qa_msg_sender_m ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_msg_sender_m.py)
GR_ADD_TEST(qa_msg_receiver_m ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_msg_receiver_m.py)
GR_ADD_TEST(qa_hier_rx_psk ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_hier_rx_psk.py)
GR_ADD_TEST(qa_hier_tx_psk ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_hier_tx_psk.py)
GR_ADD_TEST(qa_ev_to_pdu ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ev_to_pdu.py)
GR_ADD_TEST(qa_pdu_to_ev ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_pdu_to_ev.py)
GR_ADD_TEST(qa_event_sink ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_event_sink.py)
GR_ADD_TEST(qa_timer_source ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_timer_source.py)
GR_ADD_TEST(qa_if_psk_rx ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_if_psk_rx.py)
GR_ADD_TEST(qa_msg_to_event ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_msg_to_event.py)
GR_ADD_TEST(qa_if_psk_tx ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_if_psk_tx.py)
GR_ADD_TEST(qa_ieee80211_framer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ieee80211_framer.py)
GR_ADD_TEST(qa_ieee80211_deframer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ieee80211_deframer.py)
