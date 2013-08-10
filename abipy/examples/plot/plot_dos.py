#!/usr/bin/env python
#
# This example shows how to compute the gaussian DOS from
# the eigenvalues stored in the WFK file.
from abipy import *

import abipy.data as data
import matplotlib.pyplot as plt

# Open the wavefunction file computed with a homogeneous sampling of the BZ 
# and extract the band structure on the k-mesh.
gs_filename = data.ref_file("si_scf_WFK-etsf.nc")

gs_wfk = WFK_File(gs_filename)

gs_ebands = gs_wfk.ebands

# Compute the DOS with the Gaussian method.
width = 0.1
step  = 0.01

edos = gs_ebands.get_edos(method="gaussian", step=step, width=width)

# Plot DOS and IDOS
edos.plot(title="Total IDOS and DOS of Silicon")
