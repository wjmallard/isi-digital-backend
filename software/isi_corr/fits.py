#!/usr/bin/env python2.6

import pyfits, os, errno
from time import gmtime, strftime
from ConfigParser import ConfigParser, Error
import numpy as np

class IsiCorrFits ():
	def __init__ (self, time, stat, spec, temp=False):
		self.temp = temp
		self.parse_config("corr.cfg")
		hdu = self.construct_hdu(time, stat, spec)
		self.write_to_file(time, hdu)

	def parse_config (self, cfg_name):
		# Open config file.
		config = ConfigParser()
		opened = config.read(cfg_name)
		if opened != [cfg_name]:
			print "Cannot find config file."
			sys.exit(1)

		# Parse config file.
		try:
			self.obsrvrs   = config.get('fits', 'obsrvrs')
			self.source    = config.get('fits', 'source')
			self.chan_bw   = config.getfloat('fits', 'chan_bw')
			self.samp_rate = config.getint('fits', 'samp_rate')
			self.int_time  = config.getfloat('fits', 'int_time')
			self.data_dir  = config.get('fits', 'data_dir')
		except Error as ex:
			print "Error in %s:" % cfg_name
			print "--> %s" % ex.message
			sys.exit(1)

	def construct_hdu (self, time, stat, spec):
		date = strftime("%Y%b%d", time[0])
		yrsec1 = self._to_yrsec(time[0])
		yrsec2 = self._to_yrsec(time[1])
		time = np.arange(len(spec))

		# Create primary header HDU.
		head_hdu = pyfits.PrimaryHDU()
		head_hdu.header.update('obsrvrs', self.obsrvrs, 'Observers')
		head_hdu.header.update('source', self.source, 'source name')
		head_hdu.header.update('utdate', date, 'YYYYMmmDD')
		head_hdu.header.update('yrsec1', yrsec1, 'start yearsec')
		head_hdu.header.update('yrsec2', yrsec2, 'end yearsec')
		head_hdu.header.update('chbw', self.chan_bw, 'channel bandwidth in MHz')
		head_hdu.header.update('samrat', self.samp_rate, 'sample rate in MHz')
		head_hdu.header.update('tint', self.int_time, 'integration time in s')
		head_hdu.header.add_blank('OBSERVING SETUP', before='obsrvrs')
		head_hdu.header.add_blank('ROACH SETUP', before='chbw')

		# Create primary data table HDU.
		data_tbl = []
		data_tbl += [pyfits.Column(name='time',   format='J',   array=time, unit='seconds')]
		data_tbl += [pyfits.Column(name='status', format='3J',  array=stat)]
		data_tbl += [pyfits.Column(name='AA',     format='64J', array=spec[:,0])]
		data_tbl += [pyfits.Column(name='BB',     format='64J', array=spec[:,1])]
		data_tbl += [pyfits.Column(name='CC',     format='64J', array=spec[:,2])]
		data_tbl += [pyfits.Column(name='ABr',    format='64J', array=spec[:,3])]
		data_tbl += [pyfits.Column(name='ABi',    format='64J', array=spec[:,4])]
		data_tbl += [pyfits.Column(name='BCr',    format='64J', array=spec[:,5])]
		data_tbl += [pyfits.Column(name='BCi',    format='64J', array=spec[:,6])]
		data_tbl += [pyfits.Column(name='CAr',    format='64J', array=spec[:,7])]
		data_tbl += [pyfits.Column(name='CAi',    format='64J', array=spec[:,8])]
		data_hdu = pyfits.new_table(data_tbl)

		# Construct a Header and Data Unit (HDU).
		hdu = pyfits.HDUList([head_hdu, data_hdu])

		return hdu

	def write_to_file (self, time, hdu):
		if self.temp:
			outdir = "."
			fitspath = "./data.fits"
		else:
			datestamp = strftime("%Y%b%d", time[0])
			timestamp = str(self._to_yrsec(time[0]))

			outdir = "%s/%s/%s" % (self.data_dir, datestamp, self.source)
			fitspath = "%s/%s.fits" % (outdir, timestamp)

		# Create output directory.
		try:
			os.makedirs(outdir)
		except OSError as ex:
			if ex.errno == errno.EEXIST: pass
			else: raise

		# Remove output file, if it exists.
		try: os.remove(fitspath)
		except OSError as ex:
			if ex.errno == errno.ENOENT: pass
			else: raise

		hdu.writeto(fitspath)
		hdu.close()

	def _to_yrsec (self, utc):
		yrsec = (utc.tm_yday-1)*86400
		yrsec += utc.tm_hour*3600
		yrsec += utc.tm_min*60
		yrsec += utc.tm_sec
		return yrsec

