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


# frames : general classes and functions to handle generic data communication packets or frames.

'''Classes and functions for generic frames.

@var FieldTemplate: a collections.namedtuple subclass for naming metadata items on fields; C{beg}, C{end} are list positions for slicing, C{inv} inverts bits if True, C{fmt} is the struct mask for packing, C{btmsk} is a bitmask for bit fields.

'''

import os
import struct
from collections import namedtuple

#import evframes80211

# the following comment is treated as a docstring for following variable
#: a collections.namedtuple subclass for naming metadata items on fields; 'beg', 'end' are list positions for slicing, 'inv' inverts bits if True, 'fmt' is the struct mask for packing, 'btmsk' is a bitmask for bit fields.
FieldTemplate = namedtuple('FieldTemplate', ['beg', 'end', 'inv', 'fmt', 'btmsk'])



def bin2(bb, bitlen=8, with0b=False):
    '''Converts number into binary string with 0 padding for specified length.
    
    Unlike builtin function bin(), this function pads with left '0' to reach the specified length in the returned binary string. Default length is 8, excluding initial '0b'.
    @param bitlen: length of binary string to return; default 8.
    @param with0b: if True, starts binary string with '0b'; default False.
    @return: a binary string of specified length.
    '''
    if with0b:
        return '0b' + '0'*(bitlen-len(bin(bb)[2:])) + bin(bb)[2:]
    else:
        return '0'*(bitlen-len(bin(bb)[2:])) + bin(bb)[2:]


def mkbm(beg, end, bm_len, as_int=True):
    '''Makes a bitmask, optionally return as int.
    
    @param beg: start position of sequence of 1s.
    @param end: end position of senquence of 1s plus 1, for correct slicing.
    @param bm_len: total length of bitmask.
    @param as_int: if True, return an int, otherwise return a binary string. Default True.
    @return: a bitmask, as a binary string or as int (the default).
    '''
    if as_int:
    	return int('0b' + '0'*(beg) + '1'*(end - beg) + '0'*(bm_len - end), 2)
    else:
       	return '0'*(beg) + '1'*(end - beg) + '0'*(bm_len - end)


def addrmac2pkt(addrmac):
    '''Packs a string MAC address into 6 bytes.

    Receives a MAC address in readable, string format such as '6c:62:6d:1c:cf:09' and packs it into 6 bytes. When received data is not a formally valid MAC address, returns '000000'.
    @param addrmac: a MAC address in string format such as '6c:62:6d:1c:cf:09'.
    @return: a MAC address packed in 6 bytes, or '000000' on error.
    '''
    addrmacls = addrmac.split(':')
    try:
        d1, d2, d3, d4, d5, d6 = [int(ii, 16) for ii in addrmacls]
        return struct.pack('BBBBBB', d1, d2, d3, d4, d5, d6)
    except:
        return struct.pack('BBBBBB', 0, 0, 0, 0, 0, 0)

def addrpkt2mac(addrpkt):
    '''Unpacks 6 bytes MAC address into string.

    Receives 6 bytes corresponding to a packed MAC address, unpacks it and presents it as a string formmatted address such as '6c:62:6d:1c:cf:09'. When received data is not a 6B string, returns '00:00:00:00:00:00'.
    @param addrpkt: a MAC address packed in 6 bytes.
    @return: a MAC address in string format such as '6c:62:6d:1c:cf:09', or '00:00:00:00:00:00' on error.
    '''
    # note: unpack() returns integers, hex() returns 1 or 2 chars,
    #   e.g. 12, 0a, 9; rjust() pads with '0' on the left, 09
    try:
        lsdd = struct.unpack('BBBBBB', addrpkt)
        addrmac = hex(lsdd[0])[2:].rjust(2,'0')
        for dd in lsdd[1:]:
            addrmac += ':' + hex(dd)[2:].rjust(2,'0')
        return addrmac
    except:
        return '00:00:00:00:00:00'



class FrameException(Exception):
    '''An exception class for general frames.
    '''
    def __init__(self, msg):
        '''Exception constructor.
        
        @param msg: a message for the programmer to describe the exception.
        '''
        self.msg = msg
    def __str__(self):
        return repr(self.msg)



class EventFrameException(Exception):
    '''An exception to rise on Event to/from Frame conversion.
    '''
    pass 



