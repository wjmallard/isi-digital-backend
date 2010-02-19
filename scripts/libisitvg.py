#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import itertools
import math
import random
import struct

def cplx_pwr (z):
	"""Calculate the complex power of an array."""
	p = [(a*a.conj()).real for a in z]
	return p

def fxn_sum (fxns):
	"""Sum and normalize an arbitrary list of functions."""
	c = 1./len(fxns)
	f = [c*sum(a) for a in itertools.izip(*fxns)]
	return f

def interleave_tvg_bram (array, num_inputs, bram_size):
	"""Interleave ARRAY for use in NUM_INPUTS brams of BRAM_SIZE length.

	Take a byte array of arbitrary length and split it into words across
	(num_inputs/4) arrays.  Loop this as many times as necessary to fill
	each bram."""

	window_length = len(array)
	num_brams = num_inputs / 4
	num_reps = (bram_size / window_length) * num_brams

	iter_l = []
	for i in xrange(num_brams):
		# Grab one byte per input.
		iter0 = itertools.islice(array, 4*i+0, None, num_inputs)
		iter1 = itertools.islice(array, 4*i+1, None, num_inputs)
		iter2 = itertools.islice(array, 4*i+2, None, num_inputs)
		iter3 = itertools.islice(array, 4*i+3, None, num_inputs)

		# Clump bytes into words.
		iterZ = itertools.izip(iter0, iter1, iter2, iter3)
		iterC = itertools.chain.from_iterable(iterZ)

		# Flatten iterator to list.
		window = [x for x in iterC]

		# Loop sequence to fill bram.
		iterR = itertools.repeat(window, num_reps)
		iter = itertools.chain.from_iterable(iterR)

		iter_l += [iter]

	return iter_l

def scale_bram_list (iter_l, coeff=2**6):
	"""Scale a list of arrays and convert it to a list of byte strings."""
	data_l = []
	for iter in iter_l:
		A = scale_bram_data(iter, coeff)
		B = array_to_bytestring(A)
		data_l += [B]
	return data_l

def scale_bram_data (array, coeff=2**6):
	"""Scale an array of BRAM data."""
	X = [int(coeff*x) for x in array]
	return X

def array_to_bytestring (array):
	"""Convert an array to a byte string."""
	ba = [struct.pack('!i', x) for x in array]
	bs = ''.join(ba)
	return bs

def sine_wave (L, cycles=1, phase=0):
	"""Build an L-point sine wave with range [-1,1)."""
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

