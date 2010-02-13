#!/usr/bin/env python

import pylab
from pylab import plot

import numpy as np
from numpy.fft import fftshift
from numpy.fft import rfft

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
	x = np.arange(-length/2, length/2)/(float(length)/taps)
	s = np.sinc(x)
	w = np.hanning(length)
	A = s*w*data
	B = np.array_split(A, taps)
	C = np.array(B)
	D = C.sum(axis=0)
	return D

def fft_real (data, split=1):
	A = np.array_split(data, split)
	B = A[0]
	C = np.fft.rfft(B)
	D = np.fft.fftshift(C)
	E = np.abs(D)
	return E

adc = sine_fxn(128, np.pi, 4)
pfb = pfb_fir(adc, taps=4)
fft_raw = fft_real(adc, 4)
fft_pfb = fft_real(pfb)

plot(adc)
plot(pfb)
plot(fft_raw)
plot(fft_pfb)

