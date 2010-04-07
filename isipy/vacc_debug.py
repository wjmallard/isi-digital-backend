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

# Generate a test vector.
tvg_data = np.ones(num_samples)
tvg_data = tvg_data
tvg_bstr = array_to_bytestring(tvg_data)
R.write('tvg_bram', tvg_bstr)

def get_vacc_addr():
	x = R.read_int('vacc2_addr')
	sync = x >> 12
	addr = x & 0x0fff
	print "sync %d (addr %d)" % (sync, addr)

R.arm_sync()
get_vacc_addr()
R.send_sync()
get_vacc_addr()
get_vacc_addr()
get_vacc_addr()
get_vacc_addr()
get_vacc_addr()
get_vacc_addr()
get_vacc_addr()

VACC = R._read_bram('vacc2_bram', 2016, offset=0)

