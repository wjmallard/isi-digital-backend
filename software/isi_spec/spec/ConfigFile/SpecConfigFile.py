"""An interface to a spectrometer configuration file."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys

from ConfigParser import Error

from ConfigFile import ConfigFile

class SpecConfigFile (ConfigFile):
	"""An interface to the spectrometer configuration file."""

	def __init__ (self, cfg_name, fits_conf):
		"""Create a new ConfSpec object."""
		super(SpecConfigFile, self).__init__(cfg_name)
		self._fill_from_fits_config(fits_conf)

	def _parse (self, cfg_file):
		"""Parse fields from the spectrometer config.

		Turn key/value pairs from the config file
		into key/value pairs in the ConfSpec dict.
		"""
		for section in cfg_file.sections():
			for key in cfg_file.options(section):
				value_str = cfg_file.get(section, key)
				self[key] = self._infer_type(value_str)

	def _fill_from_fits_config (self, fits_conf):
		"""Add relevant fields from the FITS config.

		Augment the ConfSpec dict with necessary
		settings copied or derived from ConfFits.
		"""
		duration = fits_conf['duration']
		int_time = fits_conf['tint']
		clk_freq = fits_conf['samrat'] * 1e6 / 16
		num_integrations = int(duration / int_time)

		self['roach_id'] = fits_conf['roach_id']
		self['duration'] = duration
		self['sync_gen_period'] = int(int_time * clk_freq)
		# Each packet contains 5 integrations:
		self['max_packets'] = num_integrations / 5

