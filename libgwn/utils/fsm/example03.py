#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' FSM example with states, transitions, actions, memory and conditions.
'''


from gwnfsm import FSM

import sys, os, traceback, optparse, time, string


### Actions

def goto(fsm):
    fsm.print_state(show=['transition', 'action'])

def goinit(fsm):
    fsm.print_state(show=['transition', 'action'])

def change(fsm):
    if fsm.where == 'A':
        fsm.where = 'B'
    else:
        fsm.where = 'A'
    fsm.print_state(show=['transition', 'action'])
    print "  Function change, FSM where=" + fsm.where

def fn_error(fsm):
    fsm.print_state(show=['transition', 'action'])


### Conditions

def conditionA(fsm):
    if fsm.where == 'A':
        return True
    else:
        return False

def conditionB(fsm):
    if fsm.where == 'B':
        return True
    else:
        return False


### States

def myfsm():
    f = FSM ('INIT', memory=[]) # 
    f.where = 'B'
    f.set_default_transition (fn_error, 'INIT')

    f.add_transition_any  ('INIT', None, 'INIT')
    #f.add_transition      (' ', 'INIT', stay, 'INIT')
    f.add_transition      ('g', 'INIT', goto, 'State A', conditionA)
    f.add_transition      ('g', 'INIT', goto, 'State B', conditionB)
    f.add_transition      ('r', 'State A', goinit, 'INIT')
    f.add_transition      ('r', 'State B', goinit, 'INIT')
    f.add_transition      ('c', 'INIT', change, 'State Chg')
    f.add_transition      ('r', 'State Chg', goinit, 'INIT')

    print "--- FSM created, show state"
    f.print_state(show='state')

    inputstr = 'crgrgrjgrcrgrgr'
    print "--- Transitions for input string:", inputstr; print
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

