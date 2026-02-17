# PowerPC Firmware

C code that runs on a ROACH's PowerPC processor to stream data from the FPGA to the control computer.

## Overview

ROACH boards have a Virtex-5 FPGA and a PowerPC CPU. The PowerPC runs embedded Debian, which exposes FPGA BRAMs as files in `/proc`.

On each ROACH, `isi_push` streams data from the FPGA fabric to the control computer:

1. Polls `/proc` for new vector accumulator data
2. Packs data into UDP packets with metadata (`board_id`, `group_id`, `pkt_id`)
3. Sends packets over 1 GbE to the control computer

On the control computer, Python code receives and processes the packets:
- Spectrometer mode: `software/isi_spec/isi_spec.py`
- Correlator mode: `software/isi_corr/isi_corr.py`

Data is stored on the server in FITS format.

## `fifo_tools/`

| File | Description |
|------|-------------|
| `isi_push.c` | Stream data from FPGA to server |
| `libfpga.c/h` | FPGA utility library |
| `libwrap.c/h` | Socket wrappers |
| `Makefile` | Cross-compile for PowerPC |
| | |
| **Local** | |
| `fifo_cat.c` | Read FPGA FIFO → hexdump to stdout |
| `fifo_dump.c` | Read FPGA FIFO → write to file |
| | |
| **Network** | |
| `fifo_tx.c` | Read FPGA FIFO → send over UDP |
| `fifo_rx.c` | Receive UDP → write to file |

## Usage

Cross-compile for PowerPC, rsync to the board, and run:

```
$ isi_push 192.168.1.100 50000
```

This streams correlator data to the specified host and port.
