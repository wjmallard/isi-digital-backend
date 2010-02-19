%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                             %
%   Center for Astronomy Signal Processing and Electronics Research           %
%   http://casper.berkeley.edu                                                %
%   Copyright (C)2009 Billy Mallard                                           %
%                                                                             %
%   This program is free software; you can redistribute it and/or modify      %
%   it under the terms of the GNU General Public License as published by      %
%   the Free Software Foundation; either version 2 of the License, or         %
%   (at your option) any later version.                                       %
%                                                                             %
%   This program is distributed in the hope that it will be useful,           %
%   but WITHOUT ANY WARRANTY; without even the implied warranty of            %
%   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             %
%   GNU General Public License for more details.                              %
%                                                                             %
%   You should have received a copy of the GNU General Public License along   %
%   with this program; if not, write to the Free Software Foundation, Inc.,   %
%   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.               %
%                                                                             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function sync_gen2_init(blk, varargin)
% Initialize and configure a sync generator block.
%
% sync_gen2_init(blk, varargin)
%
% blk = The block to configure.
% varargin = {'varname', 'value', ...} pairs.
%
% Valid varnames for this block are:
% using_pfb_fir = 
% pfb_fir_taps = 
% using_fft = 
% fft_size = 
% fft_inputs = 
% fft_orders = 
% using_ct = 
% ct_type = 
% using_vacc = 
% vacc_length = 

% Declare any default values for arguments you might like.
defaults = {};
if same_state(blk, 'defaults', defaults, varargin{:}), return, end
check_mask_type(blk, 'sync_gen2');
munge_block(blk, varargin{:});

using_pfb_fir = get_var('using_pfb_fir', 'defaults', defaults, varargin{:});
pfb_fir_taps = get_var('pfb_fir_taps', 'defaults', defaults, varargin{:});
using_fft = get_var('using_fft', 'defaults', defaults, varargin{:});
fft_size = get_var('fft_size', 'defaults', defaults, varargin{:});
fft_inputs = get_var('fft_inputs', 'defaults', defaults, varargin{:});
fft_orders = get_var('fft_orders', 'defaults', defaults, varargin{:});
using_ct = get_var('using_ct', 'defaults', defaults, varargin{:});
ct_type = get_var('ct_type', 'defaults', defaults, varargin{:});
using_vacc = get_var('using_vacc', 'defaults', defaults, varargin{:});
vacc_length = get_var('vacc_length', 'defaults', defaults, varargin{:});
using_scale_factor = get_var('using_scale_factor', 'defaults', defaults, varargin{:});
scale_factor = get_var('scale_factor', 'defaults', defaults, varargin{:});

% Validate input fields.

if pfb_fir_taps < 1
    errordlg('sync_gen2: Invalid number of PFB FIR taps. Should be greater than zero.')
end

if fft_size < 1
    errordlg('sync_gen2: Invalid FFT size. Should be greater than zero.')
end

if fft_inputs < 1
    errordlg('sync_gen2: Invalid number of FFT inputs. Should be greater than zero.')
end

if length(fft_orders) < 0
    errordlg('sync_gen2: Invalid number of FFT reorders. Should be non-negative.')
end

if length(vacc_length) < 0
    errordlg('sync_gen2: Invalid vector accumulation length. Should be non-negative.')
end

if length(scale_factor) < 1
    errordlg('sync_gen2: Invalid vector scale factor. Should greater than zero.')
end

% Set default vector length (for designs without FFTs).
vector_length = 1;

% Calculate minimum PFB FIR window.
pfb_fir_window = 1;
if using_pfb_fir == 1
    pfb_fir_window = pfb_fir_taps;
end

% Calculate minimum FFT window.
fft_window = 1;
if using_fft == 1
    vector_length = 2^(fft_size - fft_inputs);
    
    fft_orders_lcm = 1;
    for i = 1:length(fft_orders)
        fft_orders_lcm = lcm(fft_orders_lcm, fft_orders(i));
    end
    fft_window = fft_orders_lcm * vector_length;
end

% Calculate minimum CT window.
ct_window = 1;
if using_ct == 1
    % TODO: Fill this in.
    ct_window = 2;
end

% Calculate minimum VACC window.
vacc_window = 1;
if using_vacc == 1
    vacc_window = vacc_length^2 * vector_length;
end

% Calculate minimum sync period.
sync_period = 1;
sync_period = lcm(sync_period, pfb_fir_window);
sync_period = lcm(sync_period, fft_window);
sync_period = lcm(sync_period, ct_window);
sync_period = lcm(sync_period, vacc_window);
sync_period = sync_period * scale_factor;

% Update diagram parameters.
set_param([blk, '/calculated_period'], 'const', num2str(sync_period));

% Display the sync period under this block.
fmtstr = sprintf('sync_period=%d', sync_period);
set_param(blk, 'AttributesFormatString', fmtstr);

save_state(blk, 'defaults', defaults, varargin{:});

