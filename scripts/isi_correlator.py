#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import libisigui
import libisicorr

hosts = ('localhost', 'fake', 'fake')
ports = (7147, 7148, 7149)
I = libisicorr.IsiCorrelator(hosts, ports)
D = libisigui.IsiGui(I)

I.program('isi_correlator.bof')

I.set_sync_period(2**12)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.send_sync()

D.start()

