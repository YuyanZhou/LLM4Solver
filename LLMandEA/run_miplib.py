
from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os

import pyscipopt as scip
import os
import sys

import random

seed = 3
random.seed(seed)

ind = int(sys.argv[1])
ind_total = int(sys.argv[2])

DIVING_IND = 4

name = "miplib"
names = ["cauctions","facilities","indset","setcover","miplib","loadbalance"]


ds = ["train"]

for t in ds:

    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    instance_list.sort()

    num = int( len(instance_list) / ind_total )

    start = (ind-1)*num
    end = ind * num if ind < ind_total else len(instance_list)

    my_diving = '''
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if not mayrounddown and not mayroundup:
        score = -1e10  # Penalize variables that cannot be rounded
        roundup = False
    else:
        roundup = candsfrac > 0.5
        
        # Calculate potential objective improvement
        obj_diff_down = obj * (rootsolval - candsol) + pscostdown
        obj_diff_up = obj * (1 - candsol) + pscostup
        obj_improvement = max(0, obj_diff_up, obj_diff_down) / (objnorm + 1e-9)
        
        # Calculate exploration and diversification scores
        exploration_score = abs(candsfrac - 0.5) * (1 + nNonz * isBinary)
        diversification_score = 1 / (nlocksdown + nlocksup + 1e-9)
        
        # Combine scores with objective coefficient
        if roundup:
            score = obj * (exploration_score + obj_improvement * diversification_score - nlocksup)
        else:
            score = obj * (exploration_score + obj_improvement * diversification_score - nlocksdown)
    
    return score, roundup
'''
    my_diving_info = "setc_gpt35"

    # diving_info = "farkasdiving"
    diving_info = "myheurdiving"

    for instance in instance_list[start:end]:
        print(instance)
        path_to_one_instance = path_to_instances + "/" + instance


        # log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/loadbalance/"+ my_diving_info +"solved/"+t+"/seed" + str(seed)
        log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/miplib/"+diving_info+"solved/"+t
        if( not os.path.exists(log_dir) ):
            os.makedirs(log_dir)

        logfile = log_dir + "/" + instance + ".log"

        model = scip.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        model.setParam('limits/time', 900)
        
        if(diving_info[:6]=="myheur"):
            file_dir = '/home/yyzhou/LLM4Heur/tmp/'
            if(DIVING_IND == 1):
                model.includeMyheurdiving()
                freq_param = 'heuristics/myheurdiving/freq'
                freqofs_param = 'heuristics/myheurdiving/freqofs'
                priority_param = 'heuristics/myheurdiving/priority'
                file_path = file_dir + 'diving.py'
                state_path = file_dir + 'state.json'
            elif(DIVING_IND == 2):
                model.includeMyheur2diving()
                freq_param = 'heuristics/myheur2diving/freq'
                freqofs_param = 'heuristics/myheur2diving/freqofs'
                priority_param = 'heuristics/myheur2diving/priority'
                file_path = file_dir + 'diving2.py'
                state_path = file_dir + 'state2.json'
            elif(DIVING_IND ==3):
                model.includeMyheur3diving()
                freq_param = 'heuristics/myheur3diving/freq'
                freqofs_param = 'heuristics/myheur3diving/freqofs'
                priority_param = 'heuristics/myheur3diving/priority'
                file_path = file_dir + 'diving3.py'
                state_path = file_dir + 'state3.json'
            else:
                model.includeMyheur4diving()
                freq_param = 'heuristics/myheur4diving/freq'
                freqofs_param = 'heuristics/myheur4diving/freqofs'
                priority_param = 'heuristics/myheur4diving/priority'
                file_path = file_dir + 'diving4.py'
                state_path = file_dir + 'state4.json'
            
        
            if(not os.path.exists(file_dir)):
                os.mkdir(file_dir)

            # check whether the file has already existed or not
            if os.path.exists(file_path):
                # delete previous contents
                os.remove(file_path)
            else:
                print("file doesn' exist")  
                

            # write the new function to the file_path for myheurdiving
            with open(file_path, 'a') as file:
                file.write(my_diving)

        else:
            freq_param = 'heuristics/'+diving_info+'/freq'
            freqofs_param = 'heuristics/'+diving_info+'/freq'
            priority_param = 'heuristics/'+diving_info+'/priority'

        # # turn off the other diving heur
        
        model.setParam('heuristics/coefdiving/freq',-1)
        model.setParam('heuristics/fracdiving/freq',-1)
        model.setParam('heuristics/distributiondiving/freq',-1)
        model.setParam('heuristics/farkasdiving/freq',-1)
        model.setParam('heuristics/linesearchdiving/freq',-1)
        model.setParam('heuristics/veclendiving/freq',-1)
        model.setParam('heuristics/pscostdiving/freq',-1)
        

        model.setParam(freq_param,1)
        model.setParam(freqofs_param,0)
        model.setParam(priority_param,100000000)

        model.hideOutput()
        # before optimize, check /home/yyzhou/scipoptsuite-9.0.0/scip/src/scip/scipdefplugins.c
        model.optimize()


