# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-30
# desc: A library for the isi_correlator.

import corr
import itertools
import pylab
import time
import struct
import sys

import IPython
ipshell = IPython.Shell.IPShellEmbed()

class IsiRoachBoard(corr.katcp_wrapper.FpgaClient):
	"""
	A wrapper around the KATCP FPGA Client class.
	"""

	ARM_RESET   = 1<<0
	FORCE_TRIG  = 1<<1
	FIFO_RESET  = 1<<2
	ACQUIRE     = 1<<3
	CAPT_RESET  = 1<<4

	def __init__ (self, host, port, id=0):
		super(IsiRoachBoard, self).__init__(host, port)
		self._host = host
		self._port = port
		self._id = id
		time.sleep(.25) # NOTE: race condition!
		self.reset()

	def _set_flag (self, flags):
		reg_state = self.read_int('control')
		reg_state |= flags
		self.write_int('control', reg_state)

	def _unset_flag (self, flags):
		reg_state = self.read_int('control')
		reg_state &= ~flags
		self.write_int('control', reg_state)

	def _toggle_reset (self, flag):
		self._set_flag(flag)
		time.sleep(.1)
		self._unset_flag(flag)

	def _read_bram (self, capt_name, bram_num, read_len):
		bram_name = "capt_%s_bram%d" % (capt_name, bram_num)
		bram_dump = self.read(bram_name, read_len*4)
		bram_data = struct.unpack('>%sI' % read_len, bram_dump)
		return bram_data

	def reset (self):
		self.write_int('fft_shift', 0)
		self.write_int('eq_coeff', 1)
		self.write_int('sync_gen2_period', 1)
		self.write_int('sync_gen2_select', 0)
		self._set_flag(IsiRoachBoard.FIFO_RESET)
		self._set_flag(IsiRoachBoard.CAPT_RESET)
		self.write_int('control', 0)

	def arm_sync (self):
		self._unset_flag(IsiRoachBoard.ARM_RESET)
		time.sleep(.1)
		self._set_flag(IsiRoachBoard.ARM_RESET)

	def send_sync (self):
		self._unset_flag(IsiRoachBoard.FORCE_TRIG)
		self.arm_sync()
		self._set_flag(IsiRoachBoard.FORCE_TRIG)

	def acquire (self):
		self._unset_flag(IsiRoachBoard.ACQUIRE)
		self._set_flag(IsiRoachBoard.CAPT_RESET)
		self._unset_flag(IsiRoachBoard.CAPT_RESET)
		self._set_flag(IsiRoachBoard.ACQUIRE)

	def read_vacc (self, chan_group):
		XX_auto = self._read_bram("auto_acc_" + chan_group, 0, 8)
		YY_auto = self._read_bram("auto_acc_" + chan_group, 1, 8)
		ZZ_auto = self._read_bram("auto_acc_" + chan_group, 2, 8)
		XY_real = self._read_bram("auto_acc_" + chan_group, 0, 8)
		YZ_real = self._read_bram("auto_acc_" + chan_group, 1, 8)
		ZX_real = self._read_bram("auto_acc_" + chan_group, 2, 8)
		XY_imag = self._read_bram("auto_acc_" + chan_group, 0, 8)
		YZ_imag = self._read_bram("auto_acc_" + chan_group, 1, 8)
		ZX_imag = self._read_bram("auto_acc_" + chan_group, 2, 8)
		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

