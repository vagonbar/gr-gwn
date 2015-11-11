#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' FSM example with states, transitions, actions.

Tnis FSM has no memory, and no conditions.
'''

import sys, os, traceback, optparse, time, string
# add path to gwnfsm, gwnblock in FSM
sys.path += ['..', '../../../../python/']
from gwnfsm import FSM


### Actions

def gotoa(fsm):
    fsm.print_state(show=['transition', 'action'])

def gotob(fsm):
    fsm.print_state(show=['transition', 'action'])

def anychar(fsm):
    fsm.print_state(show=['transition', 'action'])

def stay(fsm):
    fsm.print_state(show=['transition', 'action'])

def goinit(fsm):
    fsm.print_state(show=['transition', 'action'])

def fn_error(fsm):
    fsm.print_state(show=['transition', 'action'])

### states
# add_transition (input_symbol, state, action=None, next_state=None):

def myfsm():
    f = FSM ('INIT')  
    f.set_default_transition (fn_error, 'INIT')

    f.add_transition_any  ('INIT', anychar, 'INIT')
    f.add_transition      ('s', 'INIT', stay, 'INIT')
    f.add_transition      ('a', 'INIT', gotoa, 'State A')
    f.add_transition      ('b', 'INIT', gotob, 'State B')
    f.add_transition      ('r', 'State A', goinit, 'INIT')
    f.add_transition      ('r', 'State B', goinit, 'INIT')
    f.add_transition      ('s', 'State A', stay, 'State A')
    f.add_transition      ('s', 'State B', stay, 'State b')

    print "--- FSM created, show state"
    f.print_state(show='state')

    inputstr = 'ja r brbrajr='
    print "--- Transitions for input string:", inputstr
    f.process_list(inputstr)


if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        if options.verbose: print time.asctime()
        myfsm() #main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)

