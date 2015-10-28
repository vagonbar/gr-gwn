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

'''A testing version of a Finite State Machine (FSM) with string symbols.

This module implements a Finite State Machine (FSM). In addition to the usual states and transitions, the GWN FSM includes actions, memory, and conditions. 

An action is a user written function executed on a transition, before setting the machine to the next state.

Memory may be any object capable of recording and retrieving information, in whatever acces mode the application may need (LIFO, FIFO, etc). The memory facility is not part of the FSM machine, but an independent object. Memory may be handled in the action functions.

A conditions is a user written function or expressions which produce True or False when executed or evaluated. The action function and the transition are only executed if the condition evaluates to True. If the conditione evaluates to False, no action is executed and the machine remains in its current state.

The FSM is defined through tables of transitions. For a given input symbol the process() method uses these tables to decide which action to call and which the next state will be, if and only if the condition evaluates to True; otherwise, nothing happens.

The FSM has a table of transitions that associate::

        (input_symbol, current_state) --> (action, next_statei, condition)

where action is a function, and symbols and states can be any objects.
This table is maintained through the FSM methods add_transition() and add_transition_list().

The FSM also has a second table of transitions that associate::

        (current_state) --> (action, next_state, condition)

which allows to add transitions valid for any input symbol. The table of any symbol transitions is maintained through the FSM method add_transition_any().

The FSM has also one default transition not associated with any specific
input_symbol or state. The default transition matches any symbol on any state, and may be used as a catch-all transition. The default transition is set through the set_default_transition() method. There can be only one default transition.

On receiving a symbol, the FSM looks in the transition tables in the following order::

    1. The transitions table for (input_symbol, current_state).
    2. The transition table for (current_state), valid for and any input symbol.
    3. The default transition.
    4. If no valid transition is found, the FSM will raise an exception.

Matched transitions with the former criteria may produce a list of (action, next_state, condition). Condition is evaluated for each tuple in the list, and the first tuple on which the condition is found True is executed: the action function is called, and the next state is set.

If no transition is defined for an input symbol, the FSM will raise an exception. This can be prevented by defining a default transition. 

The action function receives a reference to the FSM as a parameter, hence the action function has access to all attributes in the FSM, such as current_state, input_symbol or memory.

The GWN Finite State Machine implementation is an extension of Noah Spurrier's FSM 20020822, C{http://www.noah.org/python/FSM/}.
'''

from gwnblock import mutex_prt


