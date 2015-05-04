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


'''
Script to add license notice at beginning of file.

Adds notice of license to GWN python modules. Optionally, it may include recognition to code originally from GNU Radio.

@var txlic1: first part of GWN license.
@var txlic2: second part of GWN license.
@var txlicgr: recognition to GNU Radio code.
'''

import sys

txlic1 = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    This file is part of GNUWiNetwork,
#    Copyright (C) 2014 by 
#        Pablo Belzarena, Gabriel Gomez Sena, Victor Gonzalez Barbone,
#        Facultad de Ingenieria, Universidad de la Republica, Uruguay.
#'''
txlicgr = '''#    This is a modified version of original code by
#         GNU Radio, http://gnuradio.org
#'''
txlic2 = '''#    GNUWiNetwork is free software: you can redistribute it and/or modify
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
'''

lslic1 = txlic1.split('\n')
lslic2 = txlic2.split('\n')
lslicgr = txlicgr.split('\n')

def mklslic(withgr=False):
    '''Makes list of license lines, optionally including GNU Radio recognition.

    @param withgr: if True, adds GNU Radio recognition.
    @return: list of license lines.
    '''
    if withgr:
        return lslic1 + lslicgr + lslic2
    else:
        return lslic1 + lslic2


def addlic2file(fname, lslic):
    '''Adds license lines to beginning of file, omits first commented lines.

    @param fname: name of file to add license to.
    @param lslic: lines of license to add to file.
    '''
    try:
        f = open(fname, 'ro')
        txlines = f.read()
        f.close()
    except:
        print 'addlicense ERROR, file', fname, 'could not be read.'
        return None

    lslines = txlines.split('\n')
    f.close()
    for i in xrange(0,len(lslines)):
        if lslines[i].startswith('#'):
            pass
        else:
            lsnewlines = lslic + lslines[i:]
            break

    f = open(fname, 'w')
    for line in lsnewlines:
        f.write(line + '\n')
    f.close()


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print 'addlicense.py: adds license notice to GWN modules.'
        print 'Typical usage:'
        print '    addlicense.py [--withgr] file ...'
        print '    --withgr option adds GNU Radio recognition to license.\n'
        sys.exit()

    elif '--withgr' == sys.argv[1]:
        withgr = True
        lsfiles = sys.argv[2:]
    else:
        withgr = False
        lsfiles = sys.argv[1:]
    #print sys.argv
    #print lsfiles

    lslic = mklslic(withgr=withgr)
    for fname in lsfiles:
        if fname.startswith('_'):
            print '  ignoring file', fname
        else:
            print '  adding license to file', fname
            addlic2file(fname, lslic)


