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


'''Dictionary of valid nicknames and attribute values for each nickname.

This module provides a dictionary of valid nicknames for events, and the attributes corresponding to each nickname.
@var ev_dc_nicknames: a dictionary {nichname: (ev_type, ev_subtype, ev_class)} to determine type, subtype and event class corresponding to a certain nickname.
'''

from gwnevent import Event, EventNameException

timer_dc = { \
    'TimerTOH'        : ('Timer',  'TOH',      Event     ), \
    'TimerTOC'        : ('Timer',  'TOC',      Event     ), \
    'TimerTOR1'       : ('Timer',  'TOR1',     Event     ), \
    'TimerTOR2'       : ('Timer',  'TOR2',     Event     ), \
    'TimerTimer'      : ('Timer',  'Timer',    Event     ), \
    'TimerCTSTout'    : ('Timer',  'CTSTout',  Event     ), \
    'TimerRTSAbort'   : ('Timer',  'CTSTout',  Event     ), \
    'TimerACKTout'    : ('Timer',  'ACKTout',  Event     ), \
    'TimerDataAbort'  : ('Timer',  'ACKTout',  Event     ) \
    }


config_dc = { \
        'TimerConfig'          : ('Request',  'SetTimerConfig',      Event    ), \
        'EventConsumerStatus'  : ('Config',   'EventConsumerStatus', Event    ) \
    }
# change type to Config in all nicknames!

data_dc = { \
        'DataIn'           : ('Data',   'DataIn',  Event     ), \
        'DataOut'          : ('Data',   'DataOut', Event     )  \
    }

ctrl_dc = { \
        #'Nickname'        : ('Ctrl',   'SubType', Event    ), \
        #'Nickname'        : ('Ctrl',   'SubType', Event    )  \
    }

mgmt_dc = { \
        #'Nickname'        : ('Mgmt',   'SubType', Event    ), \
        #'Nickname'        : ('Mgmt',   'SubType', Event    )  \
    }



ev_dc_nicknames = {}

all_dics = [timer_dc, data_dc, ctrl_dc, mgmt_dc, config_dc]
for dic in all_dics:
    ev_dc_nicknames.update(dic)

# TODO: write a function check_dics() to verify a nickname is unique,
#  i.e. not in two different dictionaries in all_dics.






