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
new_benmark1 = {'indset':indset_instances}
new_benmark2 = {'setcover':setcover_instances}

heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']

mode = 'easy'
for benchmark_name,benchmark_data in new_benmark2.items():
    path_to_instances = "/home/yyzhou/learn2branch/data/instances/" + benchmark_name + "/" + benchmark_data[mode]
    
    instance_list = os.listdir(path_to_instances)
    
    for instance in instance_list:
        path_to_one_instance = path_to_instances + "/" + instance
        log_dir = "/home/yyzhou/LLM4Heur/heur/baselines/logs/" + benchmark_name + "/solved" +"/"+ mode 
        if( not os.path.exists(log_dir) ):
            os.makedirs(log_dir)

        logfile = log_dir + "/" + instance + ".log"

        model = scip.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        model.hideOutput()
        model.optimize()
        

# filename = "brazil3.mps.gz"
# abs_filepath = "/home/yyzhou/MIPLIB_data/data/"+filename
# abs_filepath = "/home/yyzhou/learn2branch/data/instances/setcover/test_500r_1000c_0.05d/instance_20.lp"
# abs_filepath = "/home/yyzhou/learn2branch/data/instances/cauctions/test_100_500/instance_20.lp"
# abs_filepath = "/home/yyzhou/learn2branch/data/instances/setcover/test_500r_1000c_0.05d/instance_1.lp"
# abs_filepath = "/home/yyzhou/learn2branch/data/instances/indset/test_500_4/instance_20.lp"




# model.readProblem(abs_filepath)

# model.setLogfile(filename+'.log')

# model.setHeuristics(SCIP_PARAMSETTING.OFF)
# model.setPresolve(SCIP_PARAMSETTING.OFF)

# 创建自定义的Heur对象
# my_heur = MyRoundingHeur()
# model.includeHeur(my_heur, "MyRound", "Applies rounding heuristic", "Y", timingmask=SCIP_HEURTIMING.BEFORENODE)


# model.setPresolve(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭预处理
# model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭分离算法
# model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)

# model.setParam('heuristics/rounding/freq',1)
# model.setParam('heuristics/rens/freq',1)
# model.setParam('heuristics/randrounding/freq',1)
# model.setParam('heuristics/simplerounding/freq',1)
# model.setParam("heuristics/rounding/freq",SCIP_HEURTIMING.BEFORENODE)
# model.setParam('heuristics/simplerounding/freq',1)
# model.setParam('heuristics/locks/freq',1)
# model.setParam('heuristics/pscostdiving/freq',1)
# model.setParam('heuristics/pscostdiving/freqofs',0)
# model.setParam('heuristics/veclendiving/freq',1)
# model.setParam('heuristics/veclendiving/freqofs',0)
# model.setIntParam("heuristics/coefdiving/freq",1)
# model.setParam('heuristics/coefdiving/freqofs',0)
# model.setIntParam("heuristics/farkasdiving/freq",1)
# model.setIntParam("heuristics/fracdiving/freq",1)

# model.setParam("branching/fullstrong/maxdepth",0)

# model.setParam('limits/nodes', 1)  
# model.setParam('limits/solutions',10)
# print("nodes:",model.getParams)
# model.setIntParam('limits/solutions', 1)  # 限制求解器找到的解的数量为1个
# model.setParam('limits/nodes',1)
# model.setParam('limits/totalnodes',1)

# 解决优化问题
# model.optimize()
# print(model.getLPObjVal())
# 获取解决方案
# solution = model.getBestSol()
# for var in model.getVars():
#     print(var.name, solution[var])