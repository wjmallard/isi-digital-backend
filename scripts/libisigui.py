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
		self._set_accels()
		self._set_layout()

	def _set_params (self):
		self.set_default_size(800, 600)
		self.connect("destroy", self._quit_action)
		self.set_title("ISI Correlator")
		self.set_border_width(8)

	def _set_accels (self):
		group = gtk.AccelGroup()

		cmnd_map = dict \
		({ \
			'<Control>q' : self._quit_action, \
			'<Control>f' : self._fullscreen_action, \
		})

		for (cmnd, func) in cmnd_map.items():
			key, mod = gtk.accelerator_parse(cmnd)
			group.connect_group(key, mod, gtk.ACCEL_VISIBLE, func)

		self.add_accel_group(group)

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
		ctrl_panel = gtk.HBox(spacing=5)

		cp_ctrl_frame = gtk.Frame("Control")
		ctrl_panel.pack_start(cp_ctrl_frame, expand=False, padding=1)

		cp_parm_frame = gtk.Frame("System Parameters")
		ctrl_panel.pack_start(cp_parm_frame, expand=False, padding=1)

		cp_stat_frame = gtk.Frame("Status")
		ctrl_panel.pack_start(cp_stat_frame, expand=False, padding=1)

		cp_fill_frame = gtk.Frame()
		ctrl_panel.pack_end(cp_fill_frame, expand=False, padding=1)

		#
		# Control Buttons
		#

		cp_ctrl_hbox = gtk.HBox(spacing=5)
		cp_ctrl_frame.add(cp_ctrl_hbox)

		cp_ctrl_vbbox = gtk.VButtonBox()
		cp_ctrl_hbox.pack_start(cp_ctrl_vbbox, padding=5)

		freeze_button = gtk.ToggleButton("Freeze")
		freeze_button.unset_flags(gtk.CAN_FOCUS)
		freeze_button.connect("clicked", self._freeze_action)
		cp_ctrl_vbbox.pack_start(freeze_button)

		sync_button = gtk.Button("Sync")
		sync_button.unset_flags(gtk.CAN_FOCUS)
		sync_button.connect("clicked", self._sync_action)
		cp_ctrl_vbbox.pack_start(sync_button)

		update_button = gtk.Button("Update")
		update_button.unset_flags(gtk.CAN_FOCUS)
		update_button.connect("clicked", self._update_action)
		cp_ctrl_vbbox.pack_start(update_button)

		#quit_button = gtk.Button("Quit")
		#quit_button.connect("clicked", self._quit_action)
		#cp_ctrl_vbbox.pack_start(quit_button)

		#
		# System Parameters
		#

		cp_parm_hbox = gtk.HBox(spacing=5)
		cp_parm_frame.add(cp_parm_hbox)

		cp_parm_label_vbbox = gtk.VButtonBox()
		cp_parm_hbox.pack_start(cp_parm_label_vbbox)

		cp_parm_entry_vbbox = gtk.VButtonBox()
		cp_parm_hbox.pack_start(cp_parm_entry_vbbox)

		sync_period_label = gtk.Label("Sync Period")
		sync_period_label.set_alignment(1, .5)
		cp_parm_label_vbbox.pack_start(sync_period_label)

		fft_shift_label = gtk.Label("FFT Shift")
		fft_shift_label.set_alignment(1, .5)
		cp_parm_label_vbbox.pack_start(fft_shift_label)

		eq_coeff_label = gtk.Label("Eq Coeff")
		eq_coeff_label.set_alignment(1, .5)
		cp_parm_label_vbbox.pack_start(eq_coeff_label)

		sync_period_entry = gtk.Entry(3)
		sync_period_entry.connect("changed", self._sync_period_action)
		cp_parm_entry_vbbox.pack_start(sync_period_entry)

		fft_shift_entry = gtk.Entry(3)
		fft_shift_entry.connect("changed", self._fft_shift_action)
		cp_parm_entry_vbbox.pack_start(fft_shift_entry)

		eq_coeff_entry = gtk.Entry(5)
		eq_coeff_entry.connect("changed", self._eq_coeff_action)
		cp_parm_entry_vbbox.pack_start(eq_coeff_entry)

		#
		# Status
		#

		cp_stat_hbox = gtk.HBox(spacing=5)
		cp_stat_frame.add(cp_stat_hbox)

		cp_stat_vbox0 = gtk.VBox()
		cp_stat_hbox.pack_start(cp_stat_vbox0, padding=5)

		cp_stat_vbox1 = gtk.VBox()
		cp_stat_hbox.pack_start(cp_stat_vbox1, padding=0)

		cp_stat_sep0 = gtk.VSeparator()
		cp_stat_hbox.pack_start(cp_stat_sep0, padding=5)

		cp_stat_vbox2 = gtk.VBox()
		cp_stat_hbox.pack_start(cp_stat_vbox2, padding=0)

		cp_stat_vbox3 = gtk.VBox()
		cp_stat_hbox.pack_start(cp_stat_vbox3, padding=5)

		led_sync = gtk.Image()
		led_sync.set_from_file("led_off.xpm")
		cp_stat_vbox0.pack_start(led_sync)

		led_armed = gtk.Image()
		led_armed.set_from_file("led_off.xpm")
		cp_stat_vbox0.pack_start(led_armed)

		led_acquire = gtk.Image()
		led_acquire.set_from_file("led_off.xpm")
		cp_stat_vbox0.pack_start(led_acquire)

		led_unused = gtk.Image()
		led_unused.set_from_file("led_off.xpm")
		cp_stat_vbox0.pack_start(led_unused)

		led_sync_label = gtk.Label("Sync")
		led_sync_label.set_alignment(0, .5)
		cp_stat_vbox1.pack_start(led_sync_label)

		led_armed_label = gtk.Label("Armed")
		led_armed_label.set_alignment(0, .5)
		cp_stat_vbox1.pack_start(led_armed_label)

		led_acquire_label = gtk.Label("Acquire")
		led_acquire_label.set_alignment(0, .5)
		cp_stat_vbox1.pack_start(led_acquire_label)

		led_unused_label = gtk.Label("(unused)")
		led_acquire_label.set_alignment(0, .5)
		cp_stat_vbox1.pack_start(led_unused_label)

		led_adc_valid = gtk.Image()
		led_adc_valid.set_from_file("led_off.xpm")
		cp_stat_vbox2.pack_start(led_adc_valid)

		led_adc_oor = gtk.Image()
		led_adc_oor.set_from_file("led_off.xpm")
		cp_stat_vbox2.pack_start(led_adc_oor)

		led_fft_of = gtk.Image()
		led_fft_of.set_from_file("led_off.xpm")
		cp_stat_vbox2.pack_start(led_fft_of)

		led_eq_clip = gtk.Image()
		led_eq_clip.set_from_file("led_off.xpm")
		cp_stat_vbox2.pack_start(led_eq_clip)

		led_adc_valid_label = gtk.Label("ADC Valid")
		led_adc_valid_label.set_alignment(0, .5)
		cp_stat_vbox3.pack_start(led_adc_valid_label)

		led_adc_oor_label = gtk.Label("ADC OOR")
		led_adc_oor_label.set_alignment(0, .5)
		cp_stat_vbox3.pack_start(led_adc_oor_label)

		led_fft_of_label = gtk.Label("FFT OF")
		led_fft_of_label.set_alignment(0, .5)
		cp_stat_vbox3.pack_start(led_fft_of_label)

		led_eq_clip_label = gtk.Label("EQ Clip")
		led_eq_clip_label.set_alignment(0, .5)
		cp_stat_vbox3.pack_start(led_eq_clip_label)

		#
		# Logo
		#

		cp_fill_hbox = gtk.HBox(spacing=5)
		cp_fill_frame.add(cp_fill_hbox)

		cp_fill_vbox = gtk.VBox()
		cp_fill_hbox.pack_start(cp_fill_vbox, padding=5)

		isi_logo = gtk.Image()
		isi_logo.set_from_file("isi.xpm")
		cp_fill_vbox.pack_start(isi_logo)

		program_label = gtk.Label("ISI Correlator")
		cp_fill_vbox.pack_start(program_label)

		return ctrl_panel

	def _quit_action (self, widget, *args):
		gtk.main_quit()
		return True

	def _fullscreen_action (self, widget, *args):
		self.maximize()
		return True

	def _freeze_action (self, widget):
		state = widget.get_active()
		if (state):
			widget.set_label("Unfreeze")
			print "Frozen!"
		else:
			widget.set_label("Freeze")
			print "Unfrozen."

	def _sync_action (self, widget):
		self._isi_correlator.send_sync()
		print "Sync sent!"

	def _update_action (self, widget):
		print "Update clicked."

	def _sync_period_action (self, widget):
		print "Sync period changed."

	def _fft_shift_action (self, widget):
		shift = self._validate_entry(widget, 0x00, 0x7f)
		self._isi_correlator.set_fft_shift(shift)

	def _eq_coeff_action (self, widget):
		coeff = self._validate_entry(widget, 0x0000, 0xffff)
		self._isi_correlator.set_eq_coeff(coeff)

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

