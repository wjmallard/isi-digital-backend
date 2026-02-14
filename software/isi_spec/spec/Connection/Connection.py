"""A network connection manager."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

from abc import ABCMeta, abstractmethod

class Connection ():
	"""A network connection manager.

	Provides:
	* conf - ConfSpec : a configuration file
	* verbose - bool : a verbosity flag
	"""
	__metaclass__ = ABCMeta

	def __init__ (self, conf, verbose=False):
		"""Create a new connection manager."""
		self.conf = conf
		self.verbose = verbose

	@abstractmethod
	def connect (self):
		"""Connect to the remote board."""
		pass

	@abstractmethod
	def disconnect (self):
		"""Disconnect from the remote board."""
		pass

