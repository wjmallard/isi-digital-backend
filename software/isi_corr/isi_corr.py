#!/usr/bin/env python2.6

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2010"
__license__ = "GPL"
__status__ = "Development"

import fcntl, os, pwd, socket, sys, time
from corr import katcp_wrapper as katcp
from time import gmtime
from ConfigParser import ConfigParser, Error
import numpy as np

import warnings
warnings.filterwarnings("ignore")
import paramiko
warnings.filterwarnings("always")

CFG_FILE = 'corr.cfg'

START_BIN = 5
STOP_BIN = 25

pktfmt = np.dtype \
([ 
	('board_id', '>u1'),
	('group_id', '>u1'),
	('unused', '>u2'),
	('pkt_id', '>u4'),
	('payload', '>i4', 5*(72+1)),
])

class ic_opts ():
	def __init__ (self, args):
		self.args = args

		self.verbose          = False
		self.program_boards   = False
		self.configure_boards = False
		self.reset_pktids     = False
		self.align_phases     = False
		self.measure_power    = False
		self.measure_phase    = False
		self.to_temp_file     = False

		self.parse()

	def parse (self):
		for arg in self.args[1:]:
			self.args.remove(arg)
			if arg == "-h":
				self.print_usage()
				sys.exit(0)
			elif arg == "-v":
				self.verbose = True
			if arg == "-p":
				self.program_boards = True
			elif arg == "-c":
				self.configure_boards = True
			elif arg == "-r":
				self.reset_pktids = True
			elif arg == "-a":
				self.align_phases = True
			elif arg == "-l":
				self.measure_power = True
			elif arg == "-i":
				self.measure_phase = True
			elif arg == "-t":
				self.to_temp_file = True
			else:
				print "Unrecognized flag: %s" % arg
				self.print_usage()
				sys.exit(1)

	def print_usage (self):
		print "Usage: %s [options]" % self.args[0]
		print "Options:"
		print "  -h  Display this information"
		print "  -v  Verbose mode"
		print "  -p  Program boards"
		print "  -c  Configure boards"
		print "  -r  Reset packet counters"
		print "  -a  Align interboard phases"
		print "  -l  Measure ADC power levels"
		print "  -i  Measure interboard phases"
		print "  -t  Write fits data to temp file"

class ic_conf ():
	def __init__ (self, cfg_file):
		config = ConfigParser()

		opened = config.read(cfg_file)
		if opened != [cfg_file]:
			print "Cannot find config file."
			sys.exit(1)

		try:
			self.samp_rate = config.getint('fits', 'samp_rate')
			self.int_time  = config.getfloat('fits', 'int_time')
			self.duration  = config.getfloat('fits', 'duration')

			self.board_names = config.get('fpga', 'board_names').split(',')
			self.bitstream   = config.get('fpga', 'bitstream')

			self.bindport = config.getint('system', 'bindport')
			self.pushexec = config.get('system', 'pushexec')
			self.pushkill = config.get('system', 'pushkill')
			self.hostkeys = config.get('system', 'hostkeys')
		except Error as ex:
			print "Error in %s:" % cfg_file
			print "--> %s" % ex.message
			sys.exit(1)

		# Derived values:
		self.clk_freq = self.samp_rate / 16.
		self.sync_period = int(self.int_time * self.clk_freq * 1e6)
		self.num_integrations = int(self.duration / self.int_time)

		# TODO: Validate these derived values.

