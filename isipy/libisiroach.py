#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import corr
import itertools
import time
import struct
import sys

class IsiRoachBoard(corr.katcp_wrapper.FpgaClient):
	"""
	An ISI-specific extension of the KATCP FPGA Client class.
	"""

	ARM_RESET   = 1<<0
	FORCE_TRIG  = 1<<1
	FIFO_RESET  = 1<<2
	ACQUIRE     = 1<<3

	def __init__ (self, host, port=7147, id=-1):
		super(IsiRoachBoard, self).__init__(host, port)
		self._host = host
		self._port = port
		self._id = id
		self._tv = None

		self._clock_freq = 0 # MHz
		self._sync_period = 0 # sec
		self._fft_shift = 0
		self._eq_coeff = 0

	def _set_flag (self, flags):
		reg_state = self.read_int('control')
		reg_state |= flags
		self.write_int('control', reg_state)

	def _unset_flag (self, flags):
		reg_state = self.read_int('control')
		reg_state &= ~flags
		self.write_int('control', reg_state)

	def _toggle_reset (self, flag):
		self._set_flag(flag)
		time.sleep(.1)
		self._unset_flag(flag)

	def _read_bram (self, bram_name, read_len, signed=False, offset=0):
		if signed:
			fmt = '>%si'
		else:
			fmt = '>%sI'

		bram_dump = self.read(bram_name, 4*read_len, offset=4*offset)
		bram_data = struct.unpack(fmt % read_len, bram_dump)
		return bram_data

	#
	# BEGIN corr method overrides.
	#

	def progdev (self, filename):
		if self._host == None:
			return

		super(IsiRoachBoard, self).progdev(filename)

	def read_int (self, name):
		if self._host == None:
			return 0

		return super(IsiRoachBoard, self).read_int(name)

	def write_int (self, name, value):
		if self._host == None:
			return

		super(IsiRoachBoard, self).write_int(name, value)

	#
	# END corr method overrides.
	#

	def reset (self):
		if self._host == None:
			return

		self._toggle_reset(IsiRoachBoard.FIFO_RESET)

	def arm_sync (self):
		if self._host == None:
			return
		self._set_flag(IsiRoachBoard.ARM_RESET)

	def unarm_sync (self):
		if self._host == None:
			return

		self._unset_flag(IsiRoachBoard.ARM_RESET)

	def send_sync (self):
		if self._host == None:
			return

		self._unset_flag(IsiRoachBoard.FORCE_TRIG)
		self.arm_sync()
		self._set_flag(IsiRoachBoard.FORCE_TRIG)
		time.sleep(.1)
		self._unset_flag(IsiRoachBoard.FORCE_TRIG)

	def acquire (self):
		if self._host == None:
			return

		self._set_flag(IsiRoachBoard.ACQUIRE)
		time.sleep(self._sync_period)
		self._unset_flag(IsiRoachBoard.ACQUIRE)

	def set_clock_freq (self, freq=200):
		if self._host == None:
			return

		assert (freq > 25)
		self._clock_freq = freq

	def set_sync_period (self, period=1):
		if self._host == None:
			return

		if period > 0:
			select = 1
		else:
			select = 0

		clocks = int(period * self._clock_freq * 10**6)
		self.write_int('sync_gen2_period', clocks)
		self._sync_period = period

	def set_fft_shift (self, shift):
		if self._host == None:
			return

		self.write_int('fft_shift', shift)
		self._fft_shift = shift

	def set_eq_coeff (self, coeff):
		if self._host == None:
			return

		self.write_int('eq_coeff', coeff)
		self._eq_coeff = coeff

	def get_eq_coeff (self):
		if self._host == None:
			return 0

		return self.read_int('eq_coeff')

	def get_status (self):
		if self._host == None:
			return

		status = self.read_int('status')
		return status

	def load_tvg (self, tv):
		if self._host == None:
			return

		assert (len(tv) == 4)

		try:
			self.write("adc_tvg_tvg0_bram", tv[0])
			self.write("adc_tvg_tvg1_bram", tv[1])
			self.write("adc_tvg_tvg2_bram", tv[2])
			self.write("adc_tvg_tvg3_bram", tv[3])
			self._tv = tv
		except RuntimeError:
			print "Warning: Cannot load tvg on board %d." % (self._id)

