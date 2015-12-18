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

'''A Finite State Machine (FSM) engine.

This module implements a Finite State Machine (FSM) engine. In addition to the usual states and transitions, the GWN FSM includes actions, memory, and conditions. 

An action is a user written function executed on a transition, before moving the machine to the next state.

Memory may be any object capable of recording and retrieving information, in whatever access mode the application may need (LIFO, FIFO, etc). The memory facility is not part of the FSM machine, but an independent object. Memory may be handled in the action functions.

A conditions is a user written function or expression which returns True or False when executed or evaluated. The action function and the transition are only executed if the condition evaluates to True. If the condition on a transition evaluates to False, the transition is not performed, and its related action is not executed.

The FSM is defined through tables of transitions. In a current state, for a given input symbol, the process() method uses these tables to decide which action to call and which the next state will be, if and only if the condition evaluates to True; otherwise, nothing happens.

The table of transitions defines the following associations::

        (input_symbol, current_state) --> (action, next_state, condition)

where action is a function, symbols and states can be any objects, and condition is a function or an expression whith returns a boolean. This table is maintained through the FSM methods add_transition() and add_transition_list().

A second table of transitions defines another kind of association::

        (current_state) --> (action, next_state, condition)

This allows to add transitions valid for any input symbol. The table of any symbol transitions is maintained through the FSM method add_transition_any().

The FSM has also one default transition not associated with any specific
input_symbol or state. The default transition matches any symbol on any state, and may be used as a catch-all transition. The default transition is set through the set_default_transition() method. There can be only one default transition.

On receiving a symbol, the FSM looks in the transition tables in the following order::

    1. The transitions table for (input_symbol, current_state).
    2. The transitions table for (current_state), valid for and any input symbol.
    3. The default transition.
    4. If no valid transition is found, the FSM will raise an exception.

Matched transitions with the former criteria may produce a list of (action, next_state, condition). The condition is evaluated for each tuple in the list, and the first tuple on which the condition is found True is executed, the action function is called, and the next state is set as the current state.

If no transition is defined for an input symbol, the FSM will raise an exception. This can be prevented by defining a default transition. 

The action function receives a reference to the FSM as a parameter, hence the action function has access to all attributes in the FSM, such as current_state, input_symbol or memory.

The GWN Finite State Machine implementation is an extension of Noah Spurrier's FSM 20020822, C{http://www.noah.org/python/FSM/}.
'''

# TODO ensure access to gwnblock!
import sys
#sys.path = sys.path + ['../../../python']
sys.path = sys.path + ['/home/victor/IIE/GNURadio/gr-gwn/python']
from gwnblock import mutex_prt


