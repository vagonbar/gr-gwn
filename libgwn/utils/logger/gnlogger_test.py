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


'''A testing module for the GNUWiNetwork logger.

This testing module may be invoked as itself, but is also called from gnlogger C{main()}; logging differs accordingly.

Try both possibilities::
    python gnlogger.py
    python gnlogger_test.py
    
Log file is C{<gwn_base_dir>/logs/gnlogger.log}.
'''

import gnlogger
import logging

# a logger for this module
module_logger = logging.getLogger(__name__)

class Auxiliary:
    def __init__(self):
        #self.logger = logging.getLogger('spam_application.auxiliary.Auxiliary')
        # a logger for this class
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.info('creating an instance of Auxiliary')
    def do_something(self):
        self.logger.info('doing something')
        a = 1 + 1
        self.logger.info('done doing something')

def some_function():
    # function uses module logger
    module_logger.info('received a call to "some_function"')


if __name__ == '__main__':

    gnlogger.logconf()         # initializes the logging facility

    module_logger.info('start this module')

    obja = Auxiliary()
    obja.do_something()
    some_function()

    module_logger.info('finish this module')





