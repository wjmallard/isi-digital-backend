#!/usr/bin/env python2.6

import numpy as np
import sys
import time

from corr import katcp_wrapper as katcp
from IPython import Shell
ipshell = Shell.IPShellEmbed()

#np.set_printoptions(linewidth=208)
np.set_printoptions(linewidth=238)

def zero_snap (board, name):
	bram = "snap_%s_bram" % name
	zero = np.zeros(2**11, dtype='>i4').tostring()
	board.blindwrite(bram, zero)

def read_snap (board, name):
	bram = "snap_%s_bram" % name
	return np.fromstring(board.read(bram, 4*4096), '>i4')

def reset_snap (board, name):
	ctrl = "snap_%s_ctrl" % name
	zero_snap(board, name)
	board.write_int(ctrl, 0, blindwrite=True)
	board.write_int(ctrl, 1, blindwrite=True)
	board.write_int(ctrl, 0, blindwrite=True)

def reset ():
	for name in ("data0", "data1", "status0", "status1"):
		for board in (r0, r1, r2):
			reset_snap(board, name)

def brams ():
	data = None
	for name in ("data0", "data1", "status0", "status1"):
		for board in (r0, r1, r2):
			D = read_snap(board, name)
			if data == None:
				data = D
			else:
				data = np.vstack((data, D))
	return data.transpose()

def split_stat (stat):
	sync = (stat>>0)&0x1
	rx_sync = (stat>>1)&0x1
	resync = (stat>>2)&0x1
	return (sync,rx_sync,resync)

def arm2 ():
	for r in (r0, r1, r2):
		r.write_int("control", 0)
	for r in (r0, r1, r2):
		r.write_int("control", 1)
	for r in (r0, r1, r2):
		r.write_int("control", 0)

def arm ():
	zero = np.array([0], dtype='>i4').tostring()
	one  = np.array([1], dtype='>i4').tostring()

	r0.blindwrite("control", zero)
	r1.blindwrite("control", zero)
	r2.blindwrite("control", zero)

	r0.blindwrite("control", one)
	r1.blindwrite("control", one)
	r2.blindwrite("control", one)

	r0.blindwrite("control", zero)
	r1.blindwrite("control", zero)
	r2.blindwrite("control", zero)

def set_sync (period):
	for r in (r0, r1, r2):
		r.write_int("sync_gen_period", period)

def set_ids (id0, id1, id2):
	r0.write_int("corr_id", id0)
	r1.write_int("corr_id", id1)
	r2.write_int("corr_id", id2)

if __name__ == "__main__":
	r0 = katcp.FpgaClient("isiroach2", 7147)
	r1 = katcp.FpgaClient("isiroach3", 7147)
	r2 = katcp.FpgaClient("isiroach4", 7147)
	time.sleep(.01)

	if len(sys.argv) != 3:
		print "Usage: %s [loopback] [feedback]"
		sys.exit(1)

	print "clock = ~%dMHz" % r0.est_brd_clk()

	loopback = int(sys.argv[1])
	print "loopback = %d" % loopback
	r0.write_int("delay_loopback", loopback)
	r1.write_int("delay_loopback", loopback)
	r2.write_int("delay_loopback", loopback)

	feedback = int(sys.argv[2])
	print "feedback = %d" % feedback
	r0.write_int("delay_feedback", feedback)
	r1.write_int("delay_feedback", feedback)
	r2.write_int("delay_feedback", feedback)

	set_sync(800)
	reset()
	arm()
	time.sleep(2)

	Data = brams()
	(sync,rx_sync,resync) = split_stat(Data[:,6:12])
	ref_sync_time = zip(*np.nonzero(sync)[::-1])
	ref_rx_sync_time = zip(*np.nonzero(rx_sync)[::-1])
	ref_resync_time = zip(*np.nonzero(resync)[::-1])

	offset_r0_x0 = r0.read_int("resync_xaui0_offset")
	offset_r1_x0 = r1.read_int("resync_xaui0_offset")
	offset_r2_x0 = r2.read_int("resync_xaui0_offset")
	offset_r0_x1 = r0.read_int("resync_xaui1_offset")
	offset_r1_x1 = r1.read_int("resync_xaui1_offset")
	offset_r2_x1 = r2.read_int("resync_xaui1_offset")

	print "offsets: [%d/%d/%d] [%d/%d/%d]" % (offset_r0_x0, offset_r1_x0, offset_r2_x0, offset_r0_x1, offset_r1_x1, offset_r2_x1)

	#Data[1650:1700]
	#Data[1600:1625]

	ipshell()

