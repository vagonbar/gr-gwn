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


'''An API to the IEEE 802.11 frame library.

This module intends to be the only one a developer must know to create frame objects, pack frames into binary string format, unpack binary string formats into frame objects. This module offers functions to get information on known types of frames and their corresponding fields.
'''

import mac_frmbld
import mac_frmspecs


def objfrompkt(frmpkt):
    '''Create a frame object from a binary string format frame.
    
    @param frmpkt: a frame in binary string format.
    @return: a frame object.
    '''
    return mac_frmbld.mkfrmobj(frmpkt)


def pktfromobj(frmobj):  # pack
    '''Create a frame in binary string format from a frame object.
    
    @param frmobj: a frame object.
    @return: a frame in binary string format.
    '''
    return frmobj.mkpkt()


def mkframeobj(frmname, dc_frcl_fldvals={}, dc_fldvals={}, dc_frbd_fldvals={} ):
    '''Create a frame object from a frame name and dictionary of fields.

    @param frmname: a conventional name for the type of frame.
    @param dc_frcl_fldvals: a dictionary of {field: value} to update dictionary of field values in Frame Control field.
    @param dc_fldvals: a dictionary of {field: value} to update dictionary of field values in this frame.
    @param dc_frbd_fldvals: a dictionary of {field: value} to update dictionary of field values in frame body.
    @return: a frame object.
    '''
    #frmclass, frmbodyclass = mac_getfrmclass(frmname)
    return mac_frmbld.AFrame(frmname, dc_frcl_fldvals=dc_frcl_fldvals, \
        dc_fldvals=dc_fldvals, dc_frbd_fldvals=dc_frbd_fldvals )

 
def showfldvals(frmobj):
    '''Show values for all fields in a frame object.
    
    @param frmobj: a frame object.
    '''
    return mac_frmspecs.showfldvals(frmobj)


def showfieldnames(frmname):
    '''Show all field names for a frame object of given frame name.
    
    @param frmname: a frame name.
    '''
    frmclass, frmbodyclass = mac_frmspecs.getfrmclass(frmname)
    print '--- Fields for frame name: ' + frmname
    print '-- Frame Control field names:'
    print mac_frmspecs.FrmCtrlSpecs.ls_fields
    print '-- ' + frmname +' frame field names:'
    print frmclass.ls_fields
    if frmbodyclass:
        print '-- Frame body field names:'
        print frmbodyclass.ls_fields
    print '===\n'


def test():
    '''A test function for the frames interface.

    For the types of frame known, create a frame object, pack it into binary string format, create a second frame object from the packed frame.
    '''
    print '=== TEST 1: object creation, packing, unpacking to object\n'

    ls_known = ['Beacon', 'RTS', 'CTS', 'ACK', 'Data', 'Action']
    for frtype in ls_known:
        print '--- %15s ... ' % (frtype.ljust(15),),
        try:
            ob = mkframeobj(frtype)
        except:
            print ' Object creation Error'        
        try:
            pk_ob = pktfromobj(ob)
        except:
            print ' Packing error'
        try:
            ob2 = objfrompkt(pk_ob)
        except:
            print 'Unpacking error'
            continue
        print 'OK'

    print '\n=== TEST 2: show field names as help to set values\n'
    for name in ls_known:
        showfieldnames(name)
    
    print '\n=== TEST 3: object creation setting field values\n'
    #ac1 = mac_frmbld.AFrame('Action', \
    ac1 = mkframeobj('Action', \
        dc_fldvals={'fcs':555, 'address_1':'aaaaaa', 'address_2':'bbbbbb'},\
        dc_frbd_fldvals={'TCPreq':222}, \
        dc_frcl_fldvals={'ToDS':True} )
    showfldvals(ac1)



    return


if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass



