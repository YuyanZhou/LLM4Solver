import gc
import weakref

import pytest

import sys
sys.path.append('/home/yyzhou/PySCIP/PySCIPOpt/src')
import inspect


from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt

import datetime

# if __name__ == "__main__":
#     s = Model()
#     s.readProblem("bpp.mps")

#     s.optimize()

import pyscipopt as scip





# 创建一个自定义的Heur类来实现rounding heuristic
class MyRoundingHeur(Heur):

    def heurexec(self, heurtiming, nodeinfeasible):
        

        sol = self.model.createSol(self)
        vars = self.model.getVars(True)
        lpcands, lpcandssol, lpcadsfrac, nlpcands, npriolpcands, nfracimplvars = self.model.getLPBranchCands()
        print("LPBRANCH:\n")
        print(lpcands[0],lpcandssol[0],lpcadsfrac[0],nlpcands,npriolpcands)
        print("\n\n")

        for var in vars:
            if(var.vtype() == "INTEGER" or var.vtype() == "BINARY"):
                sol[var] = round(var.getLPSol())
            else:
                sol[var] = var.getLPSol()

        # for var in lpcands:
        #     self.model.



        accepted = self.model.trySol(sol)


        if accepted:
            print("\n FIND SOL")
            return {"result": SCIP_RESULT.FOUNDSOL}
        else:
            print("\n NO SOL")
            return {"result": SCIP_RESULT.DIDNOTFIND}
        

# 创建SCIP实例
model = scip.Model("Rounding_Heuristic_Example")
filename = "h80x6320d.mps.gz"
abs_filepath = "/home/yyzhou/MIPLIB_data/data/"+filename
model.readProblem(abs_filepath)



# 设置logfile
# cur_logfile_path = "/home/yyzhou/LLM4Heur/heur/logfile/"+filename+ str(datetime.datetime.now()) +'.log'
# model.setLogfile(cur_logfile_path)


# 参数设置
# model.setHeuristics(SCIP_PARAMSETTING.OFF)
# model.setPresolve(SCIP_PARAMSETTING.OFF)
# model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭分离算法
model.setIntParam('limits/solutions', 1)  # 限制求解器找到的解的数量为1个
model.setParam('limits/nodes',1)
model.setParam('limits/totalnodes',1)


# 创建自定义的Heur对象
my_heur = MyRoundingHeur()
model.includeHeur(my_heur, "MyRound", "Applies rounding heuristic", "Y", timingmask=SCIP_HEURTIMING.DURINGLPLOOP)





# 解决优化问题
model.optimize()

# print(model.getLPObjVal())
# 获取解决方案
# solution = model.getBestSol()
# for var in model.getVars():
#     print(var.name, solution[var])
