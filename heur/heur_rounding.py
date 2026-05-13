
from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING, SCIP_LPSOLSTAT

SCIP_LOCKTYPE_MODEL = 0
SCIP_LOCKTYPE_CONFLICT = 1
INT_MAX = 0x7fffffff


class MyRoundingHeur(Heur):

    def updateViolations(self, row, violrows, violrowpos, nviolrows, oldactivity, newactivity):
        lhs = row.getLhs()
        rhs = row.getRhs()
        oldviol = (self.model.isFeasLT(oldactivity, lhs) or self.model.isFeasGT(oldactivity, rhs) )
        newviol = (self.model.isFeasLT(newactivity, lhs) or self.model.isFeasGT(newactivity, rhs) )
        if ( oldviol != newviol):
            rowpos = row.getLPPos()
            assert (rowpos >= 0), "rowpos should bigger than 0"

            if( oldviol ):
                violpos = violrowpos[rowpos]
                assert (0 <= violpos and violpos < nviolrows), "assertation fault"
                assert (violrows[violpos] == row), "assertation fault"
                violrowpos[rowpos] = -1
                if( violpos != (nviolrows - 1) ):
                    violrows[violpos] = violrows[nviolrows - 1]
                    violrowpos[violrows[violpos].getLPPos()] = violpos
                
                nviolrows = nviolrows - 1
            
            else:
                assert (violrowpos[rowpos] == -1), "assertation fault"
                violrows[nviolrows] = row
                violrowpos[rowpos] = nviolrows
                nviolrows = nviolrows + 1

        return violrows, violrowpos, nviolrows

    def updateActivities(self, activities, violrows, violrowpos, nviolrows, nlprows, var, oldsolval, newsolval):
        assert (0 <= nviolrows and nviolrows <= nlprows), "nviolrows should be [0,nlprows)"
        delta = newsolval - oldsolval
        col = var.getCol()
        colrows = col.getRows()
        colvals = col.getVals()
        ncolrows = col.getNLPNonz()

        for r in range(ncolrows):
            row = colrows[r]
            rowpos = row.getLPPos()

            if (rowpos >= 0 and not row.isLocal()):

                assert row.isInLP(), "row is not in LP"

                # update row activity
                oldactivity = activities[rowpos]
                if ( (not self.model.isInfinity(-oldactivity)) and (not self.model.isInfinity(oldactivity))):
                    newactivity = oldactivity + delta * colvals[r]
                    if( self.model.isInfinity(newactivity) ):
                        newactivity = self.model.infinity()
                    elif ( self.model.isInfinity(-newactivity) ):
                        newactivity = -self.model.infinity()
                    activities[rowpos] = newactivity

                    # update row violation arrays
                    violrows, violrowpos, nviolrows = self.updateViolations(row, violrows, violrowpos, nviolrows, oldactivity, newactivity)

        return activities, violrows, violrowpos, nviolrows
    

    def selectEssentialRounding(self, sol, minobj, lpcands, nlpcands, roundvar = None, oldsolval = 0.0, newsolval = 0.0):
 
        # select rounding variable
        maxnlocks = -1
        bestdeltaobj = self.model.infinity()
        roundvar = None
        for v in range(nlpcands):
            var = lpcands[v]
            assert (var.vtype() == "BINARY" or var.vtype() == "INTEGER"), "candidate var's type should be BINARY or INTEGER"
            solval = self.model.getSolVal(sol, var)
            if( not self.model.isFeasIntegral(solval)):
                obj = var.getObj()

                # rounding down
                nlocks = var.getNLocksUpType(SCIP_LOCKTYPE_MODEL)
                if (nlocks >= maxnlocks):
                    roundval = self.model.feasFloor(solval)
                    deltaobj = obj * (roundval - solval)
                    if ( (nlocks > maxnlocks or deltaobj < bestdeltaobj) and minobj - obj < self.model.getCutoffbound()):
                        maxnlocks = nlocks
                        bestdeltaobj = deltaobj
                        roundvar = var
                        oldsolval = solval
                        newsolval = roundval

                # rounding up
                nlocks = var.getNLocksDownType(SCIP_LOCKTYPE_MODEL)
                if (nlocks >= maxnlocks):
                    roundval = self.model.feasCeil(solval)
                    deltaobj = obj * (roundval - solval)
                    if ( (nlocks > maxnlocks or deltaobj < bestdeltaobj) and minobj + obj < self.model.getCutoffbound()):
                        maxnlocks = nlocks
                        bestdeltaobj = deltaobj
                        roundvar = var
                        oldsolval = solval
                        newsolval = roundval

        return roundvar, oldsolval, newsolval

    def selectRounding(self, sol, minobj, row, direction, roundvar = None, oldsolval = 0.0, newsolval = 0.0):
        
        assert (direction == +1 or direction == -1), "direction number should be +1(up) or -1(down)"
        
        # get row entries
        rowcols = row.getCols()
        rowvals = row.getVals()
        nrowcols = row.getNLPNonz()

        # select rounding variable
        minnlocks = INT_MAX
        bestdeltaobj = self.model.infinity()
        roundvar = None

        for c in range(nrowcols):
            col = rowcols[c]
            var = col.getVar()

            vartype = var.vtype()

            if (vartype == "BINARY" or vartype == "INTEGER"):
                solval = self.model.getSolVal(sol, var)
                if (not self.model.isFeasIntegral(solval)):
                    val = rowvals[c]
                    obj = var.getObj()
                    if (direction * val < 0.0):
                        # rounding down
                        nlocks = var.getNLocksDownType(SCIP_LOCKTYPE_MODEL)
                        if ( nlocks <= minnlocks):
                            roundval = self.model.feasFloor(solval)
                            deltaobj = obj * (roundval - solval)
                            if ( (nlocks < minnlocks or deltaobj < bestdeltaobj) and minobj - obj < self.model.getCutoffbound()):
                                minnlocks = nlocks
                                bestdeltaobj = deltaobj
                                roundvar = var
                                oldsolval = solval
                                newsolval = roundval
                    else:
                        # rounding up
                        assert direction * val > 0.0, "rounding up in select rounding"
                        nlocks = var.getNLocksUpType(SCIP_LOCKTYPE_MODEL)
                        if ( nlocks <= minnlocks):
                            roundval = self.model.feasCeil(solval)
                            deltaobj = obj * (roundval - solval)
                            if ( (nlocks < minnlocks or deltaobj < bestdeltaobj) and minobj + obj < self.model.getCutoffbound()):
                                    minnlocks = nlocks
                                    bestdeltaobj = deltaobj
                                    roundvar = var
                                    oldsolval = solval
                                    newsolval = roundval

        return roundvar, oldsolval, newsolval


    def selectIncreaseRounding(self, sol, minobj, row, roundvar = None, oldsolval = 0.0, newsolval = 0.0):
        return self.selectRounding(sol, minobj, row, direction = +1, roundvar = None, oldsolval = 0.0, newsolval = 0.0)

    def selectDecreaseRounding(self, sol, minobj, row, roundvar = None, oldsolval = 0.0, newsolval = 0.0):
        return self.selectRounding(sol, minobj, row, direction = -1, roundvar = None, oldsolval = 0.0, newsolval = 0.0)

    def heurexec(self, heurtiming, nodeinfeasible):
        
        # only call heuristic, if an optimal LP solution is at hand
        if(self.model.getLPSolstat() != SCIP_LPSOLSTAT.OPTIMAL):
            print("did not run in 174")
            return {"result": SCIP_RESULT.DIDNOTRUN}
        
        # only call heuristic, if the LP objective value is smaller than the cutoff bound
        if ( self.model.isGE(self.model.getLPObjVal(), self.model.getCutoffbound()) ):
            print("did not run in 179")
            return {"result":SCIP_RESULT.DIDNOTRUN}


        lpcands, lpcandssol, lpcadsfrac, nlpcands, npriolpcands, nfracimplvars = self.model.getLPBranchCands()

        nfrac = nlpcands

        if (nfrac == 0):
            print("did not run in 188")
            return {"result":SCIP_RESULT.DIDNOTRUN}


        result = SCIP_RESULT.DIDNOTFIND

        lprows = self.model.getLPRowsData()
        nlprows = len(lprows)


        # get the activities for all globally valid rows;
        # the rows should be feasible, but due to numerical inaccuracies in the LP solver, they can be violated
        
        nviolrows = 0
        activities = [0.0 for i in range(nlprows)]
        violrowpos = [-2 for i in range(nlprows)]
        # initialization of violrows, acctually the element in the list will change 
        violrows = [lprows[0] for i in range(nlprows)] 
        for r in range(nlprows):

            row = lprows[r]
            assert row.getLPPos() == r, "row number doesn't match"

            if(not row.isLocal()):
                activities[r] = self.model.getRowActivity(row)
                if( self.model.isFeasLT(activities[r], row.getLhs()) or self.model.isFeasGT(activities[r], row.getRhs())):
                    violrows[nviolrows] = row
                    violrowpos[r] = nviolrows
                    nviolrows = nviolrows + 1
                else:
                    violrowpos[r] = -1
        

        # copy the current LP solution to the working solution 
        sol = self.model.createSol()
        self.model.linkLPSol(sol)


        # calculate the minimal objective value possible after rounding fractional variables 
        minobj = self.model.getSolTransObj(sol)
        assert minobj < self.model.getCutoffbound(), "minobj doesn't less than cut off bound"
        for c in range(nlpcands):
            var_cand_c = lpcands[c]
            val_cand_c = lpcandssol[c]
            obj = var_cand_c.getObj()
            bestroundval = self.model.feasFloor(val_cand_c)
            if (obj <= 0.0):
                bestroundval = self.model.feasCeil(val_cand_c)
            minobj = minobj + obj * (bestroundval - lpcandssol[c])
        

        # try to round remaining variables in order to become/stay feasible
        while (nfrac > 0):
            
            # minobj < SCIPgetCutoffbound(scip) should be true, otherwise the rounding variable selection
            # should have returned NULL. Due to possible cancellation we use SCIPisLE. 
            assert self.model.isLE(minobj, self.model.getCutoffbound()), "minobj doesn't less than cut off bound"

            # choose next variable to process:
            # if a violated row exists, round a variable decreasing the violation, that has least impact on other rows
            # otherwise, round a variable, that has strongest devastating impact on rows in opposite direction
            
            roundvar = None
            oldsolval, newsolval = 0.0, 0.0
            if( nviolrows > 0):
                # ToDo: finish the case that has violrows
                row = violrows[nviolrows - 1]
                rowpos = row.getLPPos()
                assert (0 <= rowpos and rowpos < nlprows), "rowpos should be [0,nlprows)"
                assert (violrowpos[rowpos] == nviolrows-1), "check the rowpos"

                if ( self.model.isFeasLT(activities[rowpos], row.getLhs()) ):
                    roundvar, oldsolval, newsolval = self.selectIncreaseRounding(sol, minobj, row, roundvar = None, oldsolval = 0.0, newsolval=0.0)
                else:
                    assert self.model.isFeasGT( activities[rowpos], row.getRhs() ), "check the nviolrows"
                    roundvar, oldsolval, newsolval = self.selectDecreaseRounding(sol, minobj, row, roundvar = None, oldsolval = 0.0, newsolval=0.0)
            else:
                # ToDo: finish the case that has no violrow
                roundvar, oldsolval, newsolval = self.selectEssentialRounding(sol, minobj, lpcands, nlpcands, roundvar=None, oldsolval=0.0, newsolval=0.0)
            

            # check, whether rounding was possible
            if roundvar is None:
                print("did not find in 271")
                return {"result":SCIP_RESULT.DIDNOTFIND}
            
            # update row activities of globally valid rows
            activities, violrows, violrowpos, nviolrows = self.updateActivities(activities, violrows, violrowpos, nviolrows, nlprows, roundvar, oldsolval, newsolval)

            # store new solution value and decrease fractionality counter
            self.model.setSolVal(sol, roundvar, newsolval)
            nfrac = nfrac - 1

            # update minimal objective value possible after rounding remaining variables
            obj = roundvar.getObj()
            if( obj > 0.0 and newsolval > oldsolval ):
                minobj = minobj + obj
            elif( obj < 0.0 and newsolval < oldsolval ):
                minobj = minobj - obj

        if( nfrac == 0 and nviolrows == 0):
            print(self.model.getSolObjVal(sol))
            accepted = self.model.checkSol(sol)

            if(accepted):
                print("find")
                self.model.addSol(sol)
                return {"result": SCIP_RESULT.FOUNDSOL}
            else:
                print("did not find in 295")
                return {"result": SCIP_RESULT.DIDNOTFIND}

        

        # print("solstat",self.model.getLPSolstat())
        # print("cut:",self.model.getCutoffbound())
        # print("nlpcands:",nlpcands)
        # print("nlprows:", nlprows)
        # print("lt:",self.model.isFeasLT(1.0,2.0))
        # print("gt:",self.model.isFeasGT(2.0,1.0))
        # print("feas floor:",self.model.feasFloor(1.1))
        # print("ceil floor:",self.model.feasCeil(1.1))
        # print("nlocks down:",lpcands[0].getNLocksDownType(SCIP_LOCKTYPE_MODEL))
        # print("nlocks up:",lpcands[0].getNLocksUpType(SCIP_LOCKTYPE_MODEL))
        # col = lpcands[0].getCol()
        # print("rows of col:",col.getRows()[0])
        # print("vals of col:",col.getVals()[0])
        
        print("did not find in 314")
        return {"result": SCIP_RESULT.DIDNOTFIND}

  

if __name__ == "__main__":
    import pyscipopt

    # 创建SCIP实例
    model = Model("Rounding_Heuristic_Example")
    # h80x6320d.mps.gz; triptim1.mps.gz; 
    filename = "h80x6320d.mps.gz"
    print(filename)
    # abs_filepath = "/home/yyzhou/MIPLIB_data/data/"+filename
    abs_filepath = "/home/yyzhou/learn2branch/data/instances/cauctions/test_100_500/instance_10.lp"

    model.readProblem(abs_filepath)
    

    # 设置参数
    # model.setPresolve(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭预处理
    model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
    # model.setIntParam("heuristics/rounding/freq",1)
    model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # 关闭分离算法
    # model.setIntParam('limits/solutions', 1)  # 限制求解器找到的解的数量为1个

    model.setParam('limits/nodes',1)
    model.setParam('limits/totalnodes',1)

    # 引入heuristics
    heuristic = MyRoundingHeur()
    model.includeHeur(heuristic, "PyHeur", "python heur", "Y", timingmask=SCIP_HEURTIMING.DURINGLPLOOP)

    # 求解最终解 
    model.optimize()

    print(model.getPrimalDualIntegral())