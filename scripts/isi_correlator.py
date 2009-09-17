#!/usr/bin/python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-09-11
# desc: A control and readout script for the ISI Correlator.

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

SNAP_ENABLE     = 1<<0
SNAP_TRIG       = 1<<1
SNAP_WE         = 1<<2

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

def bit_toggle (fpga, reg_name, flags):
	reg_state = fpga.read_int(reg_name)
	reg_state ^= flags
	fpga.write_int(reg_name, reg_state)

def bit_off_on (fpga, reg_name, flags):
	reg_state = fpga.read_int(reg_name)
	fpga.write_int(reg_name, reg_state & ~flags)
	fpga.write_int(reg_name, reg_state | flags)

def bit_on_off (fpga, reg_name, flags):
	reg_state = fpga.read_int(reg_name)
	fpga.write_int(reg_name, reg_state | flags)
	fpga.write_int(reg_name, reg_state & ~flags)

def read_snap_addr (fpga, name):
	reg_name = "capt_%s_snap64_addr" % name
	x = fpga.read_int(reg_name)
	print ("%s = %d") % (reg_name, x)

def send_sync (fpga):
	"""Sends a new sync pulse through the system."""
	bit_unset(fpga, 'control', ARM_RESET | FORCE_TRIG)
	time.sleep(.1)
	bit_set(fpga, 'control', ARM_RESET)
	time.sleep(.1)
	bit_set(fpga, 'control', FORCE_TRIG)

def uncat_adc (adc0_msb, adc0_lsb, adc1_msb, adc1_lsb):
	"""Un-concatenates and re-interleaves adc data."""
	iter0 = itertools.chain(adc0_msb)
	iter1 = itertools.chain(adc0_lsb)
	iter2 = itertools.chain(adc1_msb)
	iter3 = itertools.chain(adc1_lsb)
	adc_tuple = itertools.izip \
	( \
		iter0, iter0, iter0, iter0, \
		iter1, iter1, iter1, iter1, \
		iter2, iter2, iter2, iter2, \
		iter3, iter3, iter3, iter3 \
	)
	adc_list = [x for y in adc_tuple for x in y]
	return adc_list

def uncat_fft (eq_msb, eq_lsb):
	"""Un-concatenates and re-interleaves fft data."""
	iter0 = itertools.chain(eq_msb)
	iter1 = itertools.chain(eq_lsb)
	eq_tuple = itertools.izip \
	( \
		iter0, iter0, iter0, iter0, \
		iter1, iter1, iter1, iter1, \
	)
	eq_list = [x for y in eq_tuple for x in y]
	return eq_list

#
# FPGA data readout functions.
#

def acquire (fpga):
	bit_unset(fpga, 'control', ACQUIRE)

	bit_off_on(fpga, 'capt_adc0_snap64_ctrl', SNAP_ENABLE)
	bit_off_on(fpga, 'capt_adc1_snap64_ctrl', SNAP_ENABLE)
	bit_off_on(fpga, 'capt_pfb0_snap64_ctrl', SNAP_ENABLE)
	bit_off_on(fpga, 'capt_pfb1_snap64_ctrl', SNAP_ENABLE)
	bit_off_on(fpga, 'capt_fft_snap64_ctrl', SNAP_ENABLE)
	bit_off_on(fpga, 'capt_eq_snap64_ctrl', SNAP_ENABLE)

	bit_set(fpga, 'control', ACQUIRE)
	time.sleep(update_delay)

def read_adc (fpga):
	adc0_msb = fpga.read('capt_adc0_snap64_bram_msb', time_read_length)
	adc0_lsb = fpga.read('capt_adc0_snap64_bram_lsb', time_read_length)
	adc1_msb = fpga.read('capt_adc1_snap64_bram_msb', time_read_length)
	adc1_lsb = fpga.read('capt_adc1_snap64_bram_lsb', time_read_length)

	adc_blk0 = struct.unpack('>%sb' % time_read_length, adc0_msb)
	adc_blk1 = struct.unpack('>%sb' % time_read_length, adc0_lsb)
	adc_blk2 = struct.unpack('>%sb' % time_read_length, adc1_msb)
	adc_blk3 = struct.unpack('>%sb' % time_read_length, adc1_lsb)

	adc = uncat_adc(adc_blk0, adc_blk1, adc_blk2, adc_blk3)
	return adc

