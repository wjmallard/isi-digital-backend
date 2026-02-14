#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

# NOTE: run "ipython --pylab", copy-and-paste, and poke around.
# TODO: automate this.

from libadc083000 import *
from libisidebug import *
import time

num_samples = 1<<11

R = IsiCorrelatorDebug('localhost', 7147)
#R.progdev('test_adc_ctrl.bof')
#R.set_clock_freq(200)

A = adc083000(R)
A.set_test_pattern()
A.set_amplitude(amplitude=0, adc=2)
A.set_amplitude(amplitude=511, adc=4)

R.acquire()

adc = R.read_adc('capt', num_samples)

