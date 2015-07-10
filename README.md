# gr-gwn
GNU Radio GNU Wireless Network, data networking on GNU Radio.
This is a redesigned version of project GNUnetwork at https://github.com/vagonbar/GNUnetwork, now brought to the paradigm of GNU Radio, and built as an "out-of-tree" module. Up to date, this is a very early and experimental version. Several issues have to be dealt with, e.g. to ensure the essentially flow oriented GNU Radio blocks can be used for asynchronous communication among blocks, using the message passing mechanism of GNU Radio, and timeouts for individual blocks can be implemented.
