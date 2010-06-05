#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisiroach import IsiRoach

class IsiFEngine (IsiRoach):

	def __init__ (self, host, port=7147, id=-1):
		IsiRoach.__init__(self, host, port)

		self._id = id

		self.clock_freq = 0 # MHz
		self.sync_period = 0 # sec
		self.fft_shift = 0
		self.eq_coeff = 0

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

