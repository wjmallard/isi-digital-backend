#!/usr/bin/env python

import numpy as np
import sys
import time

from corr import katcp_wrapper as katcp
from IPython import Shell
ipshell = Shell.IPShellEmbed()

def reset_snap (board, name):
	ctrl = "snap_%s_ctrl" % name
	board.write_int(ctrl, 0)
	board.write_int(ctrl, 1)
	board.write_int(ctrl, 0)

def read_snap (board, name):
	bram = "snap_%s_bram" % name
	return np.fromstring(board.read(bram, 4*4096), '>i4')

def reset ():
	for r in (r0, r1, r2):
		reset_snap(r, "X")
		reset_snap(r, "Y")
		reset_snap(r, "Z")
		reset_snap(r, "Sfifo")

def brams ():
	X0 = read_snap(r0, "X")
	X1 = read_snap(r1, "X")
	X2 = read_snap(r2, "X")
	Y0 = read_snap(r0, "Y")
	Y1 = read_snap(r1, "Y")
	Y2 = read_snap(r2, "Y")
	Z0 = read_snap(r0, "Z")
	Z1 = read_snap(r1, "Z")
	Z2 = read_snap(r2, "Z")
	S0 = read_snap(r0, "Sfifo")
	S1 = read_snap(r1, "Sfifo")
	S2 = read_snap(r2, "Sfifo")
	return (X0,X1,X2,Y0,Y1,Y2,Z0,Z1,Z2,S0,S1,S2)

def split_data (data):
	board = (data[-1]>>20)&0x03
	port = (data[-1]>>16)&0x03
	data = data&0xffff
	return (board, port, data)

def split_stat (data):
	lo_rxe = (data>>0)&0x1
	lo_txf = (data>>1)&0x1
	x0_rxe = (data>>2)&0x1
	x0_txf = (data>>3)&0x1
	x1_rxe = (data>>4)&0x1
	x1_txf = (data>>5)&0x1
	lo_sync = (data>>6)&0x1
	x0_sync = (data>>7)&0x1
	x1_sync = (data>>8)&0x1
	getX = (data>>9)&0x1
	getY = (data>>10)&0x1
	getZ = (data>>11)&0x1
	return (lo_rxe,lo_txf,x0_rxe,x0_txf,x1_rxe,x1_txf,lo_sync,x0_sync,x1_sync,getX,getY,getZ)

def arm ():
	for r in (r0, r1, r2):
		r.write_int("control", 0)
	for r in (r0, r1, r2):
		r.write_int("control", 1)
	for r in (r0, r1, r2):
		r.write_int("control", 0)

def set_sync (period):
	for r in (r0, r1, r2):
		r.write_int("sync_gen_period", period)

def set_ids (id0, id1, id2):
	r0.write_int("corr_id", id0)
	r1.write_int("corr_id", id1)
	r2.write_int("corr_id", id2)

def read_sync_counts ():
	s0lo = r0.read_int("sync_countL")
	s0x0 = r0.read_int("sync_count0")
	s0x1 = r0.read_int("sync_count1")
	s1lo = r1.read_int("sync_countL")
	s1x0 = r1.read_int("sync_count0")
	s1x1 = r1.read_int("sync_count1")
	s2lo = r2.read_int("sync_countL")
	s2x0 = r2.read_int("sync_count0")
	s2x1 = r2.read_int("sync_count1")
	print "      lo         x0         x1"
	print "0 %10d %10d %10d" % (s0lo, s0x0, s0x1)
	print "1 %10d %10d %10d" % (s1lo, s1x0, s1x1)
	print "2 %10d %10d %10d" % (s2lo, s2x0, s2x1)

if __name__ == "__main__":
	try:
		host0 = sys.argv[1]
		host1 = sys.argv[2]
		host2 = sys.argv[3]
	except IndexError:
		print "Usage: %s HOST1 HOST2 HOST3" % sys.argv[0]
		sys.exit(1)

	r0 = katcp.FpgaClient(host0, 7147)
	r1 = katcp.FpgaClient(host1, 7147)
	r2 = katcp.FpgaClient(host2, 7147)
	time.sleep(.01)

	set_ids(1,2,3)
	time.sleep(.01)
	set_sync(800)
	time.sleep(.01)
	reset()
	time.sleep(.1)
	arm()
	time.sleep(1)

	(X0,X1,X2,Y0,Y1,Y2,Z0,Z1,Z2,S0,S1,S2) = brams()
	(X0_board, X0_sport, X0_data) = split_data(X0)
	(X1_board, X1_sport, X1_data) = split_data(X1)
	(X2_board, X2_sport, X2_data) = split_data(X2)
	(Y0_board, Y0_sport, Y0_data) = split_data(Y0)
	(Y1_board, Y1_sport, Y1_data) = split_data(Y1)
	(Y2_board, Y2_sport, Y2_data) = split_data(Y2)
	(Z0_board, Z0_sport, Z0_data) = split_data(Z0)
	(Z1_board, Z1_sport, Z1_data) = split_data(Z1)
	(Z2_board, Z2_sport, Z2_data) = split_data(Z2)
	(S0_rxel,S0_txfl,S0_rxe0,S0_txf0,S0_rxe1,S0_txf1,S0_losync,S0_x0sync,S0_x1sync,S0_getX,S0_getY,S0_getZ) = split_stat(S0)
	(S1_rxel,S1_txfl,S1_rxe0,S1_txf0,S1_rxe1,S1_txf1,S1_losync,S1_x0sync,S1_x1sync,S1_getX,S1_getY,S1_getZ) = split_stat(S1)
	(S2_rxel,S2_txfl,S2_rxe0,S2_txf0,S2_rxe1,S2_txf1,S2_losync,S2_x0sync,S2_x1sync,S2_getX,S2_getY,S2_getZ) = split_stat(S2)

	print "   X   Y   Z"
	print "0 %d:%d %d:%d %d:%d" % (X0_board, X0_sport, Y0_board, Y0_sport, Z0_board, Z0_sport)
	print "1 %d:%d %d:%d %d:%d" % (X1_board, X1_sport, Y1_board, Y1_sport, Z1_board, Z1_sport)
	print "2 %d:%d %d:%d %d:%d" % (X2_board, X2_sport, Y2_board, Y2_sport, Z2_board, Z2_sport)

	ipshell()

