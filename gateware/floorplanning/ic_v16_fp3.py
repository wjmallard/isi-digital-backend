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

	# butterfly1

	place_dsp48s(ucf, design, dsp48s, "butterfly1_0.*/cadd_",                 "bf1_0_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_0.*/csub_",                 "bf1_0_as", (2,58,2,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_0.*/cmult_.*/dsp48e_[23]/", "bf1_0_23", (2,56,2,57))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_0.*/cmult_.*/dsp48e_[01]/", "bf1_0_01", (2,54,2,55))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_1.*/cadd_",                 "bf1_1_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_1.*/csub_",                 "bf1_1_as", (2,52,2,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_1.*/cmult_.*/dsp48e_[23]/", "bf1_1_23", (2,50,2,51))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_1.*/cmult_.*/dsp48e_[01]/", "bf1_1_01", (2,48,2,49))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_2.*/cadd_",                 "bf1_2_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_2.*/csub_",                 "bf1_2_as", (2,46,2,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_2.*/cmult_.*/dsp48e_[23]/", "bf1_2_23", (2,44,2,45))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_2.*/cmult_.*/dsp48e_[01]/", "bf1_2_01", (2,42,2,43))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_3.*/cadd_",                 "bf1_3_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_3.*/csub_",                 "bf1_3_as", (2,40,2,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_3.*/cmult_.*/dsp48e_[23]/", "bf1_3_23", (2,38,2,39))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_3.*/cmult_.*/dsp48e_[01]/", "bf1_3_01", (2,36,2,37))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_4.*/cadd_",                 "bf1_4_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_4.*/csub_",                 "bf1_4_as", (2,34,2,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_4.*/cmult_.*/dsp48e_[23]/", "bf1_4_23", (2,32,2,33))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_4.*/cmult_.*/dsp48e_[01]/", "bf1_4_01", (2,30,2,31))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_5.*/cadd_",                 "bf1_5_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_5.*/csub_",                 "bf1_5_as", (2,28,2,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_5.*/cmult_.*/dsp48e_[23]/", "bf1_5_23", (2,26,2,27))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_5.*/cmult_.*/dsp48e_[01]/", "bf1_5_01", (2,24,2,25))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_6.*/cadd_",                 "bf1_6_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_6.*/csub_",                 "bf1_6_as", (2,22,2,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_6.*/cmult_.*/dsp48e_[23]/", "bf1_6_23", (2,20,2,21))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_6.*/cmult_.*/dsp48e_[01]/", "bf1_6_01", (2,18,2,19))

	place_dsp48s(ucf, design, dsp48s, "butterfly1_7.*/cadd_",                 "bf1_7_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly1_7.*/csub_",                 "bf1_7_as", (2,16,2,17))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_7.*/cmult_.*/dsp48e_[23]/", "bf1_7_23", (2,14,2,15))
	place_dsp48s(ucf, design, dsp48s, "butterfly1_7.*/cmult_.*/dsp48e_[01]/", "bf1_7_01", (2,12,2,13))

	# butterfly2

	place_dsp48s(ucf, design, dsp48s, "butterfly2_0.*/cadd_",                 "bf2_0_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_0.*/csub_",                 "bf2_0_as", (3,58,3,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_0.*/cmult_.*/dsp48e_[23]/", "bf2_0_23", (3,56,3,57))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_0.*/cmult_.*/dsp48e_[01]/", "bf2_0_01", (3,54,3,55))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_1.*/cadd_",                 "bf2_1_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_1.*/csub_",                 "bf2_1_as", (3,52,3,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_1.*/cmult_.*/dsp48e_[23]/", "bf2_1_23", (3,50,3,51))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_1.*/cmult_.*/dsp48e_[01]/", "bf2_1_01", (3,48,3,49))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_2.*/cadd_",                 "bf2_2_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_2.*/csub_",                 "bf2_2_as", (3,46,3,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_2.*/cmult_.*/dsp48e_[23]/", "bf2_2_23", (3,44,3,45))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_2.*/cmult_.*/dsp48e_[01]/", "bf2_2_01", (3,42,3,43))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_3.*/cadd_",                 "bf2_3_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_3.*/csub_",                 "bf2_3_as", (3,40,3,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_3.*/cmult_.*/dsp48e_[23]/", "bf2_3_23", (3,38,3,39))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_3.*/cmult_.*/dsp48e_[01]/", "bf2_3_01", (3,36,3,37))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_4.*/cadd_",                 "bf2_4_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_4.*/csub_",                 "bf2_4_as", (3,34,3,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_4.*/cmult_.*/dsp48e_[23]/", "bf2_4_23", (3,32,3,33))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_4.*/cmult_.*/dsp48e_[01]/", "bf2_4_01", (3,30,3,31))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_5.*/cadd_",                 "bf2_5_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_5.*/csub_",                 "bf2_5_as", (3,28,3,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_5.*/cmult_.*/dsp48e_[23]/", "bf2_5_23", (3,26,3,27))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_5.*/cmult_.*/dsp48e_[01]/", "bf2_5_01", (3,24,3,25))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_6.*/cadd_",                 "bf2_6_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_6.*/csub_",                 "bf2_6_as", (3,22,3,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_6.*/cmult_.*/dsp48e_[23]/", "bf2_6_23", (3,20,3,21))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_6.*/cmult_.*/dsp48e_[01]/", "bf2_6_01", (3,18,3,19))

	place_dsp48s(ucf, design, dsp48s, "butterfly2_7.*/cadd_",                 "bf2_7_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly2_7.*/csub_",                 "bf2_7_as", (3,16,3,17))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_7.*/cmult_.*/dsp48e_[23]/", "bf2_7_23", (3,14,3,15))
	place_dsp48s(ucf, design, dsp48s, "butterfly2_7.*/cmult_.*/dsp48e_[01]/", "bf2_7_01", (3,12,3,13))

	# butterfly3

	place_dsp48s(ucf, design, dsp48s, "butterfly3_0.*/cadd_",                 "bf3_0_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_0.*/csub_",                 "bf3_0_as", (4,58,4,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_0.*/cmult_.*/dsp48e_[23]/", "bf3_0_23", (4,56,4,57))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_0.*/cmult_.*/dsp48e_[01]/", "bf3_0_01", (4,54,4,55))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_1.*/cadd_",                 "bf3_1_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_1.*/csub_",                 "bf3_1_as", (4,52,4,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_1.*/cmult_.*/dsp48e_[23]/", "bf3_1_23", (4,50,4,51))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_1.*/cmult_.*/dsp48e_[01]/", "bf3_1_01", (4,48,4,49))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_2.*/cadd_",                 "bf3_2_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_2.*/csub_",                 "bf3_2_as", (4,46,4,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_2.*/cmult_.*/dsp48e_[23]/", "bf3_2_23", (4,44,4,45))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_2.*/cmult_.*/dsp48e_[01]/", "bf3_2_01", (4,42,4,43))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_3.*/cadd_",                 "bf3_3_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_3.*/csub_",                 "bf3_3_as", (4,40,4,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_3.*/cmult_.*/dsp48e_[23]/", "bf3_3_23", (4,38,4,39))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_3.*/cmult_.*/dsp48e_[01]/", "bf3_3_01", (4,36,4,37))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_4.*/cadd_",                 "bf3_4_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_4.*/csub_",                 "bf3_4_as", (4,34,4,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_4.*/cmult_.*/dsp48e_[23]/", "bf3_4_23", (4,32,4,33))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_4.*/cmult_.*/dsp48e_[01]/", "bf3_4_01", (4,30,4,31))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_5.*/cadd_",                 "bf3_5_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_5.*/csub_",                 "bf3_5_as", (4,28,4,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_5.*/cmult_.*/dsp48e_[23]/", "bf3_5_23", (4,26,4,27))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_5.*/cmult_.*/dsp48e_[01]/", "bf3_5_01", (4,24,4,25))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_6.*/cadd_",                 "bf3_6_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_6.*/csub_",                 "bf3_6_as", (4,22,4,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_6.*/cmult_.*/dsp48e_[23]/", "bf3_6_23", (4,20,4,21))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_6.*/cmult_.*/dsp48e_[01]/", "bf3_6_01", (4,18,4,19))

	place_dsp48s(ucf, design, dsp48s, "butterfly3_7.*/cadd_",                 "bf3_7_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly3_7.*/csub_",                 "bf3_7_as", (4,16,4,17))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_7.*/cmult_.*/dsp48e_[23]/", "bf3_7_23", (4,14,4,15))
	place_dsp48s(ucf, design, dsp48s, "butterfly3_7.*/cmult_.*/dsp48e_[01]/", "bf3_7_01", (4,12,4,13))

	# butterfly4

	place_dsp48s(ucf, design, dsp48s, "butterfly4_0.*/cadd_",                 "bf4_0_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_0.*/csub_",                 "bf4_0_as", (5,58,5,59))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_0.*/cmult_.*/dsp48e_[23]/", "bf4_0_23", (5,56,5,57))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_0.*/cmult_.*/dsp48e_[01]/", "bf4_0_01", (5,54,5,55))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_1.*/cadd_",                 "bf4_1_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_1.*/csub_",                 "bf4_1_as", (5,52,5,53))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_1.*/cmult_.*/dsp48e_[23]/", "bf4_1_23", (5,50,5,51))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_1.*/cmult_.*/dsp48e_[01]/", "bf4_1_01", (5,48,5,49))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_2.*/cadd_",                 "bf4_2_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_2.*/csub_",                 "bf4_2_as", (5,46,5,47))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_2.*/cmult_.*/dsp48e_[23]/", "bf4_2_23", (5,44,5,45))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_2.*/cmult_.*/dsp48e_[01]/", "bf4_2_01", (5,42,5,43))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_3.*/cadd_",                 "bf4_3_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_3.*/csub_",                 "bf4_3_as", (5,40,5,41))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_3.*/cmult_.*/dsp48e_[23]/", "bf4_3_23", (5,38,5,39))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_3.*/cmult_.*/dsp48e_[01]/", "bf4_3_01", (5,36,5,37))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_4.*/cadd_",                 "bf4_4_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_4.*/csub_",                 "bf4_4_as", (5,34,5,35))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_4.*/cmult_.*/dsp48e_[23]/", "bf4_4_23", (5,32,5,33))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_4.*/cmult_.*/dsp48e_[01]/", "bf4_4_01", (5,30,5,31))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_5.*/cadd_",                 "bf4_5_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_5.*/csub_",                 "bf4_5_as", (5,28,5,29))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_5.*/cmult_.*/dsp48e_[23]/", "bf4_5_23", (5,26,5,27))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_5.*/cmult_.*/dsp48e_[01]/", "bf4_5_01", (5,24,5,25))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_6.*/cadd_",                 "bf4_6_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_6.*/csub_",                 "bf4_6_as", (5,22,5,23))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_6.*/cmult_.*/dsp48e_[23]/", "bf4_6_23", (5,20,5,21))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_6.*/cmult_.*/dsp48e_[01]/", "bf4_6_01", (5,18,5,19))

	place_dsp48s(ucf, design, dsp48s, "butterfly4_7.*/cadd_",                 "bf4_7_as")
	place_dsp48s(ucf, design, dsp48s, "butterfly4_7.*/csub_",                 "bf4_7_as", (5,16,5,17))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_7.*/cmult_.*/dsp48e_[23]/", "bf4_7_23", (5,14,5,15))
	place_dsp48s(ucf, design, dsp48s, "butterfly4_7.*/cmult_.*/dsp48e_[01]/", "bf4_7_01", (5,12,5,13))

	place_dsp48s(ucf, design, dsp48s, "cross_mult_a", "cma", (6,44,7,59))
	place_dsp48s(ucf, design, dsp48s, "cross_mult_b", "cmb", (6,28,7,43))
	place_dsp48s(ucf, design, dsp48s, "cross_mult_c", "cmc", (6,12,7,27))

	place_dsp48s(ucf, design, dsp48s, "vacc_a", "vpa_c", (8,44,9,59))
	place_dsp48s(ucf, design, dsp48s, "vacc_b", "vpb_c", (8,28,9,43))
	place_dsp48s(ucf, design, dsp48s, "vacc_c", "vpc_c", (8,12,9,27))

	place_dsp48s(ucf, design, dsp48s, "sync_gen", "status", (0,0,1,11))

	print "Placing BRAMs."

	place_brams(ucf, design, brams, "biplex_real_4x0.*reorder_even", "biplex0_l")
	place_brams(ucf, design, brams, "biplex_real_4x1.*reorder_even", "biplex1_l")
	place_brams(ucf, design, brams, "biplex_real_4x2.*reorder_even", "biplex2_l")
	place_brams(ucf, design, brams, "biplex_real_4x3.*reorder_even", "biplex3_l")

	place_brams(ucf, design, brams, "biplex_real_4x0.*reorder_odd",  "biplex0_l", (0,22,0,25))
	place_brams(ucf, design, brams, "biplex_real_4x1.*reorder_odd",  "biplex1_l", (0,18,0,21))
	place_brams(ucf, design, brams, "biplex_real_4x2.*reorder_odd",  "biplex2_l", (0,14,0,17))
	place_brams(ucf, design, brams, "biplex_real_4x3.*reorder_odd",  "biplex3_l", (0,10,0,13))

	place_brams(ucf, design, brams, "biplex_real_4x0.*reorder_out",  "biplex0_r", (1,22,1,25))
	place_brams(ucf, design, brams, "biplex_real_4x1.*reorder_out",  "biplex1_r", (1,18,1,21))
	place_brams(ucf, design, brams, "biplex_real_4x2.*reorder_out",  "biplex2_r", (1,14,1,17))
	place_brams(ucf, design, brams, "biplex_real_4x3.*reorder_out",  "biplex3_r", (1,10,1,13))

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

