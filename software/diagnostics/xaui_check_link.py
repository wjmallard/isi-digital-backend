#!/usr/bin/env python

import numpy as np
import sys
import time

from corr import katcp_wrapper as katcp
from IPython import Shell
ipshell = Shell.IPShellEmbed()

def zero_snap (board, name):
	bram = "snap_%s_bram" % name
	zero = np.zeros(2**11, dtype='>i4').tostring()
	board.blindwrite(bram, zero)

def read_snap (board, name):
	bram = "snap_%s_bram" % name
	return np.fromstring(board.read(bram, 4*2048), '>i4')

def reset_snap (board, name):
	ctrl = "snap_%s_ctrl" % name
	zero_snap(board, name)
	board.write_int(ctrl, 0, blindwrite=True)
	board.write_int(ctrl, 1, blindwrite=True)
	board.write_int(ctrl, 0, blindwrite=True)

def reset ():
	for board in (r0, r1, r2):
		for name in ("data0", "data1", "status0", "status1"):
			reset_snap(board, name)

def brams ():
	D00 = read_snap(r0, "data0")
	D01 = read_snap(r1, "data0")
	D02 = read_snap(r2, "data0")
	D10 = read_snap(r0, "data1")
	D11 = read_snap(r1, "data1")
	D12 = read_snap(r2, "data1")
	S00 = read_snap(r0, "status0")
	S01 = read_snap(r1, "status0")
	S02 = read_snap(r2, "status0")
	S10 = read_snap(r0, "status1")
	S11 = read_snap(r1, "status1")
	S12 = read_snap(r2, "status1")
	return (D00,D10,D01,D11,D02,D12,S00,S10,S01,S11,S02,S12)

def split_stat (stat):
	oob = (stat>>0)&0xff
	rxf = (stat>>8)&0x1
	txf = (stat>>9)&0x1
	down = (stat>>10)&0x1
	valid = (stat>>11)&0x1
	empty = (stat>>12)&0x1
	return (oob,rxf,txf,down,valid,empty)

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

	set_sync(800)
	reset()
	arm()
	time.sleep(2)

	Data = brams()
	(D00,D10,D01,D11,D02,D12,S00,S10,S01,S11,S02,S12) = Data
	(S00_oob,S00_rxf,S00_txf,S00_down,S00_valid,S00_empty) = split_stat(S00)
	(S10_oob,S10_rxf,S10_txf,S10_down,S10_valid,S10_empty) = split_stat(S10)
	(S01_oob,S01_rxf,S01_txf,S01_down,S01_valid,S01_empty) = split_stat(S01)
	(S11_oob,S11_rxf,S11_txf,S11_down,S11_valid,S11_empty) = split_stat(S11)
	(S02_oob,S02_rxf,S02_txf,S02_down,S02_valid,S02_empty) = split_stat(S02)
	(S12_oob,S12_rxf,S12_txf,S12_down,S12_valid,S12_empty) = split_stat(S12)

	data = zip(D00,D10,D01,D11,D02,D12,S00_oob,S10_oob,S01_oob,S11_oob,S02_oob,S12_oob)
	stat00 = zip(*split_stat(S00))
	stat10 = zip(*split_stat(S10))
	stat01 = zip(*split_stat(S01))
	stat11 = zip(*split_stat(S11))
	stat02 = zip(*split_stat(S02))
	stat12 = zip(*split_stat(S12))

	ipshell()

