#!/usr/bin/python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-10-25
# desc: A control script for test_interconnect.mdl.

import corr
import sys
import time
import optparse
import itertools
import struct
import pylab
import IPython

from itertools import *

ipshell = IPython.Shell.IPShellEmbed()

# Control flags

ARM_RESET       = 1<<0
FORCE_TRIG      = 1<<1
FIFO_RESET      = 1<<2
ACQUIRE         = 1<<3
CAPT_RESET      = 1<<4

#
# Board control functions.
#

def bit_set (fpga, reg_name, flags):
	reg_state = fpga.read_int(reg_name)
	reg_state |= flags
	fpga.write_int(reg_name, reg_state)

def bit_unset (fpga, reg_name, flags):
	reg_state = fpga.read_int(reg_name)
	reg_state &= ~flags
	fpga.write_int(reg_name, reg_state)

def reset_fifo (fpga):
	bit_set(fpga, 'control', FIFO_RESET)
	time.sleep(.1)
	bit_unset(fpga, 'control', FIFO_RESET)

def send_sync (fpga):
	"""Sends a new sync pulse through the system."""
	bit_unset(fpga, 'control', ARM_RESET | FORCE_TRIG)
	time.sleep(.1)
	bit_set(fpga, 'control', ARM_RESET)
	time.sleep(.1)
	bit_set(fpga, 'control', FORCE_TRIG)

#
# FPGA data readout functions.
#

def acquire (fpga):
	bit_unset(fpga, 'control', ACQUIRE)
	bit_set(fpga, 'control', CAPT_RESET)
	bit_unset(fpga, 'control', CAPT_RESET)
	bit_set(fpga, 'control', ACQUIRE)
	time.sleep(update_delay)

def read_capt (fpga, capt_name, num_brams, read_len):
	capt_data = []
	for bram_num in xrange(0, num_brams):
		bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
		bram_data = fpga.read(bram_name, read_len*4)
		bram_vals = struct.unpack('>%sI' % read_len, bram_data)
		capt_data += [bram_vals]
	return capt_data

def read_capt8 (fpga, capt_name, num_brams, read_len):
	capt_data = []
	for bram_num in xrange(0, num_brams):
		bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
		bram_data = fpga.read(bram_name, read_len)
		bram_vals = struct.unpack('>%sB' % read_len, bram_data)
		capt_data += [bram_vals]
	return capt_data

#
# Simulation functions.
#

def unclump(A):
	A4 = islice(A, 4, None, 16)
	A5 = islice(A, 5, None, 16)
	A6 = islice(A, 6, None, 16)
	A7 = islice(A, 7, None, 16)
	A8 = islice(A, 8, None, 16)
	A9 = islice(A, 9, None, 16)
	A10 = islice(A, 10, None, 16)
	A11 = islice(A, 11, None, 16)
	A12 = islice(A, 12, None, 16)
	A13 = islice(A, 13, None, 16)
	A14 = islice(A, 14, None, 16)
	A15 = islice(A, 15, None, 16)
	A_iter = izip(A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15)
	A_list = [x for y in A_iter for x in y]
	X1 = islice(A_list, 0, None, 3)
	X2 = islice(A_list, 1, None, 3)
	X3 = islice(A_list, 2, None, 3)
	return (X1, X2, X3)

def diff (x_list, y_list):
	return [x-y for x,y in zip(x_list, y_list)]

# Parse command line arguments.

usage = "usage: %prog [options] ADDR"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-P", "--port",
	dest = "port", default = 7147,
	help = "connect on the given port")
parser.add_option("-p", "--program",
	dest = "boffile", default = None,
	help = "program with the specified bof file")

(options, args) = parser.parse_args()

if len (args) != 1:
	parser.print_help()
	sys.exit(1)

# Script begins here.

print "Connecting to %s on port %d." % (args[0], options.port)
fpga = corr.katcp_wrapper.FpgaClient(args[0], options.port)
time.sleep(.25)

if options.boffile:
	print "Programming device with %s." % (options.boffile)
	status = fpga.progdev(options.boffile)
	if status != "ok":
		print "ERROR: Cannot program device!"
		sys.exit(1)
	else:
		print "Program succeeded."

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

	(m0, m1, m2) = read_capt(fpga, "012", 3, read_length)
	(m3, m4, m5) = read_capt(fpga, "345", 3, read_length)
	(m6, m7, mZ) = read_capt(fpga, "67Z", 3, read_length)

	(txX, txY, txZ) = read_capt8(fpga, "clump", 3, read_length)
	(rxX, rxY, rxZ) = read_capt8(fpga, "xaui", 3, read_length)
	(xrX, xrY, xrZ) = read_capt8(fpga, "resync", 3, read_length)

	(XA, XB, XC) = read_capt(fpga, "X", 3, read_length)
	(YA, YB, YC) = read_capt(fpga, "Y", 3, read_length)
	(ZA, ZB, ZC) = read_capt(fpga, "Z", 3, read_length)

	c_XA.set_ydata(XA)
	c_XB.set_ydata(XB)
	c_XC.set_ydata(XC)
	ax1.relim()
	ax1.autoscale_view(tight=False, scalex=False, scaley=True)

	c_YA.set_ydata(YA)
	c_YB.set_ydata(YB)
	c_YC.set_ydata(YC)
	ax2.relim()
	ax2.autoscale_view(tight=False, scalex=False, scaley=True)

	c_ZA.set_ydata(ZA)
	c_ZB.set_ydata(ZB)
	c_ZC.set_ydata(ZC)
	ax3.relim()
	ax3.autoscale_view(tight=False, scalex=False, scaley=True)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

