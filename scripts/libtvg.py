#!/usr/bin/env python

__author__ = "William Mallard"
__license__ = "GPL"
__version__ = "0.1"

import math
import random
import struct

def sine (length, cycles=1):
	x = xrange(length)
	y = [int((1<<31)*math.sin(cycles*(2*math.pi*t)/(length-1))) for t in x]
	return wordToByteString(y)

class lfsr32 (object):
	"""A 32-stage Linear Feedback Shift Register."""

	def __init__ (self, taps=[32,31,30,10], seed=0xF0E1D2C3):
		self._taps = taps
		self._seed = seed
		self._state = seed

	def next (self):
		"""Generate the next state, and return a uint32."""
		tap_shft = (x-1 for x in self._taps)
		tap_vals = (self._state << x for x in tap_shft)
		xor_taps = reduce(lambda x,y: x^y, tap_vals)
		and_taps = xor_taps & 0x80000000
		self._state = and_taps | self._state >> 1
		return self._state

def wordToByteString (array):
	byteStrings = [struct.pack('!1i', x) for x in array]
	byteString = ''.join(byteStrings)
	return byteString

def main ():
	l = lfsr32()
	for i in xrange(1,32):
		print "%.8X" % l.next()

if __name__ == "__main__":
	main()

