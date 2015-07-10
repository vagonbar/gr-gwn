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



'''Model classes for specification of frame structures.

@var dc_frmclasses: A dictionary {frame_name: (frame_class, framebody_class) }, where frame class is the class which builds the frame, and framebody_class is the class which builds the frame body, if the frame body is structured, as in Management frames.
'''

import copy


class FrameSpecsException(Exception):
    '''An exception class for frame specifications.
    '''
    def __init__(self, msg):
        '''Exception constructor.
        
        @param msg: a message for the programmer to describe the exception.
        '''
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class FrameSpecs(object):
    '''A generic class for Frame Specification subclasses.
    
    See documentation of attribute variables in L{Frame} class.
    '''



### Control frames

class CtrlRTS(FrameSpecs):
    '''Specification for Control RTS frames.
    '''
    frmtype = 'RTS'
    bitbyte = 'bytes'
    frame_len = 20
    mask_len = 0    # bytes, no bitmask
    ls_fields = ['frame_ctrl', 'duration', 'ra', 'ta', 'fcs']
    _dc_fields        = {\
        'frame_ctrl' : ( 0,  2, False, '!H'  ), \
        'duration'   : ( 2,  4, False, '!H'  ), \
        'ra'         : ( 4, 10, False, '!6s' ), \
        'ta'         : (10, 16, False, '!6s' ), \
        'fcs'        : (16, 20, False, '!I'  ) \
        }
    dc_fldvals = { \
        'frame_ctrl' : 0, \
        'duration'   : 0, \
        'ra'         : 'ra-rts', \
        'ta'         : 'ta-rts', \
        'fcs'         : 0 }
    dc_frbd_fldvals = {}



class CtrlCTS(FrameSpecs):
    '''Specification for Control CTS frames.
    '''
    frmtype = 'CTS'
    bitbyte = 'bytes'
    frame_len = 14
    mask_len = 0    # bytes, no bitmask
    ls_fields = ['frame_ctrl', 'duration', 'ra', 'fcs']
    _dc_fields        = {\
        'frame_ctrl' : ( 0,  2, False, '!H' ), \
        'duration'   : ( 2,  4, False, '!H'  ), \
        'ra'         : ( 4, 10, False, '!6s' ), \
        'fcs'        : (10, 14, False, '!I'  ) \
        }
    dc_fldvals = { \
        'frame_ctrl' : 0, \
        'duration'   : 0, \
        'ra'         : 'ra-cts', \
        'fcs'         : 0 }
    dc_frbd_fldvals = {}

    
class CtrlACK(FrameSpecs):
    '''Specification for Control ACK frames.
    '''
    frmtype = 'ACK'
    bitbyte = 'bytes'
    frame_len = 14
    mask_len = 0    # bytes, no bitmask
    ls_fields = ['frame_ctrl', 'duration', 'ra', 'fcs']
    _dc_fields        = {\
        'frame_ctrl' : ( 0,  2, False, '!H' ), \
        'duration'   : ( 2,  4, False, '!H'  ), \
        'ra'         : ( 4, 10, False, '!6s' ), \
        'fcs'        : (10, 14, False, '!I'  ) \
        }
    dc_fldvals = { \
        'frame_ctrl' : 0, \
        'duration'   : 0, \
        'ra'         : 'ra-ack', \
        'fcs'         : 0 }
    dc_frbd_fldvals = {}


### Management frames

class MgmtFrame(FrameSpecs):
    '''Specification for Management frames.
    '''
    frmtype = 'Mgmt'
    bitbyte='bytes'
    frame_len = 28  # length with 0 bytes in frame body   
    mask_len = 0    # bytes, no bitmask
    ls_fields= ['frame_ctrl', 'duration', 'address_1', 'address_2', \
            'address_3', 'seq_ctrl', 'frame_body', 'fcs']
    _dc_fields =  {\
        'frame_ctrl' : ( 0,  2,   False,   '!H' ), \
        'duration'   : ( 2,  4,   False,   '!H'  ), \
        'address_1'  : ( 4, 10,   False,   '!6s' ), \
        'address_2'  : (10, 16,   False,   '!6s' ), \
        'address_3'  : (16, 22,   False,   '!6s' ), \
        'seq_ctrl'   : (22, 24,   False,   '!H'  ), \
        'frame_body' : (24, -4,   False,   '!s'  ), \
        'fcs'        : (-4, 48,   False,   '!I'  )   \
        }
    dc_fldvals =  {  \
        'frame_ctrl' : 0, \
        'duration'   : 0, \
        'address_1'  : 'dt-ad1-', \
        'address_2'  : 'dt-ad2-', \
        'address_3'  : 'dt-ad3-', \
        'seq_ctrl'   : 0, \
        'frame_body' : 'generic frame body20', \
        'fcs'        : 0 \
        }
    dc_frbd_fldvals = {}


