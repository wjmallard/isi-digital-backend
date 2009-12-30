#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-30
# desc: A control and readout script for the ISI Correlator.

import pylab
import time
import IPython

from libisi import *

ipshell = IPython.Shell.IPShellEmbed()

I = IsiRoachBoard('localhost', 7147)

I.write_int('fft_shift', 0x7f)
I.write_int('eq_coeff', (2**7)<<8)
I.write_int('sync_gen2_period', 2**26)
I.write_int('sync_gen2_select', 2**26)

time.sleep(2)
I.send_sync()
time.sleep(1)
I.acquire()

ipshell()

#
# ASSUME THAT NOTHING WORKS BELOW HERE ...
#

# Script begins here.

print "Setting up plots."

pylab.ion()

c3,c4 = isi.create_plot(2,
	[1, 1],
	[isi.num_chans, isi.num_chans],
	[[0,2**20],[0,2**8]],
	["FFT Power","Eq FFT Power"])
isi.customize_window("ISI Demo: F-Engine")

print "Done setting up plots."

print "Looping forever."
while True:

	isi.acquire(fpga0)

	fft = isi.read_fft(fpga0, "fft")
	eq = isi.read_fft(fpga0, "eq")

	c3[0].set_ydata(fft)
	c4[0].set_ydata(eq)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

