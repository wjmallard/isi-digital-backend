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

		canvas = self._assemble_canvas()
		vbox.pack_start(canvas)

		panel = self._assemble_panel()
		vbox.pack_start(panel, False, False)

	def _assemble_canvas (self):
		self._figure = libisiplot.IsiFigure()
		self._canvas = libisiplot.IsiCanvas(self._figure)
		return self._canvas

	def _assemble_panel (self):
		panel = gtk.HBox(spacing=5)

		control_frame = IsiControlFrame(self._isi_correlator)
		panel.pack_start(control_frame, expand=False, padding=1)

		status_frame = IsiStatusFrame(self._isi_correlator)
		panel.pack_start(status_frame, expand=False, padding=1)

		logo_frame = IsiLogoFrame()
		panel.pack_end(logo_frame, expand=False, padding=1)

		return panel

	def _quit_action (self, widget, *args):
		gtk.main_quit()
		return True

	def _fullscreen_action (self, widget, *args):
		self.maximize()
		return True

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

class IsiControlFrame (gtk.Frame):
	def __init__ (self, corr):
		gtk.Frame.__init__(self, "Control")
		self._isi_correlator = corr
		self._assemble()

	def _assemble (self):

		hbox = gtk.HBox(spacing=5)
		self.add(hbox)

		vbbox0 = gtk.VButtonBox()
		hbox.pack_start(vbbox0, padding=5)

		sep0 = gtk.VSeparator()
		hbox.pack_start(sep0, padding=0)

		vbbox1 = gtk.VButtonBox()
		hbox.pack_start(vbbox1, padding=0)

		vbbox2 = gtk.VButtonBox()
		hbox.pack_start(vbbox2, padding=5)

		#
		# Buttons
		#

		freeze_button = gtk.ToggleButton("Freeze")
		freeze_button.unset_flags(gtk.CAN_FOCUS)
		freeze_button.connect("clicked", self._freeze_action)
		vbbox0.pack_start(freeze_button)

		sync_button = gtk.Button("Sync")
		sync_button.unset_flags(gtk.CAN_FOCUS)
		sync_button.connect("clicked", self._sync_action)
		vbbox0.pack_start(sync_button)

		update_button = gtk.Button("Update")
		update_button.unset_flags(gtk.CAN_FOCUS)
		update_button.connect("clicked", self._update_action)
		vbbox0.pack_start(update_button)

		#
		# Parameter Labels
		#

		sync_period_label = gtk.Label("Sync Period")
		sync_period_label.set_alignment(1, .5)
		vbbox1.pack_start(sync_period_label)

		fft_shift_label = gtk.Label("FFT Shift")
		fft_shift_label.set_alignment(1, .5)
		vbbox1.pack_start(fft_shift_label)

		eq_coeff_label = gtk.Label("Eq Coeff")
		eq_coeff_label.set_alignment(1, .5)
		vbbox1.pack_start(eq_coeff_label)

		#
		# Parameter Entries
		#

		sync_period_entry = gtk.Entry(3)
		sync_period_entry.connect("changed", self._sync_period_action)
		vbbox2.pack_start(sync_period_entry)

		fft_shift_entry = gtk.Entry(3)
		fft_shift_entry.connect("changed", self._fft_shift_action)
		vbbox2.pack_start(fft_shift_entry)

		eq_coeff_entry = gtk.Entry(5)
		eq_coeff_entry.connect("changed", self._eq_coeff_action)
		vbbox2.pack_start(eq_coeff_entry)

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

class IsiStatusFrame (gtk.Frame):
	def __init__ (self, corr):
		gtk.Frame.__init__(self, "Status")
		self._isi_correlator = corr
		self._assemble()

	def _assemble (self):

		hbox = gtk.HBox(spacing=5)
		self.add(hbox)

		vbox0 = gtk.VBox()
		hbox.pack_start(vbox0, padding=5)

		vbox1 = gtk.VBox()
		hbox.pack_start(vbox1, padding=0)

		sep0 = gtk.VSeparator()
		hbox.pack_start(sep0, padding=5)

		vbox2 = gtk.VBox()
		hbox.pack_start(vbox2, padding=0)

		vbox3 = gtk.VBox()
		hbox.pack_start(vbox3, padding=5)

		#
		# LEDs
		#

		led_sync = gtk.Image()
		led_sync.set_from_file("led_off.xpm")
		vbox0.pack_start(led_sync)

		led_armed = gtk.Image()
		led_armed.set_from_file("led_off.xpm")
		vbox0.pack_start(led_armed)

		led_acquire = gtk.Image()
		led_acquire.set_from_file("led_off.xpm")
		vbox0.pack_start(led_acquire)

		led_unused = gtk.Image()
		led_unused.set_from_file("led_off.xpm")
		vbox0.pack_start(led_unused)

		led_sync_label = gtk.Label("Sync")
		led_sync_label.set_alignment(0, .5)
		vbox1.pack_start(led_sync_label)

		led_armed_label = gtk.Label("Armed")
		led_armed_label.set_alignment(0, .5)
		vbox1.pack_start(led_armed_label)

		led_acquire_label = gtk.Label("Acquire")
		led_acquire_label.set_alignment(0, .5)
		vbox1.pack_start(led_acquire_label)

		led_unused_label = gtk.Label("(unused)")
		led_acquire_label.set_alignment(0, .5)
		vbox1.pack_start(led_unused_label)

		led_adc_valid = gtk.Image()
		led_adc_valid.set_from_file("led_off.xpm")
		vbox2.pack_start(led_adc_valid)

		led_adc_oor = gtk.Image()
		led_adc_oor.set_from_file("led_off.xpm")
		vbox2.pack_start(led_adc_oor)

		led_fft_of = gtk.Image()
		led_fft_of.set_from_file("led_off.xpm")
		vbox2.pack_start(led_fft_of)

		led_eq_clip = gtk.Image()
		led_eq_clip.set_from_file("led_off.xpm")
		vbox2.pack_start(led_eq_clip)

		led_adc_valid_label = gtk.Label("ADC Valid")
		led_adc_valid_label.set_alignment(0, .5)
		vbox3.pack_start(led_adc_valid_label)

		led_adc_oor_label = gtk.Label("ADC OOR")
		led_adc_oor_label.set_alignment(0, .5)
		vbox3.pack_start(led_adc_oor_label)

		led_fft_of_label = gtk.Label("FFT OF")
		led_fft_of_label.set_alignment(0, .5)
		vbox3.pack_start(led_fft_of_label)

		led_eq_clip_label = gtk.Label("EQ Clip")
		led_eq_clip_label.set_alignment(0, .5)
		vbox3.pack_start(led_eq_clip_label)

class IsiLogoFrame (gtk.Frame):
	def __init__ (self):
		gtk.Frame.__init__(self)
		self._assemble()

	def _assemble (self):
	
		hbox = gtk.HBox(spacing=5)
		self.add(hbox)

		vbox = gtk.VBox()
		hbox.pack_start(vbox, padding=5)

		isi_logo = gtk.Image()
		isi_logo.set_from_file("isi.xpm")
		vbox.pack_start(isi_logo)

		program_label = gtk.Label("ISI Correlator")
		vbox.pack_start(program_label)

