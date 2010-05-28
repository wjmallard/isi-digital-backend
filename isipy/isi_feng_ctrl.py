#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from cmd import Cmd
from libisiroach import IsiRoachBoard
import sys

class IsiFengCtrl (Cmd):

	prompt = "isi> "

	def __init__ (self, addr, port=7147):
		Cmd.__init__(self)
		self._board = IsiRoachBoard(addr, port)
		if port == 7147:
			print "Connected to %s." % (addr)
		else:
			print "Connected to %s:%d." % (addr, port)
		self._board.initialize()

	#
	# ISI Commands
	#

	def do_sync_period (self, line):
		args = line.split()
		if len(args) == 0:
			print "Sync Period: %s clks" % self._board.sync_period
			return
		if len(args) != 1:
			print "Too many arguments."
			return
		s_val = args.pop(0)
		try:
			val = int(s_val, 0)
		except ValueError:
			print "Invalid value: %s" % s_val
			return
		self._board.set_sync_period(val)

	def do_fft_shift (self, line):
		args = line.split()
		if len(args) == 0:
			print "FFT Shift: 0x%02x" % self._board.fft_shift
			return
		if len(args) != 1:
			print "Too many arguments."
			return
		s_val = args.pop(0)
		try:
			val = int(s_val, 0)
		except ValueError:
			print "Invalid value: %s" % s_val
			return
		self._board.set_fft_shift(val)

	def do_eq_coeff (self, line):
		args = line.split()
		if len(args) == 0:
			print "Eq Coeff: %d" % self._board.eq_coeff
			return
		if len(args) != 1:
			print "Too many arguments."
			return
		s_val = args.pop(0)
		try:
			val = int(s_val, 0)
		except ValueError:
			print "Invalid value: %s" % s_val
			return
		self._board.set_eq_coeff(val)

	def do_status (self, line):
		args = line.split()
		if len(args) != 0:
			print "Too many arguments."
			return
		val = self._board.get_status()
		print "Status: 0x%08x" % val

	#
	# ROACH Commands
	#

	def do_est_brd_clk (self, line):
		"""Estimate the board's clock speed."""
		print "Clock: ~%dMHz" % self._board.est_brd_clk()

	def do_listbof (self, line):
		"""List all executable bof files."""
		bof_list = self._board.listbof()
		bof_list.sort()
		print "Available boffiles:"
		for bof in bof_list:
			print "  %s" % bof

	def do_listdev (self, line):
		"""List all fpga devices in /proc."""
		dev_list = self._board.listdev()
		print "Available devices:"
		for dev in dev_list:
			print "  %s" % dev

	def do_ping (self, line):
		"""Ping the board."""
		pingable = self._board.ping()
		if pingable:
			print "Board is reachable."
		else:
			print "Board is unreachable."

	def do_progdev (self, line):
		"""progdev [boffile]
		Program the board."""
		args = line.split()
		if len(args) != 1:
			print "Must specify one boffile."
			return
		bof = args.pop(0)
		print "Programming ..."
		self._board.progdev(bof)
		print "Success. Running: %s" % bof

	def do_read_int (self, line):
		"""read_int [device]
		Read 32 bits from a device."""
		args = line.split()
		if len(args) != 1:
			print "Must specify one device."
			return
		dev = args.pop(0)
		val = self._board.read_int(device)
		print "%s = %d" % (dev, val)

	def do_write_int (self, line):
		"""write_int [device] [value]
		Write 32 bits to a device."""
		args = line.split()
		if len(args) != 2:
			print "Must specify a device and a value."
			return
		dev = args.pop(0)
		val = args.pop(1)
		self._board.write_int(dev, val)

	#
	# UI Commands
	#

	def do_quit (self, line):
		"""Quit the program."""
		return True

	def do_EOF (self, line):
		"""Quit the program."""
		print "quit"
		return True

def main ():
	sys.argv.pop(0)

	if len(sys.argv) == 0:
		print "Must specify a hostname."
		return
	host = sys.argv.pop(0)

	port = 7147
	if len(sys.argv) != 0:
		s_port = sys.argv.pop(0)
		try:
			port = int(s_port)
		except ValueError:
			print "Invalid port number: %s" % s_port
			return

	IsiFengCtrl(host, port).cmdloop()

if __name__ == '__main__':
	main()

