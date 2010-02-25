#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisigui import *
from libisicorr import *

hosts = ('localhost', 'localhost', 'localhost')
ports = (7147, 7148, 7149)

I = IsiCorrelator(hosts, ports)
I.program('isi_correlator.bof')

D = IsiGui(I)

I.set_clock_freq(200)
I.set_sync_period(.25)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.arm_sync()

D.start()

