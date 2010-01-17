#!/usr/bin/env python

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010, CASPER"
__license__ = "GPL"
__status__ = "Development"

import matplotlib
matplotlib.use('GTKAgg')
from matplotlib.backends.backend_gtk import FigureCanvasGTK
from matplotlib.figure import Figure

import IPython
ipshell = IPython.Shell.IPShellEmbed()

class IsiFigure (Figure):
	def __init__ (self):
		Figure.__init__(self, figsize=(8,6), dpi=100)

class IsiCanvas (FigureCanvasGTK):
	def __init__ (self, figure):
		FigureCanvasGTK.__init__(self, figure)

		self._fig = figure

		self._num_chans = 64
		self._num_rows = 3
		self._num_cols = 3
		self._num_plots = self._num_rows * self._num_cols

		self._axes_l = None
		self._contour_l = None

		self._label_l = \
			("XX_auto", "YY_auto", "ZZ_auto", \
			 "XY_real", "YZ_real", "ZX_real", \
			 "XY_imag", "YX_imag", "ZX_imag")

		self._init_plots()

	def _init_plots (self):
		"""Initialize the axes and countours."""

		width = 1. / self._num_cols
		height = 1. / self._num_rows

		ydata = [0] * self._num_chans

		axprops = dict(xticklabels=[], yticklabels=[])

		self._axes_l = []
		self._contour_l = []

		for i in xrange(self._num_rows):
			for j in xrange(self._num_cols):

				rect = [j*width, 1-(i+1)*height, width, height]
				axes = self._fig.add_axes(rect, **axprops)
				contour, = axes.plot(ydata, '.')

				plot_num = i * self._num_cols + j
				label = self._label_l[plot_num]
				contour.set_label(label)
				self._fig.text(j*width, 1-(i+1)*height, label, fontsize=8)

				axes.set_xlim(0, self._num_chans)
				axes.set_ylim(ymin=0)

				self._axes_l += [axes]
				self._contour_l += [contour]

	def update (self, data):
		"""Update all plots with the latest data."""
		for i in xrange(self._num_plots):
			self._contour_l[i].set_ydata(data[i])
			self._axes_l[i].set_xlim(0, self._num_chans)
			self._axes_l[i].set_ylim(0, max(2**8, 1.1*max(data[i])))

