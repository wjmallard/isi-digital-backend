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

#
# Simulation functions.
#

def unclump(A):
	"""Inverts the compression operation of the clump block."""
	X = []
	num_frames = len(A)/16
	for i in xrange(0, num_frames):
		sof = i*16 + 4
		eof = sof + 12
		X += A[sof:eof]
	X1 = X[0:None:3]
	X2 = X[1:None:3]
	X3 = X[2:None:3]
	return (X1, X2, X3)

def diff (x_list, y_list):
	return [x-y for x,y in zip(x_list, y_list)]

# Parse command line arguments.

usage = "usage: %prog ADDR"
parser = optparse.OptionParser(usage=usage)
(options, args) = parser.parse_args()

if len (args) != 1:
	parser.print_help()
	sys.exit(1)

# Script begins here.

print "Connecting to %s on port %d." % (args[0], options.port)
fpga = corr.katcp_wrapper.FpgaClient(args[0], options.port)
time.sleep(.25)

print "Setting acquisition parameters."
read_length = 1<<6
update_delay = 1 # seconds

print "Setting up plot."
pylab.ion()

index = range(0, read_length)

ax1 = pylab.subplot(311)
XA = [0] * read_length
XB = [0] * read_length
XC = [0] * read_length
c_XA,c_XB,c_XC = ax1.plot(index, XA, '-', index, XB, '--', index, XC, '-.')
ax1.autoscale_view(tight=True, scalex=True, scaley=True)

ax2 = pylab.subplot(312)
YA = [0] * read_length
YB = [0] * read_length
YC = [0] * read_length
c_YA,c_YB,c_YC = ax2.plot(index, YA, '-', index, YB, '--', index, YC, '-.')
ax1.autoscale_view(tight=True, scalex=True, scaley=True)
ax2.autoscale_view(tight=True, scalex=True, scaley=True)

ax3 = pylab.subplot(313)
ZA = [0] * read_length
ZB = [0] * read_length
ZC = [0] * read_length
c_ZA,c_ZB,c_ZC = ax3.plot(index, ZA, '-', index, ZB, '--', index, ZC, '-.')
ax3.autoscale_view(tight=True, scalex=True, scaley=True)

print "Initializing control registers."
fpga.write_int('control', 0)
fpga.write_int('sync_gen2_period', 2**26)
fpga.write_int('sync_gen2_select', 1)

print "Sending intial sync pulse."
reset_fifo(fpga)
send_sync(fpga)

print "Looping forever."
while True:

	acquire(fpga)

	(V,) = read_capt(fpga, "valid", 1, read_length)
	(S,) = read_capt(fpga, "sync", 1, read_length)

	(m0, m1, m2) = read_capt(fpga, "012", 3, read_length)
	(m3, m4, m5) = read_capt(fpga, "345", 3, read_length)
	(m6, m7, mz) = read_capt(fpga, "67Z", 3, read_length)

	(txX, txY, txZ) = read_capt8(fpga, "clump", 3, read_length * 4)
	# Swapped Y and Z to test with just one cable.
	(rxX, rxZ, rxY) = read_capt8(fpga, "xaui", 3, read_length * 4)
	(xrX, xrZ, xrY) = read_capt8(fpga, "resync", 3, read_length *4)

	(tx0, tx1, tx2) = unclump(txX)
	(tx3, tx4, tx5) = unclump(txY)
	(tx6, tx7, txz) = unclump(txZ)

	(rx0, rx1, rx2) = unclump(rxX)
	(rx3, rx4, rx5) = unclump(rxY)
	(rx6, rx7, rxz) = unclump(rxZ)

	(xr0, xr1, xr2) = unclump(xrX)
	(xr3, xr4, xr5) = unclump(xrY)
	(xr6, xr7, xrz) = unclump(xrZ)

	# Swapped Y and Z to test with just one cable.
	(XA, XB, XC) = read_capt(fpga, "X", 3, read_length)
	(YA, YB, YC) = read_capt(fpga, "Z", 3, read_length)
	(ZA, ZB, ZC) = read_capt(fpga, "Y", 3, read_length)

	c_XA.set_ydata(tx2)
	c_XB.set_ydata(xr2)
	c_XC.set_ydata(XC)
	ax1.relim()
	ax1.autoscale_view(tight=False, scalex=False, scaley=True)

	c_YA.set_ydata(tx3)
	c_YB.set_ydata(xr3)
	c_YC.set_ydata(YA)
	ax2.relim()
	ax2.autoscale_view(tight=False, scalex=False, scaley=True)

	c_ZA.set_ydata(tx6)
	c_ZB.set_ydata(xr6)
	c_ZC.set_ydata(ZA)
	ax3.relim()
	ax3.autoscale_view(tight=False, scalex=False, scaley=True)

	pylab.draw()

	print "Ok, handing over control.  Enjoy!"
	ipshell()

