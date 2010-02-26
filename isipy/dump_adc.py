#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

from libisidebug import *
from time import strftime

def dump_to_file (name, data):
	timestamp = strftime("%Y%m%dT%H%M%S")
	filename = "%s_%s.dump" % (timestamp, name)

	f = open(filename, "w")
	for i in data:
	    f.write("%d\n" % i)
	f.close()

print "Connecting to board."
R = IsiCorrelatorDebug('localhost', 7147)

print "Programming board."
R.progdev('test_adc083000x2.bof')

print "Configuring board."
R.set_clock_freq(200)
R.set_sync_period(1)
R.arm_sync()

print "Acquiring data."
R.acquire()

print "Reading data."
adc = R.read_adc('capt', 2**15)

print "Dumping data to file."
dump_to_file('adc', adc)

