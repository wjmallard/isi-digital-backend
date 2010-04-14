#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisiroach import *
from libisivacc import *

class IsiCorrelator (object):
	"""
	An abstraction of the three ROACH boards and their gateware.
	"""

	def __init__ (self, \
					hosts=('isi0', 'isi1', 'isi2'), \
					ports=(7147, 7147, 7147)):
		self._boards = []
		self._vacc = None
		self._num_chans = 64
		self._update_delay = .1 # seconds

		for i in xrange(3):
			new_board = None
			if hosts[i] == 'fake':
				new_board = IsiRoachFake(i)
			else:
				new_board = IsiRoachBoard(hosts[i], ports[i], i)
			self._boards += [new_board]

		self._vacc = IsiVacc("192.168.1.202")

	def program (self, filename):
		for i in xrange(3):
			print "Programming board %d." % i
			self._boards[i].progdev(filename)
			self._boards[i].write_int('corr_id', i)
		time.sleep(.25)

	def load_tvg (self, tvs):
		for i in xrange(3):
			self._boards[i].load_tvg(tvs[i])

	def reset (self):
		for board in self._boards:
			board.reset()

	def arm_sync (self):
		for board in self._boards:
			board.arm_sync()

	def send_sync (self):
		for board in self._boards:
			board.send_sync()

	def acquire (self):
		for board in self._boards:
			board.acquire()
		time.sleep(self._update_delay)

	def set_clock_freq (self, freq=200):
		for board in self._boards:
			board.set_clock_freq(freq)

	def set_sync_period (self, period):
		for board in self._boards:
			board.set_sync_period(period)

	def set_fft_shift (self, shift):
		for board in self._boards:
			board.set_fft_shift(shift)

	def set_eq_coeff (self, coeff):
		for board in self._boards:
			board.set_eq_coeff(coeff)

	def get_status (self):
		status_l = []
		for i in xrange(3):
			status = self._boards[i].get_status()
			status_l += [status]
		return status_l

	def get_num_chans (self):
		return self._num_chans

	def get_data (self):
		self._vacc.get_next()

