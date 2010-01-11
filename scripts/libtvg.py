#!/usr/bin/env python

__author__ = "William Mallard"
__license__ = "GPL"
__version__ = "0.1"

import math
import random
import struct

def sine (length, cycles=1, phase=0):
	x = xrange(length)
	A = 2**7-1
	B = 2*math.pi*cycles/length
	C = 2*math.pi*phase
	y = [int(A*math.sin(B*t+C)) for t in x]
	return arrayToByteString(y)

def rand (length, seed=None):
    random.seed(seed)
    y = [(2**8)*random.random() for x in xrange(length)]
    return arrayToByteString(y)

def arrayToByteString (array):
	byteStrings = [struct.pack('!1b', x) for x in array]
	byteString = ''.join(byteStrings)
	return byteString

def main ():
	s = sine(8, 1.5, .5)
	print s
	r = rand(8, 1234)
	print r

if __name__ == "__main__":
	main()

