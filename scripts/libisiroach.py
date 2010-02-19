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
	CAPT_RESET  = 1<<4

	def __init__ (self, host, port, id=-1):
		super(IsiRoachBoard, self).__init__(host, port)
		self._host = host
		self._port = port
		self._id = id
		self._tv = None
		time.sleep(.25) # NOTE: race condition!

		self._fft_shift = 0
		self._eq_coeff = 0
		self._sync_period = 0

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

	def _read_bram (self, bram_name, read_len, signed=False):
		if signed:
			fmt = '>%si'
		else:
			fmt = '>%sI'

		bram_dump = self.read(bram_name, read_len*4)
		bram_data = struct.unpack(fmt % read_len, bram_dump)
		return bram_data

	def reset (self):
		self.set_fft_shift(0)
		self.set_eq_coeff(1)
		self.set_sync_period(0x8000)
		self._set_flag(IsiRoachBoard.FIFO_RESET)
		self._set_flag(IsiRoachBoard.CAPT_RESET)
		self.write_int('control', 0)

	def arm_sync (self):
		self._unset_flag(IsiRoachBoard.ARM_RESET)
		time.sleep(.1)
		self._set_flag(IsiRoachBoard.ARM_RESET)

	def send_sync (self):
		self._unset_flag(IsiRoachBoard.FORCE_TRIG)
		self.arm_sync()
		self._set_flag(IsiRoachBoard.FORCE_TRIG)

	def set_sync_period (self, period):
		if period > 0:
			select = 1
		else:
			select = 0

		self.write_int('sync_gen2_period', period)
		self.write_int('sync_gen2_select', select)
		self._sync_period = period

	def set_fft_shift (self, shift):
		self.write_int('fft_shift', shift)
		self._fft_shift = shift

	def set_eq_coeff (self, coeff):
		self.write_int('eq_coeff', coeff)
		self._eq_coeff = coeff

	def get_status (self):
		status = self.read_int('status')
		return status

	def load_tvg (self, tv):
		assert (len(tv) == 4)

		try:
			self.write("adc_tvg_tvg0_bram", tv[0])
			self.write("adc_tvg_tvg1_bram", tv[1])
			self.write("adc_tvg_tvg2_bram", tv[2])
			self.write("adc_tvg_tvg3_bram", tv[3])
			self._tv = tv
		except RuntimeError:
			print "Warning: Cannot load tvg on board %d." % (self._id)

	def acquire (self):
		self._unset_flag(IsiRoachBoard.ACQUIRE)
		self._set_flag(IsiRoachBoard.CAPT_RESET)
		self._unset_flag(IsiRoachBoard.CAPT_RESET)
		self._set_flag(IsiRoachBoard.ACQUIRE)

	def read_vacc (self, chan_group):
		bram_name = "capt_%s_acc_%c_bram%d"
		XX_auto = self._read_bram(bram_name % ("auto", chan_group, 0), 8)
		YY_auto = self._read_bram(bram_name % ("auto", chan_group, 1), 8)
		ZZ_auto = self._read_bram(bram_name % ("auto", chan_group, 2), 8)
		XY_real = self._read_bram(bram_name % ("real", chan_group, 0), 8)
		YZ_real = self._read_bram(bram_name % ("real", chan_group, 1), 8)
		ZX_real = self._read_bram(bram_name % ("real", chan_group, 2), 8)
		XY_imag = self._read_bram(bram_name % ("imag", chan_group, 0), 8)
		YZ_imag = self._read_bram(bram_name % ("imag", chan_group, 1), 8)
		ZX_imag = self._read_bram(bram_name % ("imag", chan_group, 2), 8)
		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

class IsiRoachFake(object):
	"""
	A fake ROACH board (for testing).
	"""

	def __init__ (self, id=-1):
		self._id = id

	def read_int (self, name):
		return 0

	def write_int (self, name, value):
		pass

	def progdev (self, filename):
		pass

	def reset (self):
		pass

	def arm_sync (self):
		pass

	def send_sync (self):
		pass

	def set_sync_period (self, period):
		pass

	def set_fft_shift (self, shift):
		pass

	def set_eq_coeff (self, coeff):
		pass

	def get_status (self):
		return 0

	def load_tvg (self, tv):
		pass

	def acquire (self):
		pass

	def read_vacc (self, chan_group):
		x = (1,1,1,1,1,1,1,1)
		y = (x,x,x,x,x,x,x,x,x)
		return y

