#!/usr/bin/env python2.6

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Development"

from corr import katcp_wrapper as katcp
from time import strftime, sleep
import numpy as np
import sys, os, errno
import string

BRAM_LEN = 2**13
BOF_FILE = 'isi_adc.bof'

def read_snap (fpga, name):
	bram = "snap_%s_bram" % name
	data = fpga.read(bram, 4*BRAM_LEN)
	return np.fromstring(data, '>i4')

def zero_snap (board, name):
	bram = "snap_%s_bram" % name
	zero = np.zeros(BRAM_LEN, dtype='>i4').tostring()
	board.blindwrite(bram, zero)

def reset_snap (board, name):
	ctrl = "snap_%s_ctrl" % name
	zero_snap(board, name)
	board.write_int(ctrl, 0, blindwrite=True)
	board.write_int(ctrl, 1, blindwrite=True)
	board.write_int(ctrl, 0, blindwrite=True)

def dump_to_file (data, name, datestamp, timestamp):
	# Create output directory.
	outdir = "data/%s" % (datestamp)
	try:
		os.makedirs(outdir)
	except OSError as ex:
		if ex.errno == errno.EEXIST: pass
		else: raise

	# Write data to file.
	filename = "%s/%s_%s.dump" % (outdir, timestamp, name)
	f = open(filename, "w")
	for i in data:
		f.write("%d\n" % i)
	f.close()

def reset (fpgas):
	for fpga in fpgas:
		for snap in ('adc0', 'adc1', 'adc2', 'adc3'):
			reset_snap(fpga, snap)

def read_adc (fpga):
	snap0 = np.fromstring(read_snap(fpga, 'adc0'), dtype=np.int8)
	snap1 = np.fromstring(read_snap(fpga, 'adc1'), dtype=np.int8)
	snap2 = np.fromstring(read_snap(fpga, 'adc2'), dtype=np.int8)
	snap3 = np.fromstring(read_snap(fpga, 'adc3'), dtype=np.int8)
	snap = np.vstack((snap0, snap1, snap2, snap3))
	adc = snap.reshape(4,-1,4).transpose(1,0,2).flatten()
	return adc

def arm (fpgas):
	for fpga in fpgas:
		fpga.write_int('control', 0, blindwrite=True)
	for fpga in fpgas:
		fpga.write_int('control', 1, blindwrite=True)

def main ():
	program_boards = False

	try:
		if sys.argv[1] == '-p':
			program_boards = True
			sys.argv.pop(1)

		name_list = sys.argv[1]
	except IndexError:
		prog = sys.argv[0]
		print "Usage: %s [-p] [hostname]" % prog
		print "  -p : program the board(s)"
		print
		print "For synchronous sampling of multiple boards,"
		print "provide a comma-separated list of hostnames."
		sys.exit(1)

	names = string.split(name_list, ',')

	# Connect to boards.
	print "Connecting to boards."
	fpgas = []
	for name in names:
		fpgas += [katcp.FpgaClient(name)]
	sleep(.1)

	# Program boards.
	if program_boards:
		print "Programming boards."
		for (fpga, name) in zip(fpgas, names):
			try:
				fpga.progdev(BOF_FILE)
			except RuntimeError:
				print "ERROR: Failed to program %s." % name
				sys.exit(1)
		print "Success!"

	# Acquire data.
	print "Acquiring data."
	reset(fpgas)
	arm(fpgas)
	sleep(2)

	datestamp = strftime("%Y%m%d")
	timestamp = strftime("%H%M%S")

	for (fpga, name) in zip(fpgas, names):
		data = read_adc(fpga)
		dump_to_file(data, name, datestamp, timestamp)

if __name__ == "__main__":
	main()

