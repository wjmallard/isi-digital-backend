"""A main loop controller for the ISI Digital Spectrometer."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
import os
import fcntl
from time import gmtime, asctime

class MainLoopControl ():
	"""The main loop controller.

	Terminate data collection on a Ctrl-D,
	or after a fixed observation duration,
	whichever comes first.
	"""
	def __init__ (self, conf, verbose=False):
		"""Create a main loop controller."""
		self.conf = conf
		self.verbose = verbose

		self.start_time = None
		self.stop_time = None

		self.num_packets = None
		self.packet_limit = None

	def start (self):
		"""Start the main loop.

		Record the start time.
		Initialize the packet counter.
		"""
		self.start_time = gmtime()

		# We assume that the main loop
		# is not reached until:
		# 1) the packet counter on the
		#    FPGA has been reset, and
		# 2) the udp data stream has
		#    been synchronized.
		# Synchronization consumes packet 0,
		# so the main loop starts at packet 1.
		self.num_packets = 1

		self._make_stdin_nonblocking()
		self._set_packet_counter_max()
		self._print_banner()

	def _make_stdin_nonblocking (self):
		"""Make stdin nonblocking."""
		fd = sys.stdin.fileno()
		flags = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

	def _set_packet_counter_max (self):
		"""Set the packet counter limit.

		When the packet counter reaches this limit,
		the program terminates.
		"""
		# We set the observation duration
		# by counting the number of packets received.
		self.packet_limit = self.conf['max_packets']

	def _print_banner (self):
		"""Print the main program banner."""
		print "********************************"
		print "*** ISI Digital Spectrometer ***"
		print "********************************"
		print "Start: %s" % asctime(self.start_time)

		if self.verbose:
			print "Taking %ds of data. Ctrl-D to quit." % self.conf['duration']

	def is_running (self):
		"""The main loop controller.

		Increment the packet counter.
		Check if the main loop should keep running.
		"""
		self.num_packets += 1

		if self._reached_packet_limit() \
		or self._caught_ctrl_d():
			self.stop_time = gmtime()
			return False
		else:
			return True

	def _caught_ctrl_d (self):
		"""Check if Ctrl-D has been caught."""
		try:
			raw_cmd = sys.stdin.readline()
		except IOError:
			# If stdin timed out,
			# then we didn't receive Ctrl-D.
			# Continue!
			return False
		else:
			# If stdin did not timeout, and ...
			if len(raw_cmd) == 0:
				# ... the buffer has length zero,
				# then we received Ctrl-D. Quit!
				if self.verbose:
					print "Caught Ctrl-D. Shutting down."
				return True
			else:
				# ... the buffer has non-zero length,
				# then we did receive something,
				# but it was not Ctrl-D. Continue!
				return False

	def _reached_packet_limit (self):
		"""Check if packet limit has been reached."""
		if self.num_packets > self.packet_limit:
			if self.verbose:
				print "Received %ss of data. Shutting down." % self.conf['duration']
			return True
		else:
			return False

