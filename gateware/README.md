# FPGA Gateware

Simulink models and HDL for the ISI correlator FPGA design, targeting the Xilinx Virtex-5 on ROACH boards.

## Signal Path

This section traces data streams through the Simulink design, with block names and data types at each stage.

### ADC Interface

Data enters the FPGA through the `adc083000x2` yellow block, which provides a single interface for two interleaved ADC cards with 16:1 demux:
- 16 parallel data samples per FPGA clock cycle, as `signed_8_7` (8-bit signed, 7 fractional bits)
- 8 sync bits

The sync bits from each ADC are OR'd together to detect if the one pulse per second (1pps) signal was high at any point during an FPGA clock cycle.

### Synchronization

Three blocks coordinate timing across the system:

**`sync_gen`** — Produces a periodic sync pulse with period set by the `sync_gen_period` register. This pulse triggers integration boundaries and is referenced by most downstream blocks.

**`armed_trigger`** — Synchronizes the three ROACH boards. Armed by a rising edge of the `control` register's LSB. Once armed, triggers on any of the four `adc0_sync` bits going high (limiting temporal resolution to one FPGA clock cycle). Emits a single pulse from `trig_out` that resets `sync_gen`, `pre_xaui`, and `packetizer`.

**`snap_status`** — Integrates four status bits (`adc0_sync`, `adc1_sync`, `aux0_clk`, `aux1_clk`) over each sync period. If any bit goes high, it stays high until the next sync pulse latches the accumulated status into an output register. The latched bits are included in output packets.

### F-Engine

ADC samples are cast from `signed_8_7` to `signed_18_17`. The `fft_wideband_real` block performs a streaming 128-point FFT, taking 128 real samples (16 samples per clock × 8 clocks) and producing 64 complex frequency channels (8 channels per clock × 8 clocks).

The FFT produces 8 parallel complex outputs (18-bit real + 18-bit imaginary) representing 64 frequency channels, with a full spectrum every 8 clock cycles.

The quantizer reduces FFT output from 18 bits to 4 bits per component using unbiased rounding (round to nearest even) and symmetric saturation (clamp to ±7 to avoid negative bias).

### Board Interconnect

The `clump` block packs 8 channels into groups of 3 (padded with a dummy 9th channel) for XAUI transmission. Data is buffered and transmitted with a 3/8 duty cycle to stay within the 10 Gbps link capacity.

The `resync` block uses the sync pulse to realign incoming XAUI data with the local FPGA clock domain. The `unclump` block then unpacks the data for the X-engine.

### X-Engine

Cross-multiplication produces 9 correlation terms per channel (3 autos + 6 cross products). The `vacc` (vector accumulator) integrates these over the sync period, storing results in double-buffered BRAMs for readout.

### Readout

Each `vacc` writes integrated data into a double-buffered BRAM. While the FPGA fills one half, the PowerPC reads the other via `/proc` and streams it as UDP packets to a server.

---

## Structure

### models/

Main correlator designs in Simulink (CASPER toolflow):

| File | Description |
|------|-------------|
| `isi_correlator.mdl` | **Main correlator design** |
| `isi_correlator_lib.mdl` | Shared library blocks |
| `isi_correlator_tvg.mdl` | Correlator with test vector generator |
| |
| `*_init.m` | Mask init scripts |
| `xaui_interconnect_fsm.txt` | Interconnect routing and state machine notes |

### tests/

Test benches for individual components and subsystems. Python scripts for control and readout are in `software/tests/`.

| Model | Readout | Description |
|-------|---------|-------------|
| **Synchronization** | | |
| `test_synced_cntr.mdl` | Simulation | Sync pulse-aligned counter |
| `test_integral_cntr.mdl` | Simulation | Integration period-aligned counter |
| `test_pos_extend.mdl` | Simulation | Pulse stretcher |
| `test_sync_gen2.mdl` | `roach_ctrl` | Sync pulse generator |
| `test_arm_sync.mdl` | `roach_ctrl` | Arm/sync timing |
| | | |
| **ADC** | | |
| `test_adc083000x2.mdl` | `test_adc083000x2.py` | Read ADC data |
| `test_adc_ctrl.mdl` | `test_adc_ctrl.py` | Set ADC registers |
| | | |
| **F-Engine** | | |
| `test_downshift.mdl` | Simulation | PFB output scaling |
| `test_scale.mdl` | Simulation | Equalizer component |
| `test_equalizer.mdl` | Simulation | FFT output scaling |
| `demo_fengine.mdl` | `demo_fengine.py` | **F-engine subsystem** |
| | | |
| **Packetization** | | |
| `test_9x8_strobe.mdl` | Simulation | Packetizer timing |
| `test_clump.mdl` | Simulation | Data packing |
| `test_resync.mdl` | Simulation | Stream resync |
| `test_unclump.mdl` | Simulation | Data unpacking |
| `test_clump_resync_unclump.mdl` | Simulation | End-to-end packetization |
| | | |
| **Board Interconnect** | | |
| `test_tvg.mdl` | `test_tvg.py` | Test vector generator |
| `test_capture.mdl` | `test_capture.py` | Multi-BRAM readout |
| `xaui_loop.mdl` | `roach_ctrl` | XAUI echo server |
| `xaui_switch.mdl` | `roach_ctrl` | XAUI routing matrix |
| `test_sync_rx_get.mdl` | Simulation | Align incoming XAUI data |
| `test_xaui_delay.mdl` | `roach_ctrl` | Tune XAUI interconnect delay |
| `demo_interconnect.mdl` | `demo_interconnect.py` | **Board interconnect subsystem** |
| | | |
| **X-Engine** | | |
| `test_vacc.mdl` | `roach_ctrl` | Vector accumulator |
| `demo_xengine.mdl` | `demo_xengine.py` | **X-engine subsystem** |

### floorplanning/

Scripts for DSP48E and BRAM placement on the FPGA fabric, to meet timing at 360 MHz:

| File | Description |
|------|-------------|
| `ic_planner.py` | Placement constraints (coarse) |
| `ic_v16_fp3.py` | Placement constraints (granular) |

## Build Process

The CASPER toolflow compiles Simulink models to bitstreams (`.bof` files) that run on a ROACH board.
