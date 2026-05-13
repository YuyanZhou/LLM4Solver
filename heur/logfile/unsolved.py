import gc
import weakref

import pytest
import inspect


from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os
import sys
import pyscipopt as scip

name = sys.argv[1]

names = ["cauctions","facilities","indset","setcover","miplib","loadbalance","nnverify"]

assert(name in names)

# cauctions_instances = {'easy':'test_100_500','medium':'transfer_100_500','hard':'transfer_200_1000','harder':'transfer_300_1500'}
# facilities_instances = {'easy':'test_100_100_5','medium':'transfer_100_100_5','hard':'transfer_200_100_5','harder':'transfer_400_100_5'}
# indset_instances = {'easy':'test_500_4','medium':'transfer_500_4','hard':'transfer_1000_4','harder':'transfer_1500_4'}
# setcover_instances = {'easy':'test_500r_1000c_0.05d','medium':'transfer_500r_1000c_0.05d','hard':'transfer_1000r_1000c_0.05d','harder':'transfer_2000r_1000c_0.05d'}

# benchmarks = {'cauctions':cauctions_instances,'facilities':facilities_instances,'indset':indset_instances,'setcover':setcover_instances}

# heurs = ['myheur3diving','coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']
# heurs = ['coef2diving','frac2diving','linesearch2diving','pscost2diving','veclen2diving']
# heurs = ['feaspump','rounding']
# heurs = ['objpscostdiving','rootsoldiving']
# mode = 'easy'

# ds = ["train","test", "transfer1", "transfer2", "transfer3"]
# ds = ["transfer1", "transfer2", "transfer3"]
heurs = ['myheur3diving']
ds = ["train20"]

for t in ds:

    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    for instance in instance_list:
        print(t)
        path_to_one_instance = path_to_instances + "/" + instance

        for heur in heurs:
            log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/" + name + "/unsolved/" + t + "/" +heur
            if( not os.path.exists(log_dir) ):
                os.makedirs(log_dir)  
                
            logfile = log_dir + "/" + instance + ".log"

            model = scip.Model("Heuristic_Example")
            model.readProblem(path_to_one_instance)
            model.setLogfile(logfile)

            model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # close cutting planes
            model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)

            if(heur == "coef2diving"):
                model.includeCoef2diving()
            elif(heur == "frac2diving"):
                model.includeFrac2diving()
            elif(heur == "pscost2diving"):
                model.includePscost2diving()
            elif(heur == "linesearch2diving"):
                model.includeLinesearch2diving()
            elif(heur == "veclen2diving"):
                model.includeVeclen2diving()
            elif(heur == "myheurdiving"):
                model.includeMyheurdiving()
            elif(heur == "myheur3diving"):
                model.includeMyheur3diving()
                        
            freq_param = 'heuristics/'+ heur +'/freq'
            freqofs_param = 'heuristics/'+ heur +'/freqofs'
            model.setParam(freq_param,1)
            model.setParam(freqofs_param,0)

            model.setParam('limits/nodes',1)
            model.setParam('limits/totalnodes',1)

            model.setParam('limits/time', 360)

            model.hideOutput()
            model.optimize()    
        
