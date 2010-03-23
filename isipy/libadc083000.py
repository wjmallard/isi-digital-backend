#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import struct
import sys

class adc083000 ():
	"""
	A high-level interface to a NatSemi ADC083000 board.
	"""

	CTRL_START_CONFIG  = 1<<0
	CTRL_SELECT_ADC0   = 1<<1
	CTRL_SELECT_ADC1   = 1<<2

	CONF_OE            = 1<<8
	CONF_OV            = 1<<9
	CONF_nDE           = 1<<10
	CONF_DCP           = 1<<11
	CONF_DCS           = 1<<12
	CONF_RTD           = 1<<13
	CONF_DRE           = 1<<14

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

	def __init__ (self, roach, sel_reg="adc_ctrl_sel", cmd_reg="adc_ctrl_cmd"):
		self._roach = roach
		self._sel_reg = sel_reg
		self._cmd_reg = cmd_reg

		self._write(adc083000.ADDR_CONFIGURATION, adc083000.DFLT_CONFIGURATION)
		self._write(adc083000.ADDR_OFFSET_ADJUST, adc083000.DFLT_OFFSET_ADJUST)
		self._write(adc083000.ADDR_FSV_ADJUST, adc083000.DFLT_FSV_ADJUST)
		self._write(adc083000.ADDR_ECPA_FINE, adc083000.DFLT_ECPA_FINE)
		self._write(adc083000.ADDR_ECPA_COARSE, adc083000.DFLT_ECPA_COARSE)
		self._write(adc083000.ADDR_TEST_PATTERN, adc083000.DFLT_TEST_PATTERN)

	def _write (self, adc, addr, data):
		lower = adc | adc083000.CTRL_START_CONFIG
		sel = struct.pack('!I', lower)
		clr = struct.pack('!I', 0x0)

		upper = 0x0010 | (0x000f & addr)
		lower = (0xffff & data)
		cmd = struct.pack('!HH', upper, lower)

		roach.write_int(self._cmd_reg, cmd)
		roach.write_int(self._sel_reg, sel)
		sys.sleep(.1)
		roach.write_int(self._sel_reg, clr)

	def set_config (self, state, select=3):
		adc = select << 1
		data = (0x007f & value) << 8 | 0x80ff
		self._write(adc, adc083000.ADDR_OFFSET_ADJUST, data)

	def set_offset (self, offset, select=3):
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

		adc = select << 1
		data = (0x00ff & value) << 8 | sign << 7 | 0x007f
		self._write(adc, adc083000.ADDR_OFFSET_ADJUST, data)

	def set_amplitude (self, amplitude, select=3):
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

		adc = select << 1
		data = (0x01ff & amplitude) << 7 | 0x007f
		self._write(adc, adc083000.ADDR_FSV_ADJUST, data)

	def set_phase_fine (self, phase, select=3):
		"""
		The phase of the ADC clock is adjusted
		non-linearly, with a maximum of 110ps.
		"""

		adc = select << 1
		data = (0x01ff & phase) << 7 | 0x007f
		self._write(adc, adc083000.ADDR_ECPA_FINE, data)

	def set_phase_coarse (self, phase, select = 3):
		print "Coarse phase adjust is unimplemented!"

	def set_test_pattern (self, state=True, select=3):
		"""
		The ADC is disengaged and a test pattern
		generator is connected to the outputs.
		"""

		if state:
			data = 0xffff
		else:
			data = 0xf7ff

		adc = select << 1
		self._write(adc, adc083000.ADDR_TEST_PATTERN, data)

