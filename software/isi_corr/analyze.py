#!/usr/bin/env python2.6

import sys
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from IPython import Shell
ipshell = Shell.IPShellEmbed()

DATAFILE = "corr.desc"

def Plot3D (Z):

    fig = plt.figure()
    ax = Axes3D(fig)

    x = np.arange(Z.shape[0])
    y = np.arange(Z.shape[1])
    X,Y = np.meshgrid(x,y)

    ax.plot_wireframe(X, Y, Z.transpose(), rstride=100, cstride=1)
    plt.show()

def Plot2D (Y):
    if type(Y) == list:
        for y in Y:
            plt.plot(y)
    else:
        plt.plot(Y)
    plt.show()

def PlotSegs (Y):
	plt.plot(range(0,24), Y[0:24])
	plt.plot(range(24,48), Y[24:48])
	plt.plot(range(48,64), Y[48:64])
	plt.show()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		datafile = sys.argv[1]
	else:
		datafile = DATAFILE

	try:
		data = np.fromfile(datafile, dtype=np.int32)
	except IOError:
		print "Cannot open file: %s" % datafile
		sys.exit(1)

	spectra = data.reshape(-1,9,64)

	autos_raw = spectra[:,:3,:]
	cross_raw = spectra[:,3:,:]
	cross_one = cross_raw.transpose(0,2,1).reshape(-1,2)
	cross_two = np.array([np.complex(*x) for x in cross_one])

	autos = autos_raw.transpose(1,0,2)
	cross = cross_two.reshape(-1,64,3).transpose(2,0,1)
	cross_pwr = np.abs(cross)
	cross_ang = np.angle(cross)
	cross_aun = np.unwrap(cross_ang)

	xx = autos[0]
	yy = autos[1]
	zz = autos[2]

	xy = cross_pwr[0]
	yz = cross_pwr[1]
	zx = cross_pwr[2]

	xya = cross_ang[0]
	yza = cross_ang[1]
	zxa = cross_ang[2]

	z = cross_aun
	#z = cross_aun[:,:,5:25]
	naxes = len(z)
	nrows = len(z[0])
	ncols = len(z[0][0])
	x = np.arange(ncols)
	s = np.zeros((naxes,nrows))
	for i in xrange(naxes):
		for j in xrange(nrows):
			s[i][j] = np.polyfit(x,z[i][j],1)[0]

	xys = np.average(s[0])
	yzs = np.average(s[1])
	zxs = np.average(s[2])

	ipshell()

