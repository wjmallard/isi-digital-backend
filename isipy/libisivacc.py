#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import itertools
import socket
import struct
import threading

import numpy as np

class IsiVacc (threading.Thread):

	BASE_PORT = 8880

	def __init__ (self, addr):
		threading.Thread.__init__(self)

		self._addr = addr
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.settimeout(1)

		self._num_pktid_bits = 20
		self._buf_length = 8

		num_groups = 8
		group_size = 2048

		self._ACCUM = np.zeros((self._buf_length, num_groups, group_size))
		self._PKTID = np.arange(self._buf_length * num_groups).reshape((self._buf_length, num_groups))

		self.not_killed = True

		self.CNTR = 0
		self.FREQ = np.arange(64) * 1600/64.

	def run (self):
		self._sock.bind((self._addr, IsiVacc.BASE_PORT))
		print "Opened UDP socket."

		lim_pktid = 1 << self._num_pktid_bits
		max_pktid = 0

		while self.not_killed:
			try:
				(board, group, pktid, accum) = self._read_sock()
			except IsiVaccKilled:
				continue

			if group == 8:
				continue

			#print "Board %d / Group %d / Pktid %d" % (board, group, pktid)
			slot = pktid % self._buf_length

			self._ACCUM[slot, group, 0:2016] = accum
			self._PKTID[slot, group] = pktid

			# handle full accumulations.
			for i in xrange(self._buf_length):
				s = (max_pktid + 1) % self._buf_length
				if self._PKTID[s].ptp() == 0:
					self.process_pkt(self._PKTID[s,0], self._ACCUM[s])
					max_pktid = (max_pktid + 1) % lim_pktid
					# Taint the row so that it doesn't get
					# read again on a packet counter reset.
					self._PKTID[s, 0] += 1
				else:
					break

		print "Receive loop killed."

		self._sock.close()
		print "Closed UDP socket."

	def process_pkt (self, pktid, accum):
		#print "Got a full packet with id %d!" % pktid
		data = self._descramble(accum)
		self.plot_data(pktid, data)

	def plot_data (self, pktid, data):
		"""FOR DEBUG USE ONLY"""

		self.CNTR += 1
		if self.CNTR < 20:
			return

		self.CNTR = 0

		plot = "\nPacket #%d:\n" % pktid
		for i in xrange(64):
			plot += "%4.0f MHz: %16d %16d %16d\n" % (self.FREQ[i], data[0][i], data[1][i], data[2][i])
#			plot += "%4.0f MHz: %16d %16d %16d\n" % (self.FREQ[i], data[3][i], data[5][i], data[7][i])
#			plot += "%4.0f MHz: %16d %16d %16d\n" % (self.FREQ[i], data[4][i], data[6][i], data[8][i])
		print plot,

	def _read_sock (self):
		while True:
			try:
				pkt = self._sock.recv(8192)
				break
			except socket.timeout:
				print "Waiting for UDP packets ..."
				if not self.not_killed:
					raise IsiVaccKilled

		(board, group, pktid) = struct.unpack('!BBxxI', pkt[0:8])
		data = struct.unpack('!2016I', pkt[8:8072])
		return (board, group, pktid, data)

	def _descramble (self, pkts):
		assert (len(pkts) == 8)

		# Group by 8s.

		a0 = [iter(pkts[0])] * 8
		a1 = [iter(pkts[1])] * 8
		a2 = [iter(pkts[2])] * 8
		a3 = [iter(pkts[3])] * 8
		a4 = [iter(pkts[4])] * 8
		a5 = [iter(pkts[5])] * 8
		a6 = [iter(pkts[6])] * 8
		a7 = [iter(pkts[7])] * 8

		b0 = itertools.izip(*a0)
		b1 = itertools.izip(*a1)
		b2 = itertools.izip(*a2)
		b3 = itertools.izip(*a3)
		b4 = itertools.izip(*a4)
		b5 = itertools.izip(*a5)
		b6 = itertools.izip(*a6)
		b7 = itertools.izip(*a7)

		# Rotate.

		c = itertools.izip(b0, b1, b2, b3, b4, b5, b6, b7)

		# Flatten.

		d = iter([itertools.chain(*x) for x in c])

		# Listify.

		XX_auto = list(d.next())
		YY_auto = list(d.next())
		ZZ_auto = list(d.next())
		XY_real = list(d.next())
		YZ_real = list(d.next())
		ZX_real = list(d.next())
		XY_imag = list(d.next())
		YZ_imag = list(d.next())
		ZX_imag = list(d.next())

		# Ignore the rest for now.

		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

class IsiVaccKilled (Exception):
	def __str__ (self):
		return "IsiVacc killed."

