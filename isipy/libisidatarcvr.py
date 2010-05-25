#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import socket
import struct
import threading

from time import strftime

import numpy as np

class IsiDataRcvr (threading.Thread):

	def __init__ (self, addr, port):
		threading.Thread.__init__(self)

		self._addr = addr
		self._port = port
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.settimeout(1)

		self._pktlen = 3588
		self._pktfmt = np.dtype \
		([
			('pkt_id', '>i4'),
			('adc0', '>i4', 256),
			('adc1', '>i4', 256),
			('pfb0', '>i4', 64),
			('pfb1', '>i4', 64),
			('fftR', '>i4', 64),
			('fftI', '>i4', 64),
			('raR', '>i4', 64),
			('raI', '>i4', 64),
		])

		#self._PKT = np.zeros(self._pktlen, dtype=self._pktfmt)

		self.not_killed = True
		self.dump_pending = False

	def run (self):
		self._sock.bind((self._addr, self._port))
		print "Opened UDP socket."

		while self.not_killed:
			try:
				pkt = self._read_sock()
			except IsiDataRcvrKilled:
				continue

			self.process_pkt(pkt)

		print "Receive loop killed."

		self._sock.close()
		print "Closed UDP socket."

	def _read_sock (self):
		while True:
			try:
				pkt = self._sock.recv(self._pktlen)
				break
			except socket.timeout:
				print "Waiting for UDP packets ..."
				if not self.not_killed:
					raise IsiDataRcvrKilled

		return np.frombuffer(pkt, dtype=self._pktfmt)

	def process_pkt (self, pkt):
		pktid = pkt['pkt_id']
		#print "Got a packet with id %d!" % pktid
		data = self._descramble(pkt)
		if self.dump_pending == True:
			self._dump_data(data)

	def _descramble (self, pkt):
		raw_adc0 = pkt['adc0'][0].reshape([8,32])
		raw_adc1 = pkt['adc1'][0].reshape([8,32])
		adc = np.row_stack((raw_adc0, raw_adc1)).transpose().flatten()

		raw_pfb0 = pkt['pfb0'][0].reshape([8,8]).transpose()
		raw_pfb1 = pkt['pfb1'][0].reshape([8,8]).transpose()
		pfb = np.row_stack((raw_pfb0, raw_pfb1)).flatten()

		fftR = pkt['fftR'][0].reshape([8,8]).transpose().flatten()
		fftI = pkt['fftI'][0].reshape([8,8]).transpose().flatten()

		raR = pkt['raR'][0].reshape([8,8]).transpose().flatten()
		raI = pkt['raI'][0].reshape([8,8]).transpose().flatten()

		return (adc, pfb, fftR, fftI, raR, raI)

	def _dump_data (self, data):
			print "Dumping plot data to file!"
			timestamp = strftime("%Y%m%dT%H%M%S")

			self._dump_to_file(data[0], "adc", timestamp)
			self._dump_to_file(data[1], "pfb", timestamp)
			self._dump_to_file(data[2], "fftR", timestamp)
			self._dump_to_file(data[3], "fftI", timestamp)
			self._dump_to_file(data[4], "raR", timestamp)
			self._dump_to_file(data[5], "raI", timestamp)

			self.dump_pending = False

	def _dump_to_file (self, data, name, timestamp):
		filename = "%s_%s.dump" % (timestamp, name)

		f = open(filename, "w")
		for i in data:
			f.write('%d\n' % i)
		f.close()

class IsiDataRcvrKilled (Exception):
	def __str__ (self):
		return "IsiVacc killed."

