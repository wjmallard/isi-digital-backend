#!/usr/bin/env python2.6
"""Client for running the ISI Digital Spectrometer."""

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Production"

import sys

from spec.CmdLineOptions import CmdLineOptions
from spec.ConfigFile.FitsConfigFile import FitsConfigFile
from spec.ConfigFile.SpecConfigFile import SpecConfigFile
from spec.Fits.SpecFits import SpecFits
from spec.MainLoopControl import MainLoopControl
from spec.Connection.FpgaConnection import FpgaConnection
from spec.Connection.CtrlConnection import CtrlConnection
from spec.Connection.DataConnection import DataConnection

SPEC_CFG = "spec.cfg"
FITS_CFG = "fits.cfg"

# Parse command line arguments,
# and load configuration files.
opts = CmdLineOptions(sys.argv)
conf_fits = FitsConfigFile(FITS_CFG)
conf_spec = SpecConfigFile(SPEC_CFG, conf_fits)
main_loop = MainLoopControl(conf_spec, verbose=True)

# Create a FITS data file.
fits = SpecFits(conf_fits, temp=opts.to_temp_file)

# Configure network links.
conn_fpga = FpgaConnection(conf_spec, verbose=opts.verbose)
conn_ctrl = CtrlConnection(conf_spec, verbose=opts.verbose)
conn_data = DataConnection(conf_spec, verbose=opts.verbose)

# Connect FPGA network link.
conn_fpga.connect()
if opts.program_fpga:
	conn_fpga.program_fpga()
	conn_fpga.disconnect()
	sys.exit(0)

# Connect other network links.
conn_ctrl.connect()
conn_data.connect()
conn_ctrl.start_data_streaming()

# Configure remote devices.
conn_fpga.reset_pktid_counter()
conn_data.wait_for_pktid_reset()

# Receive data.
main_loop.start()
while main_loop.is_running():
	conn_data.recv_packet()

# Write data to disk.
data = conn_data.unpack_data()
t_start = main_loop.start_time
t_stop = main_loop.stop_time
fits.write(data, t_start, t_stop, conf_spec)

# Disconnect network links.
conn_ctrl.stop_data_streaming()
conn_data.disconnect()
conn_ctrl.disconnect()
conn_fpga.disconnect()