class ic_conn_fpga ():
	"""The fpga control connection (via katcp)."""

	def __init__ (self, verbose=False):
		self.conns = []
		self.names = []
		self.verbose = verbose

	def connect (self, names):
		'''Connect to boards via katcp.'''

		if self.verbose:
			print "Connecting to boards via katcp."

		# Create a new katcp connection.
		for name in names:
			self.conns += [katcp.FpgaClient(name, 7147)]
			self.names += [name]
		time.sleep(.1)

		# Make sure we can ping each board.
		broken = []

		for (name, conn) in zip(names, self.conns):
			try:
				conn.ping()
			except KatcpClientError:
				broken += [name]

		if len(broken) > 0:
			print "*** ERROR ***"
			print "Unreachable boards:"
			for name in broken:
				print " * %s" % name
				print "Are they powered on?"
				print "Are they on the roach subnet?"
				system.exit(1)

	def disconnect (self):
		self.conns = []

	def program_boards (self, conf, targets=[], quit=True):
		'''Program ROACH boards with the specified bitstream.'''

		if self.verbose:
			print "Programming boards: %s" % conf.bitstream

		boards = []
		if len(targets) == 0:
			boards = self.conns
		else:
			for target in targets:
				boards += [self.conns[target]]

		for board in boards:
			board.progdev(conf.bitstream)
		time.sleep(.1)

		self.configure_boards(conf)
		self.reset_pktid_counters()

		if quit:
			sys.exit(0)

	def configure_boards (self, conf):
		'''Configure registers on boards.'''

		if self.verbose:
			print "Configuring boards."

		broken = []

		for (conn, name, corr_id) in zip(self.conns, conf.board_names, range(3)):
			try:
				conn.write_int('corr_id', corr_id)
				conn.write_int('sync_gen_period', conf.sync_period)
			except RuntimeError:
				broken += [name]

		if len(broken) > 0:
			print "*** ERROR ***"
			print "Boards missing some registers:"
			for name in broken:
				print " * %s" % name
			print "Have they been programmed yet?"
			sys.exit(1)

	def reset_pktid_counters (self):
		'''Reset pkt_id counters.'''

		if self.verbose:
			print "Resetting pkt_id counters."

		for conn in self.conns:
			conn.write_int('control', 0)
		for conn in self.conns:
			conn.write_int('control', 1)

	def sample_register (self, reg_name, n_samp, targets=[]):
		boards = []
		if len(targets) == 0:
			boards = self.conns
		else:
			for target in targets:
				boards += [self.conns[target]]
		n_boards = len(boards)

		samps = np.zeros((n_boards, n_samp))

		for (i, board) in zip(xrange(n_boards), boards):
			for j in xrange(n_samp):
				samps[i][j] = board.read_int(reg_name)

		return samps

class ic_conn_ctrl ():
	"""The data control connection (via ssh)."""

	def __init__ (self, verbose=False):
		self.conns = []
		self.iface = None
		self.verbose = verbose

	def connect (self, conf):
		'''Connect to boards via ssh.'''

		if self.verbose:
			print "Connecting to boards via ssh."

		broken = []

		for name in conf.board_names:
			try:
				ssh = paramiko.SSHClient()
				username = pwd.getpwuid(os.getuid()).pw_name
				ssh.load_host_keys(conf.hostkeys % username)
				ssh.connect(name, username='root', password='')
				self.conns += [ssh]
			except paramiko.SSHException:
				broken += [name]

		if len(broken) > 0:
			print "*** ERROR ***"
			print "Problem with ssh connection:"
			for name in broken:
				print " * %s" % name
			print "Cannot control data streams."
			for conn in self.conns:
				conn.close()
			sys.exit(1)

		self.iface = ssh.get_transport().sock.getsockname()[0]

	def disconnect (self):
		'''Terminate board ssh connections.'''

		for ssh in self.conns:
			ssh.close()
		self.conns = []
		self.iface = None

	def start_data_streaming (self, conf):
		'''Initiate data streaming.'''

		for (i, conn, name) in zip(range(3), self.conns, conf.board_names):
			cmd = "%s %s %d" % (conf.pushexec, self.iface, conf.bindport+i)
			stdin, stdout, stderr = conn.exec_command(cmd)
			if self.verbose:
				print "%s --> %s" % (name, self.iface)

	def stop_data_streaming (self, conf):
		'''Terminate data streaming.'''

		for (conn, name) in zip(self.conns, conf.board_names):
			stdin, stdout, stderr = conn.exec_command(conf.pushkill)
			if self.verbose:
				print "%s -\> %s" % (name, self.iface)

class ic_conn_data ():
	"""The data connection (via tcp)."""

	def __init__ (self, verbose=False):
		self.host = None
		self.port = [None]*3
		self.sock = [None]*3
		self.verbose = verbose

		self.pktbufs = [np.zeros(1, dtype=pktfmt),
						np.zeros(1, dtype=pktfmt),
						np.zeros(1, dtype=pktfmt)]

	def connect (self, conn_ctrl, conf):
		'''Open local data receiving port.'''

		self.host = conn_ctrl.iface
		for i in xrange(3):
			self.port[i] = conf.bindport + i
			self.sock[i] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock[i].bind((self.host, self.port[i]))
			self.sock[i].settimeout(1)

	def disconnect (self):
		'''Close local data receiving port.'''

		for i in xrange(3):
			self.sock[i].close()

