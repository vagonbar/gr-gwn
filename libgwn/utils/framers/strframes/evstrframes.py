#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    This file is part of GNUWiNetwork,
#    Copyright (C) 2014 by 
#        Pablo Belzarena, Gabriel Gomez Sena, Victor Gonzalez Barbone,
#        Facultad de Ingenieria, Universidad de la Republica, Uruguay.
#
#    GNUWiNetwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GNUWiNetwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GNUWiNetwork.  If not, see <http://www.gnu.org/licenses/>.
#


'''A library for events with string frames.

This module uses a simplified frame format based on strings, aimed at testing; a primary concern is legilibilty, though some packing is done to keep frame length short.

This module defines two functions, mkevent() to make an Event object from a nickname or string frame, and mkframe() to make a string frame from an Event object.

Packet format:

    - nickname, a string.
    - payload length in string format.
    - dictionary of other fields in string format.
    - payload, a string.

Fields are separated by ','. Payload length is required to unpack, since ',' may be included in string format of dictionary or payload.

'''

import gwnevents.api_events as events
import gwnevents.gwnevent as gwnevent
import sys


def mkevent(nickname=None, frame=None, ev_dc={}, payload=''):
    '''Creates an event from a nickname or from a frame.
    
    This function accepts either an event nickname or a string frame, but not both. If an event nickname is given, an Event object of that nickname is created; if a string frame is given, an Event object is created from that frame.
    @param nickname: the event nickname, default None.
    @param frame: a frame in string format, default None.
    @param ev_dc: a dictionary {field_name: value} for event creation; defaults to an empty dictionary. Disregarded if a frame is given.
    @param payload: the payload, not included in dictionary to preserve binary string format as received.
    @return: an Event object.
    '''
    if not nickname and not frame:
        raise gwnevent.EventNameException('No event nickname or frame received')
    if nickname and frame:
        raise gwnevent.EventNameException( \
            'Both event nickname and frame received')
    if nickname:
        return events.mkevent(nickname, ev_dc=ev_dc, payload = payload)
    if frame:
        ev_dc = {}
        ### unpack frame
        try:
            nickname, sep, rest1 = frame.partition(',')
            strlen, sep, rest2 = rest1.partition(',')
            if int(strlen) == 0:
                str_ev_dc = rest2
            else:
                str_ev_dc, payload = rest2[:-int(strlen)], rest2[-int(strlen):]

            ev_dc = eval(str_ev_dc.strip(','))    # leaves out final comma

            # TODO: this function should adjust frame_length. How?
            #    frame_lenght must be set in ev_dc of Event. Is it used?
            ev_dc['frame_length'] = 0
        except:
            print "mkevent unpack error : ", repr(frame)
            print "  nickname:", nickname
            print "  str_ev_dc:", str_ev_dc
            print "  payload:", payload
            return None
        try:
            ev = events.mkevent(nickname, frmpkt=frame, ev_dc=ev_dc)
            ev.payload = payload
            return  ev
        except:
            #raise events.EventNameException( \
            #    'cannot generate event: malformed packet\n' + \
            #    frame)
            print 'evstrframes: cannot generate event: malformed packet'
            print repr(frame)
            return None



def mkframe(ev_obj):
    '''Creates a string frame from an Event object.
    
    Receives an Event object, returns a string frame with the event information.
    @param ev_obj: an Event object.
    @return: a frame in string format.
    '''
    if not isinstance(ev_obj, gwnevent.Event):
        raise gwnevent.EventNameException('Parameter is not an Event object.')
        return None

    # unnecessary, ev_dc always included in mkevent, even if empty
    #if not ev_obj.ev_dc:
    #    raise events.EventNameException('ev_dc not in event object.')

    # TODO: see if all these validations are required, or force fields
    #   to be present by other means, e.g. a default ev_dc
    # WARNING: following lines impose values on these fields!
    #if not ev_obj.ev_dc.has_key('src_addr') or \
    #    not ev_obj.ev_dc.has_key('dst_addr'):
    #    raise events.EventNameException( \
    #        'ev_dc does not contain src_addr, dst_addr keys.')
    #if not ev_obj.nickname:
    #    raise events.EventNameException( 'even with no nickname.')
    if not ev_obj.ev_dc['src_addr']:
        ev_obj.ev_dc['src_addr'] = ''
    if not ev_obj.ev_dc['dst_addr']:
        ev_obj.ev_dc['dst_addr'] = ''
    if not ev_obj.ev_dc['peerlinkId']:
        ev_obj.ev_dc['peerlinkId'] = 0
    ### end of WARNING
    #
    # frame_length cannot be included in packet, alters frame_length!
    #    other encoding must be used to inclue frame_length in packet
    ### pack frame

    frame = '' + ev_obj.nickname + ',' + str(len(ev_obj.payload)) + ',' + \
        str(ev_obj.ev_dc)
    if ev_obj.payload:
        frame = frame + ',' + ev_obj.payload
    #print "mkframe   ", frame
    ev_obj.frmpkt = frame
    ev_obj.ev_dc['frame_length'] = len(ev_obj.frmpkt)
    return frame


if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass




