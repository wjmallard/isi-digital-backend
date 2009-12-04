# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-01
# desc: A library for isi_correlator development.

import corr
import itertools
import optparse
import time
import struct

#
# Static variables
#

num_samples = 0
num_chans = 0
time_read_length = 0
freq_read_length = 0
update_delay = 0

#
# Control flags
#

ARM_RESET   = 1<<0
FORCE_TRIG  = 1<<1
FIFO_RESET  = 1<<2
ACQUIRE     = 1<<3
CAPT_RESET  = 1<<4

#
# Initialization functions.
#

def board_connect (port=7147):
	usage = "usage: %prog ADDR"
	parser = optparse.OptionParser(usage=usage)
	(options, args) = parser.parse_args()

	if len (args) != 1:
		parser.print_help()
		sys.exit(1)

	print "Connecting to %s on port %d." % (args[0], port)
	fpga = corr.katcp_wrapper.FpgaClient(args[0], port)
	time.sleep(.25)
	return fpga

def board_init (fpga):
	print "Setting acquisition parameters."

	global time_read_length
	global freq_read_length
	time_read_length = num_samples / 4
	freq_read_length = num_chans / 2

	print "Initializing control registers."
	fpga.write_int('control', 0)
	fpga.write_int('sync_gen2_period', 2**26)
	fpga.write_int('sync_gen2_select', 1)

	print "Sending intial sync pulse."
	reset_fifo(fpga)
	send_sync(fpga)

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

def read_capt (fpga, capt_name, num_brams, read_len, signed=False):
	if signed:
		fmt = '>%sb'
	else:
		fmt = '>%sB'

	capt_data = []
	for bram_num in xrange(0, num_brams):
		bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
		bram_data = fpga.read(bram_name, read_len*4)
		bram_vals = struct.unpack('>%sI' % read_len, bram_data)
		capt_data += [bram_vals]
	return capt_data

def read_capt8 (fpga, capt_name, num_brams, read_len, signed=False):
	if signed:
		fmt = '>%sb'
	else:
		fmt = '>%sB'

	capt_data = []
	for bram_num in xrange(0, num_brams):
		bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
		bram_data = fpga.read(bram_name, read_len)
		bram_vals = struct.unpack(fmt % read_len, bram_data)
		capt_data += [bram_vals]
	return capt_data

#
# Stream manipulation functions
#

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
# Block readout functions
#

def read_adc (fpga, capt_block):
	(x0, x1, x2, x3) = read_capt8(fpga, capt_block, 4, time_read_length, signed=True)
	adc = uncat_adc(x1, x1, x2, x3)
	return adc

def read_fft (fpga, capt_block):
	(x0, x1) = read_capt8(fpga, capt_block, 4, freq_read_length)
	fft = uncat_fft(x0, x1)
	return fft

