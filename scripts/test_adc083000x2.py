#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-01
# desc: A control script for test_adc083000x2.mdl.

import corr
import sys
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

index = range(0, isi.num_samples)

ax1 = pylab.subplot(111)
adc = [0] * isi.num_samples
adc[0] = 128
adc[1] = -128
c_adc, = ax1.plot(index, adc, '-')
ax1.autoscale_view(tight=True, scalex=True, scaley=True)

print "Looping forever."
while True:

	isi.acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt_4x")

	c_adc.set_ydata(adc)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

