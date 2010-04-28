#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisicorr import *

I = IsiCorrelator(('isi0', 'isi1', 'isi2'))
I.program('isi_correlator.bof')

I.set_clock_freq(200)
I.set_sync_period(.002)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.arm_sync()

print "Waiting for data ..."

I.vacc_connect("192.168.1.202")

while True:
	try:
		# Ctrl-D to quit.
		raw_input()
	except EOFError:
		I.vacc_disconnect()
		break

