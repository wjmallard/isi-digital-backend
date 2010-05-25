#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisicorr import *

I = IsiCorrelator(('isiroach1', 'isiroach2', 'isiroach3'))
I.program('isi_correlator.bof')

I.set_clock_freq(200)
I.set_sync_period(.0007)
I.set_fft_shift(0x7f)
I.set_eq_coeff(1<<11)

I.arm_sync()

print "Waiting for data ..."

I.vacc_connect("straylight", 8880)

while True:
	try:
		# Ctrl-D to quit.
		raw_input()
	except EOFError:
		I.vacc_disconnect()
		break

