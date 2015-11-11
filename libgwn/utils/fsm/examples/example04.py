#!/usr/bin/env python
# -*- coding: utf-8 -*-


''' FSM for Stop and Wait ARQ protocol with sequence numbers.
'''

import sys, os, traceback, optparse, time, string
# add path to gwnfsm, gwnblock in FSM
sys.path += ['..', '../../../../python/']
from gwnfsm import FSM


### Actions

def goto(fsm):
    fsm.print_state(show=['transition', 'action'])

def goidle(fsm):
    if fsm.wait == 'ack0':
        fsm.wait = 'ack1'
    else:
        fsm.wait = 'ack0'
    fsm.print_state(show=['transition', 'action'])
    print "  Next frame ACK: " + fsm.wait

def send(fsm):
    fsm.print_state(show=['transition', 'action'])
    """if fsm.input_symbol == 'frame0':
        fsm.wait = 'ack0'
    else fsm.input_symbol == 'frame1':
        fsm.wait = 'ack1'"""
    print "  Send frame, wait for ack: " + fsm.wait

def resend(fsm):
    fsm.print_state(show=['transition', 'action'])
    print "  Resend frame, wait for ack: " + fsm.wait

def fn_error(fsm):
    fsm.print_state(show=['transition', 'action'])


### Conditions

def wait0(fsm):
    if fsm.wait == 'ack0':
        return True
    else:
        return False

def wait1(fsm):
    if fsm.wait == 'ack1':
        return True
    else:
        return False


### States

def myfsm():
    f = FSM ('Idle') # 
    f.wait = 'ack0'
    f.set_default_transition (fn_error, 'Idle')

    f.add_transition_any ('Idle', None, 'Idle')
    f.add_transition_any ('WaitAck', None, 'WaitAck')

    #f.add_transition_list (['frame0', 'frame1'], 'Idle', send, 'WaitAck', None)
    f.add_transition ('frame', 'Idle', send, 'WaitAck', None)

    """
    f.add_transition ('ack0', 'WaitAck', goidle, 'Idle', "self.wait=='ack0'")
    f.add_transition (['nak', 'ack1', 'tout'], \
                        'WaitAck', resend, 'WaitAck', "self.wait=='ack0'")

    f.add_transition ('ack1', 'WaitAck', goidle, 'Idle', "self.wait=='ack1'")
    f.add_transition (['nak', 'ack0', 'tout'], \
                        'WaitAck', resend, 'WaitAck', "self.wait=='ack1'")
    """
    f.add_transition ('ack0', 'WaitAck', goidle, 'Idle', wait0)
    f.add_transition_list (['nak', 'ack1', 'tout'], \
                        'WaitAck', resend, 'WaitAck', wait0)

    f.add_transition ('ack1', 'WaitAck', goidle, 'Idle', wait1)
    f.add_transition_list (['nak', 'ack0', 'tout'], \
                        'WaitAck', resend, 'WaitAck', wait1)

    print "--- FSM created, show state"
    f.print_state(show='state')

    #inputevs = [] # list of input events
    #f.process_list(inputevs)
    event = 'j'
    while event:
        event = raw_input('Event:')
        f.process(event)

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

