#!/usr/bin/python

# GNU Radio, message and PDU tests
# tests conversiones Event objects <---> PDUs
#
# PDU is a cons (car, cdr) where car, cdr are PMT types;
#  for CONS, CAR, CDR see
#     https://en.wikipedia.org/wiki/CAR_and_CDR
#     https://en.wikipedia.org/wiki/Cons
#  for the PMT functions see
#     http://gnuradio.org/doc/doxygen/page_pmt.html#pmt_pairs

"""
TODO: see if pmt.to_pmt, pmt_to_python work... seems no!
>>> pmt.pmt_to_python.pmt_from_dict(dic)
((b . 1) (a . 0))
>>> pmt_dic = pmt.pmt_to_python.pmt_from_dict(dic)
>>> pmt.pmt_to_python.pmt_to_dict(pmt_dic)
{'a': 0L, 'b': '1'}
"""

import sys
import pmt
import utils.framers.ieee80211.api_frmevs as api_frmevs
import utils.framers.ieee80211.api_frames as api_frames
from gwnevents import api_events as api_events 

# create event
ev_1 = api_events.mkevent('DataData')
print "[Evento 1]"
print ev_1
print

# create frame from event
frame_obj = api_frmevs.evtofrm(ev_1)

print "[Frame object]"
print frame_obj
print "[Event frame packet]"
print repr(ev_1.frmpkt)
print

send_str = ev_1.frmpkt
print "[Frame 1]"
print repr(send_str)    # repr() required! 
print

# frame to message
send_pmt = pmt.make_u8vector(len(send_str), ord(' '))
for i in range(len(send_str)):
	pmt.u8vector_set(send_pmt, i, ord(send_str[i]))
print "[send PMT]"
print repr(send_pmt)
print
print "[PMT is u8vector]", pmt.is_u8vector(send_pmt)
print

# message to PDU
car = pmt.PMT_NIL   # metadata
cdr = send_pmt
send_pdu = pmt.cons(car, cdr)
print "[PDU to sent]"
print "   [car]", car
print "   [cdr]", cdr
print

# transmit and receive
rec_pdu = send_pdu

# PDU to message
# Collect metadata, convert to Python format:
car = pmt.to_python(pmt.car(rec_pdu))
# Collect message, convert to Python format:
cdr = pmt.cdr(rec_pdu)
print "[PDU received]"
print "   [car]", car
print "   [cdr]", cdr
print
# Convert to string:
rec_str = "".join([chr(x) for x in pmt.u8vector_elements(cdr)])

print "[rec_str == send_str]", rec_str == send_str
print


# string to event
frm_rec_obj = api_frames.objfrompkt(rec_str)
ev = api_frmevs.frmtoev(frm_rec_obj)
print "[Event received]"
print ev
print






