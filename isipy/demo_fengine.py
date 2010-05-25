#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

#from libisigui import *
#from libisiplot import *
from libisidebug import *
#from libisifenggui import *

R = IsiCorrelatorDebug('isiroach1', 7147)
R.progdev('demo_fengine.bof')

R.set_clock_freq(200)
R.set_sync_period(.25)
R.set_fft_shift(0x7f)
R.set_eq_coeff(1<<11)

R.arm_sync()

print "Waiting for data ..."

R.start_recv("straylight", 8880)

#G = IsiFEngineGui(R)
#G.start()

while True:
	try:
		# Ctrl-D to quit.
		x = raw_input()
		if x == '':
			R.schedule_dump()
		elif x == 's':
			coeff_cur = R.get_eq_coeff()
			print "Current coeff: %d" % coeff_cur
			coeff_str = raw_input("scaling: ")
			try:
				coeff = int(coeff_str)
			except ValueError:
				print "Invalid scaling coefficient!"
				continue
			R.set_eq_coeff(coeff)
			
	except EOFError:
		R.stop_recv()
		break

