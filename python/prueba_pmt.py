#!/usr/bin/python


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

print "[PMT is u8vector]", pmt.is_u8vector(send_pmt)
print

# message to PDU
send_pdu = send_pmt

# transmit
rec_pdu = send_pdu

# PDU to message
rec_pmt = rec_pdu

# message to string
rec_str = "".join([chr(x) for x in pmt.u8vector_elements(rec_pmt)])
print "[Frame 2]"
print repr(rec_str)
print

print "[rec_str == send_str]", rec_str == send_str
print

# string to event
frm_rec_obj = api_frames.objfrompkt(rec_str)
ev = api_frmevs.frmtoev(frm_rec_obj)
print "[Event received]"
print ev
print






