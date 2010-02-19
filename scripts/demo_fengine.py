#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-09-11
# desc: A control script for demo_fengine.mdl.

from libisigui import *
from libisiplot import *
from libisidebug import *
from libisifenggui import *

import IPython
ipshell = IPython.Shell.IPShellEmbed()

R = IsiCorrelatorDebug('localhost', 7147)
R.progdev('demo_fengine.bof')

R.set_sync_period(2**12)
R.set_fft_shift(0x7f)
R.set_eq_coeff((2**7)<<8)
R.send_sync()

G = IsiFEngineGui(R)
C = G.get_canvas()

C.add_plot(0, [0]*128, "adc", line='-')
C.add_plot(1, [0]*128, "pfb", line='-')
C.add_plot(2, [0]*64, "fft")
C.add_plot(3, [0]*64, "eq")

G.start()