def display_power (conn_fpga):
	'''Display power levels sampled from ADC.'''

	names = conn_fpga.names
	samps = conn_fpga.sample_register('sample_adc', 1000)

	print "Power levels:"
	for (n, s) in zip(names, samps):
		print " * %s = [%d, %d]" % (n, min(s), max(s))

	sys.exit(0)

def display_phase (conn_ctrl, conn_data, conf):
	phase = measure_phase(conn_ctrl, conn_data, conf)

	print "Interboard phases:"
	print " * AB = %+f clks" % phase[0]
	print " * BC = %+f clks" % phase[1]
	print " * CA = %+f clks" % phase[2]

	sys.exit(0)

def align_phases (conn_fpga, conn_data, conf):
	while True:
		phase_raw = measure_phase(conn_ctrl, conn_data, conf, verbose=False)
		phase = np.round(phase_raw).astype(np.int32)

		print "Phases: [%+3d] [%+3d] [%+3d]" % (phase[0], phase[1], phase[2])

		matched = np.nonzero(phase == 0)[0]
		num_matched = len(matched)
		targets = []
		if num_matched == 0:
			# All three boards are unaligned,
			# so arbitrarily reprogram Y and Z.
			targets = [1, 2]
			print "Resetting boards B and C."
		elif num_matched == 1:
			# Two boards are aligned,
			# so reprogram the third.
			targ_id = matched[0]
			targets = [targ_id]
			print "Resetting board %s." % ('A','B','C')[targ_id]
		elif num_matched == 2:
			# All three boards are as close to
			# aligned as they're going to get.
			print "The boards are as close to being aligned as they are going to get."
		elif num_matched == 3:
			# All three boards are aligned.
			print "All boards are aligned."
			break
		else:
			print "Something is seriously wrong. Aborting!"
			sys.exit(1)

		conn_fpga.program_boards(conf, targets, quit=False)

	sys.exit(0)

def measure_phase (conn_ctrl, conn_data, conf, verbose=True):
	(time, stat, spec) = receive_data(conn_ctrl, conn_data, conf, 50)
	if len(spec) == 0:
		print "Not receiving packets. Aborting phase measurement."

	phase = calculate_phase(spec)

	return phase

def calculate_phase (spectra):
	cross_raw = spectra[:,3:,:]
	cross_one = cross_raw.transpose(0,2,1).reshape(-1,2)
	cross_two = np.array([np.complex(*x) for x in cross_one])
	cross = cross_two.reshape(-1,64,3).transpose(2,0,1)
	cross_ang = np.angle(cross)
	cross_aun = np.unwrap(cross_ang)

	z = cross_aun[:,:,START_BIN:STOP_BIN]
	naxes = len(z)
	nrows = len(z[0])
	ncols = len(z[0][0])
	x = np.arange(ncols)
	s = np.zeros((naxes,nrows))
	for i in xrange(naxes):
		for j in xrange(nrows):
			s[i][j] = np.polyfit(x,z[i][j],1)[0]

	slope = np.average(s, axis=1)
	phase = 64*slope/np.pi

	return phase

def sync_data_streams (conn_data):
	"""Advance data streams to the same pkt_id and group_id."""

	X = conn_data.sock[0]
	Y = conn_data.sock[1]
	Z = conn_data.sock[2]

	A = conn_data.pktbufs[0]
	B = conn_data.pktbufs[1]
	C = conn_data.pktbufs[2]

	X.recv_into(A)
	Y.recv_into(B)
	Z.recv_into(C)

	a = A['pkt_id']
	b = B['pkt_id']
	c = C['pkt_id']
	t = max(a,b,c)

	# Advance streams to latest pkt_id.
	advance_stream(X, A, 'pkt_id', t)
	advance_stream(Y, B, 'pkt_id', t)
	advance_stream(Z, C, 'pkt_id', t)

	# Advance streams to latest group_id.
	advance_stream(X, A, 'group_id', 2)
	advance_stream(Y, B, 'group_id', 5)
	advance_stream(Z, C, 'group_id', 8)

def advance_stream (conn, buf, field, target):
	"""Advance a sequential packet stream.

	Receive packets from conn into buf
	until buf[field] matches target."""

	while buf[field] < target:
		conn.recv_into(buf)

