#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-01
# desc: A control script for test_adc083000x2.mdl.

import corr
import pylab
import IPython

import libisidemo as isi

ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<7
isi.update_delay = 1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

print "Setting up plot."
pylab.ion()

(adc, c1) = isi.create_plot(1, 1, isi.num_samples, -128, 128, "Voltage")

print "Looping forever."
while True:

	isi.acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt_4x")

	c1.set_ydata(adc)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

