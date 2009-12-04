#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-09-11
# desc: A control script for demo_fengine.mdl.

import corr
import pylab
import IPython

import libisidemo as isi

ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<7
isi.num_chans = 1<<6
isi.update_delay = .1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

fft_shift = 1<<6
eq_coeff = 1<<8

fpga.write_int('fft_shift', fft_shift)
fpga.write_int('eq_coeff', eq_coeff)

# Script begins here.

print "Setting up plots."

pylab.ion()

(adc, c1) = isi.create_plot(4, 1, isi.num_samples, -256, 256, "Voltage")
(pfb, c2) = isi.create_plot(4, 2, isi.num_samples, -256, 256, "Voltage")
(fft, c3) = isi.create_plot(4, 3, isi.num_chans, -256, 256, "Power")
(eq, c4) = isi.create_plot(4, 4, isi.num_chans, -256, 256, "Eq. Power")

print "Done setting up plots."

print "Looping forever."
while True:

	isi.acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt_4x")
	pfb = isi.read_adc(fpga, "pfb_capt_4x")
	fft = isi.read_fft(fpga, "fft_capt_2x")
	eq = isi.read_fft(fpga, "eq_capt_2x")

	c1.set_ydata(adc)
	c2.set_ydata(pfb)
	c3.set_ydata(fft)
	c4.set_ydata(eq)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

