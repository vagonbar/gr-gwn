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


'''An interface for the events library with string based test frames.

This module is an interface to the events module.

To create an event object use function C{mkevent()}. This function creates events of different types, according to the event modules imported by this module. 

To add different types of events:

    - import library of specific event type.
    - add to function mkevent as necessary.
'''

import sys
sys.path += ['..']

import gwnevents.api_events as events
# event modules, for different types of events
#import evtimer
#import evconfig
import utils.framers.ieee80211.evframes80211 as evframes80211

from utils.framers.ieee80211.mac_frmbld import MacFrameException
from frames import EventFrameException
from gwnevents.gwnevent import EventNameException 

# import api_frames for test function
from utils.framers.ieee80211 import api_frames as api_frames


"""
class EventFrameException(Exception):
    '''An exception to rise on Event to/from Frame conversion.
    '''
    pass 
"""



"""
def mkevent(nickname, **kwargs):
    '''Returns an event of the given event nickname.

    @param nickname: a valid event nickname, i.e. one that is a key in dictionary of valid nicknames.
    @param kwargs: a dictionary of variables depending on the type of event. Field C{ev_dc} is a dictionary of fields and values for the corresponding event type; field C{frmpkt} is a binary packed frame.
    @return: an Event object.
    '''
    frmpkt, ev_dc = '', {}
    if kwargs.has_key('ev_dc'):
        ev_dc = kwargs['ev_dc']
    if kwargs.has_key('frmpkt'):
        frmpkt = kwargs['frmpkt']
        ev_dc['frame_length'] = len(frmpkt)
    else:
        ev_dc['frame_length'] = 0
        frmpkt = ''
    if kwargs.has_key('payload'):
        payload = kwargs['payload']
    else:
        payload = ''
    if evtimer.dc_nicknames.has_key(nickname):
        ptype, psubtype, eventclass = evtimer.dc_nicknames[nickname]
        return eventclass(nickname, ptype, psubtype, ev_dc)    
    elif evframes80211.dc_nicknames.has_key(nickname):
        ev_type, ev_subtype, eventclass = evframes80211.dc_nicknames[nickname]
        ev = eventclass(nickname, ev_type, ev_subtype, frmpkt, ev_dc)
        ev.payload = payload
        return ev
    elif evconfig.dc_nicknames.has_key(nickname):
        ptype, psubtype, eventclass = evconfig.dc_nicknames[nickname]
        return eventclass(nickname, ptype, psubtype, ev_dc)    
    else:
        raise EventNameException(nickname + ' is not a valid nickname.')
"""



def frmtoev(frmobj):
    '''Make an Event object from a Frame object.
    
    @param frmobj: a Frame object.
    @return: an Event object.
    '''

    # load event fields common to all types of frames
    ev_dc = {}
    payload = ''
    ev_dc['duration'] = frmobj.dc_fldvals['duration']
    ev_dc['frame_length'] = frmobj.frame_len

    # determine frame type; if Action, determine type of action frame
    # load event fields accordint to type of frame
    if frmobj.frmtype == 'Action':                        # Mgmt Action frame
        act = frmobj.dc_frbd_fldvals['Action']
        if act == 1:
            nickname = 'ActionOpen'
        elif act == 2:
            nickname = 'ActionConfirm'
        elif act == 3:
            nickname = 'ActionClose'
        else:
          #raise MacFrameException('invalid Action field code: ' + act)
          print 'error in action field'
          return
        ev_dc['src_addr'] = frmobj.dc_fldvals['address_1'] # Mgmt, Data frames
        ev_dc['dst_addr'] = frmobj.dc_fldvals['address_2'] # Mgmt, Data frames
        ev_dc['peerlinkId'] = frmobj.dc_frbd_fldvals['peerlinkId']
    elif frmobj.frmtype in ['Beacon']:                    # Mgmt Beacon frame
        nickname = 'MgmtBeacon'
        ev_dc['src_addr'] = frmobj.dc_fldvals['address_1'] # Mgmt, Data frames
        ev_dc['dst_addr'] = frmobj.dc_fldvals['address_2'] # Mgmt, Data frames
        ev_dc['peerlinkId'] = frmobj.dc_frbd_fldvals['peerlinkId']
    elif frmobj.frmtype == 'Data':      # a Data event
        nickname = 'DataData'
        ev_dc['src_addr'] = frmobj.dc_fldvals['address_1'] # Mgmt, Data frames
        ev_dc['dst_addr'] = frmobj.dc_fldvals['address_2'] # Mgmt, Data frames
        payload = frmobj.dc_fldvals['frame_body']
    elif frmobj.frmtype in ['RTS', 'CTS', 'ACK']:    # Ctrl frames
        nickname = 'Ctrl' + frmobj.frmtype[-3:]      # CtrlRTS --> RTS
        if frmobj.dc_fldvals.has_key('ta'):
            ev_dc['src_addr'] = frmobj.dc_fldvals['ta']
        ev_dc['dst_addr'] = frmobj.dc_fldvals['ra']
    else:
        raise MacFrameException(frmogj.frmtype + ' not a valid frame type')
        
    # make Event object
    ev = events.mkevent(nickname, ev_dc=ev_dc, payload=payload)
    ev.ev_dc['frame_length'] = frmobj.frame_len    # adjust frame length
    ev.frmpkt = frmobj.frmpkt
    ev.frmobj = frmobj    # ref to Frame obj associated with this event
    return ev


