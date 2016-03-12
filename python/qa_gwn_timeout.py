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

'''GWNBlock tests, not in QA system, run directly.
'''

print "=== Test of GWNTimeout\n"
print "--- Test 1, normal timeout"
import gwnblock
import time
blk = gwnblock.gwnblock(number_timeouts=1)
blk.timeouts[0].debug = True
print "    Timer thread object exists?", ; print blk.timeouts[0].timer
blk.timeouts[0].start(2)
print "    Timer thread object exists?", ; print blk.timeouts[0].timer
time.sleep(4)               # wait for timeout
print "    Timer thread object exists?", ; print blk.timeouts[0].timer

print; print "--- Test 2, cancel before timeout"
blk.timeouts[0].start(15)
time.sleep(2)
blk.timeouts[0].cancel()
print "    Timer thread object exists?", ; print blk.timeouts[0].timer
print "Try cancel on a cancelled timer thread:"
blk.timeouts[0].cancel()

print; print "--- Test 3, restart with additional info in ev_dc:"
blk.timeouts[0].start(3, ev_dc={'name':'My Timeout!'})

