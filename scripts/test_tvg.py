#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

# NOTE: run "ipython --pylab", copy-and-paste, and poke around.
# TODO: automate this.

from libisidebug import *
from libisitvg import *

num_samples = 1<<11

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('test_tvg.bof')

tvg_sine = sine_wave(num_samples, cycles=1.5)
tvg_data = scale_bram_data(tvg_sine)
tvg_bstr = array_to_bytestring(tvg_data)
R.write("tvg_bram", tvg_bstr)

data_tvg = R.read("tvg_bram", num_samples)
data_capt = R.read("capt_bram0", num_samples)

