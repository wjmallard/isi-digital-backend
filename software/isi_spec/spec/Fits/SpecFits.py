"""An interface to a FITS data file for the ISI Digital Spectrometer."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

from sys import exit

from numpy import arange
import pyfits

from Fits import Fits

class SpecFits (Fits):
	"""A FITS file for the ISI Spectrometer."""

	def __init__ (self, *args, **kwargs):
		"""Create a new FitsSpec object."""
		super(SpecFits, self).__init__(*args, **kwargs)

	def _make_data_hdu (self, data):
		"""Construct an HDU data section.

		Data should be a tuple of:
		* time : timestamp
		* stat : status bits
		* spec : spectrum
		"""
		try:
			time, stat, spec = data
		except ValueError:
			print "_make_data_hdu: Malformed data."
			raise

		data_tbl = []
		data_tbl += [pyfits.Column(name='time',     format='J',   array=time, unit='seconds')]
		data_tbl += [pyfits.Column(name='status',   format='J',   array=stat)]
		data_tbl += [pyfits.Column(name='spectrum', format='64J', array=spec)]
		data_hdu = pyfits.new_table(data_tbl)

		return data_hdu