class IsiCorrelator(object):
	"""
	An abstraction of the three ROACH boards and their gateware.
	"""

	def __init__ (self):
		self._boards = []
		self._num_chans = 64
		self._sync_period = 2**26 # clocks
		self._update_delay = .1 # seconds

	def connect (self, hosts=("isi0", "isi1", "isi2"), ports=(7147, 7147, 7147)):
		assert (len(hosts) == 3)
		assert (len(ports) == 3)
		for i in xrange(3):
			self._boards += [IsiRoachBoard(hosts[i], ports[i], i)]

	def set_sync_period (self, sync_period):
		self._sync_period = sync_period

		if sync_period > 0:
			sync_select = 1
		else:
			sync_select = 0

		for board in self._boards:
			board.write_int('sync_gen2_period', sync_period)
			board.write_int('sync_gen2_select', sync_select)

	def set_fft_shift (shift):
		for board in self._boards:
			board.write_int('fft_shift', shift)

	def set_eq_coeff (coeff):
		for board in self._boards:
			board.write_int('eq_coeff', coeff)

	def reset (self):
		for board in self._boards:
			board.reset()

	def arm_sync (self):
		for board in self._boards:
			board.arm_sync()

	def acquire (self):
		for board in self._boards:
			board.acquire()
		time.sleep(self._update_delay)

	def get_data ():
		"""Permute data into a useful order."""
		XA = self._boards[0].read_vacc('A')
		XB = self._boards[0].read_vacc('B')
		XC = self._boards[0].read_vacc('C')
		YA = self._boards[1].read_vacc('A')
		YB = self._boards[1].read_vacc('B')
		YC = self._boards[1].read_vacc('C')
		ZA = self._boards[2].read_vacc('A')
		ZB = self._boards[2].read_vacc('B')

		#
		# Begin fucking magic.
		#

		# 3-D matrix transpose: (x,y,z)->(y,x,z)
		a = itertools.izip(XA, XB, XC, YA, YB, YC, ZA, ZB)

		# 3-D matrix transpose: (y,x,z)->(y,z,x)
		b = [itertools.izip(*x) for x in a]

		# 2-D matrix collapse: (y,z,x)->(y,z*x)
		XX_auto = [x for y in b[0] for x in y]
		YY_auto = [x for y in b[1] for x in y]
		ZZ_auto = [x for y in b[2] for x in y]
		XY_real = [x for y in b[3] for x in y]
		YZ_real = [x for y in b[4] for x in y]
		ZX_real = [x for y in b[5] for x in y]
		XY_imag = [x for y in b[6] for x in y]
		YZ_imag = [x for y in b[7] for x in y]
		ZX_imag = [x for y in b[8] for x in y]

		#
		# End fucking magic.
		#

		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)



#
# ASSUME THAT NOTHING WORKS BELOW HERE ...
#

#
# Plot control functions.
#

def create_plots (num_channels):
	#(num_plots, num_subplots, x_lengths, y_bounds, labels):

	num_rows = 8
	num_cols = 9
	y_min = 0
	y_max = 2**28

	xdata = range(0, num_channels)
	ydata_ll = []
	for i in xrange(num_rows):
		ydata_l = []
		for j in xrange(num_cols):
			ydata = [0] * num_channels
			y[0] = y_min
			y[1] = y_max
			ydata_l += ydata
		ydata_ll += [ydata_l]

	xoffset = 0.0
	yoffset = 1.0
	xwidth = 1. / num_cols
	ywidth = 1. / num_rows
	plot_rect = [xoffset, yoffset, xwidth, ywidth]

	axprops = dict(yticks=[])
	yprops = dict(rotation=90)

	fig = pylab.figure()

	ax_list = []
	c_list = []
	for i in xrange(num_plots):
		plot_rect[1] -= plot_delta
		ax = fig.add_axes(plot_rect, **axprops)

		c_sublist = []
		for j in xrange(num_subplots[i]):
			c, = ax.plot(x_list[i][j], y_list[i][j], '.')
			c_sublist += [c]

		ax.set_ylabel(labels[i], **yprops)
		print "bound=[%d,%d]" % (y_bounds[i][0], y_bounds[i][1])
		ax.autoscale_view(tight=True, scalex=True, scaley=True)
		pylab.setp(ax.get_xticklabels(), visible=False)

		ax_list += [ax]
		c_list += [c_sublist]

	return c_list

def customize_window (window_title):
	m = pylab.get_current_fig_manager()
	m.set_window_title(window_title)