class Frame(object):
    '''A class to represent a general data communication frame or packet.
    
    An instantiation of this class with adequate values in member variables will represent a particular type of frame, such as a MAC frame, or the Frame Control field of a MAC frame, or any other type of frame. This class assumes a frame is a sequence of bytes which can be decomposed in a series of fields where different type of data are contained. Some variable members in this class describe these fields, and some others record the actual values for each field. This class allows the packing of data into a frame, and the unpacking of data from a frame.
    Field frontiers may be byte or bit defined; a variable member defines this.
    
    @todo: for bit fields, there may be a limit size; verify this, state limit.

    @todo: check these lengths for redundancy! Some may be calculated.
    
    @warning: not totally independent of frame structure. For instance, assumes FCS field of 4 bytes at end of frame; this is used to adjust length in frame body for data of variable length loaded in frame body.
    
    @ivar bitbyte: 'bits' or 'bytes', indicates how this frame will be parsed.
    @ivar frame_len: length of this frame.
    @ivar mask_len: length of mask, for bit fields.
    @ivar max_frame_len: maximum admitted frame length.
    @ivar body_len: actual frame body length.
    @ivar ls_fields: a list of field names used to display or process them in the usual order.
    @ivar dc_fields: a dictionary {field: tuple}, tuple defines field structure. The dictionary of fields in frame describes the position, structure, and type of data kept in each field. Key is field name, value is a named tuple L{FieldTemplate} including (begin, end, inv, type of data, bitmask); bitmask is used to extract bit fields; begin, end indicate positions of field in packed frame; inv is True if bits or bytes in field must be inverted for packing and unpacking; type indicates on which type each field is to be unpacked.
    @ivar dc_fldvals: a dictionary {field: value}; the key is the field name, value is the content in bytes of this field.
    '''
    #@ivar fixed_frame_len: length of fixed length part of frame; the sum of all fixed length fields in frame.


    def __init__(self):
        pass


    def mkdcfields(self, dc_fields):
        '''Makes dictionary of field structure using named tuples as values.
        
        Stores dictionary as instance attribute in object (self._dc_fields).
        @param dc_fields: a dictionary {field: tuple}, tuple defines field structure.
        '''
        _dc_fields = {}
        for fld in dc_fields.keys():  # load bitmask as first in template tuple
            beg, end, inv, fmt = dc_fields[fld]
            if self.bitbyte == 'bits':
                btmsk = mkbm(beg, end, self.mask_len, as_int=True)
            else:
                btmsk = 'bytes, no bitmask'
            _dc_fields[fld] = FieldTemplate(beg, end, inv, fmt, btmsk)
        self.dc_fields = _dc_fields
        return

    
    def fillfldvals(self, fillchr='0'):
        '''Fill values in {field : value} dictionary with int or character.
        
        For byte fields, if field is a string, values are filled with fillchr according to length and type of data in field values dictionary; if field is not a string, value is set to 0. For bit fields, values are set to 0.
        @param fillchr: the fill character, defaults to '0' for bytes, 0 for bits.
        '''
        if self.bitbyte == 'bytes':
            for fld in self.ls_fields:
                if type(self.dc_fldvals[fld]) == str:
                    fillval = fillchr * (self.dc_fields[fld].end - \
                        self.dc_fields[fld].beg) 
                    self.dc_fldvals[fld] = fillval
                else:
                    self.dc_fldvals[fld] = 0
        else:
            for fld in self.ls_fields:
                self.dc_fldvals[fld] = 0
        return

        
    def consistchk(self):
        '''Run a consistency check on var members.

        Verifies:
        
            - if keys in dc_fldvals have descriptions in dc_fields.
            - lengths in frame and fields.
            
        @raise FrameException: on consistency errors.
        '''
        # verify if keys in dc_fldvals have descriptions in dc_fields
        rslt = True
        if set(self.ls_fields) == set(self.dc_fields.keys()) and \
                set(self.ls_fields) == set(self.dc_fldvals.keys()):
            pass
        else:
            msg = 'Fields differ in ls_fields, dc_fields and dc_fldvals'
            raise FrameException(msg)
        # verify lengths
        """print 'en consistchk', be_obj
        if self.dc_fields[be_obj.ls_fields[-1]][1] != self.frame_len:
           msg = 'Lengths differ in frame_len and dc_fields'
           raise FrameException(msg)
        """
        return rslt


    def setfrmbdy(self, new_frmbdy=None):
        '''Set new frame body, adjust frame body template.

        @param new_frmbdy: new frame body, even if it is the null string. If None, returns with no action.
        '''
        if 'frame_body' not in self.ls_fields:    # frame has no frame body
            return
        if new_frmbdy is None:   # beware, new_frmbody may be ''
            if self.dc_fldvals.has_key('frame_body'):
                new_frmbdy = self.dc_fldvals['frame_body']
            else:
                return
        # start of frame body is end of previous field
        fld_before = self.ls_fields[self.ls_fields.index('frame_body') - 1]
        fb_beg = self.dc_fields[fld_before].end
        fb_end = fb_beg + len(new_frmbdy)
        mask_fb = '!' + str(len(new_frmbdy)) + 's'
        self.dc_fields['frame_body'] = FieldTemplate(beg=fb_beg, end=fb_end, \
            inv=False, fmt=mask_fb, btmsk='bytes, no bitmask')
        # new length; FCS is 4 bytes, only field after frame body
        new_len = fb_end + 4
        self.dc_fields['fcs'] = FieldTemplate(beg=-4, end=new_len, \
            inv=False, fmt='!I', btmsk='bytes, no bitmask')
        self.dc_fldvals['frame_body'] = new_frmbdy
        self.frame_len = new_len
        return


    def updtfldvals(self, dc_fldvals=None):
        '''Update frame with new values.
        
        @param dc_fldvals: a dictionary {field: value}.
        '''
        self.dc_fldvals.update(dc_fldvals)
        self.setfrmbdy()
        return


    def mkpkt(self, dbg=False):
        '''Convert this frame into binary data.
        
        @param dbg: debug, if True prints info on each field packing.
        @raises FrameException: on errors in field template, lengths.
        @return: a string of binary data (a packet).
        '''
        if self.bitbyte == 'bits':
            pkint = 0
            for fld in self.ls_fields:
                pkint = pkint | self.dc_fldvals[fld] << \
                    (self.mask_len - self.dc_fields[fld].end)
            return struct.pack('!I', pkint)[-self.frame_len:]
        else:
            pkbyts = ''
            for fld in self.ls_fields:
                try:
                    pkfld = struct.pack(self.dc_fields[fld].fmt, \
                        self.dc_fldvals[fld])
                    pkbyts = pkbyts + pkfld
                    if dbg:
                        print fld, len(pkfld), repr(pkfld)
                except:
                    msg = '  pack error on field: ' + fld + \
                        '\n  template: ' + repr(self.dc_fields[fld]) + \
                        '\n  value   : ' + repr(self.dc_fldvals[fld]) + '\n'
                    raise FrameException(msg)

            if len(pkbyts) != self.frame_len:
                msg = 'wrong length; packet: ' + str(len(pkbyts)), \
                    ' frame:', str(self.frame_len)
                raise FrameException(msg)
            return pkbyts


    def mkdic(self, pk):
        '''Make dictionary {field: value}.
        
        This function returns a dictionary {field: value}.
        @warning: does not automatically update var member dictionary.
        @param pk: the packet to decode.
        @return: a dictionary of {field: value}.
        '''
        dc_fldvals = {}
        if self.bitbyte == 'bits':
            pkt = '\x00' * (4 - self.frame_len) + pk     # as unsigned integer
            (pkint,) = struct.unpack('!I', pkt)
            for fld in self.ls_fields:
                dc_fldvals[fld] = (pkint & self.dc_fields[fld].btmsk) \
                    >> (self.mask_len - self.dc_fields[fld].end)
            #self.dc_fldvals = dc_fldvals
            return dc_fldvals
        else:
            for fld in self.ls_fields:
                (dc_fldvals[fld],) = struct.unpack( self.dc_fields[fld].fmt, \
                    pk[ self.dc_fields[fld].beg : self.dc_fields[fld].end ] )
            #self.dc_fldvals = dc_fldvals
            return dc_fldvals


    def mkhexfl(self, fname, data=None):
        '''Make a hex file from packet to be imported by wireshark.
        
        Creates a .bin file and a .hex file.
        @param fname: a file name with no extensions, 'bin' and 'hex' added by function.
        @param data: a string as produced by mkpkt().
        @return: the return code of system command od, which converts to hex.
        '''
        f = open(fname+'.bin', 'w')
        f.write(self.mkpkt())
        f.close()
        return os.system('cat '+fname+'.bin | od -Ax -tx1 -v > '+fname+'.hex')


    def __str__(self):
        '''Show all object attributes.
        '''
        ss = 'Frame type  : ' + self.frmtype + \
           '\nBit or bytes: ' + self.bitbyte + \
           '\nFrame length: ' + str(self.frame_len) + '\n'
        for fld in self.ls_fields:
            if self.bitbyte == 'bits':
                ss += '%10s: %s' % \
                    ( fld, bin2(self.dc_fields[fld].btmsk, self.mask_len) )
                ss += '%4d %4d %6s %6s' % self.dc_fields[fld][:-1]
                #ss += ' :  %s' % (self.dc_fldvals[fld].__repr__(),) +'\n'
            else:
                ss += '%10s: %s' % ( fld, self.dc_fields[fld].btmsk )
                ss += '%4d %4d %6s %6s' % self.dc_fields[fld][:-1]
            ss += ' :  %s' % (self.dc_fldvals[fld].__repr__(),) +'\n'
        return ss



if __name__ == '__main__':
    import doctest
    print "frames.py: running doctest file..."
    try:
        doctest.testfile('frames.txt')
        print "frames.py: ...doctest run done. No messages means no errors."
    except:
        print "           ...no doctest file found."

    


