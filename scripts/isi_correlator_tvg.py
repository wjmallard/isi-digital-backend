#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisidebug import *
from libisitvg import *

import IPython
ipshell = IPython.Shell.IPythonShellEmbed()

L=2**7
s1 = xrange(L)
d1 = interleave_tvg_bram(s1, 16, 2**11)
tv1 = scale_bram_list(d1, coeff=1)

R = IsiCorrelatorDebug('localhost', 7147)

R.load_tvg(tv1)

R.set_sync_period(2**12)
R.set_fft_shift(0x7f)
R.set_eq_coeff((2**7)<<8)

R.acquire()
R.arm_sync()
R.send_sync()

data = R.read_adc("adc_capt_4x", 128)

ipshell()

