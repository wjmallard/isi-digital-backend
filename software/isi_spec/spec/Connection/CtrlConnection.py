"""An ssh connection manager."""
__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys
import os
import pwd

import warnings
warnings.filterwarnings("ignore")
import paramiko
warnings.filterwarnings("always")

from Connection import Connection

class CtrlConnection (Connection):
	"""An ssh connection manager.

	Controls software running on the PowerPC.
	"""
	def __init__ (self, *args, **kwargs):
		"""Create a new ssh connection manager."""
		super(CtrlConnection, self).__init__(*args, **kwargs)

		self.ssh = None

		self.is_connected = False
		self.is_streaming = False

	def connect (self):
		"""Connect to the remote board."""
		if self.verbose:
			print "Connecting via ssh."

		try:
			self.ssh = paramiko.SSHClient()
			username = pwd.getpwuid(os.getuid()).pw_name
			self.ssh.load_host_keys(self.conf['hostkeys'] % username)
			self.ssh.connect(self.conf['roach_id'], username='root', password='')
		except paramiko.SSHException as ex:
			print "*** ERROR ***"
			print "Problem with ssh connection:"
			print "--> %s" % ex
			print "Cannot control data streams."
			sys.exit(1)

		self._is_connected = True

	def disconnect (self):
		"""Disconnect from the remote board."""
		if self.verbose:
			print "Disconnecting ssh."

		if self._is_streaming:
			print "WARN: disconnect():"
			print "Currently streaming data."
			print "Shutting down data stream ..."
			self.stop_data_streaming()

		if not self._is_connected:
			print "WARN: disconnect():"
			print "Not connected via ssh."
			return

		self.ssh.close()
		self.ssh = None

		self._is_connected = False

	def start_data_streaming (self):
		"""Initiate data streaming from the remote board."""
		if self.verbose:
			print "Starting data stream."

		if not self._is_connected:
			print "Cannot initiate streaming!"
			print "Not connected via ssh."
			sys.exit(1)

		ssh = self.ssh
		init_stream = self.conf['pushexec']
		local_host = self.conf['rx_addr']
		local_port = self.conf['rx_port']

		cmd = "%s %s %d" % (init_stream, local_host, local_port)
		stdin, stdout, stderr = ssh.exec_command(cmd)

		self._is_streaming = True

	def stop_data_streaming (self):
		"""Terminate data streaming from the remote board."""
		if self.verbose:
			print "Stopping data stream."

		if not self._is_connected:
			print "WARN: stop_data_streaming():"
			print "Not connected via ssh."
			return

		if not self._is_streaming:
			print "WARN: stop_data_streaming():"
			print "Not streaming via ssh."
			return

		ssh = self.ssh
		kill_stream = self.conf['pushkill']
		local_host = self.conf['rx_addr']

		stdin, stdout, stderr = ssh.exec_command(kill_stream)

		self._is_streaming = False

