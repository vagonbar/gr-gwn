#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/victor/IIE/GNURadio/gr-gwn/python
export PATH=/home/victor/IIE/GNURadio/gr-gwn/build/python:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export PYTHONPATH=/home/victor/IIE/GNURadio/gr-gwn/build/swig:$PYTHONPATH
/usr/bin/python2 /home/victor/IIE/GNURadio/gr-gwn/python/qa_msg_receiver_m.py 
