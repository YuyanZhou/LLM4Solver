
import pyscipopt
import os
import sys
import pyscipopt as scip

name = sys.argv[1]

names = ["cauctions","facilities","indset","setcover","miplib","loadbalance"]

assert(name in names)

heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving','coef2diving','frac2diving','linesearch2diving','pscost2diving','veclen2diving']
# heurs = ['coef2diving','frac2diving','linesearch2diving','pscost2diving','veclen2diving']

# mode = 'easy'

# ds = ["train","test", "transfer1", "transfer2", "transfer3"]
# ds = ["transfer1", "transfer2", "transfer3"]
ds = ["train","test","train1","train10","train50"]

for t in ds:
    
    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    for instance in instance_list:
        path_to_one_instance = path_to_instances + "/" + instance

        for heur in heurs:

            if(name == "indset" and heur == 'farkasdiving'):
                continue

            log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/" + name + "/heursolved/" + t + "/" +heur
            if( not os.path.exists(log_dir) ):
                os.makedirs(log_dir)  
                
            logfile = log_dir + "/" + instance + ".log"

            model = scip.Model("Heuristic_Example")
            model.readProblem(path_to_one_instance)
            model.setLogfile(logfile)

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
                        
            freq_param = 'heuristics/'+ heur +'/freq'
            freqofs_param = 'heuristics/'+ heur +'/freqofs'
            model.setParam(freq_param,1)
            model.setParam(freqofs_param,0)

            model.setParam('limits/time', 1800)

            model.hideOutput()
            model.optimize()    
        
