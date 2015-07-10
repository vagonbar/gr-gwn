# Install script for directory: /home/victor/IIE/GNURadio/gr-gwn/python

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/home/victor/IIE/GNURadio/gr-gwn")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "Release")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

# Install shared libraries without execute permission?
IF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  SET(CMAKE_INSTALL_SO_NO_EXE "1")
ENDIF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/gwn" TYPE FILE FILES
    "/home/victor/IIE/GNURadio/gr-gwn/python/__init__.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/msg_sender_m.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/msg_receiver_m.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/gwnblock.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/hier_rx_psk.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/gwnutils.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/gwncrc.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/hier_tx_psk.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/ev_to_pdu.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/pdu_to_ev.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/timer_source.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/event_sink.py"
    "/home/victor/IIE/GNURadio/gr-gwn/python/gwn_if_psk_rx.py"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/gwn" TYPE FILE FILES
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/__init__.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/msg_sender_m.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/msg_receiver_m.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwnblock.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/hier_rx_psk.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwnutils.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwncrc.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/hier_tx_psk.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/ev_to_pdu.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/pdu_to_ev.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/timer_source.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/event_sink.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwn_if_psk_rx.pyc"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/__init__.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/msg_sender_m.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/msg_receiver_m.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwnblock.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/hier_rx_psk.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwnutils.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwncrc.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/hier_tx_psk.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/ev_to_pdu.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/pdu_to_ev.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/timer_source.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/event_sink.pyo"
    "/home/victor/IIE/GNURadio/gr-gwn/build/python/gwn_if_psk_rx.pyo"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")

