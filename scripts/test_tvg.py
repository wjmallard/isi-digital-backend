#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2010-01-10
# desc: A control script for test_tvg.mdl.

import corr
import pylab
import IPython

import libisidemo as isi
import libtvg as tvg

ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<11
isi.update_delay = 1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

tvg_data = tvg.sine(isi.num_samples, cycles=1.5)
fpga.write("tvg_bram", tvg_data)

print "Setting up plot."

pylab.ion()

c1, = isi.create_plot(1,
	[1],
	[isi.num_samples],
	[[-2**31, 2**31]],
	["Data"])
isi.customize_window("ISI Test: tvg")

print "Looping forever."
while True:

	isi.acquire(fpga)
	isi.send_sync(fpga)

	capt = isi.read_capt(fpga, None, 3, isi.num_samples, signed=True)

	c1[0].set_ydata(capt[2])

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

