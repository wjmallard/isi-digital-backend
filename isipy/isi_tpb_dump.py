#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import libisiroach
import socket
import sys

import numpy as np
from libisiroach import IsiRoachBoard
from time import strftime

DATA_SOCK = "/tmp/isi_data_sock"
CTRL_SOCK = "/tmp/isi_ctrl_sock"

datafmt = np.dtype \
([
	('pkt_id', '>i4'), 
	('pb0', '>i4', 256),
])
DATA = np.zeros(1, dtype=datafmt)

def open_data_client_sock (sockname):
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	try:
		sock.bind(sockname)
	except socket.error:
		print "WARN: %s exists! Removing." % sockname
		socket.os.unlink(sockname)
		sock.bind(sockname)
	print "Opened data socket."
	return sock

def open_ctrl_client_sock (sockname):
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		sock.connect(sockname)
	except socket.error:
		print "ERROR: Cannot connect to recv server."
		sys.exit(1)
	print "Opened ctrl socket."
	return sock

def close_data_client_sock (sock):
	sockname = sock.getsockname()
	sock.close()
	socket.os.unlink(sockname)
	print "Closed data socket."

def close_ctrl_client_sock (sock):
	sock.close()
	print "Closed ctrl socket."

def dump_to_file (name, data):
	#timestamp = strftime("%Y%m%dT%H%M%S")
	#filename = "data/%s_%s.dump" % (timestamp, name)
	filename = "data/%s.dump" % (name)
	f = open(filename, "w")
	for i in data:
		f.write("%d\n" % i)
	f.close()

if __name__ == "__main__":

	data_sock = open_data_client_sock(DATA_SOCK)
	ctrl_sock = open_ctrl_client_sock(CTRL_SOCK)
	ctrl_sock.send("subscribe %s" % DATA_SOCK)
	data_sock.recv_into(DATA)
	close_data_client_sock(data_sock)
	close_ctrl_client_sock(ctrl_sock)

	print "Dumping data to file ..."
	dump_to_file("pb0", DATA['pb0'][0])