# Management frames, frame bodies

class BeaconFrameBody(FrameSpecs):
    '''Specification for Beacon frame body.

    NOTE: added peerlinkId for testing events; to be revised.
    '''
    frmtype = 'BeaconFrameBody'
    bitbyte = 'bytes'
    frame_len = 60
    mask_len = 0    # bytes, no bitmask
    ls_fields = ['Timestamp', 'BeaconInterval', 'CapabilitiesInfo', 'SSID', 'SupportedRates', 'peerlinkId']
    _dc_fields              = {\
        'Timestamp'        : ( 0,  8, False, '!Q'   ), \
        'BeaconInterval'   : ( 8, 10, False, '!H'   ), \
        'CapabilitiesInfo' : (10, 12, False, '!H'   ), \
        'SSID'             : (12, 46, False, '!34s' ), \
        'SupportedRates'   : (46, 58, False, '!12s' ), \
        'peerlinkId'       : (58, 60, False, '!H'   )  \
        }
    dc_fldvals        = { \
        'Timestamp'        :   1, \
        'BeaconInterval'   :   1, \
        'CapabilitiesInfo' :   1, \
        'SSID'             :   chr(0) + chr(32) + 'S'*32, \
            #'-'*34, \
            #chr(0) + chr(32) + 'S'*32, 
            #struct.pack('!2c', 0 , 32) + 'S'*32, \
        'SupportedRates'   :  '-'*12, \
            #chr(1) + chr(10) + 'R'*10,
            #struct.pack('!2c', 0 , 10) +'R'*10 \
        'peerlinkId'       :  0 \
        }
    #dc_frbd_fldvals = {}


class MeshActionFrameBody(FrameSpecs):
    '''Specification for Action frame bodies.

    IEEE 802.11-2012 sec 8.3.3.13 pag 436.

    Example: 8.5.2.4 TPC Request frame format; different fields for different types of Action frames.
    Category 13: Mesh (table 8-38); Action: 1 Open, 2 Confirm, 3 Close (table 8-261).

    NOTE: added peerlinkId for testing events; to be revised.    
    Field peer Link ID: IEEE 802.11-2012 sec 8.4.2.104; in table 8-54, element 117: Mesh Peering Management, length = 5, 7, 9, 21, 23, or 25.
    '''
    frmtype = 'MeshActionFrameBody'
    bitbyte = 'bytes'
    frame_len = 7   # variable if vendor specific parameters are present
    mask_len = 0    # bytes, no bitmask
    ls_fields = ['Category', 'Action', 'Dialog', 'TCPreq', 'peerlinkId']
    _dc_fields = {\
        'Category'     : (0,  1, False, '!B'  ), \
        'Action'       : (1,  2, False, '!B'  ), \
        'Dialog'       : (2,  3, False, '!B'  ), \
        'TCPreq'       : (3,  5, False, '!H'  ), \
        'peerlinkId'   : (5,  7, False, '!H'  )  \
            }
    dc_fldvals = { \
        'Category'     : 13, \
        'Action'       :  1, \
        'Dialog'       :  0, \
        'TCPreq'       :  0, \
        'peerlinkId'   :  0  \
            }


### Data frame

class Data(FrameSpecs):
    '''Specification for a Data frame.
    '''
    frmtype = 'Data'
    bitbyte='bytes'
    frame_len = 40  # fixed frame length, with 0 in frame body
    mask_len = 0    # bytes, no bitmask
    ls_fields= ['frame_ctrl', 'duration', 'address_1', 'address_2', \
        'address_3', 'seq_ctrl', 'qos', 'ht', 'address_4', 'frame_body', 'fcs']
    _dc_fields =  {\
        'frame_ctrl' : ( 0,  2,   False,   '!H' ), \
        'duration'   : ( 2,  4,   False,   '!H'  ), \
        'address_1'  : ( 4, 10,   False,   '!6s' ), \
        'address_2'  : (10, 16,   False,   '!6s' ), \
        'address_3'  : (16, 22,   False,   '!6s' ), \
        'seq_ctrl'   : (22, 24,   False,   '!H'  ), \
        'qos'        : (24, 26,   False,   '!H'  ), \
        'ht'         : (26, 30,   False,   '!I'  ), \
        'address_4'  : (30, 36,   False,   '!6s' ), \
        'frame_body' : (36, -4,   False,   '!2342s'  ), \
        'fcs'        : (-4, -1,   False,   '!I'  )   \
            }
    dc_fldvals =  {  \
        'frame_ctrl' : 0, \
        'duration'   : 0, \
        'address_1'  : 'dt-ad1-', \
        'address_2'  : 'dt-ad2-', \
        'address_3'  : 'dt-ad3-', \
        'seq_ctrl'   : 0, \
        'qos'        : 0, \
        'ht'         : 0, \
        'address_4'  : 'dt-ad2-', \
        'frame_body' : 'this is the frame body!', \
        'fcs'        : 0 \
        }    

