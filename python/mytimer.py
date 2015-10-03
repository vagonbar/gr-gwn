#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gwnblock import GWNPort
import threading
import time
from gwnblock import mutex_prt


class GWNTimer(GWNPort, threading.Thread):
    '''A timer class to add inside timers to GWN blocks.

    Objects of this class can attached to a gwnblock to act as internal timers. An object of this class sends messages to the block to which it is attached, at regular intervals. A timer object sends a message for an specified number of times, then a final second message to indicate the first series has exhausted.
    '''
    def __init__(self, block, port, port_nr, interrupt=True, interval=1.0, \
            retry=1, nickname1='TimerTOR1', nickname2='TimerTOR2', add_info=None):
        '''Constructor.

        @param interrupt: if True, timer is interrupted, i.e. does not send any messages.
        @param interval: time between messages to send.
        @param retry: how many times to send message 1, then send message 2 once.
        @param nickname1: message to send at regular intervals for retry times.
        @param nickname2: message to send when retries have exhausted.
        @param add_info: additional information for this timer.
        '''
        GWNPort.__init__(self, block, port, port_nr)
        threading.Thread.__init__(self)

        #self.block = block
        #self.port = port
        #self.port_nr = port_nr
        self.interrupt = interrupt
        self.interval = interval
        self.retry = retry
        self.nickname1 = nickname1
        self.nickname2 = nickname2
        self.add_info = add_info

        self.counter = 0
        self.exit_flag = False   # ir True, ends timer
        self.debug = True
        self.ini_time = time.time()
        mutex_prt ("--- Timer built, retry:" + str(self.retry))
        return


    def set_interrupt(self, interrupt):
        '''Interrupts generation of timer messages.'''
        #lock_obj.acquire()
        self.interrupt = interrupt
        #lock_obj.release()
        if self.debug:
            ss = '   GWNTimer INTERRUPT set to ' + str(interrupt)
            mutex_prt(ss)
        return


    def stop(self):
        '''Stops timer thread.'''
        if self.debug:
            ss = '   GWNTimer STOP, stopping timer %d in block %s' % \
                (0, 'Timer0')
               #(self.port_nr, self.block.blkname)
            mutex_prt(ss)
        self.exit_flag = True
        return


    def reset(self, retry=None):
        '''Resets counter to 0, starts timing again.

        Sets interrupt to False and starts timing again, from 0 count.
        @param retry: new retry value, default None.
        '''
        if retry:
            self.retry = retry
        self.counter = 0
        self.set_interrupt(False)
        if self.debug:
            ss = '   GWNTimer RESET, counter back to 0'
            if retry:
                ss += ' new retry value ' +  str(retry)
            else:
                ss += ' retry value left in ' + str(self.retry)
            mutex_prt(ss)
        return


    def run(self):
        '''Runs timer thread, uses time.sleep.'''
        while not self.exit_flag:               # timer not stopped
            #if not self.interrupt:              # timer not interrupted
                self.counter = 0
                ## post timer messages
                while self.counter < self.retry and not self.exit_flag: 
                    # sends messages until count reaches number of retries
                    self.counter = self.counter + 1
                    if self.debug:
                        mutex_prt("   GWNTimer counter" + str(self.counter))
                    if not self.interrupt and self.nickname1:
                        # test repetition required inside while
                        self.post_message(self.nickname1)
                    else:                # interrupted, does send but counts
                        pass #break  # no message sent
                        #self.post_message(self.nickname2)
                    time.sleep(self.interval)   # waits interval
                ## post final message
                if not self.interrupt and not self.exit_flag:
                    # test repetition required, things may have changed!
                    if self.nickname2:
                        self.post_message(self.nickname2)
                    self.interrupt = True
            #else:
            #    time.sleep(1.0)
        return



    ### handle and post message functions
    
    def post_message(self, nickname):
        '''Posts timer event and timer metadata on block port.'''
        ss = 'in post message, message %s, elapsed time %f' % \
            (nickname, time.time() - self.ini_time)
        mutex_prt(ss)
        return


    def handle_msg(self, msg_pmt):
        '''Timer message handler, regenerates event, passes to process_data.'''
        pass
        return


    def __str__(self):
        return  '  timer %s index %d in block %s' % \
            (self.port, self.port_nr, self.block.blkname)
        return 



if __name__ == "__main__":
    print 'test'
    tmr = GWNTimer('blockBB', 'portPP', 'portNrNN', retry=10, interrupt=False)
    tmr.start()
    time.sleep(3)
    #print '    timer interrupted'
    tmr.set_interrupt(True)
    time.sleep(4)
    #print '   timer restored (uninterupted)'
    tmr.set_interrupt(False)
    time.sleep(6)
    #print '   timer reset, conter back to 0'
    tmr.reset()
    time.sleep(4)
    tmr.reset(retry=4)
    time.sleep(7)
    #print '    timer stopped'
    tmr.stop()
    tmr.exit_flag = True
    time.sleep(2)


