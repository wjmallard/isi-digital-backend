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
isi.update_delay = 1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

fft_shift = 1<<6
eq_coeff = 1<<8

fpga.write_int('fft_shift', fft_shift)
fpga.write_int('eq_coeff', eq_coeff)

# Script begins here.

print "Setting up plots."

pylab.ion()

c1,c2,c3,c4 = isi.create_plot(4,
	[1, 1, 1, 1],
	[isi.num_samples, isi.num_samples, isi.num_chans, isi.num_chans],
	[[-128,128],[-128,128],[0,2**16],[0,2**16]],
	["ADC Voltage","FIR Voltage","FFT Power","Eq FFT Power"])
isi.customize_window("ISI Demo: F-Engine")

print "Done setting up plots."

print "Looping forever."
while True:

	isi.acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt_4x")
	pfb = isi.read_adc(fpga, "pfb_capt_4x")
	fft = isi.read_fft(fpga, "fft")
	eq = isi.read_fft(fpga, "eq")

	c1[0].set_ydata(adc)
	c2[0].set_ydata(pfb)
	c3[0].set_ydata(fft)
	c4[0].set_ydata(eq)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