def read_pfb (fpga):
	pfb0_msb = fpga.read('capt_pfb0_snap64_bram_msb', time_read_length)
	pfb0_lsb = fpga.read('capt_pfb0_snap64_bram_lsb', time_read_length)
	pfb1_msb = fpga.read('capt_pfb1_snap64_bram_msb', time_read_length)
	pfb1_lsb = fpga.read('capt_pfb1_snap64_bram_lsb', time_read_length)

	pfb_blk0 = struct.unpack('>%sb' % time_read_length, pfb0_msb)
	pfb_blk1 = struct.unpack('>%sb' % time_read_length, pfb0_lsb)
	pfb_blk2 = struct.unpack('>%sb' % time_read_length, pfb1_msb)
	pfb_blk3 = struct.unpack('>%sb' % time_read_length, pfb1_lsb)

	pfb = uncat_adc(pfb_blk0, pfb_blk1, pfb_blk2, pfb_blk3)
	return pfb

def read_fft (fpga):
	fft_msb = fpga.read('capt_fft_snap64_bram_msb', freq_read_length)
	fft_lsb = fpga.read('capt_fft_snap64_bram_lsb', freq_read_length)

	fft_blk0 = struct.unpack('>%sB' % freq_read_length, fft_msb)
	fft_blk1 = struct.unpack('>%sB' % freq_read_length, fft_lsb)

	fft = uncat_fft(fft_blk0, fft_blk1)
	return fft

def read_eq (fpga):
	eq_msb = fpga.read('capt_eq_snap64_bram_msb', freq_read_length)
	eq_lsb = fpga.read('capt_eq_snap64_bram_lsb', freq_read_length)

	eq_blk0 = struct.unpack('>%sB' % freq_read_length, eq_msb)
	eq_blk1 = struct.unpack('>%sB' % freq_read_length, eq_lsb)

	eq = uncat_fft(eq_blk0, eq_blk1)
	return eq

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
sample_length = 1<<7
num_chans = 1<<6
time_read_length = sample_length / 4
freq_read_length = num_chans / 2

fft_shift = 1<<6
eq_coeff = 1<<8
update_delay = .1 # seconds

print "Setting up plot."
pylab.ion()

ax1 = pylab.subplot(411)
#title("Raw ADC Output")
#xlabel("Samples")
pylab.ylabel("Voltage")
adc = [0] * sample_length
c1, = ax1.plot(adc)
ax1.autoscale_view(tight=True, scalex=True, scaley=True)

ax2 = pylab.subplot(412)
#title("PFB FIR Data")
#xlabel("Samples")
pylab.ylabel("Voltage")
pfb = [0] * sample_length
c2, = ax2.plot(pfb)
ax2.autoscale_view(tight=True, scalex=True, scaley=True)

fft = [0] * num_chans
fft[0] = 256
ax3 = pylab.subplot(413)
c3, = ax3.plot(fft)
ax3.autoscale_view(tight=True, scalex=True, scaley=True)
#title("Spectrometer")
#xlabel("Frequency Bin")
pylab.ylabel("Power")

eq = [0] * num_chans
eq[0] = 256
ax4 = pylab.subplot(414)
c4, = ax4.plot(eq)
ax4.autoscale_view(tight=True, scalex=True, scaley=True)
#title("Spectrometer")
#xlabel("Frequency Bin")
pylab.ylabel("Eq. Power")

print "Initializing control registers."
fpga.write_int('fft_shift', fft_shift)
fpga.write_int('eq_coeff', eq_coeff)
fpga.write_int('control', 0)
fpga.write_int('capt_adc0_snap64_ctrl', 0)
fpga.write_int('capt_adc1_snap64_ctrl', 0)
fpga.write_int('capt_pfb0_snap64_ctrl', 0)
fpga.write_int('capt_pfb1_snap64_ctrl', 0)
fpga.write_int('capt_fft_snap64_ctrl', 0)
fpga.write_int('capt_eq_snap64_ctrl', 0)

fpga.write_int('sync_gen2_period', 2**26)
fpga.write_int('sync_gen2_select', 1)

print "Sending intial sync pulse."
send_sync(fpga)


print "Looping forever."
while True:

	acquire(fpga)
	adc = read_adc(fpga)
	pfb = read_pfb(fpga)
	fft = read_fft(fpga)
	eq = read_eq(fpga)

	c1.set_ydata(adc)
	ax1.relim()
	ax1.autoscale_view(tight=False, scalex=False, scaley=True)

	c2.set_ydata(pfb)
	ax2.relim()
	ax2.autoscale_view(tight=False, scalex=False, scaley=True)

	c3.set_ydata(fft)
	#ax3.relim()
	#ax3.autoscale_view(tight=False, scalex=False, scaley=True)

	c4.set_ydata(eq)
	#ax4.relim()
	#ax4.autoscale_view(tight=False, scalex=False, scaley=True)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

