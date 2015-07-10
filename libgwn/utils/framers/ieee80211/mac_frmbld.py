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


'''A library to build frames from specifications.
'''


import struct
from frames import Frame
from mac_frmspecs import *
import mac_frmspecs

from frames import FieldTemplate


def mkfrmobj(pkt):
    '''Makes a Frame object from a packed frame.

    Returns a Frame object with attributes and dictionaries loaded from a packed frame.
    @param pkt: a packed frame.
    @return: a Frame object.
    '''
    # make vars and dictionaries to return
    dc_frcl_fldvals, dc_fldvals, dc_frbd_fldvals = {}, {}, {}
    fc_obj = AFrameControl()                   # an FC object
    fc_obj.dc_fldvals = fc_obj.mkdic(pkt[:2])  # unpack FC field
    frmtype = fc_obj.getfctype()               # determine frame type from FC
    # create frame object of determined type, set FC field
    fr_obj = AFrame(frmtype, dc_fldvals={'frame_ctrl':pkt[:2]})
    fr_obj._fc_obj = fc_obj                    # assign FC object
    fr_obj.frame_len = len(pkt)                # set frame length from packet

    # extract frame body from packet and assign as field in frame object
    if fr_obj.dc_fields.has_key('frame_body'):
        fld_after = fr_obj.ls_fields[fr_obj.ls_fields.index('frame_body') + 1]
        fb_beg = fr_obj.dc_fields['frame_body'].beg
        fb_end = fr_obj.dc_fields[fld_after].beg
        body = pkt[fb_beg:fb_end]              # extract frame body from packet
        fr_obj.setfrmbdy(new_frmbdy=body)      # sets FB and adjusts FB template

    # build dictionary of field values, update in this object
    dc_fldvals = fr_obj.mkdic(pkt)             # extract values from packet
    fr_obj.updtfldvals(dc_fldvals=dc_fldvals)  # update in this object

    # create object for frame body and assign as attribute in frame object
    frmclass, frmbodyclass = mac_frmspecs.dc_frmclasses[frmtype]
    if frmbodyclass:
        _fb_obj = AFrameBody(frmbodyclass)
        body_pkt = fr_obj.dc_fldvals['frame_body']
        _fb_obj.dc_fldvals = _fb_obj.mkdic(body_pkt)
        #_fb_obj.updtfldvals(dc_fldvals=dc_frbd_fldvals)
        fr_obj._fb_obj = _fb_obj
        fr_obj.dc_frbd_fldvals = _fb_obj.dc_fldvals
    else:
        _fb_obj = None

    fr_obj.frmkpkt = pkt
    return fr_obj



### an Exception for MAC frames

class MacFrameException(Exception):
    '''An exception class for MAC frames.
    '''
    def __init__(self, msg):
        '''Exception constructor.
        
        @param msg: a message for the programmer to describe the exception.
        '''
        self.msg = msg
    def __str__(self):
        return repr(self.msg)



### Frame Control field class

class AFrameControl(Frame):
    '''Frame Control (FC) field for MAC frame.
    
    A class to define frame control field in MAC frames.
    @ivar frmtype: a conventional name for the type of frame.
    @ivar bitbyte: 'bits' or 'bytes', indicates how this frame will be parsed.
    @ivar frame_len: the actual length of this frame.
    @ivar masklen: length of bitmask.
    @ivar dc_fields: a dictionary of {field: FieldTemplate} for field parsing.
    @ivar dc_fldvals: a dictionary of {field: value} to update dictionary of field values in frame body.
    '''
        
    def __init__(self, frmtype='', dc_fldvals={}):
        '''A Frame Control field structure.
        
        @param frmtype: conventional name for frame type.
        @param dc_fldvals: a dictionary of {field: value} to update field values.
        '''
        #frmclass = mac_frmspecs.FrmCtrlSpecs
        self.frmtype = 'FC'
        frmclass = FrmCtrlSpecs
        self.bitbyte = frmclass.bitbyte
        self.frame_len = frmclass.frame_len
        self.mask_len = frmclass.mask_len
        self.ls_fields = copy.copy(frmclass.ls_fields)
        self.mkdcfields(frmclass._dc_fields)
        self.dc_fldvals = copy.copy(frmclass.dc_fldvals)
        self.dc_fldvals.update(dc_fldvals)   # update field values
        if frmtype:
            self.setfctype(frmtype)          # set FC cat, type, subtype
        return


    def setfctype(self, frmtype):
        '''Sets frame control values for a certain frame type.

        @param frmtype: a frame type.
        @raises MacFrameException: on wrong frame type name.
        '''
        if mac_frmspecs.FrmCtrlSpecs.dc_frmtype.has_key(frmtype):
            self.dc_fldvals.update( \
                mac_frmspecs.FrmCtrlSpecs.dc_frmtype[frmtype] )
        else:
            msg = 'in Frame Control, wrong frame type ' + frmtype
            raise MacFrameException(msg)

        return


    def getfcint(self):
        '''Get frame control value as an 2-byte int.

        @return: frame control value as an 2-byte int.
        '''
        pkint = 0
        for fld in self.ls_fields:
            pkint = pkint | self.dc_fldvals[fld] << \
                (self.mask_len - self.dc_fields[fld].end)
        return pkint


    def getfctype(self):
        '''Return frame conventional name.
        
        @return: conventional frame name, or None if no valid combination of values.
        '''
        dc_frmtype = mac_frmspecs.FrmCtrlSpecs.dc_frmtype
        for key in dc_frmtype.keys():
            if dc_frmtype[key] == { \
                'ProtVer': self.dc_fldvals['ProtVer'], \
                'Type': self.dc_fldvals['Type'], \
                'SubType': self.dc_fldvals['SubType'] }:
                return key
        else:
            return None