class ExceptionFSM(Exception):
    '''FSM Exception class.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`


class FSM:
    '''GWN Finite State Machine (GWN-FSM) with string symbols.

    @ivar state_transitions: a dictionary { (input event, current state): [ (action, next statei, condition) ] }. Defines a transition from the current state when a certain event is received.
    @ivar state_transitions_any: a dictionary of tuples { (current_state): [ (action, next_state, condition) ] }. Defines a transition from the current state when an event of any kind is received.
    @ivar default_transition: optionally define a transition when an invalid input is received. It is used as to keep the machine going instead of rising an exception.
    @ivar input_symbol: the event received.
    @ivar initial_state: the state from where the machine starts.
    @ivar current_state: the state on which the machine is right now.
    @ivar next_state: the FSM state to go in a transition.
    @ivar action: a function to excecute on transition.
    @ivar memory: an object made available to the action functions.
    '''

    def __init__(self, initial_state, memory=None):
        '''GWN FSM constructor.

        @param initial_state: the FSM initial state.
        @param memory:  an object intended to pass along to the action functions. A usual option is a list used as a stack.'''

        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).
        self.state_transitions_any = {}
        self.default_transition = None

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory

        self.debug = False


    def reset (self):
        '''Brings the machine back to its initial state.

        Sets the current state to the initial state and sets input_symbol to None.'''
        self.current_state = self.initial_state
        self.input_symbol = None


    def add_transition (self, input_symbol, state, action=None, \
            next_state=None, condition=None):
        '''Adds a transition.

        This function adds a transition from current state to another state. The transition is expressed through the association::

           (input_symbol, current_state) --> [ (action, next_state, condition) ]

        On the destination list, the first transition where condition returns True will be the one executed.

        Transitions for a list of symbols may be added with the function add_transition_list().
        @param input_symbol: the received event.
        @param state: the current state.
        @param action: a function to execute on transition. This action may be set to None in which case the process() method will ignore the action and only set the next_state.
        @param next_state: the state to which the machine will be moved and made the current state. If next_state is None, the current state will remain unchanged.
        @param condition: a function or expression which returns True or False; if True, transition is performed, otherwise the transition is ignored, the FSM remains in its state and action is not executed. If this parameter is None, no conditions are checked, and transition is performed.
        '''

        if next_state is None:
            next_state = state
        if self.state_transitions.has_key( (input_symbol, state) ):
            self.state_transitions[(input_symbol, state)] = \
                self.state_transitions[(input_symbol, state)] + \
                [ (action, next_state, condition) ]
        else:
            self.state_transitions[(input_symbol, state)] = \
                [ (action, next_state, condition) ]


    def add_transition_list (self, list_input_symbols, state, \
            action=None, next_state=None, condition=None):
        '''Adds the same transition for a list of input events.

        The action may be set to None in which case the process() method will
        ignore the action and only set the next_state. The next_state may be
        set to None in which case the current state will be unchanged. 
        @param list_input_symbols: a list of objects, or a string.
        @param state: the current state.
        @param action: a function to execute on transition. If None, no action is performed, but transition to the next state is unaffected.
        @param next_state: the state which will become the current state. If None, current state is not altered.
        '''
        if next_state is None:
            next_state = state
        for input_symbol in list_input_symbols:
            self.add_transition (input_symbol, state, action, next_state, condition)


    def add_transition_any (self, state, action=None, next_state=None, condition=None):
        '''Adds a transition for any input symbol.

        Adds a transition that associates::

                (current_state) --> [ (action, next_state, condition) ]

        Any input symbol will match the current state. This function is performed only if no exact match could be found for (input_symbol, current_state), but only if condition evaluates to True.
        @param state: the current state.
        @param action: a function to execute on transition. If None, no action is performed, but transition to the next state is unaffected.
        @param next_state: the state which will become the current state. If None, current state is not altered.
        @param condition: a function or expression which evaluates to True or False.
        '''

        if next_state is None:
            next_state = state
        #self.state_transitions_any [state] = (action, next_state, condition)
        if self.state_transitions_any.has_key(state):
            self.state_transitions_any[state] = \
                self.state_transitions_any[state] + \
                [ (action, next_state, condition) ]
        else:
            self.state_transitions_any[state] = \
                [ (action, next_state, condition) ]


    def set_default_transition (self, action, next_state):
        '''Sets a default transition.

        The default transition can be removed by setting the attribute default_transition to None.
        @param action: a function to execute on transition. If None, no action will be performed, and transition to the next state is done.
        @param next_state: the state which will become the current state. If None, current state is not altered.
        '''
        self.default_transition = [ (action, next_state, None) ]


    def get_transition (self, input_symbol, state):
        '''Returns a list of destinations for an input_symbol and state.

        This function does not modify the FSM state. It is normally called by process(). 
        @param input_symbol: the input symbol received.
        @param state: the current state.
        @return: a list of destinations, i.e. tuples (action, next_state, condition).
        '''

        if self.state_transitions.has_key((input_symbol, state)):
            return self.state_transitions[(input_symbol, state)]
        elif self.state_transitions_any.has_key (state):
            return self.state_transitions_any[state]
        elif self.default_transition is not None:
            return self.default_transition
        else:
            raise ExceptionFSM ('Transition is undefined: (%s, %s).' %
                (str(input_symbol), str(state)) )


    def process (self, input_symbol, event=None, block=None):
        '''Processes input, calls an action, changes state.

        This function calls get_transition() to find the action and next_state associated with the input_symbol and current_state. If the action is None only the current state is changed. This function processes a single input symbol. To process a list of symbols, or a string, process_list() may be called.
        @param input_symbol: the input symbol received.
        @param ev: an Event object, to pass on to action functions.
        @param block: a reference to the block to which the FSM is attached, to pass on to action functions.
        '''
        # list of possible destinations for (input_symbol, current_state):
        ls_dest = self.get_transition (input_symbol, self.current_state)
        if self.debug:
            mutex_prt( "\n    FSM process: " + input_symbol + ", " + \
                self.current_state)

        for dest in ls_dest:
            action, next_state, condition = dest

            ### determine value of all conditions
            # consider no condition, one condition, a list of conditions
            if type(condition) is str:           # condition is a string
               condition = [condition] 
            if condition is None:           # no condition
                if self.debug:
                    mutex_prt("    FSM Condition: None")
                cond_val = True
            elif type(condition) is list:   # condition is a list of conditions
                cond_val = True
                for cond in condition:
                    #this_cond = cond(self, event, block)
                    if type(cond) is str:   # condition is a string
                        cond_val = eval(cond)
                    else:                   # condition is a function
                        cond_val = cond_val and this_cond
                    if self.debug:
                        mutex_prt("    FSM Condition in list: " + \
                            str(cond) + ", value: " + str(cond_val))
            else:
                raise ExceptionFSM ('Condition must be a list of functions ' +\
                    'or strings')
            if self.debug:
                mutex_prt("    FSM cond_val: " + str(cond_val))

            ### do transition
            if cond_val:  # no condition or all conditions True
                self.input_symbol = input_symbol
                self.action = action
                self.next_state = next_state
                # execute action
                if self.action is not None:
                    ret_val = self.action(self, event, block)
                else:
                    ret_val = None

                if self.debug:
                    self.print_state(show=['transition'])
                    mutex_prt("    FSM change state to: " + \
                        self.next_state + "\n")

                self.current_state = self.next_state   # change state
                self.next_state = None
                return ret_val
            else:      # condition not met, consider next destination
                continue # continue loop #return None
        return None


    def process_list (self, input_symbols):
        '''Processes a list of input symbols.

        This function takes a list of symbols and sends each symbol to the process() function. The list may be a string or any iterable object.
        @param input_symbols: a list of symbols.
        '''
        for s in input_symbols:
            self.process (s)


    def print_state(self, show=[]):
        '''Prints FSM state, transitions.

        This function may be called in the action functions.
        @param show: whole or partial list of ["state", "transition", "memory"], shows accordingly.
        '''
        if 'state' in show:    # TODO: convert to use mutex_prt
            mutex_prt("    FSM initial_state: " + self.initial_state)
            mutex_prt("    FSM state_transitions:")
            for item in self.state_transitions.items():
                symbol, cur_state, dst_state, cond = \
                    item[0][0], item[0][1], item[1][0][1], item[1][0][2]
                if item[1][0][0]:
                    function = item[1][0][0].func_name 
                else:
                    function = 'None' 
                msg_dbg = '      {0} --- {1} | {2} --> {3}'.format( \
                    cur_state, symbol, function, dst_state)
                msg_dbg += '\n        cond = {4}'.format( \
                    cur_state, symbol, function, dst_state, cond)
                mutex_prt(msg_dbg)
            mutex_prt("    FSM state_transitions_any:")
            for item in self.state_transitions_any.items():
                mutex_prt( '     ' + str(item) )
            mutex_prt ("    FSM default_transition:")
            mutex_prt ("     " + str(self.default_transition) + "\n")
        if 'transition' in show:
            ss = '    FSM transition: ' + self.current_state + ' --- ' + \
                str(self.input_symbol) + ' | '
            if self.action:  # not None
                ss += self.action.func_name 
            else:
                ss += "None"
            ss += ' --> ' + str(self.next_state)
            mutex_prt(ss)
        if 'action' in show and self.action:
            ss = "    FSM action %s: state %s, symbol %s" % \
                (self.action.func_name, self.current_state, \
                self.input_symbol) # + "\n"
            mutex_prt(ss)

        if 'memory' in show:
            mutex_prt ('    FSM memory: ' + str(self.memory) )
        return


