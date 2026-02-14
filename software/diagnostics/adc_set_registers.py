#!/usr/bin/env python2.6

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010"
__license__ = "GPL"
__status__ = "Development"

import struct
import time

class Adc ():
	"""
	A high-level interface to a National ADC083000 board.
	"""

	CTRL           = 0
	ADC0           = 4
	ADC1           = 8

	CONF_OE        = 1<<8
	CONF_OV        = 1<<9
	CONF_nDE       = 1<<10
	CONF_DCP       = 1<<11
	CONF_DCS       = 1<<12
	CONF_RTD       = 1<<13
	CONF_DRE       = 1<<14

	ADDR_CONFIG    = 0x1
	ADDR_OFFSET    = 0x2
	ADDR_AMPLITUDE = 0x3
	ADDR_PHASE_FIN = 0xd
	ADDR_PHASE_CRS = 0xe
	ADDR_TEST_PTRN = 0xf

	DFLT_CONFIG    = 0xb2ff
	DFLT_OFFSET    = 0x007f
	DFLT_AMPLITUDE = 0x807f
	DFLT_PHASE_FIN = 0x007f
	DFLT_PHASE_CRS = 0x03ff
	DFLT_TEST_PTRN = 0xf7ff

	def __init__ (self, board):
		self._board = board
		self._reg = 'adc083000x2_ctrl'
		#self.reset_to_defaults()

	def _regwrite (self, adc, addr, data):
		addr &= 0x0f
		dmsb = (data>>8) & 0xff
		dlsb = (data>>0) & 0xff
		cmd = '%c%c%c%c' % (dmsb, dlsb, addr, 0x01)
		print "Writing cmd: %s" % repr(cmd)

		self._board.blindwrite(self._reg, cmd, offset=adc)
		time.sleep(.001)

	def reset_to_defaults (self):
		print "Resetting control registers to defaults."
		self._regwrite(Adc.ADC0, Adc.ADDR_CONFIG, Adc.DFLT_CONFIG)
		self._regwrite(Adc.ADC0, Adc.ADDR_OFFSET, Adc.DFLT_OFFSET)
		self._regwrite(Adc.ADC0, Adc.ADDR_AMPLITUDE, Adc.DFLT_AMPLITUDE)
		self._regwrite(Adc.ADC0, Adc.ADDR_PHASE_FIN, Adc.DFLT_PHASE_FIN)
		self._regwrite(Adc.ADC0, Adc.ADDR_PHASE_CRS, Adc.DFLT_PHASE_CRS)
		self._regwrite(Adc.ADC0, Adc.ADDR_TEST_PTRN, Adc.DFLT_TEST_PTRN)
		self._regwrite(Adc.ADC1, Adc.ADDR_CONFIG, Adc.DFLT_CONFIG)
		self._regwrite(Adc.ADC1, Adc.ADDR_OFFSET, Adc.DFLT_OFFSET)
		self._regwrite(Adc.ADC1, Adc.ADDR_AMPLITUDE, Adc.DFLT_AMPLITUDE)
		self._regwrite(Adc.ADC1, Adc.ADDR_PHASE_FIN, Adc.DFLT_PHASE_FIN)
		self._regwrite(Adc.ADC1, Adc.ADDR_PHASE_CRS, Adc.DFLT_PHASE_CRS)
		self._regwrite(Adc.ADC1, Adc.ADDR_TEST_PTRN, Adc.DFLT_TEST_PTRN)

	def set_config (self, adc, state):
		data = (0x007f & state) << 8 | 0x80ff
		self._regwrite(adc, Adc.ADDR_CONFIG, data)

	def set_offset (self, adc, offset):
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

		data = (0x00ff & value) << 8 | sign << 7 | 0x007f
		self._regwrite(adc, Adc.ADDR_OFFSET, data)

	def set_amplitude (self, adc, amplitude):
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

		data = (0x01ff & amplitude) << 7 | 0x007f
		self._regwrite(adc, Adc.ADDR_AMPLITUDE, data)

	def set_phase_fine (self, adc, phase):
		"""
		The phase of the ADC clock is adjusted
		non-linearly, with a maximum of 110ps.
		"""

		data = (0x01ff & phase) << 7 | 0x007f
		self._regwrite(adc, Adc.ADDR_PHASE_FIN, data)

	def set_phase_coarse (self, adc, phase):
		print "Coarse phase adjust is unimplemented!"

	def enable_phase_adjust (self):
		data = 0x807f
		self._regwrite(Adc.ADC0, Adc.ADDR_PHASE_CRS, data)

	def disable_phase_adjust (self):
		data = 0x007f
		self._regwrite(Adc.ADC0, Adc.ADDR_PHASE_CRS, data)

	def set_test_pattern (self, adc, state=True):
		"""
		The ADC is disengaged and a test pattern
		generator is connected to the outputs.
		"""

		if state:
			data = 0xffff
		else:
			data = 0xf7ff

		self._regwrite(adc, Adc.ADDR_TEST_PTRN, data)

	def offset (self, offset0=0, offset1=0):
		if offset0 < -255 \
			or offset0 > 255 \
			or offset1 < -255 \
			or offset1 > 255:
			print "Invalid offset. Must be in [-255,255]."
			return
		self.set_offset(Adc.ADC0, offset0)
		self.set_offset(Adc.ADC1, offset1)

	def amplitude (self, ampl0=256, ampl1=256):
		if ampl0 < 0 \
			or ampl0 > 511 \
			or ampl1 < 0 \
			or ampl1 > 511:
			print "Invalid amplitude. Must be in [0,511]."
			return
		self.set_amplitude(Adc.ADC0, ampl0)
		self.set_amplitude(Adc.ADC1, ampl1)

	def phase (self, phase=0):
		if phase < 0 \
			or phase > 511:
			print "Invalid phase. Must be in [0,511]."
			return
		self.set_phase_fine(Adc.ADC1, phase)

	def test (self, test0=False, test1=False):
		self.set_test_pattern(Adc.ADC0, test0)
		self.set_test_pattern(Adc.ADC1, test1)

if __name__ == "__main__":
	from corr import katcp_wrapper as katcp
	from IPython import Shell
	import sys

	ipshell = Shell.IPShellEmbed()

	try:
		board = sys.argv[1]
	except IndexError:
		print "Usage: %s HOST" % sys.argv[0]
		sys.exit(1)

	R = katcp.FpgaClient(board, 7147)
	adc = Adc(R)
	print "Available commands:"
	print "  adc.amplitude(adc0, adc1)"
	print "  adc.offset(adc0, adc1)"
	print "  adc.phase(adc1)"
	print "  adc.test(adc0, adc1)"
	print "  adc.reset_to_defaults()"
	print "No arg resets to default."
	ipshell()