def evtofrm(evobj, fr_dc_fldvals={}, fr_dc_frbd_fldvals={}):
    '''Make a Frame object from an Event object.
    
    Dictionaries of field values C{dc_fldvals, dc_frbd_fldvals} allow to adjust values in frame object fields and in frame body fields of frame object, respectively. 
    @param evobj: an Event object.
    @param fr_dc_fldvals: dictionary of field values for frame object, default {}.
    @param fr_dc_frbd_fldvals: dictionary of field values for frame body in frame object, default {}.
    @return: a Frame object.
    '''
    if evframes80211.dc_evtoframes.has_key(evobj.nickname):
        frmname, dc_frbd_fldvals = evframes80211.dc_evtoframes[evobj.nickname]
        dc_frbd_fldvals.update(fr_dc_frbd_fldvals)
        dc_fldvals = fr_dc_fldvals
    else:
        raise EventFrameException(evobj.nickname + ' not a frame name')

    ## set frame field values from event field values
    dc_fldvals['duration'] = evobj.ev_dc['duration']
    if 'Ctrl' in evobj.nickname:        # a Ctrl event 
        dc_fldvals['ta'] = evobj.ev_dc['src_addr']
        dc_fldvals['ra'] = evobj.ev_dc['dst_addr']
    elif 'Mgmt' in evobj.nickname:      # a Mgmt event
        dc_fldvals['address_1'] = evobj.ev_dc['src_addr'] # Mgmt, Data frames
        dc_fldvals['address_2'] = evobj.ev_dc['dst_addr'] # Mgmt, Data frames
        if 'Beacon' in evobj.nickname:  # a Mgmt Beacon event
            dc_frbd_fldvals['peerlinkId'] = evobj.ev_dc['peerlinkId']        
    elif 'Action' in evobj.nickname:    # a Mgmt Action event
        dc_fldvals['address_1'] = evobj.ev_dc['src_addr'] # Mgmt, Data frames
        dc_fldvals['address_2'] = evobj.ev_dc['dst_addr'] # Mgmt, Data frames
        dc_frbd_fldvals['peerlinkId'] = evobj.ev_dc['peerlinkId']
    elif 'Data' in evobj.nickname:      # a Data event
        dc_fldvals['address_1'] = evobj.ev_dc['src_addr'] # Mgmt, Data frames
        dc_fldvals['address_2'] = evobj.ev_dc['dst_addr'] # Mgmt, Data frames
        dc_fldvals['frame_body'] = evobj.payload
    else:                               # an unknown type of event
        msg = 'not a valid event nickname for field settings'
        raise EventFrameException(evobj.nickname + msg)
    ##

    # make Frame object, record frame length
    frmobj = api_frames.mkframeobj(frmname, dc_fldvals=dc_fldvals, \
        dc_frbd_fldvals=dc_frbd_fldvals) 
    #evobj.ev_dc['frame_length'] = frmobj.frame_len
    evobj.frmpkt = frmobj.mkpkt()
    evobj.ev_dc['frame_length'] = len(evobj.frmpkt)
    evobj.frmobj = frmobj    # ref to Frame obj associated with this event
    return frmobj


    
if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass



