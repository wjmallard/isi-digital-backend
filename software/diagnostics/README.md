# Diagnostics Toolkit

Scripts for debugging the ISI correlator during hardware bringup.

## Debugging Checklist

### Board Connectivity

| Check | Tool | Action |
|-------|------|--------|
| Can you reach the board? | `roach_ctrl` | `add_board`, `ping` |

### ADC Subsystem

| Check | Tool | Action |
|-------|------|--------|
| Is the ADC producing data? | `adc_capture_samples.py` | Capture and inspect |
| Is the ADC interleave timing aligned? | `adc_measure_interleave_skew.py` | Adjust via `adc_set_registers.py` |

### Sync Generator

| Check | Tool | Action |
|-------|------|--------|
| Is `sync_gen_period` non-zero? | `roach_ctrl` | `read_int sync_gen_period` |
| Is the sync pulse firing? | `check_sync_generator.py` | Check sync signals |

### XAUI Interconnect

| Check | Tool | Action |
|-------|------|--------|
| Is the XAUI link up? | `xaui_check_link.py` | Check FIFOs, valid |
| Are the cables connected correctly? | `xaui_verify_cable_order.py` | Verify routing matrix |
| Is inter-board timing aligned? | `xaui_tune_delays.py` | Tune loopback/feedback delays |

### Data Flow

| Check | Tool | Action |
|-------|------|--------|
| Are `pkt_ids` increasing? | `roach_ctrl` | `read_int pkt_id` repeatedly |
| Do vaccs match `sync_gen_period`? | `roach_ctrl` | `read_int` to compare values |

## Tool Reference

### `roach_ctrl`

Interactive CLI for controlling ROACH boards. Supports tab completion.

```
$ ./roach_ctrl
roach> add_board isiroach2
roach> ping
```

| Command | Description |
|---------|-------------|
| `add_board HOST` | Connect to a ROACH board |
| `ping` | Check if board responds |
| `list_boards` | Show connected boards |
| `program BOF` | Load a bitstream (.bof file) |
| `deprogram` | Unload the current bitstream |
| `listbof` | List available bitstreams |
| `listdev` | List FPGA registers |
| `read_int REG` | Read a 32-bit register |
| `write_int REG VAL` | Write a 32-bit register |
| `est_brd_clk` | Estimate board clock speed |

### `adc_set_registers.py`

Interactive tool for tuning ADC083000 registers. Drops into IPython.

```
$ ./adc_set_registers.py isiroach2
>>> adc.offset(10, -5)
>>> adc.amplitude(256, 256)
```

| Command | Description |
|---------|-------------|
| `adc.offset(adc0, adc1)` | Set DC offset (-255 to 255, ~0.18mV/step) |
| `adc.amplitude(adc0, adc1)` | Set gain (0-511, 256=nominal 700mVpp) |
| `adc.phase(val)` | Set fine phase for ADC1 (0-511, max 110ps) |
| `adc.test(adc0, adc1)` | Enable test pattern (True/False) |
| `adc.reset_to_defaults()` | Reset all registers to defaults |
