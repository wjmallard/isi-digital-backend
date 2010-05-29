#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import corr
import time
import struct

class IsiRoachBoard(corr.katcp_wrapper.FpgaClient):
	"""
	An ISI-specific extension of the KATCP FPGA Client class.
	"""

	ARM_RESET   = 1<<0
	FORCE_TRIG  = 1<<1
	RESET       = 1<<2
	ACQUIRE     = 1<<3

	def __init__ (self, host, port=7147, id=-1):
		super(IsiRoachBoard, self).__init__(host, port)
		self._host = host
		self._port = port
		self._id = id

		self.clock_freq = 0 # MHz
		self.sync_period = 0 # sec
		self.fft_shift = 0
		self.eq_coeff = 0

		time.sleep(.25)

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

	def _read_bram8 (self, bram_name, read_len, signed=False, offset=0):
		if signed:
			fmt = '>%sb'
		else:
			fmt = '>%sB'

		bram_dump = self.read(bram_name, read_len, offset=offset)
		bram_data = struct.unpack(fmt % read_len, bram_dump)
		return bram_data

	def initialize (self):
		board_is_programmed = True
		try:
			self.status()
		except RuntimeError:
			board_is_programmed = False

		if board_is_programmed:
			print "Status: Programmed."
			try:
				self.clock_freq = int(self.est_brd_clk())
				self.clock_freq -= self.clock_freq % 5
				print "* Clock freq = %d MHz" % self.clock_freq

				clks = self.read_int('sync_gen2_period')
				self.sync_period = float(clks) / (self.clock_freq * 10**6)
				print "* Sync Period = %fs" % self.sync_period

				self.fft_shift = self.read_int('fft_shift')
				print "* FFT Shift = 0x%x" % self.fft_shift

				self.eq_coeff = self.read_int('eq_coeff')
				print "* EQ Coeff = %d" % self.eq_coeff
			except RuntimeError:
				print "WARN: Failed to read some registers."
		else:
			print "Status: Unprogrammed."

	def reset (self):
		self._toggle_reset(IsiRoachBoard.RESET)

	def arm_sync (self):
		self._set_flag(IsiRoachBoard.ARM_RESET)

	def unarm_sync (self):
		self._unset_flag(IsiRoachBoard.ARM_RESET)

	def force_trig (self):
		self._unset_flag(IsiRoachBoard.FORCE_TRIG)
		self._set_flag(IsiRoachBoard.FORCE_TRIG)
		self._unset_flag(IsiRoachBoard.FORCE_TRIG)

	def set_sync_period (self, period):
		clks = int(period * self.clock_freq * 10**6)
		self.write_int('sync_gen2_period', clks)
		self.sync_period = period

	def set_fft_shift (self, shift):
		self.write_int('fft_shift', shift)
		self.fft_shift = shift

	def set_eq_coeff (self, coeff):
		self.write_int('eq_coeff', coeff)
		self.eq_coeff = coeff

	def get_status (self):
		return self.read_int('status')

