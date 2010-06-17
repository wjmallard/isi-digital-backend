#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import numpy as np
import sys

import IPython
ipshell = IPython.Shell.IPShellEmbed()

ACCS_PER_PKT = 5
VALS_PER_PKT = 72 * ACCS_PER_PKT
num_groups = 8

class IsiCorrTrans ():

	def __init__ (self, ifile, ofile):
		self._ifile = open(ifile, "r")
		self._ofile = open(ofile, "w")

		self.main()

		self._ofile.close()
		self._ifile.close()

	def main (self):
		x = np.fromfile(self._ifile, dtype='i4')
		y = x.reshape(-1, num_groups, VALS_PER_PKT)

		fmt = "%12d" * 9 + "\n"

		count = 0
		for accs in y:
			acc_list = np.split(accs, ACCS_PER_PKT, axis=1)
			for i in xrange(ACCS_PER_PKT):
				xyz = np.split(acc_list[i], 9, axis=1)

				data = np.vstack(( \
					xyz[0].transpose().flatten(), \
					xyz[1].transpose().flatten(), \
					xyz[2].transpose().flatten(), \
					xyz[3].transpose().flatten(), \
					xyz[4].transpose().flatten(), \
					xyz[5].transpose().flatten(), \
					xyz[6].transpose().flatten(), \
					xyz[7].transpose().flatten(), \
					xyz[8].transpose().flatten(), \
				)).transpose()

				self._ofile.write("Packet #%d:\n" % count)
				for i in xrange(64):
					self._ofile.write(fmt % \
					( \
						data[i][0], \
						data[i][1], \
						data[i][2], \
						data[i][3], \
						data[i][4], \
						data[i][5], \
						data[i][6], \
						data[i][7], \
						data[i][8], \
					))

				count += 1

def main ():
	sys.argv.pop(0)

	if len(sys.argv) == 0:
		print "Must specify an input file."
		return
	ifile = sys.argv.pop(0)

	if len(sys.argv) == 0:
		print "Must specify an outut file."
		return
	ofile = sys.argv.pop(0)

	IsiCorrTrans(ifile, ofile)

if __name__ == "__main__":
	main()

