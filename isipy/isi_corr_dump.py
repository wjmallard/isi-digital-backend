#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisicorr import *

hosts = ('isi0', 'isi2', 'isi3')
ports = (7147, 7147, 7147)

I = IsiCorrelator(hosts, ports)
#I.program('isi_correlator.bof')

I.set_clock_freq(200)
I.set_sync_period(.002)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.arm_sync()

print "Waiting for data ..."

while True:
	I.get_data()