### a generic frame class

class AFrame(Frame):
    '''A frame of any type, uses frame specs to build.

    @todo: revise coordination with ancestor class Frame.
    
    @ivar frmtype: a conventional name for the type of frame.
    @ivar bitbyte: 'bits' or 'bytes', indicates how this frame will be parsed.
    @ivar frame_len: the actual length of this frame.
    @ivar _fc_obj: a Frame Control object for this frame.
    @ivar _fb_obj: a frame body object for the frame body of this frame, if the frame body is structured, as in Management Mesh Action frames; None if frame body is data.
    @ivar dc_fields: a dictionary of {field: FieldTemplate} for field parsing.
    @ivar dc_fldvals: a dictionary of {field: value} to update dictionary of field values in frame body.
    @ivar frmpkt: the frame packed into binary data as for transmission. Defaults to None, load using self.mkpkt().
    '''

    def __init__(self, frmtype, \
        dc_frcl_fldvals={}, dc_fldvals={}, dc_frbd_fldvals={}):
        '''Builds a frame of any type, according to given  parameter values.

        @param frmtype: a conventional name for the type of frame.
        @param dc_frcl_fldvals: a dictionary of {field: value} to update dictionary of field values in Frame Control field.
        @param dc_fldvals: a dictionary of {field: value} to update dictionary of field values in this frame.
        @param dc_frbd_fldvals: a dictionary of {field: value} to update dictionary of field values in frame body.
        
        >>> ac1 = AFrame('Action', dc_fldvals={'fcs':555, 'address_1':'aaaaaa', 'address_2':'bbbbbb'}, dc_frbd_fldvals={'TCPreq':222}, dc_frcl_fldvals={'ToDS':True})
        >>> ac1.dc_fldvals['fcs'], ac1.dc_fldvals['address_1'], ac1.dc_fldvals['address_2']
        (555, 'aaaaaa', 'bbbbbb')
        >>> ac1.dc_frbd_fldvals['TCPreq']
        222
        >>> ac1.dc_frcl_fldvals['ToDS']
        True
        '''
        self.frmtype = frmtype

        self.dc_fldvals = dc_fldvals
        self.dc_frbd_fldvals = dc_frbd_fldvals
        if mac_frmspecs.dc_frmclasses.has_key(frmtype):
            frmclass, frmbodyclass = \
                mac_frmspecs.dc_frmclasses[self.frmtype]
        else:
            raise MacFrameException('AFrame: wrong frmtype,' + frmtype)
        self.bitbyte = frmclass.bitbyte
        self.frame_len = frmclass.frame_len
        self.mask_len = frmclass.mask_len    # bytes, no bitmask
        self.ls_fields = copy.copy(frmclass.ls_fields)
        self.mkdcfields(frmclass._dc_fields)
        self.dc_fldvals = copy.copy(frmclass.dc_fldvals)
        # produce frame control field value from FCframe object
        self._fc_obj = AFrameControl(self.frmtype)
        #self._fc_obj.setfctype(frmclass.frmtype)
        self._fc_obj.dc_fldvals.update(dc_frcl_fldvals)
        self.updtfldvals({'frame_ctrl':self._fc_obj.getfcint()})
        self.dc_frcl_fldvals = self._fc_obj.dc_fldvals  # point to FC obj dic
        # update other field values for this frame
        self.updtfldvals(dc_fldvals)
        # load frame body field if frame type stores mgmt info in it
        if frmbodyclass:   # frame body with mgmt info
            self._fb_obj = AFrameBody(frmbodyclass, \
                 dc_fldvals=dc_frbd_fldvals)
            self.updtfldvals({'frame_body':self._fb_obj.mkpkt()})
            self.dc_frbd_fldvals = self._fb_obj.dc_fldvals  # point to FB obj dic
        else:
            self._fb_obj = None     # required to recognize FB with data
            self.dc_frbd_fldvals = {}
        self.frmpkt = None          # load using self.mkpkt()
        #self.frmpkt = self.mkpkt()
        return


class AFrameBody(Frame):
    '''A class to build a frame body field.

    @ivar frmtype: a conventional name for the type of frame.
    @ivar bitbyte: 'bits' or 'bytes', indicates how this frame will be parsed.
    @ivar frame_len: the actual length of this frame.
    @ivar masklen: length of bitmask.
    @ivar dc_fields: a dictionary of {field: FieldTemplate} for field parsing.
    @ivar dc_fldvals: a dictionary of {field: value} to update dictionary of field values in frame body.
    '''
    def __init__(self, frmclass, dc_fldvals={}):
        '''Constructor.
        
        A frame body class for frames in which frame body is structured.
        @param frmclass: the frame body class to build frame body field.
        @param dc_fldvals: dictionary {field: value}.
        '''
        #frmclass, frmbodyclass = mac_frmspecs.getfrmclass(frmtype)
        self.frmtype = 'FrameBody'
        self.bitbyte = frmclass.bitbyte
        self.frame_len = frmclass.frame_len
        self.mask_len = frmclass.mask_len    # bytes, no bitmask
        self.ls_fields = copy.copy(frmclass.ls_fields)
        self.mkdcfields(frmclass._dc_fields)
        self.dc_fldvals = copy.copy(frmclass.dc_fldvals)
        # update field values for this frame
        self.updtfldvals(dc_fldvals)
        return


### classes to make frames of specified types

class ADataFrame(AFrame):
    '''A class to ease creation of Data frames.
    '''
    pass

class ACtrlFrame(AFrame):
    '''A class to ease creation of Control frames.
    '''
    pass
    
class AMgmtFrame(AFrame):
    '''A class to ease creation of Management frames.
    '''
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()

