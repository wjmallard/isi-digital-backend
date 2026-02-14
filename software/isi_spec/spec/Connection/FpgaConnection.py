"""A katcp connection manager."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
from time import sleep

from corr import katcp_wrapper as katcp

from Connection import Connection

class FpgaConnection (Connection):
	"""A katcp connecton manager.

	Controls spectrometer gateware running on the FPGA.
	Interfaces to the FPGA via a tcpborphserver daemon
	running in Linux on the PowerPC.
	"""
	def __init__ (self, *args, **kwargs):
		"""Create a new katcp connection manager."""
		super(FpgaConnection, self).__init__(*args, **kwargs)

		self.katcp = None
		self.name = self.conf['roach_id']

	def connect (self):
		"""Connect to the remote board"""
		if self.verbose:
			print "Connecting via katcp."

		self.katcp = katcp.FpgaClient(self.name)
		sleep(.1)
		try:
			self.katcp.ping()
		except katcp.KatcpClientError:
			print "*** ERROR ***"
			print "%s unreachable." % self.name
			print "Is it powered on?"
			print "Is it on the ROACH subnet?"
			sys.exit(1)

	def disconnect (self):
		"""Disconnect from the remote board."""
		if self.verbose:
			print "Disconnecting katcp."

		self.katcp = None

	def program_fpga (self):
		"""Flash the FPGA with a bitstream.

		The desired bitstream is specified in spec.cfg.
		We briefly sleep() to let the system stabilize.
		We then set all config registers on the board,
		and reset the packet counter for good measure.
		"""
		if self.verbose:
			print "Programming board: %s" % self.conf['bitstream']

		self.katcp.progdev(self.conf['bitstream'])
		sleep(.1)

		self._configure_board()
		self.reset_pktid_counter()

	def _configure_board (self):
		"""Configure registers on the FPGA.

		Register settings are specified in, or derived
		from, spec.cfg and fits.cfg.
		"""
		if self.verbose:
			print "Configuring board."

		self.katcp.write_int('sync_gen_period', self.conf['sync_gen_period'])

	def reset_pktid_counter (self):
		"""Reset the FPGA packet counter.

		The FPGA keeps a running count of packets as it
		sends them. These serve as timestamps, relative
		to the start of an observing run.

		The spectrometer bitstream's packet counter will
		reset when it sees a rising edge on the 'control'
		register's least significant bit.
		"""
		if self.verbose:
			print "Resetting pkt_id counters."

		self.katcp.write_int('control', 0)
		self.katcp.write_int('control', 1)

