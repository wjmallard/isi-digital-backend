#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

# NOTE: run "ipython --pylab", copy-and-paste, and poke around.
# TODO: automate this.

from libisidebug import *
import time

# temporary!
from libisiroach import IsiRoachBoard
# remove after reimplementing acquire().

num_samples = 1<<11
sync_period = 1 # sec
clock_freq = 200 # MHz
sync_clocks = sync_period * clock_freq * 10**6

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('test_adc083000x2.bof')

R.set_sync_period(sync_clocks)
R._set_flag(IsiRoachBoard.ARM_RESET)

R._set_flag(IsiRoachBoard.ACQUIRE)
time.sleep(sync_period)
R._unset_flag(IsiRoachBoard.ACQUIRE)

adc = R.read_adc('adc_capt', num_samples)

