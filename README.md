# ISI Digital Spectrometer/Correlator

A real-time FX correlator for the Infrared Spatial Interferometer (ISI) at [Mount Wilson Observatory](https://www.mtwilson.edu/).

Designed and built by William Mallard at the UC Berkeley [Space Sciences Laboratory](https://www.ssl.berkeley.edu/), Townes Lab, 2009–2011.

## Design

A wideband FX correlator built on three [CASPER](https://casper-astro.github.io/) [ROACH](https://casper.berkeley.edu/wiki/ROACH) boards (Xilinx Virtex-5), each running identical gateware: a polyphase filter bank, a streaming 128-point FFT, 10 Gbps board interconnect, and a cross-correlation engine. The three boards digitize signals from three telescopes at 5.76 GSps each, processing a combined 138 Gbps data stream in real time to produce correlated power spectra across 64 spectral channels.

See the [Architecture Document](docs/ARCHITECTURE.md) for full details.

## Optimization

In 2010, the CASPER [DSP library](https://github.com/casper-astro/mlib_devel/) had only been used up to FPGA clock rates around 200 MHz. The ISI correlator needed a clock rate of 360 MHz. I achieved this 1.8× speed-up by redesigning the library's core DSP blocks around high-speed Virtex-5 DSP48E primitives, fixing timing bottlenecks throughout the FFT pipeline, and manually constraining logic placement on the FPGA fabric.

Throughout the process, I contributed [my optimizations](https://github.com/casper-astro/mlib_devel/commits?author=wjmallard) upstream to the CASPER `mlib_devel` library, where they benefited other radio astronomy projects built on the platform. I also documented my floorplanning methodology in [CASPER Memo #42](https://casper.berkeley.edu/wiki/Speed_Optimization_with_PlanAhead).

See the [Optimization Document](docs/OPTIMIZATION.md) for full details.

## Science

The ISI had been tracking apparent size fluctuations in [Betelgeuse](https://en.wikipedia.org/wiki/Betelgeuse) for [over 15 years](https://doi.org/10.1086/309049), but it couldn't determine whether the star itself was pulsating or if its dust shell was changing. The existing system measured total power across a 2.7 GHz band centered at 27 THz (11 µm, mid-infrared) — lumping together all molecules in the star and dust shell. My correlator split this 2.7 GHz band into 60 usable spectral channels, resolving individual molecular signatures and making it possible to disentangle the star from the dust.

Published in [Wishnow et al. 2010](https://doi.org/10.1117/12.857656).

## Structure

| Directory | Contents |
|-----------|----------|
| [`docs/`](docs/) | [Architecture](docs/ARCHITECTURE.md) and [Optimization](docs/OPTIMIZATION.md) writeups |
| [`gateware/`](gateware/) | Simulink models and HDL for the FPGA design |
| [`firmware/`](firmware/) | C code for PowerPC data streaming |
| [`software/`](software/) | Python instrument control and data acquisition |
