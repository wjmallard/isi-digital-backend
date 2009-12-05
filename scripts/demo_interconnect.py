#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-10-25
# desc: A control script for demo_interconnect.mdl.

import corr
import pylab
import IPython

import libisidemo as isi

ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<6
isi.update_delay = .1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

# Script begins here.

print "Setting up plots."

pylab.ion()

c1,c2,c3 = isi.create_plot(3,
	[3] * 3,
	[isi.num_samples] * 3,
	[[0, 256]] * 3,
	["A","B","C"])
isi.customize_window("ISI Demo: Board Interconnect")

print "Looping forever."
while True:

	isi.acquire(fpga)

	(V,) = isi.read_capt(fpga, "valid", 1, isi.num_samples)
	(S,) = isi.read_capt(fpga, "sync", 1, isi.num_samples)

	(m0, m1, m2) = isi.read_capt(fpga, "012", 3, isi.num_samples)
	(m3, m4, m5) = isi.read_capt(fpga, "345", 3, isi.num_samples)
	(m6, m7, mz) = isi.read_capt(fpga, "67Z", 3, isi.num_samples)

	(txX, txY, txZ) = isi.read_capt8(fpga, "clump", 3, isi.num_samples * 4)
	# Swapped Y and Z to test with just one cable.
	(rxX, rxZ, rxY) = isi.read_capt8(fpga, "xaui", 3, isi.num_samples * 4)
	(xrX, xrZ, xrY) = isi.read_capt8(fpga, "resync", 3, isi.num_samples *4)

	(tx0, tx1, tx2) = isi.unclump(txX)
	(tx3, tx4, tx5) = isi.unclump(txY)
	(tx6, tx7, txz) = isi.unclump(txZ)

	(rx0, rx1, rx2) = isi.unclump(rxX)
	(rx3, rx4, rx5) = isi.unclump(rxY)
	(rx6, rx7, rxz) = isi.unclump(rxZ)

	(xr0, xr1, xr2) = isi.unclump(xrX)
	(xr3, xr4, xr5) = isi.unclump(xrY)
	(xr6, xr7, xrz) = isi.unclump(xrZ)

	# Swapped Y and Z to test with just one cable.
	(XA, XB, XC) = isi.read_capt(fpga, "X", 3, isi.num_samples)
	(YA, YB, YC) = isi.read_capt(fpga, "Z", 3, isi.num_samples)
	(ZA, ZB, ZC) = isi.read_capt(fpga, "Y", 3, isi.num_samples)

	c1[0].set_ydata(tx2)
	c1[1].set_ydata(xr2)
	c1[2].set_ydata(XC)

	c2[0].set_ydata(tx3)
	c2[1].set_ydata(xr3)
	c2[2].set_ydata(YA)

	c3[0].set_ydata(tx6)
	c3[1].set_ydata(xr6)
	c3[2].set_ydata(ZA)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

