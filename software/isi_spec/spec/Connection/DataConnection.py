"""A udp connection manager. """
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import socket

import numpy as np

from Connection import Connection

class DataConnection (Connection):
	"""A udp connection manager.

	Receives streaming data from the PowerPC.
	"""
	def __init__ (self, *args, **kwargs):
		"""Create a new udp connection manager."""
		super(DataConnection, self).__init__(*args, **kwargs)

		self.sock = None

		# Data stream packet structure:
		# * 1 packet_id per packet.
		# * 5 accumulations per packet.
		#   * 64 values per accumulation.
		#   * 1 status per accumulation.
		pkt_format = np.dtype \
		([
			('pkt_id', '>u4'),
			('vacc', '>i4', 5*(64+1)),
		])
		size = self.conf['max_packets']
		self.pkt_buf = np.zeros((size, 1), dtype=pkt_format)

		self.pkt_cnt = 0

	def connect (self):
		"""Connect to the remote board."""
		if self.verbose:
			print "Connecting via udp."

		local_host = self.conf['rx_addr']
		local_port = self.conf['rx_port']

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((local_host, local_port))

	def disconnect (self):
		"""Disconnect from the remote board."""
		if self.verbose:
			print "Disconnecting udp."

		self.sock.close()
		self.sock = None

	def wait_for_pktid_reset (self):
		"""Wait for the packet id to reset.

		The pkt_id is reset at the start of an observation.
		Once a reset command is sent via the ssh connection,
		it takes some time for the packet stream to catch up.
		We drop all packets with a non-zero pkt_id until the
		pkt_id resets to zero. We leave the zeroth packet in
		the packet buffer.
		"""
		# Receive packets into pkt_buf[0]
		# until pkt_id 0 is received.
		self.pkt_cnt = 0
		self.recv_packet()
		while (self.pkt_buf[0]['pkt_id'] != 0):
			self.pkt_cnt = 0
			self.recv_packet()

	def recv_packet (self):
		"""Receive a data stream packet.

		Receive a packet and store it into the packet buffer.
		Increment the packet counter.
		"""
		try:
			self.sock.recv_into(self.pkt_buf[self.pkt_cnt])
		except socket.timeout:
			print "Unexpectedly stopped receiving packets."
			sys.exit(1)

		self.pkt_cnt += 1

	def unpack_data (self):
		"""Unpack the packet buffer; return a 3-tuple.

		Transform the contents of the packet buffer into a
		tuple of timestamps, status bits, and spectra.

		The data tuple contains:
		* time : numpy array, shape: (N,)
		* stat : numpy array, shape: (N,)
		* spec : numpy array, shape: (N, 64)
		Where N is the number of spectra received.

		Returns: (time, stat, spec)
		"""
		# There are 5 spectra in each packet,
		# so the number of spectra received is:
		num_spec = 5 * self.pkt_cnt

		# Reshape packet buffer into a data table.
		data = self.pkt_buf['vacc'][:,0,:].reshape((-1,65))

		# Slice out relevant pieces.
		time = np.arange(num_spec)
		stat = data[0:num_spec, 64]
		spec = data[0:num_spec, 0:64]

		return (time, stat, spec)

