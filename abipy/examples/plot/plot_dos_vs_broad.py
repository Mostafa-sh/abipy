#!/usr/bin/env python
#
# This example shows how to compute and plot several
# gaussian DOS by varying the broadening parameters.
from abipy import *

import abipy.data as data
import matplotlib.pyplot as plt

# Open the wavefunction file computed with a homogeneous sampling of the BZ 
# and extract the band structure on the k-mesh.
gs_filename = data.ref_file("si_scf_WFK-etsf.nc")

gs_wfk = WFK_File(gs_filename)

gs_bands = gs_wfk.ebands

# Compute the DOS with the Gaussian method.
# Plot bands and DOS.
widths = [0.1, 0.2, 0.3]
step = 0.1

plotter = ElectronDosPlotter()

for width in widths:
   edos = gs_bands.get_edos(method="gaussian", step=step, width=width)
   label="$\sigma = %s$ [eV]" % width
   plotter.add_edos(label, edos)

plotter.plot()
