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


'''Functions to create events of different types.

To create an event object use function C{mkevent()}. This function creates events of different types, according to the event modules imported by this module.
'''

import sys
import types

from gwnevent import EventNameException

import utils.framers.ieee80211.evframes80211 as evframes80211

#sys.path = sys.path + ['..']



def mkevent(nickname, ev_dc={}, payload='', frmpkt=''):        #**kwargs):
    '''Returns an event of the given event nickname.

    This function creates an event of the adequate event type and main attributes based only in the nickname. To this purpose, the nickname given as a parameter is searched in a dictionary of valid nicknames; this dictionary provides a mapping of nicknames to type, subtype and generating class.

    This function receives a list of keyword arguments, variable according to the type of event to create. Besides, the programmer may include any keyword, under her own responsibility.
    @param nickname: a valid event nickname, i.e. one that is a key in dictionary of valid nicknames.
    @param ev_dc: a dictionary {field_name: value} for event creation; defaults to an empty dictionary.
    @param payload: a data event payload, defaults to the empty string.
    @param frmpkt: a binary packed frame, defaults to the empty string.
    @return: an Event object.
    '''

    from gwnevent_dc import ev_dc_nicknames
    import utils.framers.ieee80211.evframes80211

    # determine and assign frame length if there is a frame packet
    if frmpkt:
        ev_dc['frame_length'] = len(frmpkt)
    elif ev_dc.has_key('frmpkt'):
        ev_dc['frame_length'] = len(ev_dc['frmpkt'])

    # create event from nickname
    if ev_dc_nicknames.has_key(nickname):
        ev_type, ev_subtype, eventclass = ev_dc_nicknames[nickname]
        #ev = eventclass(nickname, ptype, psubtype, ev_dc)
        ev = eventclass(nickname, ev_type, ev_subtype, ev_dc=ev_dc)

    # an IEEE 802.11 frame event, see if it can be generalized and decoupled
    elif evframes80211.dc_nicknames.has_key(nickname):
        ev_type, ev_subtype, eventclass = evframes80211.dc_nicknames[nickname]
        ev = eventclass(nickname, ev_type, ev_subtype, frmpkt, ev_dc)
        #ev.payload = payload
        #return ev

    else:
        raise EventNameException(nickname + ' is not a valid nickname.')

    # add complementary attributes, if given
    if payload:
        ev.payload = payload
    if frmpkt:
        ev.frmpkt = frmpkt

    ## add complementary attributes from ev_dc if required
    # if ev_dc.has_key('some_key_1'):
    #       ev.some_key_1 = ev_dc['some_key_1']

    return ev



if __name__ == '__main__':
    import doctest
    doctest.testmod()
