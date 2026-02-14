#!/usr/bin/env python2.6

__author__ = "William Mallard"
__email__ = "wjm@llard.net"
__copyright__ = "Copyright 2011"
__license__ = "GPL"
__status__ = "Development"

import re
import sys

def main ():
	try:
		ndf_name = sys.argv[1]
		ucf_name = sys.argv[2]
	except IndexError:
		print "Usage: %s [ndf] [ucf]" % sys.argv[0]
		sys.exit(1)

	print "*************************"
	print "* ISI Corr Floorplanner *"
	print "*************************"
	print "ndf: %s" % ndf_name
	print "ucf: %s" % ucf_name

	design = extract_design_name(ndf_name)

	print "design: %s" % design
	print

	print "Collecting DSP48E names."
	dsp48s = parse_dsp48_names(ndf_name, design)
	print "Collecting BRAM names."
	brams = parse_bram_names(ndf_name, design)
	print "Collecting register names."
	registers = parse_register_names(ndf_name, design)
	print

	ucf = open(ucf_name, 'w')

	print "Placing DSP48s."

	place_dsp48s(ucf, design, dsp48s, "biplex_real_4x0", "biplex0", (0,44,1,51))
	place_dsp48s(ucf, design, dsp48s, "biplex_real_4x1", "biplex1", (0,36,1,43))
	place_dsp48s(ucf, design, dsp48s, "biplex_real_4x2", "biplex2", (0,28,1,35))
	place_dsp48s(ucf, design, dsp48s, "biplex_real_4x3", "biplex3", (0,20,1,27))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_0", "bf1_0", (2,54,2,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_1", "bf1_1", (2,48,2,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_2", "bf1_2", (2,42,2,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_3", "bf1_3", (2,36,2,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_4", "bf1_4", (2,30,2,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_5", "bf1_5", (2,24,2,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_6", "bf1_6", (2,18,2,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_7", "bf1_7", (2,12,2,17))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_0", "bf2_0", (3,54,3,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_1", "bf2_1", (3,48,3,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_2", "bf2_2", (3,42,3,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_3", "bf2_3", (3,36,3,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_4", "bf2_4", (3,30,3,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_5", "bf2_5", (3,24,3,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_6", "bf2_6", (3,18,3,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_7", "bf2_7", (3,12,3,17))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_0", "bf3_0", (4,54,4,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_1", "bf3_1", (4,48,4,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_2", "bf3_2", (4,42,4,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_3", "bf3_3", (4,36,4,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_4", "bf3_4", (4,30,4,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_5", "bf3_5", (4,24,4,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_6", "bf3_6", (4,18,4,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_7", "bf3_7", (4,12,4,17))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_0", "bf4_0", (5,54,5,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_1", "bf4_1", (5,48,5,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_2", "bf4_2", (5,42,5,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_3", "bf4_3", (5,36,5,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_4", "bf4_4", (5,30,5,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_5", "bf4_5", (5,24,5,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_6", "bf4_6", (5,18,5,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_7", "bf4_7", (5,12,5,17))

	place_dsp48s(ucf, design, dsp48s, "cross_mult_a", "cma", (6,44,7,59))
	place_dsp48s(ucf, design, dsp48s, "cross_mult_b", "cmb", (6,28,7,43))
	place_dsp48s(ucf, design, dsp48s, "cross_mult_c", "cmc", (6,12,7,27))

	place_dsp48s(ucf, design, dsp48s, "vacc_a", "vpa_c", (8,44,9,59))
	place_dsp48s(ucf, design, dsp48s, "vacc_b", "vpb_c", (8,28,9,43))
	place_dsp48s(ucf, design, dsp48s, "vacc_c", "vpc_c", (8,12,9,27))

	place_dsp48s(ucf, design, dsp48s, "sync_gen", "status", (0,0,1,11))

	print "Placing BRAMs."

	place_brams(ucf, design, brams, "biplex_real_4x0", "biplex0", (0,22,1,25))
	place_brams(ucf, design, brams, "biplex_real_4x1", "biplex1", (0,18,1,21))
	place_brams(ucf, design, brams, "biplex_real_4x2", "biplex2", (0,14,1,17))
	place_brams(ucf, design, brams, "biplex_real_4x3", "biplex3", (0,10,1,13))

	place_brams(ucf, design, brams, "butterfly[12]_0", "bf12_0", (2,27,2,29))
	place_brams(ucf, design, brams, "butterfly[12]_1", "bf12_1", (2,24,2,26))
	place_brams(ucf, design, brams, "butterfly[12]_2", "bf12_2", (2,21,2,23))
	place_brams(ucf, design, brams, "butterfly[12]_3", "bf12_3", (2,18,2,20))
	place_brams(ucf, design, brams, "butterfly[12]_4", "bf12_4", (2,15,2,17))
	place_brams(ucf, design, brams, "butterfly[12]_5", "bf12_5", (2,12,2,14))
	place_brams(ucf, design, brams, "butterfly[12]_6", "bf12_6", (2,9,2,11))
	place_brams(ucf, design, brams, "butterfly[12]_7", "bf12_7", (2,6,2,8))

	place_brams(ucf, design, brams, "butterfly[34]_0", "bf34_0", (3,27,3,29))
	place_brams(ucf, design, brams, "butterfly[34]_1", "bf34_1", (3,24,3,26))
	place_brams(ucf, design, brams, "butterfly[34]_2", "bf34_2", (3,21,3,23))
	place_brams(ucf, design, brams, "butterfly[34]_3", "bf34_3", (3,18,3,20))
	place_brams(ucf, design, brams, "butterfly[34]_4", "bf34_4", (3,15,3,17))
	place_brams(ucf, design, brams, "butterfly[34]_5", "bf34_5", (3,12,3,14))
	place_brams(ucf, design, brams, "butterfly[34]_6", "bf34_6", (3,9,3,11))
	place_brams(ucf, design, brams, "butterfly[34]_7", "bf34_7", (3,6,3,8))

	place_brams(ucf, design, brams, "vacc_a[018]", "vpa_l",  (5,24,5,27))
	place_brams(ucf, design, brams, "vacc_a[234]", "vpa_ru", (6,26,6,29))
	place_brams(ucf, design, brams, "vacc_a[567]", "vpa_rl", (6,22,6,25))

	place_brams(ucf, design, brams, "vacc_b[01]",  "vpb_lu", (5,19,5,21))
	place_brams(ucf, design, brams, "vacc_b[8]",   "vpb_ll", (5,14,5,16))
	place_brams(ucf, design, brams, "vacc_b[234]", "vpb_ru", (6,18,6,21))
	place_brams(ucf, design, brams, "vacc_b[567]", "vpb_rl", (6,14,6,17))

	place_brams(ucf, design, brams, "vacc_c[018]", "vpc_l",  (5,8,5,11))
	place_brams(ucf, design, brams, "vacc_c[234]", "vpc_ru", (6,10,6,13))
	place_brams(ucf, design, brams, "vacc_c[567]", "vpc_rl", (6,6,6,9))

	place_brams(ucf, design, brams, "packetizer_a.*bram[189]", "vpa_l")
	place_brams(ucf, design, brams, "packetizer_a.*bram[234]", "vpa_ru")
	place_brams(ucf, design, brams, "packetizer_a.*bram[567]", "vpa_rl")

	place_brams(ucf, design, brams, "packetizer_b.*bram[1]",   "vpb_lu")
	place_brams(ucf, design, brams, "packetizer_b.*bram[89]",  "vpb_ll")
	place_brams(ucf, design, brams, "packetizer_b.*bram[234]", "vpb_ru")
	place_brams(ucf, design, brams, "packetizer_b.*bram[567]", "vpb_rl")

	place_brams(ucf, design, brams, "packetizer_c.*bram[189]", "vpc_l")
	place_brams(ucf, design, brams, "packetizer_c.*bram[234]", "vpc_ru")
	place_brams(ucf, design, brams, "packetizer_c.*bram[567]", "vpc_rl")

	place_brams(ucf, design, brams, "delay_status", "delay_status", (4,0,5,5))

	print "Placing Shared BRAMs."

	place_shared_brams(ucf, design, "packet_a_bram0", "vpa_out")
	place_shared_brams(ucf, design, "packet_a_bram1", "vpa_out", (5,22,5,23))
	place_shared_brams(ucf, design, "packet_b_bram0", "vpb_out")
	place_shared_brams(ucf, design, "packet_b_bram1", "vpb_out", (5,17,5,18))
	place_shared_brams(ucf, design, "packet_c_bram0", "vpc_out")
	place_shared_brams(ucf, design, "packet_c_bram1", "vpc_out", (5,12,5,13))

	print "Placing registers."
	
	place_registers(ucf, design, registers, "snap_status.*register_x0", "status")
	place_registers(ucf, design, registers, "armed_trig.*register_x0", "status", (8,0,19,29))

	ucf.close()

	print
	print "Constraints generated!"

#      _             _  _    ___       
#     | |           | || |  / _ \      
#   __| | ___  _ __ | || |_| (_) | ___ 
#  / _` |/ __|| '_ \|__   _|> _ < / __|
# | (_| |\__ \| |_) |  | | | (_) |\__ \
#  \__,_||___/| .__/   |_|  \___/ |___/
#             | |                      
#             |_|                      

def parse_dsp48_names (ndf, design):
	pattern = ".*\"(.*?dsp48e_inst)\".*"
	return parse_instance_names(ndf, pattern)

def place_dsp48s (ucf, design, dsp48s, substr, pblock, locs=None):
	pre = "INST \"%s_XSG_core_config/%s_XSG_core_config/" % (design, design)
	post = "\" AREA_GROUP = \"%s\";\n" % (pblock)
	ctype = "DSP48"
	place_instances(pre, post, ctype, ucf, design, dsp48s, substr, pblock, locs)

#  _                                 
# | |                                
# | |__   _ __  __ _  _ __ ___   ___ 
# | '_ \ | '__|/ _` || '_ ` _ \ / __|
# | |_) || |  | (_| || | | | | |\__ \
# |_.__/ |_|   \__,_||_| |_| |_||___/

def parse_bram_names (ndf, design):
	pattern = ".*NLW_MACRO_ALIAS \(string \"bmg_.*(%s_x0\/.*/.*r[ao]m\d*/.*?)\"\).*" % (design)
	# NOTE: every netlist has two lines like this,
	#       so we sort and cut every other result.
	return parse_instance_names(ndf, pattern)[::2]

def place_brams (ucf, design, brams, substr, pblock, locs=None):
	pre = "INST \"%s_XSG_core_config/%s_XSG_core_config/" % (design, design)
	post = "/BU2/U0/blk_mem_generator/valid.cstr/ramloop[0].ram.r/v5_init.ram/SP.WIDE_PRIM18.SP\" AREA_GROUP = \"%s\";\n" % (pblock)
	ctype = "RAMB36"
	place_instances(pre, post, ctype, ucf, design, brams, substr, pblock, locs)

#       _                            _   _                                 
#      | |                          | | | |                                
#  ___ | |__    __ _  _ __  ___   __| | | |__   _ __  __ _  _ __ ___   ___ 
# / __|| '_ \  / _` || '__|/ _ \ / _` | | '_ \ | '__|/ _` || '_ ` _ \ / __|
# \__ \| | | || (_| || |  |  __/| (_| | | |_) || |  | (_| || | | | | |\__ \
# |___/|_| |_| \__,_||_|   \___| \__,_| |_.__/ |_|   \__,_||_| |_| |_||___/

def place_shared_brams (ucf, design, name, pblock, locs=None):
	pre = "INST \"%s_%s_ramblk/%s_" % (design, name, design)
	post = "_ramblk/ramb36_0\" AREA_GROUP = \"%s\";\n" % (pblock)
	ctype = "RAMB36"
	place_instances(pre, post, ctype, ucf, design, [name], name, pblock, locs)

#                    _       _                   
#                   (_)     | |                  
#  _ __  ___   __ _  _  ___ | |_  ___  _ __  ___ 
# | '__|/ _ \ / _` || |/ __|| __|/ _ \| '__|/ __|
# | |  |  __/| (_| || |\__ \| |_|  __/| |   \__ \
# |_|   \___| \__, ||_||___/ \__|\___||_|   |___/
#              __/ |                             
#             |___/                              

def parse_register_names (ndf, design):
	pattern = ".*\(instance \(rename .*\"(.*synth_reg_inst.*)\"\).*"
	return parse_instance_names(ndf, pattern)

def place_registers (ucf, design, insts, substr, pblock, locs=None):
	pre = "INST \"%s_XSG_core_config/%s_XSG_core_config/" % (design, design)
	post = "\" AREA_GROUP = \"%s\";\n" % (pblock)
	ctype = "SLICE"
	place_instances(pre, post, ctype, ucf, design, insts, substr, pblock, locs)

#             _            
#            (_)           
#  _ __ ___   _  ___   ___ 
# | '_ ` _ \ | |/ __| / __|
# | | | | | || |\__ \| (__ 
# |_| |_| |_||_||___/ \___|

def extract_design_name (ndf):
	"""
	Deduce the design name from the netlist.

	ndf = name of netlist
	"""
	design = None

	# NOTE: this relies on the existence of an fft.
	pattern = ".*\(instance \(rename (.*)_x0_fft.*"
	match = re.compile(pattern).match

	fd = open(ndf, 'r')
	for line in fd:
		m = match(line)
		if m:
			design = m.group(1)
			break
	fd.close()

	return design

def find_instances (insts, substr):
	"""
	Search a list of instances for substrings.

	insts  = list of instances
	substr = search string
	"""
	pattern = '.*%s.*' % substr
	search = re.compile(pattern).search
	found = [i for i in insts for m in (search(i),) if m]
	return found

def parse_instance_names (ndf, pattern):
	"""
	Search a netlist for instances.

	ndf     = netlist to search
	pattern = pattern to match
	"""
	match = re.compile(pattern).match

	fd = open(ndf, 'r')
	insts = [m.group(1) for l in fd for m in (match(l),) if m]
	fd.close()

	insts.sort()
	return insts

def place_instances (pre, post, ctype, ucf, design, insts, substr, pblock, locs):
	"""
	Generate constraints for specified instances.

	ucf    = constraints file
	design = name of design
	insts  = list of instances
	substr = search string
	pblock = name of pblock
	locs   = (x0,y0,x1,y1)
	"""
	insts = find_instances(insts, substr)

	group = build_instance_group(insts, pre, post)
	ucf.writelines(group)

	if locs:
		place = build_instance_place(pblock, ctype, locs)
		ucf.writelines(place)

def build_instance_group (insts, pre, post):
	"""
	Convert a list of instances into ucf pblock declarations.

	insts = list of instances
	pre   = ucf prefix for this instance type
	post  = ucf suffix for this instance type
	"""
	return ["%s%s%s" % (pre, i, post) for i in insts]

def build_instance_place (pblock, ctype, locs):
	"""
	Generate a ucf pblock placement constraint.

	pblock = name of pblock
	ctype  = type of constraint
	locs   = grid coordinates
	"""
	return "AREA_GROUP \"%s\" RANGE=%s_X%dY%d:%s_X%dY%d;\n" % (pblock, ctype, locs[0], locs[1], ctype, locs[2], locs[3])

if __name__ == "__main__":
	main()

