#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import socket
import struct
import threading

import numpy as np

class IsiVacc (threading.Thread):

	def __init__ (self, addr, port):
		threading.Thread.__init__(self)

		self._addr = addr
		self._port = port
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.settimeout(1)

		self._num_pktid_bits = 20
		self._buf_length = 8

		num_groups = 8
		group_size = 2048

		self._ACCUM = np.zeros((self._buf_length, num_groups, group_size), dtype=np.int32)
		self._PKTID = np.arange(self._buf_length * num_groups, dtype=np.int32).reshape((self._buf_length, num_groups))

		self.not_killed = True

		self.CNTR = 0
		self.FREQ = np.arange(64) * 1600/64

	def run (self):
		self._sock.bind((self._addr, self._port))
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

			# find full accumulations and process them.
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
		data = np.frombuffer(pkt[8:8072], dtype='>i4')
		return (board, group, pktid, data)

	def process_pkt (self, pktid, accum):
		#print "Got a full packet with id %d!" % pktid
		data = self._descramble(accum)
		self._plot_data(pktid, data)

	def _descramble (self, pkts):
		XX_auto = pkts[0:8,  0: 8].transpose().flatten()
		YY_auto = pkts[0:8,  8:16].transpose().flatten()
		ZZ_auto = pkts[0:8, 16:24].transpose().flatten()
		XY_real = pkts[0:8, 24:32].transpose().flatten()
		YZ_real = pkts[0:8, 32:40].transpose().flatten()
		ZX_real = pkts[0:8, 40:48].transpose().flatten()
		XY_imag = pkts[0:8, 48:56].transpose().flatten()
		YZ_imag = pkts[0:8, 56:64].transpose().flatten()
		ZX_imag = pkts[0:8, 64:72].transpose().flatten()

		# Ignore the rest for now.

		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

	def _plot_data (self, pktid, data):
		"""FOR DEBUG USE ONLY"""

		self.CNTR += 1
		if self.CNTR < 100:
			return

		self.CNTR = 0

		plot = "\nPacket #%d:\n" % pktid
		for i in xrange(64):
			plot += "%4.0f MHz: %12d %12d %12d %12d %12d %12d\n" % (self.FREQ[i], data[0][i], data[1][i], data[2][i], (data[3][i]**2+data[4][i]**2)**.5, (data[5][i]**2+data[6][i]**2)**.5, (data[7][i]**2+data[8][i]**2)**.5)
		print plot,

class IsiVaccKilled (Exception):
	def __str__ (self):
		return "IsiVacc killed."

