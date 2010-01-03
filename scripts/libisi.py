# auth: Billy Mallard
# mail: wjm@llard.net
# date: 2009-12-30
# desc: The ISI Correlator library.

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
		XY_real = self._read_bram("real_acc_" + chan_group, 0, 8)
		YZ_real = self._read_bram("real_acc_" + chan_group, 1, 8)
		ZX_real = self._read_bram("real_acc_" + chan_group, 2, 8)
		XY_imag = self._read_bram("imag_acc_" + chan_group, 0, 8)
		YZ_imag = self._read_bram("imag_acc_" + chan_group, 1, 8)
		ZX_imag = self._read_bram("imag_acc_" + chan_group, 2, 8)
		return (XX_auto, YY_auto, ZZ_auto, \
			XY_real, YZ_real, ZX_real, \
			XY_imag, YZ_imag, ZX_imag)

class IsiRoachFake(object):
	"""
	A fake ROACH board (for testing).
	"""

	def __init__ (self, id=0):
		self._id = id

	def read_int (self, name):
		return 0

	def write_int (self, name, value):
		pass

	def progdev (self, filename):
		pass

	def reset (self):
		pass

	def arm_sync (self):
		pass

	def send_sync (self):
		pass

	def acquire (self):
		pass

	def read_vacc (self, chan_group):
		x = (1,1,1,1,1,1,1,1)
		y = (x,x,x,x,x,x,x,x,x)
		return y

class IsiCorrelator(object):
	"""
	An abstraction of the three ROACH boards and their gateware.
	"""

	def __init__ (self, hosts=('isi0', 'isi1', 'isi2'), ports=(7147, 7147, 7147)):
		self._boards = []
		self._hosts = hosts
		self._ports = ports
		self._num_chans = 64
		self._sync_period = 2**26 # clocks
		self._update_delay = .1 # seconds

		self._connect()

	def _connect (self):
		assert (len(self._hosts) == 3)
		assert (len(self._ports) == 3)

		for i in xrange(3):
			if self._hosts[i] == 'fake':
				self._boards += [IsiRoachFake(i)]
			else:
				self._boards += [IsiRoachBoard(self._hosts[i], self._ports[i], i)]

	def program (self, filename):
		print "Programming boards ..."
		for board in self._boards:
			board.progdev(filename)
		time.sleep(.25)
		print "... done!"

	def set_sync_period (self, sync_period):
		self._sync_period = sync_period

		if sync_period > 0:
			sync_select = 1
		else:
			sync_select = 0

		for board in self._boards:
			board.write_int('sync_gen2_period', sync_period)
			board.write_int('sync_gen2_select', sync_select)

	def set_fft_shift (self, shift):
		for board in self._boards:
			board.write_int('fft_shift', shift)

	def set_eq_coeff (self, coeff):
		for board in self._boards:
			board.write_int('eq_coeff', coeff)

	def reset (self):
		for board in self._boards:
			board.reset()

	def arm_sync (self):
		for board in self._boards:
			board.arm_sync()

	def send_sync (self):
		for board in self._boards:
			board.send_sync()

	def acquire (self):
		for board in self._boards:
			board.acquire()
		time.sleep(self._update_delay)

	def get_data (self):
		"""Permutes data into a useful order."""
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

class IsiDisplay(object):
	"""
	A real-time graphical baseline display.
	"""

	def __init__ (self):
		self._num_rows = 3
		self._num_cols = 3
		self._num_plots = self._num_rows * self._num_cols

		self._num_channels = 64
		self._ymin = 0
		self._ymax = 2**8

		self._fig = None
		self._axes_l = None
		self._contour_l = None

		self._label_l = \
			("XX_auto", "YY_auto", "ZZ_auto", \
			 "XY_real", "YZ_real", "ZX_real", \
			 "XY_imag", "YX_imag", "ZX_imag")

		self._init_window()
		self._init_plots()

	def _init_window (self):
		"""Initializes _fig. Creates a graph window."""
		
		pylab.ion()
		self._fig = pylab.figure()
		m = pylab.get_current_fig_manager()
		m.set_window_title("ISI Correlator")

	def _init_plots (self):
		"""Initializes _axes_l and _contour_l."""

		width = 1. / self._num_cols
		height = 1. / self._num_rows

		xdata = range(0, self._num_channels)
		ydata = [0] * self._num_channels
		ydata[0] = self._ymax
		ydata[1] = self._ymin

		axprops = dict(yticks=[])

		self._axes_l = []
		self._contour_l = []

		for i in xrange(self._num_rows):
			for j in xrange(self._num_cols):

				rect = [j*width, 1-(i+1)*height, width, height]
				axes = self._fig.add_axes(rect, **axprops)
				contour, = axes.plot(xdata, ydata, '.')

				plot_num = i * self._num_cols + j
				label = self._label_l[plot_num]
				contour.set_label(label)
				axes.text(1, 2, label, fontsize=10)

				axes.autoscale_view(tight=True, scalex=True, scaley=True)
				pylab.setp(axes.get_xticklabels(), visible=False)

				self._axes_l += [axes]
				self._contour_l += [contour]

	def set_data (self, data):
		"""
		Updates the ydata for all contours and redraws the plots.
		"""
		for i in xrange(self._num_plots):
			self._contour_l[i].set_ydata(data[i])
		pylab.draw()

