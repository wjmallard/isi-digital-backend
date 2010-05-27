#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import select
import socket
import struct
import sys

import numpy as np

class IsiDataRecv ():

	def __init__ (self, addr, port, pktfmt, datafmt):

		self._addr = addr
		self._port = port
		self._data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._ctrl_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self._ctrl_sock_name = "/tmp/isi_ctrl_sock"

		self._PKT = np.zeros(1, dtype=pktfmt)
		self._DATA = np.zeros(1, dtype=datafmt)

		self._ilist = [self._data_sock, self._ctrl_sock, sys.stdin]
		self._olist = []

		self.not_killed = True

	def main (self):
		self._open_sockets()
		print "Entering receive loop."

		got_a_packet = False

		while self.not_killed:
			irdy, ordy, erdy = select.select(self._ilist, self._olist, [])

			for iobj in irdy:

				if iobj == self._data_sock:
					self._data_sock.recv_into(self._PKT)
					self._descramble()
					got_a_packet = True
					#print "Got packet #%d." % self._PKT['pkt_id'][0]

				elif iobj == self._ctrl_sock:
					print "A new control stream has connected."
					client, address = self._ctrl_sock.accept()
					self._ilist.append(client)

				elif iobj == sys.stdin:
					try:
						raw_cmd = raw_input()
					except EOFError:
						print "Caught Ctrl-D."
						self.not_killed = False

				else:
					data = iobj.recv(1024)
					if data:
						self._handle_command(iobj, data)
					else:
						print "A control stream has disconnected."
						iobj.close()
						self._ilist.remove(iobj)

			if got_a_packet:
				got_a_packet = False
				for oobj in ordy:
					try:
						oobj.send(self._DATA)
					except socket.error:
						print "A data stream has disconnected."
						oobj.close()
						self._olist.remove(oobj)

		print "Exited receive loop."
		self._close_sockets()

	def _open_sockets (self):
		self._data_sock.bind((self._addr, self._port))
		print "Opened UDP socket."

		try:
			self._ctrl_sock.bind(self._ctrl_sock_name)
		except socket.error, e:
			print "WARN: ctrl_sock exists! Removing."
			socket.os.unlink(self._ctrl_sock_name)
			self._ctrl_sock.bind(self._ctrl_sock_name)
		self._ctrl_sock.listen(5)
		print "Opened UNIX socket."

	def _close_sockets (self):
		self._ctrl_sock.close()
		socket.os.unlink(self._ctrl_sock_name)
		print "Closed UNIX socket."

		self._data_sock.close()
		print "Closed UDP socket."

	def _handle_command (self, iobj, data):
		args = data.lstrip().strip().split()
		cmd = args.pop(0).lower()

		if cmd == "subscribe":
			print "Subscribing: %s" % args
			name = args.pop(0)
			sock = self._open_push_sock(name)
			if sock:
				print "A data stream has connected."
				self._olist.append(sock)

		elif cmd == "dump":
			print "Dumping to: %s" % args
			iobj.send(self._DATA)

		else:
			print "Unknown command: %s" % data

	def _open_push_sock (self, name):
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		try:
			sock.connect(name)
		except socket.error, e:
			print "ERROR: Cannot connect to %s." % name
			sock.close()
			sock = None
		return sock
		print "Opened UNIX DGRAM socket."

