#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

# NOTE: run "ipython --pylab", copy-and-paste, and poke around.
# TODO: automate this.

from libisidebug import *

num_samples = 1<<11

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('test_capt.bof')

R.write_int('control', 0x03)
R.read_int('status')
R.read('capt_bram0', 4 * num_samples)

