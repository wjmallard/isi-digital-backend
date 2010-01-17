#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import libisicorr

import corr
import itertools
import pylab
import time
import struct
import sys

import IPython
ipshell = IPython.Shell.IPShellEmbed()

class IsiCorrelatorDebug (libisicorr.IsiRoachBoard):
	def __init__ (self, host, port):
		super(IsiCorrelatorDebug, self).__init__(host, port)

		self._data_l = []
		self._figure = None

	def gen_plot (self, data_l):
		assert (type(data_l) == list)

		if (type(data[0]) != list):
			self._data_l = [data_l]
		else:
			self._data_l = data_l

		num_plots = len(self._data_l)
		plot_delta = 1. / num_plots
		plot_offset = 1.0
		plot_rect = [0.04, plot_offset, 0.96, plot_delta]

		axprops = dict(xticklabels=[], yticklabels=[])
		self._figure = pylab.figure()

		c_list = []
		for i in xrange(num_plots):
			data = self._data_l[i]
			plot_rect[1] -= plot_delta
			ax = self._figure.add_axes(plot_rect, **axprops)
			c, = ax.plot(data, '.')
			ax.autoscale_view(tight=True, scalex=True, scaley=True)

		return c_list

	def _read_bram8 (self, bram_name, read_len):
		bram_dump = self.read(bram_name, read_len)
		bram_data = struct.unpack('>%sb' % read_len, bram_dump)
		return bram_data

	def read_capt (self, capt_name, num_brams, read_len):
		capt_data = []
		for bram_num in xrange(num_brams):
			bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
			bram_vals = self._read_bram(bram_name, read_len)
			capt_data += [bram_vals]
		return capt_data

	def read_capt8 (self, capt_name, num_brams, read_len):
		capt_data = []
		for bram_num in xrange(num_brams):
			bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
			bram_vals = self._read_bram8(bram_name, read_len)
			capt_data += [bram_vals]
		return capt_data

	#
	# Block verification methods.
	#

	def uncat_adc (self, adc0_msb, adc0_lsb, adc1_msb, adc1_lsb):
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

	def uncat_fft (self, eq_msb, eq_lsb):
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

	def unclump(self, A):
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

	def diff (self, x_list, y_list):
		return [x-y for x,y in zip(x_list, y_list)]

	#
	# Block readout functions
	#

	def read_adc (self, capt_block, read_len):
		(x0, x1, x2, x3) = self.read_capt8(capt_block, 4, read_len/4)
		adc = self.uncat_adc(x0, x1, x2, x3)
		return adc

	def read_fft (self, capt_block, read_len):
		msb = self.read_capt(capt_block + "_msb", 4, read_len/4)
		lsb = self.read_capt(capt_block + "_lsb", 4, read_len/4)
		fft = self.uncat_fft(msb, lsb)
		return fft