def recv_data_streams (conn_data, num_pkts, verbose=False):
	if verbose:
		print "Receiving %d packets." % num_pkts

	X = conn_data.sock[0]
	Y = conn_data.sock[1]
	Z = conn_data.sock[2]

	pkts = np.zeros((num_pkts, 9, 1), dtype=pktfmt)

	for count in xrange(num_pkts):
		pktbuf = pkts[count]
		try:
			X.recv_into(pktbuf[0])
			X.recv_into(pktbuf[1])
			X.recv_into(pktbuf[2])
			Y.recv_into(pktbuf[3])
			Y.recv_into(pktbuf[4])
			Y.recv_into(pktbuf[5])
			Z.recv_into(pktbuf[6])
			Z.recv_into(pktbuf[7])
			Z.recv_into(pktbuf[8])
		except socket.timeout:
			print "Unexpectedly stopped receiving packets."
			break

	if verbose:
		print "Received %d packets." % (count+1)
		print "Shutting down."

	return pkts

def cleanup_data_streams (pkts, num_pkts):
	pids = pkts['pkt_id'][:,:,0]
	data = pkts['payload']

	final_pid_measured = pids[-1]
	final_pid_expected = pids[0] + (num_pkts - 1) * np.ones(9, dtype=np.int32)

	pkts_dropped = False
	for (m, e) in zip(final_pid_measured, final_pid_expected):
		if m != e:
			pkts_dropped = True

	#from IPython import Shell
	#Shell.IPShellEmbed()()

	if pkts_dropped:
		print "ERROR: Dropped some packets!"
		print final_pid_measured

	# TODO: Fill in.

	raw_data = data
	return raw_data

def descramble_data_streams (raw_data):
	x = raw_data.reshape(-1,9,5,73)
	stat = x[:,2::3,:,-1].transpose(0,2,1).reshape(-1,3)
	spec = x[:,:8,:,:-1].reshape(-1,8,5,9,8).transpose(0,2,3,1,4).reshape(-1,9,64)
	return (stat, spec)

def receive_data (conn_ctrl, conn_data, conf, num_ints, verbose=False):
	# There are five integrations per packet.
	num_pkts = num_ints / 5

	conn_ctrl.connect(conf)
	conn_data.connect(conn_ctrl, conf)
	conn_ctrl.start_data_streaming(conf)

	time_start = gmtime()

	print "Capturing %.2fs of data." % conf.duration

	sync_data_streams(conn_data)
	pkts = recv_data_streams(conn_data, num_pkts, verbose=verbose)

	time_stop = gmtime()

	conn_ctrl.stop_data_streaming(conf)
	conn_data.disconnect()
	conn_ctrl.disconnect()

	raw_data = cleanup_data_streams(pkts, num_pkts)
	(stat, data) = descramble_data_streams(raw_data)

	return ((time_start, time_stop), stat, data)

if __name__ == "__main__":
	opts = ic_opts(sys.argv)
	conf = ic_conf(CFG_FILE)
	conn_fpga = ic_conn_fpga(verbose=True)
	conn_ctrl = ic_conn_ctrl(verbose=False)
	conn_data = ic_conn_data(verbose=False)

	verbose = opts.verbose

	print "******************************"
	print "*** ISI Correlator Control ***"
	print "******************************"

	conn_fpga.connect(conf.board_names)
	if opts.program_boards:
		conn_fpga.program_boards(conf)
	if opts.configure_boards:
		conn_fpga.configure_boards(conf)
	if opts.measure_power:
		display_power(conn_fpga)
	if opts.measure_phase:
		display_phase(conn_ctrl, conn_data, conf)
	if opts.reset_pktids:
		conn_fpga.reset_pktid_counters()
	if opts.align_phases:
		align_phases(conn_fpga, conn_data, conf)

	(time, stat, spec) = receive_data(conn_ctrl, conn_data, conf, conf.num_integrations, verbose=verbose)
	if len(spec) == 0:
		print "Received zero packets!"
		print "Are the boards programmed?"
		print "Are the boards configured?"

	print "Writing data as binary."
	datafile = open('data.numpy', 'w')
	spec.tofile(datafile)
	datafile.close()

	#statfile = open('stat.numpy', 'w')
	#stat.tofile(statfile)
	#statfile.close()

	print "Writing data as fits."
	from fits import IsiCorrFits
	IsiCorrFits(time, stat, spec, temp=opts.to_temp_file)

