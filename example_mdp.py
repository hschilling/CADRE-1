""" Optimization of the CADRE MDP."""

from __future__ import print_function

import numpy as np

from openmdao.core.mpi_wrap import MPI
from openmdao.core.problem import Problem
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver

try:
    from openmdao.core.petsc_impl import PetscImpl as impl
except ImportError:
    impl = None

from openmdao.solvers.ln_gauss_seidel import LinearGaussSeidel
from openmdao.solvers.petsc_ksp import PetscKSP

from CADRE.CADRE_mdp import CADRE_MDP_Group

# These numbers are for the CADRE problem in the paper.
n = 1500
m = 300
npts = 6
restart = False

# These numbers are for quick testing
#n = 150
#m = 6
#npts = 2


# Instantiate
model = Problem(impl=impl)
root = model.root = CADRE_MDP_Group(n=n, m=m, npts=npts)

# add SNOPT driver
model.driver = pyOptSparseDriver()
model.driver.options['optimizer'] = "SNOPT"
model.driver.opt_settings = {'Major optimality tolerance': 1e-3,
                             'Iterations limit': 500000000,
                             "New basis file": 10}

# Restart File
if restart is True and os.path.exists("fort.10"):
    model.driver.opt_settings["Old basis file"] = 10

# Add parameters and constraints to each CADRE instance.
names = ['pt%s' % i for i in range(npts)]
for i, name in enumerate(names):

    # add parameters to driver
    model.driver.add_desvar("%s.CP_Isetpt" % name, low=0., high=0.4)
    model.driver.add_desvar("%s.CP_gamma" % name, low=0, high=np.pi/2.)
    model.driver.add_desvar("%s.CP_P_comm" % name, low=0., high=25.)
    model.driver.add_desvar("%s.iSOC" % name, indices=[0], low=0.2, high=1.)

    model.driver.add_constraint('%s.ConCh'% name, upper=0.0)
    model.driver.add_constraint('%s.ConDs'% name, upper=0.0)
    model.driver.add_constraint('%s.ConS0'% name, upper=0.0)
    model.driver.add_constraint('%s.ConS1'% name, upper=0.0)
    model.driver.add_constraint('%s_con5.val'% name, equals=0.0)

# Add Parameter groups
model.driver.add_desvar("bp1.cellInstd", low=0., high=1.0)
model.driver.add_desvar("bp2.finAngle", low=0., high=np.pi/2.)
model.driver.add_desvar("bp3.antAngle", low=-np.pi/4, high=np.pi/4)

# Add objective
model.driver.add_objective('obj.val')

# For Parallel exeuction, we must use KSP
model.root.ln_solver = PetscKSP()

# Recording
from openmdao.recorders import DumpRecorder
rec = DumpRecorder(out='data.dmp')
model.driver.add_recorder(rec)
rec.options['includes'] = ['obj.val', '*.ConCh', '*.ConDs', '*.ConS0', '*.ConS1', '*_con*.val']

model.setup()
model.run()


#----------------------------------------------------------------
# Below this line, code I was using for verifying and profiling.
#----------------------------------------------------------------
#profile = False
#params = model.driver.get_desvars().keys()
#unks = model.driver.get_objectives().keys() + model.driver.get_constraints().keys()
#if profile is True:
#    import cProfile
#    import pstats
#    def zzz():
#        for j in range(1):
#            model.run()
#    cProfile.run("model.calc_gradient(params, unks, mode='rev', return_format='dict')", 'profout')
#    #cProfile.run("zzz()", 'profout')
#    p = pstats.Stats('profout')
#    p.strip_dirs()
#    p.sort_stats('cumulative', 'time')
#    p.print_stats()
#    print('\n\n---------------------\n\n')
#    p.print_callers()
#    print('\n\n---------------------\n\n')
#    p.print_callees()
#else:
#    #model.check_total_derivatives()
#    Ja = model.calc_gradient(params, unks, mode='rev', return_format='dict')
#    for key1, value in sorted(Ja.items()):
#        for key2 in sorted(value.keys()):
#            print(key1, key2)
#            print(value[key2])
#    #print(Ja)
#    #Jf = model.calc_gradient(params, unks, mode='fwd', return_format='dict')
#    #print(Jf)
#    #Jf = model.calc_gradient(params, unks, mode='fd', return_format='dict')
#    #print(Jf)
#    import pickle
#    pickle.dump(Ja, open( "mdp_derivs.p", "wb" ))
#
#import pickle
#data = {}
#varlist = []
#picklevars = ['obj.val',
              #'pt0_con1.val', 'pt0_con2.val', 'pt0_con3.val', 'pt0_con4.val', 'pt0_con5.val',
              #'pt1_con1.val', 'pt1_con2.val', 'pt1_con3.val', 'pt1_con4.val', 'pt1_con5.val',
              #]
#for var in picklevars:
    #data[var] = model[var]
#pickle.dump(data, open( "mdp_execute.p", "wb" ))
