#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Ev Socket
# Generated: Fri Apr 29 12:19:08 2016
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late
import ctypes
import sys
if sys.platform.startswith('linux'):
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import gwn
import sys

from distutils.version import StrictVersion
class ev_socket(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Ev Socket")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Ev Socket")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "ev_socket")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################
        self.gwn_pdu_to_ev_0 = gwn.pdu_to_ev('event')
        self.gwn_event_sink_0 = gwn.event_sink(False)
        self.gwn_ev_to_pdu_0 = gwn.ev_to_pdu('event')
        self.gwn_data_source_0 = gwn.data_source(False, 1.0, 10, '00:00:00:00:00:00', '00:00:00:00:00:00', "SERVER payload", {}, False)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("TCP_SERVER", "", "50007", 10000, False)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("TCP_CLIENT", "", "50007", 10000, False)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.gwn_pdu_to_ev_0, 'pdu'))    
        self.msg_connect((self.gwn_data_source_0, 'out0'), (self.gwn_ev_to_pdu_0, 'in0'))    
        self.msg_connect((self.gwn_ev_to_pdu_0, 'pdu'), (self.blocks_socket_pdu_0_0, 'pdus'))    
        self.msg_connect((self.gwn_pdu_to_ev_0, 'out0'), (self.gwn_event_sink_0, 'in0'))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ev_socket")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    if(StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0")):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = ev_socket()
    tb.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets
