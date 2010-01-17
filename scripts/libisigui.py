#!/usr/bin/env python

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
		self._axes_l = None
		self._contour_l = None
		self._label_l = \
			("XX_auto", "YY_auto", "ZZ_auto", \
			 "XY_real", "YZ_real", "ZX_real", \
			 "XY_imag", "YX_imag", "ZX_imag")

		self._set_params()

		vbox = gtk.VBox(False, 8)
		self.add(vbox)

		canvas = self._gen_canvas()
		vbox.pack_start(canvas)

		cpanel = self._gen_cpanel()
		vbox.pack_start(cpanel, False, False)

		self.show_all()

	def _set_params (self):
		self.set_default_size(800, 600)
		self.connect("destroy", self._quit_action)
		self.set_title("ISI Correlator")
		self.set_border_width(8)

	def _gen_canvas (self):
		self._figure = libisiplot.IsiFigure()
		self._canvas = libisiplot.IsiCanvas(self._figure)
		return self._canvas

	def _gen_cpanel (self):
		cpanel = gtk.HBox()

		sync_button = gtk.Button("Sync")
		sync_button.connect("clicked", self._sync_action)
		cpanel.pack_start(sync_button, True, True, 0)

		shell_button = gtk.Button("Shell")
		shell_button.connect("clicked", self._shell_action)
		cpanel.pack_start(shell_button, True, True, 0)

		quit_button = gtk.Button("Quit")
		quit_button.connect("clicked", self._quit_action)
		cpanel.pack_start(quit_button, True, True, 0)

		return cpanel

	def _sync_action (self, widget):
		print "Sync sent!"

	def _shell_action (self, widget):
		import IPython
		ipshell = IPython.Shell.IPythonShellEmbed()
		ipshell()

	def _quit_action (self, widget):
		gtk.main_quit()

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

