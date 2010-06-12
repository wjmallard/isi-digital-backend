#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from cmd import Cmd
from libisiroach import IsiRoach

class IsiRoachCtrl (Cmd):

	prompt = "isi> "

	def __init__ (self, addr, port=7147):
		Cmd.__init__(self)

		self._board = IsiRoach(addr, port)
		if port == 7147:
			print "Connected to %s." % (addr)
		else:
			print "Connected to %s:%d." % (addr, port)

	#
	# ISI Commands
	#

	def do_zero_ctrl (self, line):
		self._board.zero_ctrl()
		print "Zeroed control register."

	def do_arm (self, line):
		self._board.arm()
		print "Armed."

	def do_trig (self, line):
		self._board.trig()
		print "Forced a trigger."

	def do_reset (self, line):
		self._board.reset()

	def do_control (self, line):
		val = self._board.get_control()
		print "Control: 0x%08x" % val

	def do_status (self, line):
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

	def do_deprogram (self, line):
		"""Deprogram the FPGA."""
		self._board.progdev("")
		print "FPGA deprogrammed."

	def do_program (self, line):
		"""program [boffile]
		Program the board with the specified boffile."""
		args = line.split()
		if len(args) != 1:
			print "Must specify one boffile."
			return
		bof = args.pop(0)
		print "Programming ..."
		self._board.progdev(bof)
		print "Success!"

	def complete_program (self, text, line, begidx, endidx):
		bof_list = self._board.listbof()
		bof_list.sort()
		return [x for x in bof_list if x.startswith(text)]

	def do_read_int (self, line):
		"""read_int [device]
		Read 32 bits from a device."""
		args = line.split()
		if len(args) != 1:
			print "Must specify one device."
			return
		dev = args.pop(0)
		val = self._board.read_int(dev)
		print "%s = %d" % (dev, val)

	def complete_read_int (self, text, line, begidx, endidx):
		args = line.split()
		if len(args) > 1 and begidx == endidx:
			return []
		dev_list = self._board.listdev()
		return [x for x in dev_list if x.startswith(text)]

	def do_write_int (self, line):
		"""write_int [device] [value]
		Write 32 bits to a device."""
		args = line.split()
		if len(args) != 2:
			print "Must specify a device and a value."
			return
		dev = args.pop(0)
		s_val = args.pop(0)
		try:
			val = int(s_val, 0)
		except ValueError:
			print "Invalid value: %s" % s_val
			return
		self._board.write_int(dev, val)

	complete_write_int = complete_read_int

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
	import sys

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

	IsiRoachCtrl(host, port).cmdloop()

if __name__ == '__main__':
	main()

