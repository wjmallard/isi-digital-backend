#!/usr/bin/env python2.6

import numpy as np
from numpy.fft import fft

BANDWIDTH = 3e9 # Hz

def get_phase (filename):
	"""find phase of each spectral bin"""
	raw_data = np.fromfile(filename, dtype=np.int, sep='\n')
	window = np.hamming(len(raw_data)/2)
	evens = np.array(raw_data[0::2], dtype=np.double)
	odds = np.array(raw_data[1::2], dtype=np.double)
	pwrs = fft(window*evens).conj() * fft(window*odds)
	phase = np.angle(pwrs)
	return phase

def fit_phase (phase):
	"""do a linear fit of the phase
	over the positive frequencies"""
	start = int(.05*len(phase)) # adjust to beg of linear region
	stop = int(.20*len(phase)) # adjust to end of linear region
	x = range(start,stop)
	y = phase[start:stop]
	coeffs = np.polyfit(x,y,1)
	return coeffs

def calc_delay (coeffs, fft_length):
	"""calculate delay (in ps)
	based on slope of phase"""
	slope = coeffs[0] # rad/chan
	chan_bw = BANDWIDTH/fft_length # Hz/chan
	delay_raw = (slope / chan_bw) / (2*np.pi) # sec
	delay_exp = 1/(2*BANDWIDTH)
	delay = delay_raw - delay_exp
	return int(delay*1e12)

if __name__ == "__main__":
	import sys

	try:
		filename = sys.argv[1]
	except IndexError:
		print "Usage: %s FILENAME" % sys.argv[0]
		sys.exit(1)

	phase = get_phase(filename)
	coeff = fit_phase(phase)
	delay = calc_delay(coeff, len(phase))

	print "Delay: %dps" % delay

