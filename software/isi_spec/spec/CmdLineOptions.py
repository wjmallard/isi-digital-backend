"""An interface to command line options."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys

class CmdLineOptions ():
	"""An interface to ommand line options.

	Parses options from the command line,
	and makes them available as fields.
	"""
	def __init__ (self, args):
		"""Create a new option parser."""
		self.args = args

		self.verbose = False
		self.program_fpga = False
		self.to_temp_file = False

		self._parse()

	def _parse (self):
		"""Parse all command line options."""
		for arg in self.args[1:]:
			self.args.remove(arg)
			if arg == "-h":
				self.print_usage()
				sys.exit(0)
			if arg == "-v":
				self.verbose = True
			elif arg == "-p":
				self.program_fpga = True
			elif arg == "-t":
				self.to_temp_file = True
			else:
				print "Unrecognized flag: %s" % arg
				self.print_usage()
				sys.exit(1)

	def print_usage (self):
		"""Print program usage message."""
		print "Usage: %s [options]" % self.args[0]
		print "Options:"
		print "  -h  Display this information"
		print "  -v  Verbose mode"
		print "  -p  Program FPGA"
		print "  -t  Write fits data to temp file"

