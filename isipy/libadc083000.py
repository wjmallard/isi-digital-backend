#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import struct

class adc083000 ():
	"""
	An interface to a NatSemi ADC board.
	"""

	ADDR_CONFIGURATION = 0x1
	ADDR_OFFSET        = 0x2
	ADDR_FSV_ADJUST    = 0x3
	ADDR_ECPA_FINE     = 0xD
	ADDR_ECPA_COARSE   = 0xE
	ADDR_TEST_PATTERN  = 0xF

	DFLT_CONFIGURATION = 0x92FF
	DFLT_OFFSET        = 0x007F
	DFLT_FSV_ADJUST    = 0x807F
	DFLT_ECPA_FINE     = 0x007F
	DFLT_ECPA_COARSE   = 0x003F
	DFLT_TEST_PATTERN  = 0xF7FF

	def __init__ (self):
		pass

	def _write (self, addr, data):
		upper = (0x000f & addr) | 0x0010
		lower = (0xffff & data)
		cmd = struct.pack('!HH', upper, lower)
		# TODO: write cmd to serial device
		print "Write: %s" % cmd

	
