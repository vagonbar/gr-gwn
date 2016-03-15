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


'''A generic class for events of all types.

Class Event is a generic class for all types of events. Class Event is expected to be specialized into different, more specific types of events, implemented as subclasses. A hierarchy of event types and subtypes is possible. Events are distinguished by a nickname, a descriptive name used to recognize the type of event whatever their position in the event class hierarchy. Event nicknames are a convention of this project.

Nickname: 1. A descriptive name added to or replacing the actual name of a person, place, or thing (American Heritage Dictionary).

To create an event object use function C{events.mkevent()}. This function creates events of different types, according to the event modules imported by this module.
'''

import sys
import types

### for IEEE 802.11, not in generic GWN blocks
#from utils.framers.ieee80211.frames import addrmac2pkt, addrpkt2mac



sys.path = sys.path + ['..']



class Event:
    '''Events interchanged by blocks.

    Events are the objects interchanged by blocks in GWN. Events of a certain type are described by a nickname, from which type, subtype are determined. Nicknames are recorded in dictionary gwnevent_dc.dc_nicknames.
    @ivar nickname: a descriptive name to indicate the type of event.
    @ivar ev_type: the event type.
    @ivar ev_subtype: the event subtype.
    @ivar ev_dc: a dictionary of complementary data, e.g. {'add_info': 'additional information'}.
    '''

    def __init__(self, nickname, ev_type, ev_subtype, ev_dc={}):
        '''Constructor.
        
        @param nickname: a descriptive name to indicate the type of event.
        '''
        self.nickname = nickname
        self.ev_type = ev_type
        self.ev_subtype = ev_subtype
        self.ev_dc = ev_dc
        
    def __str__(self):
        ss = 'Event class name: ' + self.__class__.__name__
        ss += "\nNickname: '%s'; Type: '%s'; SubType: '%s'"  % \
            (self.nickname, self.ev_type, self.ev_subtype)
        ss += '\nEvent dict: ' + str(self.ev_dc)
        #for key in self.ev_dc.keys():
        #    ss += '\n  ' + key + ': ' + str(self.ev_dc[key])
        return ss

    def getname(self):
        '''Returns event nickname.
        
        TODO: see if really needed, nickname is public
        '''
        return self.nickname



class EventConfig(Event):
    '''A Configuration Event.

    A Configuration Event is used to set some behavior in blocks.
    '''
    def __init__(self, nickname, ev_type, ev_subtype, ev_dc={}):
        '''Constructor. Creates a Configuration Event.
        '''
        Event.__init__(self, nickname, ev_type, ev_subtype, ev_dc)


    def __str__(self):
        ss = Event.__str__(self)
        return ss



class EventTimer(Event):
    '''A Timer Event.

    A Timer Event is sent by a block to signal other blocks a certain instant in time.
    '''
    def __init__(self, nickname, ev_type, ev_subtype, ev_dc={}):
        '''Constructor. Creates a Timer Event.
        '''
        Event.__init__(self, nickname, ev_type, ev_subtype, ev_dc)

    def __str__(self):
        ss = Event.__str__(self)
        return ss



class EventComm(Event):
    '''A Comunication Event.

    A Communications Event contains information of interest for the communication with entities outside the flowgraph, via the operating system, a hardware communications device, or through some other means. A Communication Event happens between a source entity and a destination entity, hence the presence of a source address and a destination addess. Information may be some type of payload to be moved from source to destination, or some control or management information sent from source to destination.
    '''
 
    def __init__(self, nickname, ev_type, ev_subtype, ev_dc={}, \
            src_addr='', dst_addr='', payload='', frmpkt=''):
        '''Constructor. Creates a Communications Event.

        @param src_addr: source address.
        @param dst_addr: destination address.
        @param payload: data to be carried from source to destination.
        @param frmpkt: a binary packed frame, defaults to the empty string.
        '''
        Event.__init__(self, nickname, ev_type, ev_subtype, ev_dc)
        #self.src_addr = addrmac2pkt(src_addr)
        #self.dst_addr = addrmac2pkt(dst_addr)
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.payload  = payload
        self.frmpkt = frmpkt

    def __str__(self):
        ss = Event.__str__(self)
        #ss += '\n  ' + 'src_addr: ' + addrpkt2mac(self.src_addr)
        #ss += '\n  ' + 'dst_addr: ' + addrpkt2mac(self.dst_addr)
        ss += '\n  ' + 'src_addr: ' + self.src_addr
        ss += '\n  ' + 'dst_addr: ' + self.dst_addr
        ss += '\n  ' + 'payload: ' + self.payload
        ss += '\n  ' + 'frmpk: ' + repr(self.frmpkt)
        return ss


class EventNameException(Exception):
    '''An exception to rise on non valid parameters for event construction.
    '''
    pass 





if __name__ == '__main__':
    import doctest
    doctest.testmod()


