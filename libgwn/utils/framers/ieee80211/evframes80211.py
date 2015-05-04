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


'''A library for events with IEEE 802.11 frames.

@var dc_nicknames: a dictionary of nicknames, types, subtypes, and classnames, C{ {nickname: (type, subtype, classname)} }; C{classname} is the class used to build the object. This dictionary allows to build a frame event object by just saying its nickname. Module function C{mkevent()} uses this module variable.
'''

from gwnevents.gwnevent import Event, EventNameException
import api_frames


class EventFrame(Event):
    '''An event associated with a frame.
    
    @ivar nickname: a descriptive name for this event.
    @ivar ev_type: frame event type.
    @ivar ev_subtype: frame event subtype.
    @ivar ev_dc: a dictionary of complementary data, e.g. {'src_addr': source address, 'dst_addr': destination address, 'duration': duration}.
    @ivar frmpkt: a packed frame in bin format, as for transmission.
    @ivar frmobj: a reference to a Frame object on which this event originated; defaults to None.
    '''

    def __init__(self, nickname, ev_type, ev_subtype, frmpkt=None, ev_dc={}):
        '''Constructor.
        '''
        self.nickname = nickname
        self.ev_type = ev_type
        self.ev_subtype = ev_subtype
        self.frmpkt = frmpkt
        self.frmobj = None    # ref to Frame obj associated with this event
        self.ev_dc = { \
            'src_addr': 'addr_1', \
            'dst_addr': 'addr_1', \
            'duration': 10, \
            'retry': 0, \
            'frame_length': 0, \
            'peerlinkId': 0, \
            }
        self.payload = ''
        self.ev_dc.update(ev_dc)
        return

    def __str__(self):
        ss = Event.__str__(self)
        ss += '\n  Frame packet: ' + repr(self.frmpkt)   #str(self.frmpkt)
        ss += '\n  Payload: ' + repr(self.payload)
        #ss += '\n  Frame: ' + repr(self.frame)
        return ss

    def __eq__(self, other):
        eq = True
        if self.nickname != other.nickname or \
            self.ev_type != other.ev_type or \
            self.ev_subtype != other.ev_subtype:
            return False
        #self.frmpkt = frmpkt
        #self.frmobj = None    # ref to Frame obj associated with this event
        for fld in self.ev_dc.keys():
            if self.ev_dc[fld] != other.ev_dc[fld]:
                eq = False
                #print "Events not equal,", fld+':', \
                #    self.ev_dc[fld], other.ev_dc[fld]
                break
        return eq


class EventFrameMgmt(EventFrame):

    def __init__(self, nickname, ev_type, ev_subtype, frmpkt=None, ev_dc={}):
        '''Constructor.
        '''
        EventFrame.__init__(self, nickname, ev_type, ev_subtype, \
            frmpkt=frmpkt, ev_dc=ev_dc)
       
## dictionary of event nicknames to event type, subtype and build class
#    nickname         : (ev_type, ev_subtype, event class    )
dc_nicknames = { \
    'CtrlRTS'         : ('Ctrl',   'RTS',     EventFrame     ), \
    'CtrlCTS'         : ('Ctrl',   'CTS',     EventFrame     ), \
    'CtrlACK'         : ('Ctrl',   'ACK',     EventFrame     ), \
    'DataData'        : ('Data',   'Data',    EventFrame     ), \
    'ActionOpen'      : ('Mgmt',   'Action',  EventFrameMgmt ), \
    'ActionClose'     : ('Mgmt',   'Action',  EventFrameMgmt ), \
    'ActionConfirm'   : ('Mgmt',   'Action',  EventFrameMgmt ), \
    'MgmtBeacon'      : ('Mgmt',   'Beacon',  EventFrameMgmt ), \
    }

## dictionary of event nicknames to frame nicknames and field values
#    nickname         : (frame_type, dc_frbd_fldvals             )
dc_evtoframes = { \
    'CtrlRTS'         : ('RTS', {} ), \
    'CtrlCTS'         : ('CTS', {} ), \
    'CtrlACK'         : ('ACK', {} ), \
    'DataData'        : ('Data', {} ), \
    'ActionOpen'      : ('Action', {'Action':1} ), \
    'ActionClose'     : ('Action', {'Action':3}), \
    'ActionConfirm'   : ('Action', {'Action':2}), \
    'MgmtBeacon'      : ('Beacon', {} ), \
    }

dc_frametoev = {}
for evnm in dc_evtoframes.keys():
    (frmnm, dc_frbd_fldvals) = dc_evtoframes[evnm]
    dc_frametoev[frmnm] = evnm
    

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    

