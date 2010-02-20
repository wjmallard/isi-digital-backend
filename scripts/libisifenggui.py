#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import libisiplot
import libisicorr

from time import strftime

class IsiFEngineGui (gtk.Window):
	"""The control and status GUI for the ISI F-Engine."""

	def __init__ (self, corr):
		gtk.Window.__init__(self)

		self._isi_fengine = corr

		self._canvas = None
		self._figure = None

		self._dump_pending = False

		self._set_params()
		self._set_accels()
		self._set_layout()

	def _set_params (self):
		self.set_default_size(800, 600)
		self.connect("destroy", self._quit_action)
		self.set_title("ISI F-Engine")
		self.set_border_width(8)

	def _set_accels (self):
		group = gtk.AccelGroup()

		cmd_map = dict \
		({ \
			'<Control>q' : self._quit_action, \
			'<Control>f' : self._fullscreen_action, \
			'<Control>d' : self._filedump_action, \
		})

		for (cmd, fxn) in cmd_map.items():
			key, mod = gtk.accelerator_parse(cmd)
			group.connect_group(key, mod, gtk.ACCEL_VISIBLE, fxn)

		self.add_accel_group(group)

	def _set_layout (self):
		self._figure = libisiplot.IsiFigure()
		self._canvas = libisiplot.IsiCanvas2(self._figure, 2, 2)
		self.add(self._canvas)

	def _quit_action (self, widget, *args):
		gtk.main_quit()
		return True

	def _fullscreen_action (self, widget, *args):
		self.maximize()
		return True

	def _filedump_action (self, widget, *args):
		self._dump_pending = True
		return True

	def _dump_to_file (self, data, name, timestamp):
		filename = "%s_%s.dump" % (timestamp, name)

		f = open(filename, "w")
		for i in data:
			f.write('%d\n' % i)
		f.close()

	def _update (self):
		self._isi_fengine.acquire()
		# TODO: replace with 1pps!
		self._isi_fengine.send_sync()

		adc = self._isi_fengine.read_adc("capt_adc_data", 128)
		pfb = self._isi_fengine.read_adc("capt_pfb", 128)
		fft = self._isi_fengine.read_fft("capt_fft_data", 64)
		eq = self._isi_fengine.read_fft("capt_eq_data", 64)

		if self._dump_pending:
			print "Dumping plot data to file!"
			timestamp = strftime("%Y%m%dT%H%M%S")

			self._dump_to_file(adc, "adc", timestamp)
			self._dump_to_file(pfb, "pfb", timestamp)
			self._dump_to_file(fft, "fft", timestamp)
			self._dump_to_file(eq, "eq", timestamp)

			self._dump_pending = False

		self._canvas.set_data(0, adc)
		self._canvas.set_data(1, pfb)
		self._canvas.set_data(2, fft)
		self._canvas.set_data(3, eq)

		self._canvas.draw()
		return True

	def get_canvas (self):
		return self._canvas

	def start (self):
		gobject.idle_add(self._update)
		self.show_all()
		gtk.main()

