# Instrument Control Software

Acquisition controllers that run on a control computer:
1. Configure the ROACH board(s)
2. Start and stop observations
3. Receive observation data
4. Write data to disk in FITS format

## Modes

| Mode | Boards | Directory |
|------|--------|-----------|
| Spectrometer | 1 | `isi_spec/` |
| Correlator | 3 | `isi_corr/` |

## `isi_spec/`

Configures the system in single-board spectrometer mode. Acquires data for a specified observation duration.

| File | Description |
|------|-------------|
| `run_spec.py` | Acquisition controller |
| `spec.cfg` | System config |
| `fits.cfg` | Observation config |
| | |
| `spec/Connection/` | FPGA and CPU comms |
| `spec/ConfigFile/` | Config file parsers |
| `spec/Fits/` | FITS file writer |
| `spec/MainLoopControl.py` | Termination control |

### Control Flow

1. Parse config files
2. Connect to a board
   - KATCP for setting FPGA registers
   - SSH for running fifo_tools on the PowerPC
   - UDP receiver on control computer
3. Start acquisition
   - Reset packet counter
   - Arm for next sync pulse
4. Start data streaming
   - `fifo_tools` firmware streams FPGA BRAMs to control computer
5. Receive UDP packets from board
6. Store data in FITS format

## `isi_corr/`

Configures the system in three-board spectrometer/correlator mode. Acquires data for a specified observation duration.

| File | Description |
|------|-------------|
| `isi_corr.py` | Acquisition controller |
| `corr.cfg` | System and Observation config |
| | |
| `fits.py` | FITS output |
| `analyze.py` | Post-processing |

### Control Flow

**Setup:** `isi_corr.py -p`
1. Connect to all 3 boards
   - KATCP for setting FPGA registers
   - SSH for running fifo_tools on the PowerPC
   - UDP receiver on control computer
2. Program boards with bitstream
3. Configure boards
   - Set board IDs (`corr_id`: 0, 1, 2)
   - Set `sync_period`

**Align:** `isi_corr.py -a`
1. Connect to all 3 boards
2. Measure phase offsets from cross-correlations
3. Reprogram misaligned boards until aligned

**Observe:** `isi_corr.py -r`
1. Connect to all 3 boards
2. Start acquisition
   - Reset packet counter
   - Arm for next sync pulse
3. Start data streaming
   - `fifo_tools` firmware streams FPGA BRAMs to control computer
4. Synchronize UDP streams
   - Advance all 3 streams to same `pkt_id` and `group_id`
5. Receive UDP packets from boards
6. Reorder channels by frequency
7. Store data in FITS format

## `diagnostics/`

Scripts and interactive tools for hardware bringup and debugging, organized as a [checklist by subsystem](diagnostics/README.md) (ADC, sync, XAUI, data flow).

## `tests/`

Python readout and control scripts that pair with the [gateware test benches](../gateware/README.md#tests).
