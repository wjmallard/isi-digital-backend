#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-01
# desc: A control script for test_adc083000x2.mdl.

import corr
import pylab

import libisidemo as isi

import IPython
ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<6
isi.update_delay = .25 # seconds

fpga = isi.board_connect()
fpga.progdev('test_adc083000x2.bof')
#fpga.progdev('demo_fengine.bof')
isi.board_init(fpga)

print "Setting up plot."

pylab.ion()

c1, = isi.create_plot(1,
	[1],
	[isi.num_samples],
	[[-128, 128]],
	["Voltage"])
isi.customize_window("ISI Test: adc083000x2")

print "Looping forever."
while True:

	isi.acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt")

	c1[0].set_ydata(adc)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

