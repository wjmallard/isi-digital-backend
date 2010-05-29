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

CTRL_SOCK = "/tmp/isi_ctrl_sock"

class IsiDataRecv ():

	def __init__ (self, addr, port, pktfmt, datafmt):

		self._addr = addr
		self._port = port
		self._recv_sock = None
		self._ctrl_sock = None

		self._PKT = np.zeros(1, dtype=pktfmt)
		self._DATA = np.zeros(1, dtype=datafmt)

		self._ilist = None
		self._olist = None

		self.not_killed = True

	def main (self):
		self._open_recv_socket(self._addr, self._port)
		self._open_ctrl_socket(CTRL_SOCK)

		self._ilist = [self._recv_sock, self._ctrl_sock, sys.stdin]
		self._olist = []

		got_a_packet = False

		print "Entering receive loop."

		while self.not_killed:
			irdy, ordy, erdy = select.select(self._ilist, self._olist, [])

			for iobj in irdy:

				if iobj == self._recv_sock:
					self._recv_sock.recv_into(self._PKT)
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

		self._close_ctrl_socket()
		self._close_recv_socket()

	def _open_recv_socket (self, addr, port):
		self._recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._recv_sock.bind((addr, port))
		print "Opened recv socket."

	def _open_ctrl_socket (self, sockname):
		self._ctrl_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		try:
			self._ctrl_sock.bind(sockname)
		except socket.error, e:
			print "WARN: ctrl_sock exists! Removing."
			socket.os.unlink(sockname)
			self._ctrl_sock.bind(sockname)
		self._ctrl_sock.listen(5)
		print "Opened ctrl socket."

	def _open_send_socket (self, name):
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		try:
			sock.connect(name)
		except socket.error, e:
			print "ERROR: Cannot connect to %s." % name
			sock.close()
			sock = None
		return sock
		print "Opened send socket."

	def _close_recv_socket (self):
		self._recv_sock.close()
		print "Closed recv socket."

	def _close_ctrl_socket (self):
		sockname = self._ctrl_sock.getsockname()
		self._ctrl_sock.close()
		socket.os.unlink(sockname)
		print "Closed ctrl socket."

	def _handle_command (self, iobj, data):
		args = data.lstrip().strip().split()
		cmd = args.pop(0).lower()

		if cmd == "subscribe":
			print "Subscribing: %s" % args
			name = args.pop(0)
			sock = self._open_send_socket(name)
			if sock:
				print "A data stream has connected."
				self._olist.append(sock)

		elif cmd == "dump":
			print "Dumping to: %s" % args
			iobj.send(self._DATA)

		else:
			print "Unknown command: %s" % data

