from libisidebug import *
from libisitvg import *
import numpy as np

num_samples = 1<<11

# Connect to board.
#R = IsiCorrelatorDebug('localhost', 7149)
R = IsiCorrelatorDebug('isi3', 7147)
R.progdev('test_vacc.bof')

# Initialize board.
R.set_clock_freq(200)
R.set_sync_period(.002)

def get_vacc_addr():
	x = R.read_int('vacc_addr')
	sync = x >> 12
	addr = x & 0x0fff
	print "sync %d (addr %d)" % (sync, addr)

R.reset()

# Generate a test vector.
#tvg_data = np.zeros(num_samples)
#tvg_data[0] = 2
#tvg_data[7] = 1
#tvg_data = np.ones(num_samples)
tvg_data = np.arange(num_samples)
tvg_bstr = array_to_bytestring(tvg_data)
R.write('tvg_bram', tvg_bstr)

R.arm_sync()
R.send_sync()

VACC = R._read_bram('vacc_bram', 4096, offset=0)

