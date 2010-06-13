#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import numpy as np
import sys

from isi_data_recv import IsiDataRecv

ACCS_PER_PKT = 5
VALS_PER_PKT = 72 * ACCS_PER_PKT

pktfmt = np.dtype \
([
	('board_id', '>i1'),
	('group_id', '>i1'),
	('unused', '>i2'),
	('pkt_id', '>i4'),
	('vacc', '>i4', VALS_PER_PKT),
])

accfmt = np.dtype \
([
	('XX_auto', '>i4', 64),
	('YY_auto', '>i4', 64),
	('ZZ_auto', '>i4', 64),
	('XY_real', '>i4', 64),
	('XY_imag', '>i4', 64),
	('YZ_real', '>i4', 64),
	('YZ_imag', '>i4', 64),
	('ZX_real', '>i4', 64),
	('ZX_imag', '>i4', 64),
], copy=True)

datafmt = np.dtype \
([
	('pkt_id', '>i4'),
	('accums', accfmt, ACCS_PER_PKT),
])

# TODO: Find these a home!
buf_length = 4
num_groups = 8
pktlen = buf_length * num_groups
pktdim = (buf_length, num_groups)
accdim = (buf_length, num_groups, VALS_PER_PKT)

class IsiCorrRecv (IsiDataRecv):

	def __init__ (self, addr, port):
		IsiDataRecv.__init__(self, addr, port, pktfmt, datafmt)

		self._buf_length = buf_length
		self._max_pktid = 0
		self._lim_pktid = 1<<20 # for a 20 bit pktid (from FPGA code)

		self._ACCUM = np.zeros(accdim, dtype=np.int32)
		self._PKTID = np.arange(pktlen, dtype=np.int32).reshape(pktdim)

	def descramble (self):
		board = self._PKT['board_id'][0]
		group = self._PKT['group_id'][0]
		pktid = self._PKT['pkt_id'][0]

		if pktid % 20 != 0:
			return False

		if group == 8:
			return False

		#print "Board %d / Group %d / Pktid %d" % (board, group, pktid)
		slot = pktid % self._buf_length
		print "Board %d / Group %d / Pktid %d --> Slot %d" % (board, group, pktid, slot)

		self._ACCUM[slot][group] = self._PKT['vacc'].copy()
		self._PKTID[slot][group] = self._PKT['pkt_id'].copy()

		# find full accumulations and process them.
		packet_ready = False
		for i in xrange(self._buf_length):
			s = (self._max_pktid + i) % self._buf_length
			if self._PKTID[s].ptp() == 0:
				self.process_pkt(self._PKTID[s,0], self._ACCUM[s])
				self._max_pktid = (self._max_pktid + i) % self._lim_pktid
				# Taint the row so that it doesn't get
				# read again on a packet counter reset.
				self._PKTID[s,0] += 1
				packet_ready = True
				break

		return packet_ready

	def process_pkt (self, pktid, accums):
		self._DATA['pkt_id'] = pktid

		print "Processing #%d." % pktid

		acc_list = np.split(accums, ACCS_PER_PKT, axis=1)

		for i in xrange(ACCS_PER_PKT):
			xyz = np.split(acc_list[i], 9, axis=1)
			ACC = self._DATA['accums'][0]

			ACC['XX_auto'][i] = xyz[0].transpose().flatten()
			ACC['YY_auto'][i] = xyz[1].transpose().flatten()
			ACC['ZZ_auto'][i] = xyz[2].transpose().flatten()
			ACC['XY_real'][i] = xyz[3].transpose().flatten()
			ACC['XY_imag'][i] = xyz[4].transpose().flatten()
			ACC['YZ_real'][i] = xyz[5].transpose().flatten()
			ACC['YZ_imag'][i] = xyz[6].transpose().flatten()
			ACC['ZX_real'][i] = xyz[7].transpose().flatten()
			ACC['ZX_imag'][i] = xyz[8].transpose().flatten()

		#print "Processed %d." % pktid

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

	IsiCorrRecv(host, port).main()

if __name__ == "__main__":
	main()

