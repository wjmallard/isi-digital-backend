#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisigui import *
from libisiplot import *
from libisidebug import *
from libisifenggui import *

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('demo_fengine.bof')

R.set_clock_freq(200)
R.set_sync_period(.25)
R.set_fft_shift(0x7f)
R.set_eq_coeff((2**7)<<8)
R.arm_sync()

G = IsiFEngineGui(R)
C = G.get_canvas()

C.add_plot(0, [0]*128, "adc", line='-')
C.add_plot(1, [0]*128, "pfb", line='-')
C.add_plot(2, [0]*64, "fft")
C.add_plot(3, [0]*64, "eq")

G.start()

