#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import struct

class adc083000 ():
	"""
	A high-level interface to a NatSemi ADC083000 board.
	"""

	ADDR_CONFIGURATION = 0x1
	ADDR_OFFSET_ADJUST = 0x2
	ADDR_FSV_ADJUST    = 0x3
	ADDR_ECPA_FINE     = 0xd
	ADDR_ECPA_COARSE   = 0xe
	ADDR_TEST_PATTERN  = 0xf

	DFLT_CONFIGURATION = 0x92ff
	DFLT_OFFSET_ADJUST = 0x007f
	DFLT_FSV_ADJUST    = 0x807f
	DFLT_ECPA_FINE     = 0x007f
	DFLT_ECPA_COARSE   = 0x003f
	DFLT_TEST_PATTERN  = 0xf7ff

	def __init__ (self):
		self._write(adc083000.ADDR_CONFIGURATION, adc083000.DFLT_CONFIGURATION)
		self._write(adc083000.ADDR_OFFSET_ADJUST, adc083000.DFLT_OFFSET_ADJUST)
		self._write(adc083000.ADDR_FSV_ADJUST, adc083000.DFLT_FSV_ADJUST)
		self._write(adc083000.ADDR_ECPA_FINE, adc083000.DFLT_ECPA_FINE)
		self._write(adc083000.ADDR_ECPA_COARSE, adc083000.DFLT_ECPA_COARSE)
		self._write(adc083000.ADDR_TEST_PATTERN, adc083000.DFLT_TEST_PATTERN)

	def _write (self, addr, data):
		upper = 0x0010 | (0x000f & addr)
		lower = (0xffff & data)
		cmd = struct.pack('!HH', upper, lower)
		# TODO: write cmd to serial device
		print "Write: %s" % repr(cmd)

	def set_offset (self, offset):
		"""
		The input offset of the ADC is adjusted
		linearly and monotonically by this value.
		00h provides a nominal zero offset, while
		FFh provides a nominal 45 mV of offset.
		Thus, each code step provides 0.176 mV.
		"""

		if offset >= 0:
			value = offset
			sign = 0
		else:
			value = -offset
			sign = 1

		data = (0xffff & value) << 8 | sign << 7 | 0x7f
		self._write(adc083000.ADDR_OFFSET_ADJUST, data)

	def set_amplitude (self, amplitude):
		"""
		The gain of the ADC is adjusted	linearly
		and monotonically with a 9 bit data value.
		Adjustment range is +/-20% of the nominal
		700 mVpp differential value.

		0   = 560 mVpp
		256 = 700 mVpp
		511 = 840 mVpp

		For best performance, this value should be
		limited to the range 192 to 448 (+/-15%).
		"""

		data = (0xff80 & amplitude) | 0x7f
		self._write(adc083000.ADDR_FSV_ADJUST, data)

	def set_phase_fine (self, phase):
		"""
		The phase of the ADC clock is adjusted
		non-linearly, with a maximum of 110ps.
		"""

		data = (0xff80 & phase) | 0x7f
		self._write(adc083000.ADDR_ECPA_FINE, data)

	def set_phase_coarse (self, phase):
		print "Coarse phase adjust is unimplemented!"

	def set_test_pattern (self, state=True):
		"""
		The ADC is disengaged and a test pattern
		generator is connected to the outputs.
		"""

		if state:
			data = 0xffff
		else:
			data = 0xf7ff

		self._write(adc083000.ADDR_TEST_PATTERN, data)

