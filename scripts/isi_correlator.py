#!/usr/bin/env python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-30
# desc: The ISI Correlator display.

from libisigui import *
from libisicorr import *
from libisitvg import *

L=2**7
f1 = sine_wave(L, cycles=200, phase=0)
f2 = sine_wave(L, cycles=200, phase=.5)
f3 = sine_wave(L, cycles=400, phase=0)
n1 = random_noise(L, seed=0xFC96)
n2 = random_noise(L, seed=0xEB85)
n3 = random_noise(L, seed=0xDA74)
s1 = fxn_sum((f1,))
s2 = fxn_sum((f1,))
s3 = fxn_sum(([0]*L,))

tv1 = prep_for_bram(s1, 16, 2**11)
tv2 = prep_for_bram(s2, 16, 2**11)
tv3 = prep_for_bram(s3, 16, 2**11)

hosts = ('localhost', 'localhost', 'localhost')
ports = (7147, 7148, 7149)
I = IsiCorrelator(hosts, ports)
D = IsiGui(I)

#I.program('isi_correlator_tvg.bof')
I.load_tvg((tv1, tv2, tv3))

I.set_sync_period(2**12)
I.set_fft_shift(0x7f)
I.set_eq_coeff((2**7)<<8)

I.send_sync()

D.start()

