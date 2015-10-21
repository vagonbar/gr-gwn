#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gwnblock import GWNPort
import threading
import time
from gwnblock import mutex_prt


class GWNTimeout(GWNPort):
    '''A time class to add implement timeouts inside GWN blocks.

    Objects of this class can attached to a gwnblock to act as internal timeouts. An object of this class sends a messages to the block to which it is attached once the specified time has elapsed.
    '''
    def __init__(self, block, port, port_nr, timeout=1.0, nickname='TimerTOR2'):
        '''Constructor.

        @param timeout: timeout in seconds.
        @param nickname: message to send at timeut.
        #@param add_info: additional information for this timeout.
        '''
        GWNPort.__init__(self, block, port, port_nr)

        self.block = block
        self.port = port
        self.port_nr = port_nr
        self.timeout = timeout
        self.nickname = nickname
        self.debug = True
        #self.add_info = add_info
        self.timer = None

        """self.counter = 0
        self.exit_flag = False   # ir True, ends timer
        self.debug = True
        self.ini_time = time.time()"""
        mutex_prt ("   GWNTimeout BUILT, timeout:" + str(self.timeout))
        return


    def start(self, timeout=None, nickname=None):
        '''Starts timer until timeout.'''
        if timeout:
            self.timeout = timeout
        if nickname:
            self.nickname = nickname
        self.timer = threading.Timer(self.timeout, self.post_message)
        self.timer.start()
        if self.debug:
            ss = '   GWNTimeout STARTED, timeout  ' + str(self.timeout) + \
                ', nickname ' + self.nickname
            mutex_prt(ss)
        return


    def stop(self):
        '''Stops timer if action has not started.'''
        if self.timer.is_alive():
            self.timer.cancel()
            ss = '   GWNTimeout CANCEL done'
        else:
            ss = '   GWNTimeout not alive'
            # ss = '   GWNTimeout not alive, timeout %d in block %s' % \
            #    (0, 'Timer0')
            #    (self.port_nr, self.block.blkname)
        mutex_prt(ss)
        del(self.timer)
        return


    ### handle and post message functions
    
    def post_message(self):
        '''Posts timer event and timer metadata on block port.'''
        ss = '   GWN Timeout, in post_message, nickname ' + self.nickname
        #ss = 'in post message, message %s, elapsed time %f' % \
        #    (nickname, time.time() - self.ini_time)
        mutex_prt(ss)
        self.timeout = None  # destroy timer object
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
    tmr = GWNTimeout('blockBB', 'portPP', 'portNrNN', timeout=1.0)
    tmr.start()
    time.sleep(3)
    tmr.stop()

    tmr.start(timeout=2, nickname='TimerTOH')
    time.sleep(4)

    tmr.start(timeout=3, nickname='TimerTOC')
    time.sleep(1)
    tmr.stop()
    time.sleep(3)

    """
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
    """

