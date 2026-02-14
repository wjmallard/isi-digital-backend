"""An interface to a FITS configuration file."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
from string import split, strip
#from collections import OrderedDict
from OrderedDict import OrderedDict

from ConfigFile import ConfigFile

class FitsConfigFile (ConfigFile):
	"""An interface to the FITS configuration file."""

	def __init__ (self, cfg_name):
		"""Create a new ConfFits object."""
		# The superclass constructor calls _parse,
		# and _parse() expects header to already
		# exist. So, we create the header before
		# we call the superclass constructor.
		self.header = OrderedDict()
		super(FitsConfigFile, self).__init__(cfg_name)

	def _parse (self, cfg_file):
		"""Parse fields from the FITS config.

		Since the data is already available here,
		we build a FITS header OrderedDict in the
		process, which we'll use later to build a
		header HDU.
		"""
		for section in cfg_file.sections():
			self.header[section] = OrderedDict()

			for key in cfg_file.options(section):

				val_raw = cfg_file.get(section, key)
				value, label = self._parse_cfg_line(val_raw)

				# Add key/value/label to header list.
				self.header[section][key] = (value, label)

				# Store key/value for external use.
				self[key] = value

	def _parse_cfg_line (self, val_raw):
		"""Parse a line from the FITS config.

		Split the value field from a fits.cfg line
		into a value/label pair.
		Coerce the value to an int, float, or str.
		Return a (value, label) tuple.
		"""
		value_str, label = [strip(x) for x in split(val_raw, ':')]
		value = self._infer_type(value_str)
		return (value, label)

