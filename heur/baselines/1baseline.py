import gc
import weakref

import pytest
import inspect


from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os

import pyscipopt as scip


cauctions_instances = {'easy':'test_100_500','medium':'transfer_100_500','hard':'transfer_200_1000','harder':'transfer_300_1500'}
facilities_instances = {'easy':'test_100_100_5','medium':'transfer_100_100_5','hard':'transfer_200_100_5','harder':'transfer_400_100_5'}
indset_instances = {'easy':'test_500_4','medium':'transfer_500_4','hard':'transfer_1000_4','harder':'transfer_1500_4'}
setcover_instances = {'easy':'test_500r_1000c_0.05d','medium':'transfer_500r_1000c_0.05d','hard':'transfer_1000r_1000c_0.05d','harder':'transfer_2000r_1000c_0.05d'}

benchmarks = {'cauctions':cauctions_instances,'facilities':facilities_instances,'indset':indset_instances,'setcover':setcover_instances}

heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']
new_heurs = ['rounding','randrounding','simplerounding']

mode = 'easy'

for benchmark_name,benchmark_data in benchmarks.items():
    path_to_instances = "/home/yyzhou/learn2branch/data/instances/" + benchmark_name + "/" + benchmark_data[mode]
    
    instance_list = os.listdir(path_to_instances)
    
    for instance in instance_list:
        path_to_one_instance = path_to_instances + "/" + instance
    
        for heur in new_heurs:
            log_dir = "/home/yyzhou/LLM4Heur/heur/baselines/logs/" + benchmark_name + "/unsolved/" + heur
            if( not os.path.exists(log_dir) ):
                os.makedirs(log_dir)  
             
            logfile = log_dir + "/" + instance + ".log"

            model = scip.Model("Heuristic_Example")
            model.readProblem(path_to_one_instance)
            model.setLogfile(logfile)

            model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭分离算法
            model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
            
            freq_param = 'heuristics/'+ heur +'/freq'
            freqofs_param = 'heuristics/'+ heur +'/freqofs'
            model.setParam(freq_param,1)
            model.setParam(freqofs_param,0)

            model.setParam('limits/nodes',1)
            model.setParam('limits/totalnodes',1)

            model.hideOutput()
            model.optimize()
        
