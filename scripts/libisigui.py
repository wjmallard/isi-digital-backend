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

import IPython
ipshell = IPython.Shell.IPShellEmbed()

class IsiGui (gtk.Window):
	def __init__ (self, corr):
		gtk.Window.__init__(self)

		self._isi_correlator = corr
		self._num_chans = corr.get_num_chans()

		self._canvas = None
		self._figure = None

		self._set_params()
		self._set_layout()

	def _set_params (self):
		self.set_default_size(800, 600)
		self.connect("destroy", self._quit_action)
		self.set_title("ISI Correlator")
		self.set_border_width(8)

	def _set_layout (self):
		vbox = gtk.VBox(False, 8)
		self.add(vbox)

		canvas = self._gen_canvas()
		vbox.pack_start(canvas)

		ctrl_panel = self._gen_ctrl_panel()
		vbox.pack_start(ctrl_panel, False, False)

	def _gen_canvas (self):
		self._figure = libisiplot.IsiFigure()
		self._canvas = libisiplot.IsiCanvas(self._figure)
		return self._canvas

	def _gen_ctrl_panel (self):
		ctrl_panel = gtk.HButtonBox()

		freeze_checkbox = gtk.ToggleButton("Freeze")
		freeze_checkbox.connect("clicked", self._freeze_action)
		ctrl_panel.pack_start(freeze_checkbox, True, True, 0)

		sync_button = gtk.Button("Sync")
		sync_button.connect("clicked", self._sync_action)
		ctrl_panel.pack_start(sync_button, True, True, 0)

		fft_shift_entry = gtk.Entry(3)
		fft_shift_entry.connect("changed", self._fft_shift_action)
		ctrl_panel.pack_start(fft_shift_entry, True, True, 0)

		eq_coeff_entry = gtk.Entry(5)
		eq_coeff_entry.connect("changed", self._eq_coeff_action)
		ctrl_panel.pack_start(eq_coeff_entry, True, True, 0)

		quit_button = gtk.Button("Quit")
		quit_button.connect("clicked", self._quit_action)
		ctrl_panel.pack_start(quit_button, True, True, 0)

		return ctrl_panel

	def _freeze_action (self, widget):
		state = widget.get_active()
		if (state):
			print "Frozen!"
		else:
			print "Unfrozen."

	def _sync_action (self, widget):
		self._isi_correlator.send_sync()
		print "Sync sent!"

	def _fft_shift_action (self, widget):
		shift = self._validate_entry(widget, 0x00, 0x7f)
		self._isi_correlator.set_fft_shift(shift)

	def _eq_coeff_action (self, widget):
		coeff = self._validate_entry(widget, 0x0000, 0xffff)
		self._isi_correlator.set_eq_coeff(coeff)

	def _quit_action (self, widget):
		gtk.main_quit()

	def _validate_entry (self, widget, min, max):
		text = widget.get_text()

		value = -1
		if text != "":
			try:
				value = int(text, 16)
			except ValueError:
				pass

		if value < min:
			value = min
		elif value > max:
			value = max

		widget.set_text("%x" % value)
		return value
		

	def _update (self):
		self._isi_correlator.acquire()
		data = self._isi_correlator.get_data()
		self._canvas.update(data)
		self._canvas.draw()
		return True

	def start (self):
		gobject.idle_add(self._update)
		self.show_all()
		gtk.main()

