#!/usr/bin/python
#
# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-09-11
# desc: A control script for demo_fengine.mdl.

import corr
import sys
import pylab
import IPython

import libisidemo as isi

ipshell = IPython.Shell.IPShellEmbed()

isi.num_samples = 1<<7
isi.num_chans = 1<<6
isi.update_delay = .1 # seconds

fpga = isi.board_connect()
isi.board_init(fpga)

fft_shift = 1<<6
eq_coeff = 1<<8

fpga.write_int('fft_shift', fft_shift)
fpga.write_int('eq_coeff', eq_coeff)

# Script begins here.

print "Setting up plot."
pylab.ion()

ax1 = pylab.subplot(411)
#title("Raw ADC Output")
#xlabel("Samples")
pylab.ylabel("Voltage")
adc = [0] * sample_length
c1, = ax1.plot(adc)
ax1.autoscale_view(tight=True, scalex=True, scaley=True)

ax2 = pylab.subplot(412)
#title("PFB FIR Data")
#xlabel("Samples")
pylab.ylabel("Voltage")
pfb = [0] * sample_length
c2, = ax2.plot(pfb)
ax2.autoscale_view(tight=True, scalex=True, scaley=True)

fft = [0] * num_chans
fft[0] = 256
ax3 = pylab.subplot(413)
c3, = ax3.plot(fft)
ax3.autoscale_view(tight=True, scalex=True, scaley=True)
#title("Spectrometer")
#xlabel("Frequency Bin")
pylab.ylabel("Power")

eq = [0] * num_chans
eq[0] = 256
ax4 = pylab.subplot(414)
c4, = ax4.plot(eq)
ax4.autoscale_view(tight=True, scalex=True, scaley=True)
#title("Spectrometer")
#xlabel("Frequency Bin")
pylab.ylabel("Eq. Power")

print "Looping forever."
while True:

	acquire(fpga)

	adc = isi.read_adc(fpga, "adc_capt_4x")
	pfb = isi.read_adc(fpga, "pfb_capt_4x")
	fft = isi.read_fft(fpga, "fft_capt_4x")
	eq = isi.read_fft(fpga, "eq_capt_4x")

	c1.set_ydata(adc)
	c2.set_ydata(pfb)
	c3.set_ydata(fft)
	c4.set_ydata(eq)

	pylab.draw()

print "Ok, handing over control.  Enjoy!"
ipshell()