### Frame Control field

class FrmCtrlSpecs(FrameSpecs):
    '''Specification for Management Frame Control field.

    @ivar dc_frmtype: a dictionary of frame types. Keys are frame type names, e.g. 'RTS', 'Data'; values are a dictionary {'ProtVer':<int>, 'Type':<int>, 'SubType':<int>} which define the field values in frame control for the required frame type.
    '''
    frmtype = 'FrameControl'
    bitbyte = 'bits'
    frame_len = 2
    mask_len = 16
    ls_fields= ['ProtVer', 'Type', 'SubType', 'ToDS', 'FromDS', \
        'MoreFrags', 'Retry', 'PwrMgmt', 'MoreData', 'Protected', 'Order']
    _dc_fields      = { \
        'ProtVer'  : ( 6,  8, 0,     'int'  ), \
        'Type'     : ( 4,  6, 0,     'int'  ), \
        'SubType'  : ( 0,  4, 0,     'int'  ), \
        'ToDS'     : (15, 16, False, 'bool' ), \
        'FromDS'   : (14, 15, False, 'bool' ), \
        'MoreFrags': (13, 14, False, 'bool' ), \
        'Retry'    : (12, 13, False, 'bool' ), \
        'PwrMgmt'  : (11, 12, False, 'bool' ), \
        'MoreData' : (10, 11, False, 'bool' ), \
        'Protected': ( 9, 10, False, 'bool' ), \
        'Order'    : ( 8,  9, False, 'bool' )  \
         }
    dc_fldvals      = { \
        'ProtVer'  : 0, \
        'Type'     : 0, \
        'SubType'  : 0, \
        'ToDS'     : False, \
        'FromDS'   : False, \
        'MoreFrags': False, \
        'Retry'    : False, \
        'PwrMgmt'  : False, \
        'MoreData' : False, \
        'Protected': False, \
        'Order'    : False  \
         }
    dc_frmtype = { \
        'RTS'   : {'ProtVer':0, 'Type':1, 'SubType':11}, \
        'CTS'   : {'ProtVer':0, 'Type':1, 'SubType':12}, \
        'ACK'   : {'ProtVer':0, 'Type':1, 'SubType':13}, \
        'Data'  : {'ProtVer':0, 'Type':2, 'SubType':0}, \
        'Beacon': {'ProtVer':0, 'Type':0, 'SubType':8}, \
        'Action': {'ProtVer':0, 'Type':0, 'SubType':13} \
        }

            
### a dictionary of frame types and classes to build them
dc_frmclasses = { \
    'FC'    : (FrmCtrlSpecs, None), \
    'RTS'   : (CtrlRTS, None), \
    'CTS'   : (CtrlCTS, None), \
    'ACK'   : (CtrlACK, None), \
    'Data'  : (Data, None), \
    'Beacon': (MgmtFrame, BeaconFrameBody), \
    'Action': (MgmtFrame, MeshActionFrameBody),  \
    'BeaconFrameBody': (BeaconFrameBody, None) \
    }


def getfrmclass(frmtype):
    '''Returns classes to build an object of specified frame type.
    '''
    if dc_frmclasses.has_key(frmtype):
        frmclass, frmbodyclass = dc_frmclasses[frmtype]
    else:
        raise FrameSpecsException('Wrong frmtype,' + frmtype)
    return frmclass, frmbodyclass


def showfldvals(obj):
    '''Decently print all frame object information.

    @param obj: a frame object.
    '''
    print '--- Frame fields ---'
    print obj           # main frame fields
    print '--- Frame Control fields ---'
    print obj._fc_obj   # frame control
    if obj._fb_obj:
        print '--- Frame Body fields ---'
        print obj._fb_obj   # frame body
    return




