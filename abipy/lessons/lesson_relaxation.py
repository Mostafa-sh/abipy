#!/usr/bin/env python
"""
Template for lessons: paragraph with a brief description of the lesson separated by a blank line from the text below.

Detailed description of the tutorial (goals, step-by-step description of the operations to be performed)
Users will import this module to access the public API. Each module should provide a help method
that prints this doc string. One of more factory functions (make_flow, make_convergence_flow ...)
that build and return a subclass of abilab.Flow. The Flow subclass provides a `analyze` method 
that performs the post-processing of the results and produces the final results (matplotlib plots, pandas dataframes, ...)
Users should be able to run the tutorial either via this script, or interactively inside ipython or ipython notebooks
The working directory of the flow should be named: flow_[name_of_the_lesson][_extra_info] so that each 
lesson will be done in different directories.

Example::

\033[91m Title\033[0m

\033[94m Background\033[0m

\033[94m The related abinit variables\033[0m

\033[1m ionmov \033[0m
\033[1m optcell \033[0m
\033[1m dilatmx \033[0m
\033[1m ecutsm \033[0m
\033[1m ntime \033[0m

\033[94m The abipy flows in this lesson\033[0m

\033[94m The cource of this lesson\033[0m

Start this lesson by importing it in a new namespace:

\033[92m In []:\033[0m from abipy.lessons import lesson_relaxation as lesson

As always you can reread this lessons text using the command:

\033[92m In []:\033[0m lesson.help()

To build the flow:

\033[92m In []:\033[0m flow = lesson.make_flow()

To print the input files

\033[92m In []:\033[0m flow.show_inputs()

Start the flow with the scheduler and wait for completion.

\033[92m In []:\033[0m flow.make_scheduler().start()

To analyze the results.

\033[92m In []:\033[0m flow.analyze()
"""
from __future__ import division, print_function

import sys
import os
import shutil
import numpy as np
import abipy.abilab as abilab
import abipy.data as abidata
from abipy.core import Structure
from pymatgen.io.abinitio.eos import EOS
from abipy.lessons.lesson_helper_functions import abinit_help

def help(stream=sys.stdout):
    """
    Display the tutorial text.
    """
    stream.write(__doc__)


def get_local_copy():
    """
    Copy this script to the current working dir to explore and edit
    """
    dst = os.path.basename(__file__[:-1])
    if os.path.exists(dst):
        raise RuntimeError("file %s already exists. Remove it before calling get_local_copy" % dst)
    shutil.copyfile(__file__[:-1], dst)


class RelaxGaNFlow(abilab.Flow):
    def analyze(self):
        with abilab.GsrRobot.open(self) as robot:
            data = robot.get_dataframe()
            robot.pairplot(x_vars="nkpts", y_vars=["a", "volume"]) #, hue="tsmear")

            #grid = sns.PairGrid(data, x_vars="nkpts", y_vars=["a", "volume"]) #, hue="tsmear")
            #grid.map(plt.plot, marker="o")
            #grid.add_legend()
            #plt.show()

class RelaxSiFlow(abilab.Flow):
    def analyze(self):
        etotals = self.read_etotals(unit="eV")
        volumes = self.volumes
        num_sites = self.structure.num_sites

        eos_fit = EOS.DeltaFactor().fit(self.volumes/num_sites, etotals/num_sites)

        eos_fit.plot()


def make_relax_gan_flow():
    # Structural relaxation for different k-point samplings.
    ngkpt_list = [[2,2,2],[4,4,4],[6,6,6]]
    inp = abilab.AbiInput(pseudos=abidata.pseudos("31ga.pspnc", "7n.pspnc"),ndtset=len(ngkpt_list))
    inp.set_structure(abidata.cif_file("gan2.cif"))

    # Global variables
    inp.set_variables(
        ecut=10,
        tolvrs=1e-10,
        optcell=2,
        ionmov=3,
        ntime=50,
        dilatmx=1.05,
        ecutsm=0.5,
    )

    for i,ngkpt in enumerate(ngkpt_list):
      inp[i+1].set_kmesh(ngkpt=ngkpt, shiftk=[0,0,0])

    return RelaxGaNFlow.from_inputs("flow_gan_relax", inputs=inp.split_datasets(), task_class=abilab.RelaxTask)


def make_relax_si_flow():
    # Structural relaxation for different k-point samplings.
    scale_volumes = np.arange(94, 108, 2) / 100.

    inp = abilab.AbiInput(pseudos=abidata.pseudos("14si.pspnc"),ndtset=len(scale_volumes))

    structure = Structure.from_file("si.cif")

    # Global variables
    inp.set_variables(
        ecut=10,
        tolvrs=1e-10,
        optcell=2,
        ionmov=3,
        ntime=50,
        dilatmx=1.05,
        ecutsm=0.5,
    )

    inp.set_kmesh(ngkpt=[2, 2, 2], shiftk=[0, 0, 0])

    for idt,scal_vol in enumerate(scale_volumes):
        new_lattice = structure.lattice.scale(structure.volume*scal_vol)

        new_structure = Structure(new_lattice, structure.species, structure.frac_coords)

        inp[idt+1].set_structure(new_structure)

    return RelaxGaNFlow.from_inputs("flow_si_relax", inputs=inp.split_datasets(), task_class=abilab.RelaxTask)



if __name__ == "__main__":
    flow = make_relax_gan_flow()

    #flow.show_inputs()
    flow.make_scheduler().start()
    flow.analyze()
