#!/usr/bin/env python

__author__ = "William Mallard"
__license__ = "GPL"
__version__ = "0.1"

import itertools
import math
import random
import struct

def cplx_pwr (z):
	"""Calculate the complex power of an array."""
	p = [(a*a.conj()).real for a in z]
	return p

def scaleByteString (array):
	c = 2**6
	X = [int(c*x) for x in array]
	A = [struct.pack('!1b', x) for x in X]
	B = ''.join(A)
	return B

def scaleArray (array):
	c = 2**6
	X = [int(c*x) for x in array]
	return X

def sine_wave (L, cycles=1, phase=0):
	x = xrange(L)
	omega = 2*math.pi*cycles/L
	phi = 2*math.pi*phase
	y = [math.sin(omega*t+phi) for t in x]
	return y

def square_wave (L):
	"""Build an L-point square wave with range [-1,1)."""
	s = int(L/2)
	y = [1]*s + [-1]*s
	return y

def square_fs (L, N):
	"""Build an L-point square wave from N fourier coefficients."""
	X = xrange(L)
	C = [2*n+1 for n in xrange(N)]
	c = 4./math.pi
	f = [[(1./n)*math.sin(n*2*math.pi*x/L) for x in X] for n in C]
	y = [c*sum(a) for a in itertools.izip(*f)]
	return y

def triangle_wave (L):
	"""Build an L-point triangle wave with range [-1,1)."""
	s = int(L/4)
	s0 = [float(x)/s for x in xrange(s)]
	s1 = [1-float(x)/s for x in xrange(2*s)]
	s2 = [x-1 for x in s0]
	y = s0 + s1 + s2
	return y

def triangle_fs (L, N):
	"""Build an L-point triangle wave from N fourier coefficients."""
	X = xrange(L)
	C = [2*n+1 for n in xrange(N)]
	c = 8./(math.pi**2)
	f = [[((-1)**((n-1)/2.))*(1/n**2.)*math.sin(n*2*math.pi*x/L) for x in X] for n in C]
	y = [c*sum(a) for a in itertools.izip(*f)]
	return y

def sawtooth_wave (L):
	"""Build an L-point sawtooth wave with range [-1,1)."""
	y = [(2.*x/L)-1 for x in xrange(L)]
	return y

def sawtooth_fs (L, N):
	"""Build an L-point sawtooth wave from N fourier coefficients."""
	X = xrange(L)
	C = [n+1 for n in xrange(N)]
	c = -2./math.pi
	f = [[(1./n)*math.sin(n*2*math.pi*x/L) for x in X] for n in C]
	y = [c*sum(a) for a in itertools.izip(*f)]
	return y

def random_noise (L, seed=None):
	"""Build an L-point random array with range [-1,1)."""
	random.seed(seed)
	y = [2*random.random()-1 for x in xrange(L)]
	return y

def main ():
	L = 8
	N = 100

	f0 = sine_wave(L)
	f1 = square_wave(L)
	f2 = square_fs(L, N)
	f3 = triangle_wave(L)
	f4 = triangle_fs(L, N)
	f5 = sawtooth_wave(L)
	f6 = sawtooth_fs(L, N)
	f7 = random_noise(L, seed=1234)

	s0 = scaleByteString(f0)
	s1 = scaleByteString(f1)
	s2 = scaleByteString(f2)
	s3 = scaleByteString(f3)
	s4 = scaleByteString(f4)
	s5 = scaleByteString(f5)
	s6 = scaleByteString(f6)
	s7 = scaleByteString(f7)

	print "Sine:            %s" % (scaleArray(f0))
	print "Square (pure):   %s" % (scaleArray(f1))
	print "Square (fs):     %s" % (scaleArray(f2))
	print "Triangle (pure): %s" % (scaleArray(f3))
	print "Triangle (fs):   %s" % (scaleArray(f4))
	print "Sawtooth (pure): %s" % (scaleArray(f5))
	print "Sawtooth (fs):   %s" % (scaleArray(f6))
	print "Random Noise:    %s" % (scaleArray(f7))

if __name__ == "__main__":
	main()

