
from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os

import pyscipopt as scip
import os
import sys

name = sys.argv[1]

names = ["cauctions","facilities","indset","setcover","miplib","loadbalance"]

assert(name in names)

# cauctions_instances = {'easy':'test_100_500','medium':'transfer_100_500','hard':'transfer_200_1000','harder':'transfer_300_1500'}
# facilities_instances = {'easy':'test_100_100_5','medium':'transfer_100_100_5','hard':'transfer_200_100_5','harder':'transfer_400_100_5'}
# indset_instances = {'easy':'test_500_4','medium':'transfer_500_4','hard':'transfer_1000_4','harder':'transfer_1500_4'}
# setcover_instances = {'easy':'test_500r_1000c_0.05d','medium':'transfer_500r_1000c_0.05d','hard':'transfer_1000r_1000c_0.05d','harder':'transfer_2000r_1000c_0.05d'}

# benchmarks = {'cauctions':cauctions_instances,'facilities':facilities_instances,'indset':indset_instances,'setcover':setcover_instances}
# new_benmark1 = {'indset':indset_instances}
# new_benmark2 = {'setcover':setcover_instances}

# heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']

# mode = 'easy'
heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']
# ds = ["train","train1","train10","train50", "test", "transfer1", "transfer2", "transfer3"]
ds = ["valid"]

for t in ds:

    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    for instance in instance_list:
        print(t)
        path_to_one_instance = path_to_instances + "/" + instance
        log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/" + name + "/solved/" + t  
        if( not os.path.exists(log_dir) ):
            os.makedirs(log_dir)

        logfile = log_dir + "/" + instance + ".log"

        model = scip.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        if name == "loadbalance":
            model.setParam('limits/time', 900)
        else:
            model.setParam('limits/time', 3600)


        model.hideOutput()
        # before optimize, check /home/yyzhou/scipoptsuite-9.0.0/scip/src/scip/scipdefplugins.c
        model.optimize()

        if name == "loadbalance":
            primal_dual_integral = model.getPrimalDualIntegral()
            data_dir = "/home/yyzhou/LLM4Heur/heur/logfile/integral/" + name + "/" + t 
            if( not os.path.exists(data_dir) ):
                os.makedirs(data_dir)
            data_path = data_dir + "/integral.txt"
            integral_info = instance + ":" + str(primal_dual_integral) +"\n"
            with open(data_path, 'a') as file:
                file.write(integral_info)
