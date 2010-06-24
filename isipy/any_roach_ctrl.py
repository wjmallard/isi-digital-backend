#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from cmd import Cmd
from corr import katcp_wrapper as katcp
from time import sleep

class AnyRoachCtrl (Cmd):

	prompt = "roach> "

	def __init__ (self):
		Cmd.__init__(self)

		self._boards = []
		self._ids = None

	#
	# Cmd Methods
	#

	def precmd (self, line):
		args = line.split()

		if len(args) == 0 \
			or args[0] == 'EOF' \
			or args[0] == 'help' \
			or args[0].endswith("_board"):
			# Do nothing.
			pass

		elif len(self._boards) == 0:
			# Do not execute the command.
			print "No active boards."
			return ""

		else:
			# Parse the list of target boards.

			if len(args) >= 2:

				arg1 = args.pop(1)
				s_ids = arg1.split(',')
				num_ids = len(s_ids)

				self._ids = None
				for s_id in s_ids:

					# Parse the next board ID in the list.
					try:
						id = int(s_id, 0)
					except ValueError:
						# If it's not a valid integer:
						if num_ids == 1:
							# Assume no board list was specified.
							break
						else:
							# Skip it and move to the next one.
							print "Invalid board ID: %s" % s_id
							continue

					# Make sure that board has been loaded.
					if id >= len(self._boards) or id < 0:
						print "Unknown board ID: %d" % id
						continue

					# Looks good, so add it to the list.
					if self._ids:
						self._ids += [id]
					else:
						self._ids = [id]

			if self._ids:
				# The first arg was a board ID,
				# and we already removed it,
				# so return the remaining line.
				line = ' '.join(args)
				self._ids.sort()
			else:
				# The first arg was not a board ID,
				# so return a list of all boards,
				# and return the original line.
				self._ids = range(len(self._boards))

		return line

	def postcmd (self, stop, line):
		self._ids = None
		return stop

	def emptyline (self):
		pass

	#
	# Meta Commands
	#

	def do_list_boards (self, line):
		num_boards = len(self._boards)

		print "Boards:"
		for i in xrange(num_boards):
			info = self._boards[i]._bindaddr
			print " [%d] %s : %d" % (i, info[0], info[1])

	def do_add_board (self, line):
		args = line.split()

		if len(args) == 0:
			print "Must specify a hostname."
			return
		addr = args.pop(0)

		# Parse arguments.
		if len(args) == 0:
			port = 7147
		else:
			s_port = args.pop(0)
			try:
				port = int(s_port, 0)
			except ValueError:
				print "Invalid port: %s" % s_port
				return

		# Add board to list, if it is reachable.
		board = katcp.FpgaClient(addr, port)
		sleep(.25)
		try:
			board.ping()
		except katcp.KatcpClientError:
			print "Board is unreachable: %s:%d" % (addr, port)
			return
		self._boards.append(board)

		if port == 7147:
			print "Connected to %s." % (addr)
		else:
			print "Connected to %s:%d." % (addr, port)

	#
	# ROACH Commands
	#

	def do_est_brd_clk (self, line):
		"""Estimate the board's clock speed."""

		for id in self._ids:
			clk = self._boards[id].est_brd_clk()
			print "[%d] Clock: ~%dMHz" % (id, clk)

	def do_listbof (self, line):
		"""List all executable bof files."""

		bof_list = self._boards[0].listbof()
		bof_list.sort()
		print "Available boffiles:"
		for bof in bof_list:
			print "  %s" % bof

	def do_listdev (self, line):
		"""List all fpga devices in /proc."""

		for id in self._ids:
			print "[%d] Available devices:" % id
			dev_list = self._boards[id].listdev()
			dev_list.sort()
			for dev in dev_list:
				print "  %s" % dev

	def do_ping (self, line):
		"""Ping the board."""

		for id in self._ids:
			pingable = self._boards[id].ping()
			if pingable:
				print "[%d] Board is reachable." % id
			else:
				print "[%d] Board is unreachable." % id

	def do_deprogram (self, line):
		"""Deprogram the FPGA."""

		for id in self._ids:
			self._boards[id].progdev("")
			print "[%d] FPGA deprogrammed." % id

	def do_program (self, line):
		"""program [boffile]
		Program the board with the specified boffile."""

		args = line.split()

		if len(args) != 1:
			print "Must specify one boffile."
			return

		bof = args.pop(0)

		bof_list = self._boards[0].listbof()
		if not bof in bof_list:
			print "Unknown bof file: %s" % bof
			return

		for id in self._ids:
			print "[%d] Programming ..." % id
			self._boards[id].progdev(bof)
			print "[%d] Success!" % id

	def complete_program (self, text, line, begidx, endidx):

		line = self.precmd(line)

		if len(self._boards) == 0:
			return line

		args = line.split()
		if (len(args) == 1 and len(text) == 0) \
		or (len(args) == 2 and len(text) != 0):

			bof_list = self._boards[0].listbof()
			bof_list.sort()
			return [x for x in bof_list if x.startswith(text)]

		return []

	def do_read_int (self, line):
		"""read_int [device]
		Read 32 bits from a device."""

		args = line.split()

		if len(args) != 1:
			print "Must specify one device."
			return

		dev = args.pop(0)

		for id in self._ids:
			try:
				val = self._boards[id].read_int(dev)
				print " [%d] %s = %d" % (id, dev, val)
			except RuntimeError:
				print "[%d] Cannot read register: %s" % (id, dev)

	def complete_read_int (self, text, line, begidx, endidx):

		line = self.precmd(line)

		if len(self._boards) == 0:
			return line

		args = line.split()
		if (len(args) == 1 and len(text) == 0) \
		or (len(args) == 2 and len(text) != 0):

			dev_list = self._boards[0].listdev()
			dev_list.sort()
			return [x for x in dev_list if x.startswith(text)]

		return []

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

		for id in self._ids:
			try:
				self._boards[id].write_int(dev, val)
				print " [%d] %s = %d" % (id, dev, val)
			except RuntimeError:
				print "[%d] Cannot write register: %s" % (id, dev)

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

if __name__ == '__main__':
	AnyRoachCtrl().cmdloop()

