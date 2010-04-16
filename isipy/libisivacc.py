#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import itertools
import socket
import struct

class IsiVacc (object):

	BASE_PORT = 8880

	def __init__ (self, addr):
		self._socks = [None]*9
		self._last_pkt_id = -1
		self._is_initialized = False

		for i in xrange(9):
			port = IsiVacc.BASE_PORT + i
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.bind((addr, port))
			self._socks[i] = sock

	def _read_sock (self, id):
		pkt = self._socks[id].recv(8192)
		(board, group, pkt_id) = struct.unpack('!BBxxI', pkt[0:8])
		data = struct.unpack('!2016I', pkt[8:8072])
		return (board, group, pkt_id, data)

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

	def get_next (self):
		pids = [None]*8
		dats = [None]*8

		if not self._is_initialized:
			print "Synchronizing UDP streams."

		expected_pkt_id = self._last_pkt_id + 1

		cs = 0 # <-- current socket
		while cs < 8:

			pkt_id = pids[cs]

			# Grab the next packet available on the curr socket,
			# and use the packet id and data to fill the buffer.
			# (if all is well, this should run exactly 8 times.)
			if pkt_id == None:
				(board, group, pkt_id, data) = self._read_sock(cs)
				pids[cs] = pkt_id
				dats[cs] = data

			# If a stream is behind, drop old packets to catch up.
			if pkt_id < expected_pkt_id:
				while pkt_id < expected_pkt_id:
					if self._is_initialized:
						print "WARN: Got a packet late on socket %d." % cs
					(board, group, pkt_id, data) = self._read_sock(cs)
				pids[cs] = pkt_id
				dats[cs] = data

			# If a stream is ahead, update and start from the top.
			if pkt_id > expected_pkt_id:
				if self._is_initialized:
					print "WARN: Got a packet early on socket %d." % cs
				expected_pkt_id = pkt_id
				cs = 0
				continue

			# Move on to the next socket.
			cs += 1

		self._last_pkt_id = expected_pkt_id

		if not self._is_initialized:
			print "Streams are synchronized!"
			self._is_initialized = True

		return self._descramble(dats)

