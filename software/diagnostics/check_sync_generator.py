#!/usr/bin/env python2.6

import numpy as np
import sys
import time

from corr import katcp_wrapper as katcp
from IPython import Shell
ipshell = Shell.IPShellEmbed()

np.set_printoptions(linewidth=208)
#np.set_printoptions(linewidth=238)

BRAM_LEN = 2**14

def zero_snap (board):
	bram = "snap_bram"
	zero = np.zeros(BRAM_LEN, dtype='>i4').tostring()
	board.blindwrite(bram, zero)

def read_snap (board):
	bram = "snap_bram"
	return np.fromstring(board.read(bram, 4*BRAM_LEN), '>i4')

def reset_snap (board):
	ctrl = "snap_ctrl"
	zero_snap(board)
	board.write_int(ctrl, 0, blindwrite=True)
	board.write_int(ctrl, 1, blindwrite=True)
	board.write_int(ctrl, 0, blindwrite=True)

def reset ():
	for board in (r0, r1, r2):
		reset_snap(board)

def brams ():
	data = None
	for board in (r0, r1, r2):
		D = read_snap(board)
		if data == None:
			data = D
		else:
			data = np.vstack((data, D))
	return data.transpose()

def split_stat (stat):
	Sync0 = (stat>>0)&0x1
	Sync1 = (stat>>1)&0x1
	Aux0  = (stat>>2)&0x1
	Aux1  = (stat>>3)&0x1
	trig  = (stat>>4)&0x1
	sync0 = (stat>>5)&0x1
	sync1 = (stat>>6)&0x1
	aux0  = (stat>>7)&0x1
	aux1  = (stat>>8)&0x1
	return (Sync0,Sync1,Aux0,Aux1,sync0,sync1,aux0,aux1)

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
	(Sync0,Sync1,Aux0,Aux1,sync0,sync1,aux0,aux1) = split_stat(Data[:,0])

	#Data[1650:1700]
	#Data[1600:1625]

	ipshell()

