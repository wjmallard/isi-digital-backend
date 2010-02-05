#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisiroach import *

class IsiCorrelator(object):
	"""
	An abstraction of the three ROACH boards and their gateware.
	"""

	def __init__ (self, \
					hosts=('isi0', 'isi1', 'isi2'), \
					ports=(7147, 7147, 7147)):
		self._boards = []
		self._hosts = hosts
		self._ports = ports
		self._num_chans = 64
		self._update_delay = .1 # seconds

		self._connect()

	def _connect (self):
		assert (len(self._hosts) == 3)
		assert (len(self._ports) == 3)

		for i in xrange(3):
			new_board = None
			if self._hosts[i] == 'fake':
				new_board = IsiRoachFake(i)
			else:
				new_board = IsiRoachBoard(self._hosts[i], self._ports[i], i)
			self._boards += [new_board]

	def program (self, filename):
		print "Programming boards ..."
		for board in self._boards:
			board.progdev(filename)
		time.sleep(.25)
		print "... done!"

	def load_tvg (self, tvs):
		for i in xrange(3):
			self._boards[i].load_tvg(tvs[i])

	def set_sync_period (self, period):
		for board in self._boards:
			board.set_sync_period(period)

	def set_fft_shift (self, shift):
		for board in self._boards:
			board.set_fft_shift(shift)

	def set_eq_coeff (self, coeff):
		for board in self._boards:
			board.set_eq_coeff(coeff)

	def get_num_chans (self):
		return self._num_chans

	def get_status (self):
		status_l = []
		for i in xrange(3):
			status = self._boards[i].get_status()
			status_l += [status]
		return status_l

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

	def get_data (self):
		"""Read vacc data and permute it into a useful order."""
		XA = self._boards[0].read_vacc('A')
		XB = self._boards[0].read_vacc('B')
		XC = self._boards[0].read_vacc('C')
		YA = self._boards[1].read_vacc('A')
		YB = self._boards[1].read_vacc('B')
		YC = self._boards[1].read_vacc('C')
		ZA = self._boards[2].read_vacc('A')
		ZB = self._boards[2].read_vacc('B')

		#
		# Begin fucking magic.
		#

		# 3-D matrix transpose: (x,y,z)->(y,x,z)
		a = itertools.izip(XA, XB, XC, YA, YB, YC, ZA, ZB)

		# 3-D matrix transpose: (y,x,z)->(y,z,x)
		b = [itertools.izip(*x) for x in a]

		# 2-D matrix collapse: (y,z,x)->(y,z*x)
		XX_auto = [x for y in b[0] for x in y]
		YY_auto = [x for y in b[1] for x in y]
		ZZ_auto = [x for y in b[2] for x in y]
		XY_real = [x for y in b[3] for x in y]
		YZ_real = [x for y in b[4] for x in y]
		ZX_real = [x for y in b[5] for x in y]
		XY_imag = [x for y in b[6] for x in y]
		YZ_imag = [x for y in b[7] for x in y]
		ZX_imag = [x for y in b[8] for x in y]

		#
		# End fucking magic.
		#

		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

