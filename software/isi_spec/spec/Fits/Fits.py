"""An interface to a FITS data file."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
import os
import errno
from time import strftime
from abc import ABCMeta, abstractmethod

import pyfits

class Fits ():
	"""
	A generic FITS file.

	Contains one Header and Data Unit (HDU).
	"""
	__metaclass__ = ABCMeta

	TEMP_PATH = './data.fits'

	def __init__ (self, conf, temp=False):
		"""Create a new FITS file.

		Parse header information from fits.cfg.
		If temp is True, set path to TEMP_PATH.
		"""
		self.temp = temp
		self.conf = conf
		self.header = conf.header

	def write (self, data, start_time, stop_time, conf):
		"""Write data to disk as a FITS file.

		Construct a file path from the base path
		specified in spec.cfg and the start_time.

		Package the header and data into an HDU,
		and write it to disk.
		"""
		path = self._construct_path(conf['data_dir'], start_time)
		hdu = self._make_fits_file(data, start_time, stop_time)
		hdu.writeto(path)
		hdu.close()

	def _construct_path (self, data_dir, start_time):
		if self.temp:
			outdir = "."
			fitspath = Fits.TEMP_PATH
		else:
			datestamp = strftime("%Y%b%d", start_time)
			timestamp = str(self._to_yrsec(start_time))
			source = self.conf['source']

			outdir = "%s/%s/%s" % (data_dir, datestamp, source)
			fitspath = "%s/%s.fits" % (outdir, timestamp)

		# Create output directory.
		try:
			os.makedirs(outdir)
		except OSError as ex:
			if ex.errno == errno.EEXIST: pass
			else: raise

		# Remove output file, if it exists.
		try:
			os.remove(fitspath)
		except OSError as ex:
			if ex.errno == errno.ENOENT: pass
			else: raise

		return fitspath

	def _make_fits_file (self, data, start_time, stop_time):
		"""Package headers and data into a FITS file.

		Construct a FITS header HDU and data HDU.
		Combine these into an HDU list.
		"""
		head_hdu = self._make_head_hdu(start_time, stop_time)
		data_hdu = self._make_data_hdu(data)
		return pyfits.HDUList([head_hdu, data_hdu])

	def _make_head_hdu (self, start_time, stop_time):
		"""Construct an HDU header section.

		Iterate through stored fits.cfg settings.
		Populate the %DATE%, %START%, and %STOP%
		fields in the header with actual numbers.
		Write all setting values and labels into
		the header, grouped into header sections.
		"""
		head_hdu = pyfits.PrimaryHDU()

		time_fields = self._fill_time_fields(start_time, stop_time)

		for section, options in self.header.items():
			for option, val_pair in options.items():
				# Split value and label.
				value, label = val_pair

				# If this is a time field,
				# replace field with time.
				if value in time_fields:
					value = time_fields[value]

				# Add key/value to header.
				head_hdu.header.update(option, value, label)

			# Add a section label.
			first_option = list(options)[0]
			head_hdu.header.add_blank(section, before=first_option)

		return head_hdu

	def _fill_time_fields (self, start_time, stop_time):
		"""Create a dict to update header placeholders.

		fits.cfg contains placeholder fields for
		time information, so we generate a dict
		to replace these with actual time info.

		Valid fields:
		* %DATE% - start date (eg, 2012Jan01).
		* %START% - start time, in yearseconds.
		* %STOP% - stop time, in yearseconds.
		"""
		tf = {}
		tf['%DATE%']  = strftime("%Y%b%d", start_time)
		tf['%START%'] = self._to_yrsec(start_time)
		tf['%STOP%']  = self._to_yrsec(stop_time)
		return tf

	def _to_yrsec (self, utc):
		"""Convert a utc time struct to yearseconds.

		time.gmtime() returns a time.struct_time.
		IDL likes yrsecs, so we convert to those.

		time.struct_time - the date as a 9-tuple.
		yrsecs - num seconds since start of year.
		"""
		yrsec = (utc.tm_yday - 1) * 86400
		yrsec += utc.tm_hour * 3600
		yrsec += utc.tm_min * 60
		yrsec += utc.tm_sec
		return yrsec

	@abstractmethod
	def _make_data_hdu (self, data):
		"""Construct an HDU data section."""
		pass

