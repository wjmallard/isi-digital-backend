# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-01
# desc: A library for isi_correlator development.

import corr
import itertools
import pylab
import time
import struct
import sys

import IPython
ipshell = IPython.Shell.IPShellEmbed()

#
# Static variables
#

num_samples = 0
num_chans = 0
time_read_length = 0
freq_read_length = 0
update_delay = 0
sync_period = 2**26

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

def board_connect (host='localhost', port=7147):
	print "Connecting to %s on port %d." % (host, port)
	fpga = corr.katcp_wrapper.FpgaClient(host, port)
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
	fpga.write_int('sync_gen2_period', sync_period)
	fpga.write_int('sync_gen2_select', 1)

	print "Sending intial sync pulse."
	reset_fifo(fpga)
	send_sync(fpga)

#
# Plot control functions.
#

def create_plot (num_plots, num_subplots, x_lengths, y_bounds, labels):

	x_list = []
	y_list = []
	for i in xrange(num_plots):
		num_points = x_lengths[i]

		x_sublist = []
		y_sublist = []
		for j in xrange(num_subplots[i]):
			x = range(0, num_points)
			y = [0] * num_points
			y[0] = y_bounds[i][0]
			y[1] = y_bounds[i][1]

			x_sublist += [x]
			y_sublist += [y]

		x_list += [x_sublist]
		y_list += [y_sublist]

	plot_delta = 1. / num_plots
	plot_offset = 1.0
	plot_rect = [0.04, plot_offset, 0.96, plot_delta]

	axprops = dict(yticks=[])
	yprops = dict(rotation=90)

	fig = pylab.figure()

	ax_list = []
	c_list = []
	for i in xrange(num_plots):
		plot_rect[1] -= plot_delta
		ax = fig.add_axes(plot_rect, **axprops)

		c_sublist = []
		for j in xrange(num_subplots[i]):
			c, = ax.plot(x_list[i][j], y_list[i][j], '.')
			c_sublist += [c]

		ax.set_ylabel(labels[i], **yprops)
		print "bound=[%d,%d]" % (y_bounds[i][0], y_bounds[i][1])
		ax.autoscale_view(tight=True, scalex=True, scaley=True)
		pylab.setp(ax.get_xticklabels(), visible=False)

		ax_list += [ax]
		c_list += [c_sublist]

	return c_list

def customize_window (window_title):
	m = pylab.get_current_fig_manager()
	m.set_window_title(window_title)

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
	time.sleep(1)
	bit_unset(fpga, 'control', FIFO_RESET)

def send_sync (fpga):
	"""Sends a new sync pulse through the system."""
	bit_unset(fpga, 'control', ARM_RESET | FORCE_TRIG)
	time.sleep(.1)
	bit_set(fpga, 'control', ARM_RESET)
	time.sleep(.1)
	bit_set(fpga, 'control', FORCE_TRIG)

#
# Data readout functions.
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
# Block verification functions.
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
	iter0 = itertools.chain(eq_msb[0])
	iter1 = itertools.chain(eq_msb[1])
	iter2 = itertools.chain(eq_msb[2])
	iter3 = itertools.chain(eq_msb[3])
	iter4 = itertools.chain(eq_lsb[0])
	iter5 = itertools.chain(eq_lsb[1])
	iter6 = itertools.chain(eq_lsb[2])
	iter7 = itertools.chain(eq_lsb[3])
	eq_tuple = itertools.izip \
	( \
		iter0, iter1, iter2, iter3, \
		iter4, iter5, iter6, iter7, \
	)
	eq_list = [x for y in eq_tuple for x in y]
	return eq_list

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

#
# Block readout functions
#

def read_adc (fpga, capt_block):
	(x0, x1, x2, x3) = read_capt8(fpga, capt_block, 4, time_read_length, signed=True)
	adc = uncat_adc(x0, x1, x2, x3)
	return adc

def read_fft (fpga, capt_block):
	msb = read_capt(fpga, capt_block + "_msb", 4, freq_read_length/4)
	lsb = read_capt(fpga, capt_block + "_lsb", 4, freq_read_length/4)
	fft = uncat_fft(msb, lsb)
	return fft

