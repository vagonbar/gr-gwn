#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' FSM for testing, tests (tries to) all features.
'''

import sys, os, traceback, optparse, time, string
# add path to gwnfsm, gwnblock in FSM
#sys.path += ['..', '../../../python/']
from gwnfsm import FSM


### Actions

def fn_none(fsm):
    print '\n--- FSM none, nothing done\n'
    return

def fn_goA(fsm):
    print '\n--- FSM fn_goA; symbol ' + fsm.input_symbol
    fsm.print_state(show=['action', 'transition'])
    return

def fn_goB(fsm):
    print '\n--- FSM fn_goB; symbol ' + fsm.input_symbol
    fsm.print_state(show=['action', 'transition'])
    return

def fn_init(fsm):
    print '\n--- FSM fn_init; symbol ' + fsm.input_symbol
    fsm.print_state(show=['action', 'transition'])
    return

def fn_chgtoC(fsm):
    if fsm.to_c == True:
        fsm.to_c = False
    else:
        fsm.to_c = True
    print '\n--- FSM fn_toC; symbol ' + fsm.input_symbol + \
        '; to_c set to ' + str(fsm.to_c)
    fsm.print_state(show=['action', 'transition'])

def fn_chgwhr(fsm):
    if fsm.where == 'A':
        fsm.where = 'B'
    elif fsm.where == 'B':
        fsm.where = 'C'
    else:
        fsm.where = 'A'
    print '\n--- FSM fn_init; symbol ' + fsm.input_symbol + \
        '; where set to ' + fsm.where
    fsm.print_state(show=['action', 'transition'])
    return

def show(fsm):
    print '\n--- FSM show; symbol ' + fsm.input_symbol + \
        '; where=' + fsm.where + ', to_c=' + str(fsm.to_c)
    fsm.print_state(show=['action', 'transition'])

def fn_error(fsm):
    fsm.print_state(show=['action', 'transition'])


### Condition functions

def cn_toc(fsm):
    return fsm.to_c


### States

def myfsm():
    f = FSM ('INIT')

    # initial conditions
    f.where = 'A'
    f.to_c = False
    f.debug = False

    f.set_default_transition (fn_error, 'INIT')

    # transitions for any input symbol
    f.add_transition_any ('INIT', None, 'INIT')
    f.add_transition_any ('State A', fn_none, 'State A')

    # add ordinary transitions
    f.add_transition ('s', 'INIT', show, 'INIT', None)

    f.add_transition ('g', 'INIT', fn_goA, 'State A', "self.where=='A'")
    f.add_transition ('g', 'INIT', fn_goB, 'State B', "self.where=='B'")
    f.add_transition ('g', 'INIT', [fn_goA, fn_goB], 'State C', \
        ["self.where=='C'", cn_toc])
    f.add_transition ('r', 'State A', fn_init, 'INIT', None)
    f.add_transition ('r', 'State B', fn_init, 'INIT', None)
    f.add_transition ('r', 'State C', fn_init, 'INIT', None)

    f.add_transition ('w', 'INIT', fn_chgwhr, 'Chg Where', None)
    f.add_transition ('c', 'INIT', fn_chgtoC, 'Chg ToC', None)
    f.add_transition ('r', 'Chg Where', fn_init, 'INIT', None)
    f.add_transition ('r', 'Chg ToC', fn_init, 'INIT', None)


    print "\n--- FSM created, show state"
    f.print_state(show='state')

    #inputevs = [] # list of input events
    #f.process_list(inputevs)
    event = 'j'
    while event:
        event = raw_input('Event:')
        for ev in event:
            f.process(ev)

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        if options.verbose: print time.asctime()
        print 'Input events (chars). To test all functions at once, input'
        print '    jsjsgrgjrwrsgrwrsgrcrsgrs'
        print 'Press any key to start.'
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

