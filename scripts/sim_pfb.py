#!/usr/bin/env python

import pylab
from pylab import plot
import numpy as np

def sine_fxn (length, cycles, windows=1):
	assert (length > 0)
	assert (cycles > 0)
	assert (windows > 0)
	L = length * windows
	C = cycles * windows
	x = (2*np.pi) * np.arange(-L/2, L/2)/(float(L)/C)
	y = np.sin(x)
	return y

def pfb_fir (data, taps=4):
	assert (taps>0)
	length = len(data)
	x = np.arange(-length/4, length/2)/(float(length)/taps)
	s = np.sinc(x)
	w = np.hanning(length)
	A = s*w*data
	B = np.array_split(A, taps)
	C = np.array(B)
	D = C.sum(axis=0)
	return D

def fft_real (data):
	A = np.fft.rfft(data)
	B = np.fft.fftshift(A)
	C = np.abs(B)
	return C

adc = sine_fxn(128, np.pi, 4)
pfb = pfb_fir(adc, taps=4)
fft_raw = fft_real(adc[0:128])
fft_pfb = fft_real(pfb)

plot(adc)
plot(pfb)
plot(fft_raw)
plot(fft_pfb)

