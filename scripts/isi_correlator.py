#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-30
# desc: The ISI Correlator display.

from libisi import *

I = IsiCorrelator(hosts=('localhost', 'localhost', 'fake'), ports=(7147,7148,0))
D = IsiDisplay()

#I.program('isi_correlator.bof')

I.set_sync_period(2**12)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.send_sync()

while True:
	I.acquire()
	data = I.get_data()
	D.set_data(data)

