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
import time

num_samples = 1<<11
sync_period = 1 # sec
clock_freq = 200 # MHz
sync_clocks = sync_period * clock_freq * 10**6

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('test_tvg.bof')

R.write_int('sync_gen2_period', sync_clocks)
R.write_int('sync_gen2_select', 1)
R.write_int('control', 0x01)

tvg_sine = sine_wave(num_samples, cycles=1.5)
tvg_data = scale_bram_data(tvg_sine)
tvg_bstr = array_to_bytestring(tvg_data)
R.write("tvg_bram", tvg_bstr)

R.write_int('control', 0x08)
time.sleep(sync_period)
R.write_int('control', 0x00)

data_tvg = R.read("tvg_bram", num_samples)
data_capt = R.read("capt_bram0", num_samples)

diff = zip(data_tvg, data_capt)

