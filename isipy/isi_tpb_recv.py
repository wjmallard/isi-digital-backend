#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import numpy as np
import sys

from isi_data_recv import IsiDataRecv

pktfmt = np.dtype \
([  
	('pkt_id', '>i4'),
	('pb0', '>i4', 256),
])

datafmt = pktfmt

class IsiTpbRecv (IsiDataRecv):

	def __init__ (self, addr, port):
		IsiDataRecv.__init__(self, addr, port, pktfmt, datafmt)

	def descramble (self):
		pb0 = self._PKT['pb0'][0].reshape([8,32]).transpose()

		self._DATA['pkt_id'] = self._PKT['pkt_id']
		self._DATA['pb0'] = pb0.flatten()

def main ():
	sys.argv.pop(0)

	if len(sys.argv) == 0:
		print "Must specify a hostname."
		return
	host = sys.argv.pop(0)

	if len(sys.argv) == 0:
		print "Must specify a port."
		return
	s_port = sys.argv.pop(0)
	try:
		port = int(s_port)
	except ValueError:
		print "Invalid port number: %s" % s_port
		return

	IsiTpbRecv(host, port).main()

if __name__ == "__main__":
	main()

