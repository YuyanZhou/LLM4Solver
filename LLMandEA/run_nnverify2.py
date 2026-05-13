
from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os

import pyscipopt as scip
import os
import sys

import random


ind = int(sys.argv[1])
ind_total = int(sys.argv[2])

seed = int(sys.argv[3])
random.seed(seed)

confs = [3, 5, 7, 0, 3, 3, 4]

heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']

DIVING_IND = 4

name = "nnverify"
names = ["cauctions","facilities","indset","setcover","miplib","loadbalance","nnverify"]


ds = ["valid50"]

for t in ds:

    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    instance_list.sort()

    num = int( len(instance_list) / ind_total )

    start = (ind-1)*num
    end = ind * num if ind < ind_total else len(instance_list)


    for instance in instance_list[start:end]:
        print(instance)
        print(confs)
        path_to_one_instance = path_to_instances + "/" + instance

        log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/nnverify/scipsolved/"+t+"/seed" + str(seed)
        if( not os.path.exists(log_dir) ):
            os.makedirs(log_dir)

        logfile = log_dir + "/" + instance + ".log"

        model = scip.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        model.setParam('limits/time', 900)
        
        for conf,heur in zip(confs,heurs):
            freq_param = 'heuristics/'+ heur +'/freq'
            freqofs_param = 'heuristics/'+heur+'/freqofs'

            default_freq = model.getParam(freq_param)
            if(default_freq == -1):
                default_freq = 1
            default_freqofs = model.getParam(freqofs_param)

            id1 = conf % 4
            id2 = int(conf/4)

            if id1==0:
                model.setParam(freq_param,-1)
            elif id1==1:
                model.setParam(freq_param,int(default_freq/2))
            elif id1==2:
                model.setParam(freq_param,int(default_freq))
            else:
                model.setParam(freq_param,int(default_freq*2))
            
            if id2==0:
                model.setParam(freqofs_param,0)
            else:
                model.setParam(freqofs_param,default_freqofs)

        # turn off the other diving heur
        
        

        model.hideOutput()
        # before optimize, check /home/yyzhou/scipoptsuite-9.0.0/scip/src/scip/scipdefplugins.c
        model.optimize()

