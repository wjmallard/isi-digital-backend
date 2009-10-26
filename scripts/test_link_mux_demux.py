#!/usr/bin/python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-10-25
# desc: A control script for test_link_mux_demux.mdl.

import corr
import sys
import time
import optparse
import itertools
import struct
import pylab
import IPython

ipshell = IPython.Shell.IPShellEmbed()

# Control flags

ARM_RESET       = 1<<0
FORCE_TRIG      = 1<<1
FIFO_RESET      = 1<<2
ACQUIRE         = 1<<3
CAPT_RESET      = 1<<4

#
# Miscellaneous functions.
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
read_length = 1<<4
update_delay = 1 # seconds

print "Setting up plot."
pylab.ion()

index = range(0, read_length)

ax1 = pylab.subplot(411)
mx = [0] * read_length
dx = [0] * read_length
c_mx,c_dx = ax1.plot(index, mx, '-', index, dx, '--')
ax1.autoscale_view(tight=True, scalex=True, scaley=True)

ax2 = pylab.subplot(412)
my = [0] * read_length
dy = [0] * read_length
c_my,c_dy = ax2.plot(index, my, '-', index, dy, '--')
ax2.autoscale_view(tight=True, scalex=True, scaley=True)

ax3 = pylab.subplot(413)
mz = [0] * read_length
dz = [0] * read_length
c_mz,c_dz = ax3.plot(index, mz, '-', index, dz, '--')
ax3.autoscale_view(tight=True, scalex=True, scaley=True)

ax4 = pylab.subplot(414)
x0 = [0] * read_length
x1 = [0] * read_length
c_x0,c_x1 = ax4.plot(index, x0, '-', index, x1, '--')
ax4.autoscale_view(tight=True, scalex=True, scaley=True)

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
	(mx, my, mz) = read_capt(fpga, "mux", 3, read_length)
	(xL, x0, x1) = read_capt(fpga, "xaui", 3, read_length)
	(dx, dy, dz) = read_capt(fpga, "demux", 3, read_length)

	c_mx.set_ydata(mx)
	c_dx.set_ydata(dx)
	ax1.relim()
	ax1.autoscale_view(tight=False, scalex=False, scaley=True)

	c_my.set_ydata(my)
	c_dy.set_ydata(dy)
	ax2.relim()
	ax2.autoscale_view(tight=False, scalex=False, scaley=True)

	c_mz.set_ydata(mz)
	c_dz.set_ydata(dz)
	ax3.relim()
	ax3.autoscale_view(tight=False, scalex=False, scaley=True)

	c_x0.set_ydata(x0)
	c_x1.set_ydata(x1)
	ax4.relim()
	ax4.autoscale_view(tight=False, scalex=False, scaley=True)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

