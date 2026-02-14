"""An interface to a configuration file."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
from abc import ABCMeta, abstractmethod

from ConfigParser import ConfigParser, Error

class ConfigFile (dict):
	"""An interface to a configuration file.

	An abstract base class providing:
	* filename - str : name of config file

	Provides dictionary access to fields parsed
	from a config file with ConfigParser.
	"""
	__metaclass__ = ABCMeta

	def __init__ (self, cfg_name):
		"""Create a new Conf object."""
		dict.__init__(self)

		self.filename = cfg_name

		cfg_file = self._open(cfg_name)
		self._parse(cfg_file)

	def _open (self, cfg_name):
		"""Open a config file; return a ConfigParser."""
		config = ConfigParser()
		opened = config.read(cfg_name)
		if opened != [cfg_name]:
			print "Cannot find config file: %s." % filename
			sys.exit(1)
		return config

	@abstractmethod
	def _parse (self, cfg_file):
		"""Parse config file fields."""
		pass

	def _infer_type (self, value_str):
		"""Infer the type of a config value.

		Try to infer the type of a config value.
		If it's not an int, then we try a float;
		if it's not a float, then we assume it's
		a string.
		"""
		for cast in [int, float, str]:
			try:
				value = cast(value_str)
				break
			except ValueError:
				continue

		return value