class ExceptionFSM(Exception):
    '''FSM Exception class.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`


class FSM:
    '''GWN Finite State Machine (GWN-FSM) with string as symbols.

    The GWN FSM uses strings as input symbols. However, any object can be passed to the action function as a parameter. The action function receives a reference to the FSM itself, which allows the action function access to all attributes in the FSM object.
    @ivar state_transitions: a dictionary { (input symbol, current state): [ (action, next state, condition) ] }. Defines a transition from the current state when a certain symbol is received.
    @ivar state_transitions_any: a dictionary of tuples { (current_state): [ (action, next_state, condition) ] }. Defines a transition from the current state when any symbol is received.
    @ivar default_transition: optionally define a transition when an invalid input is received. It is used to keep the machine going instead of rising an exception.
    @ivar input_symbol: the symbol received.
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
        # a default transition
        self.default_transition = None

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory

        self.debug = False
        return


    def reset (self):
        '''Brings the machine back to its initial state.

        Sets the current state to the initial state and sets input_symbol to None. WARNING: memory is left untouched.'''
        self.current_state = self.initial_state
        self.input_symbol = None


    def add_transition (self, input_symbol, state, action=None, \
            next_state=None, condition=None):
        '''Adds a transition.

        This function adds a transition from the current state to another state. The transition is expressed through the association::

           (input_symbol, current_state) --> [ (action, next_state, condition) ]

        On the destination list, the first transition where condition returns True will be the one executed.

        Transitions for a list of symbols may be added with the function add_transition_list().
        @param input_symbol: the received symbol.
        @param state: the current state.
        @param action: a function to execute on transition. This action may be set to None in which case the process() method will ignore the action and only set the next_state. This parameter may be given as a list of functions.
        @param next_state: the state to which the machine will be moved and made the current state. If next_state is None, the current state will remain unchanged.
        @param condition: a function or expression which returns True or False; if True, transition is performed, otherwise the transition is ignored, i.e. the FSM remains in its state and action is not executed. If this parameter is None, no conditions are checked, and transition is performed. This parameter may be given as a list of expressions or functions.
        '''
        if next_state is None:          # a loop transition, remains in state
            next_state = state
        # adds transition to dictionary of transitions
        if self.state_transitions.has_key( (input_symbol, state) ):
            self.state_transitions[(input_symbol, state)] = \
                self.state_transitions[(input_symbol, state)] + \
                [ (action, next_state, condition) ]
        else:
            self.state_transitions[(input_symbol, state)] = \
                [ (action, next_state, condition) ]
        return


    def add_transition_list (self, list_input_symbols, state, \
            action=None, next_state=None, condition=None):
        '''Adds the same transition for a list of input symbols.

        The action may be set to None in which case the process() method will
        ignore the action and only set the next_state. The next_state may be
        set to None in which case the current state will be unchanged. 
        @param list_input_symbols: a list of symbols.
        @param state: the current state.
        @param action: a function to execute on transition. This action may be set to None in which case the process() method will ignore the action and only set the next_state. This parameter may be given as a list of functions.
        @param next_state: the state to which the machine will be moved and made the current state. If next_state is None, the current state will remain unchanged.
        @param condition: a function or expression which returns True or False; if True, transition is performed, otherwise the transition is ignored, i.e. the FSM remains in its state and action is not executed. If this parameter is None, no conditions are checked, and transition is performed. This parameter may be given as a list of expressions or functions.
        '''
        if next_state is None:          # a loop transition, remains in state
            next_state = state
        for input_symbol in list_input_symbols:
            self.add_transition (input_symbol, state, action, next_state, condition)
        return


    def add_transition_any (self, state, action=None, next_state=None, condition=None):
        '''Adds a transition for any input symbol.

        Adds a transition that associates::

                (current_state) --> [ (action, next_state, condition) ]

        Any input symbol will match the current state. This function is performed only if no exact match could be found for (input_symbol, current_state), but only if condition evaluates to True.
        @param state: the current state.
        @param action: a function to execute on transition. This action may be set to None in which case the process() method will ignore the action and only set the next_state.
        @param next_state: the state to which the machine will be moved and made the current state. If next_state is None, the current state will remain unchanged.
        @param condition: a function or expression which returns True or False; if True, transition is performed, otherwise the transition is ignored, i.e. the FSM remains in its state and action is not executed. If this parameter is None, no conditions are checked, and transition is performed. This parameter may be given as a list of expressions or functions.
        '''

        if next_state is None:
            next_state = state
        # adds transition to dictionary of transitions for any symbol
        if self.state_transitions_any.has_key(state):
            self.state_transitions_any[state] = \
                self.state_transitions_any[state] + \
                [ (action, next_state, condition) ]
        else:
            self.state_transitions_any[state] = \
                [ (action, next_state, condition) ]
        return


    def set_default_transition (self, action, next_state):
        '''Sets a default transition.

        The default transition can be removed by setting the attribute default_transition to None.
        @param action: a function to execute on transition. This action may be set to None in which case the process() method will ignore the action and only set the next_state.
        @param next_state: the state to which the machine will be moved and made the current state. If next_state is None, the current state will remain unchanged.
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
        '''Receives input, calls an action, changes state.

        This function calls get_transition() to find the action and next_state associated with the input_symbol and current_state. If the action is None only the current state is changed. This function processes a single input symbol. To process a list of symbols, or a string, process_list() may be called.

        Action may be a single function or a list of functions. If action is list of functions, functions are executed in turn, and return values gathered in a list, which is returned.

        Conditions may be a single condition or a list of conditions. If condition is a list of conditions, they are ANDed to determine if transition is valid. A condition may be a boolean function or an expression which evaluates to True or False.
        @param input_symbol: the input symbol received.
        @param event: an Event object, to pass on to the action function.
        @param block: a reference to the block to which the FSM is attached, to pass on to action functions.
        @return: a list of the return values of actions executed, or None.
        '''
        if self.debug:
            mutex_prt( "\n    FSM process: " + input_symbol + ", " + \
                self.current_state)
        # list of possible destinations for (input_symbol, current_state):
        ls_dest = self.get_transition (input_symbol, self.current_state)

        for dest in ls_dest:
            action, next_state, condition = dest

            ### determine value of all conditions
            # consider no condition, one condition, a list of conditions
            if condition and type(condition) is not list:   # string or function
               condition = [condition]      # make it a list
            if condition is None:           # no condition, aka no list
                if self.debug:
                    mutex_prt("    FSM Condition: None")
                cond_val = True
            elif type(condition) is list:   # a list of conditions
                cond_val = True
                for cond in condition:      # AND all conditions
                    if type(cond) is str:   # condition is a string
                        cond_val = cond_val and eval(cond)
                    else:                   # condition is a function
                        if event and block:
                            this_cond_val = cond(self, event, block)
                        elif event:
                            this_cond_val = cond(self, event)
                        elif block:
                            this_cond_val = cond(self, block)
                        else:
                            this_cond_val = cond(self)
                        cond_val = cond_val and this_cond_val
                    if self.debug:
                        mutex_prt("    FSM Condition in list: " + \
                            str(cond) + ", value: " + str(cond_val))
            else:
                raise ExceptionFSM ('Condition must be a list of functions ' +\
                    'or expressions')
            if self.debug:
                mutex_prt("    FSM cond_val: " + str(cond_val))

            ### do transition
            if cond_val:  # no condition or all conditions True
                self.input_symbol = input_symbol
                self.action = action
                self.next_state = next_state

                # execute action, account for a list of actions
                ret_val = []
                if not self.action:
                    self.action = []
                elif self.action and type(self.action) is not list:
                    self.action = [self.action]
                for fn_act in self.action:
                    if event and block:
                        ret_val += [fn_act(self, event, block)]
                    elif event:
                        ret_val += [fn_act(self, event)]
                    elif block:
                        ret_val += [fn_act(self, block)]
                    else:
                        ret_val += [fn_act(self)]

                if self.debug:
                    self.print_state(show=['transition'])
                    mutex_prt("    FSM change state to: " + \
                        self.next_state + "\n")

                self.current_state = self.next_state   # change state
                self.next_state = None
                return ret_val
            else:        # condition not met, consider next destination
                continue # continue loop #return None
        return None


    def process_list (self, input_symbols):
        '''Processes a list of input symbols.

        This function takes a list of symbols and sends each symbol to the process() function. The list may be a string or any iterable object.
        @param input_symbols: a list of symbols.
        '''
        for s in input_symbols:
            self.process (s)
        return


    def print_state(self, show=[]):
        '''Prints FSM state, transitions.

        This function may be called in the action functions.
        @param show: whole or partial list of ["state", "transition", "memory"], shows accordingly.
        '''
        if 'state' in show:
            mutex_prt("    FSM initial_state: " + self.initial_state)
            mutex_prt("    FSM state_transitions:")

            for key in self.state_transitions.keys():
                symbol, cur_state = key
                for item in self.state_transitions[key]:    
                    function, dst_state, cond = \
                        item[0], item[1], item[2]
                    if type(function) is list:
                        function = [fn.func_name for fn in function]
                    else:
                        function = function.func_name
                    # should detect if condition is function, use name
                    msg_dbg = '      {0} --- {1} | {2} --> {3}'.format( \
                        cur_state, symbol, function, dst_state)
                    msg_dbg += '\n        cond = {0}'.format(cond)
                    mutex_prt(msg_dbg)

            mutex_prt("    FSM state_transitions_any:")
            for item in self.state_transitions_any.items():
                mutex_prt( '     ' + str(item) )
            mutex_prt ("    FSM default_transition:")
            mutex_prt ("     " + str(self.default_transition) + "\n")
        if 'action' in show and self.action:
            ss = "    FSM state %s, symbol %s" % \
                (self.current_state, self.input_symbol) # + "\n"
            for fn_act in self.action:    # asumes it is a list
                ss += '\n        action:' + fn_act.func_name
            mutex_prt(ss)
        if 'transition' in show:
            ss = '    FSM transition: ' + self.current_state + ' --- ' + \
                str(self.input_symbol) + ' | '
            ss += ' --> ' + str(self.next_state)
            mutex_prt(ss)

        if 'memory' in show:
            mutex_prt ('    FSM memory: ' + str(self.memory) )
        return


