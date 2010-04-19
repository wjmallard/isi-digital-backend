#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisicorr import *
import numpy as np

hosts = ('isi0', 'isi2', 'isi3')
ports = (7147, 7147, 7147)

I = IsiCorrelator(hosts, ports)
#I.program('isi_correlator.bof')

I.connect_vacc("192.168.1.202")

I.set_clock_freq(200)
I.set_sync_period(.002)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.arm_sync()

def DO_STUFF (pktid, accum):
	print "Got a full packet with id %d!" % pktid

print "Waiting for data ..."

num_pktid_bits = 20
lim_pktid = 1 << num_pktid_bits

buf_length = 8
num_groups = 8
group_size = 2048

ACCUM = np.zeros((buf_length, num_groups, group_size))
PKTID = np.arange(buf_length * num_groups).reshape((buf_length, num_groups))

max_pktid = 0

while True:
	(board, group, pktid, accum) = I._vacc._read_sock()

	if group == 8:
		continue

	print "Board %d / Group %d / Pktid %d" % (board, group, pktid)
	slot = pktid % buf_length

	ACCUM[slot, group, 0:2016] = accum
	PKTID[slot, group] = pktid

	# handle full accumulations.
	for i in xrange(buf_length):
		s = (max_pktid + 1) % buf_length
		if PKTID[s].ptp() == 0:
			DO_STUFF(PKTID[s,0], ACCUM[s])
			max_pktid = (max_pktid + 1) % lim_pktid
			# Taint the row so that it doesn't get
			# read again on a packet counter reset.
			PKTID[s, 0] += 1
		else:
			break

