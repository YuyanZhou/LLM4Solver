import random
import math
import numpy as np

eps = 1e-6

def isLT(val1, val2):
    return val1 -val2 < -eps

def isEQ(val1, val2):
    return abs(val1-val2) <= eps

def isGT(val1, val2):
    return val1 -val2 > eps


def coefdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    if( mayrounddown or mayroundup):
        if( mayrounddown and mayroundup):
            roundup = (candsfrac > 0.5)
        else:
            roundup = mayrounddown
    else:
        roundup = ( (nlocksdown > nlocksup) or (nlocksdown == nlocksup and candsfrac > 0.5) )
    

    if( roundup ):
        candsfrac = 1.0 - candsfrac
        score = nlocksup
    else:
        score = nlocksdown

    # penalize too small fractions
    if(candsfrac < 0.01):
        score = score * 0.01
    
    # prefer decisions on binary variables
    if( not isBinary):
        score = score * 0.1

    # penalize the variable if it may be rounded.
    if( mayrounddown or mayroundup ):
      score = min(score*0.1, score - 100)

    return (score, roundup)

    

def fracdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # choose rounding direction:
    # if variable may be rounded in either both or neither direction, round corresponding to the fractionality
    # otherwise, round in the infeasible direction, because feasible direction is tried by rounding
    # the current fractional solution
    if( mayrounddown != mayroundup):
        roundup = mayrounddown
    else:
        roundup = (candsfrac > 0.5)

    if(objnorm > eps):
        obj = obj / objnorm

    if(roundup):
        candsfrac = 1.0 - candsfrac
        objgain = obj * candsfrac
    else:
        objgain = -obj * candsfrac
    
    assert(objgain >= -1.0 and objgain <= 1.0)

    # penalize too small fractions
    if( candsfrac < 0.01 ):
        candsfrac = candsfrac + 10.0

    # prefer decisions on binary variables
    if( not isBinary ):
        candsfrac = candsfrac * 1000

    # prefer variables which cannot be rounded by scoring their fractionality
    if( not (mayrounddown or mayroundup) ):
        score = -candsfrac # [-1,0], acctually (-0.99,0.01)
    else:
        score = -2.0 - objgain # [-3,-1]

    return (score, roundup)

def pscostdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    candsfrac = max(candsfrac, 0.1)
    candsfrac = min(candsfrac, 0.9)

    assert((pscostdown>=0) and (pscostup>=0))

    if(mayrounddown != mayroundup):
        roundup = mayrounddown
    elif(  candsol < rootsolval - 0.4  ):
        roundup = False
    elif(  candsol > rootsolval + 0.4  ):
        roundup = True
    elif(  candsfrac < 0.3 ):
        roundup = False
    elif(  candsfrac > 0.7 ):
        roundup = True
    elif(  pscostdown == pscostup ):
        roundup = ( random.uniform(0.0, 1.0) >= 0.5 )
    elif(  pscostdown > pscostup):
        roundup = True
    else:
        roundup = False

    if( roundup ):
      pscostquot = math.sqrt(candsfrac) * (1.0 + pscostdown) / (1.0 + pscostup)
    else:
      pscostquot = math.sqrt(1.0 - candsfrac) * (1.0 + pscostup) / (1.0 + pscostdown)

    if( isBinary and (not(mayrounddown or mayroundup) ) ):
      pscostquot = 1000.0 * pscostquot

    assert(pscostquot >= 0)
    
    score = pscostquot

    return (score, roundup)

def linesearchdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # preferred branching direction is further away from the root LP solution
    if(candsol < rootsolval):
        roundup = False
        disquot = (candsfrac + eps) / (rootsolval - candsol)

        # avoid roundable candidates
        if(mayrounddown):
            disquot = disquot * 1000
    elif(candsol > rootsolval):
        roundup = True
        disquot = (1.0 - candsfrac + eps) / (candsol - rootsolval)

        # avoid roundable candidates
        if(mayroundup):
            disquot = disquot * 1000
    else:
        roundup = False
        disquot = math.inf

    score = -disquot

    return (score, roundup)



def veclendiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    roundup = (obj >= 0.0)
    if(roundup):
        objdelta = (1.0 - candsfrac) * obj
    else:
        objdelta = -candsfrac * obj
    
    assert(objdelta >= 0.0)

    score = (nNonz + 1.0) / (objdelta + eps)

    # prefer decisions on binary variables
    if(not isBinary):
        score = score * 0.001

    return (score, roundup)




def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    candsfrac = max(candsfrac, 0.1)
    candsfrac = min(candsfrac, 0.9)

    # assert((pscostdown>=0) and (pscostup>=0))

    if(mayrounddown != mayroundup):
        roundup = mayrounddown
    elif(  candsol < rootsolval - 0.4  ):
        roundup = False
    elif(  candsol > rootsolval + 0.4  ):
        roundup = True
    elif(  candsfrac < 0.3 ):
        roundup = False
    elif(  candsfrac > 0.7 ):
        roundup = True
    elif(  pscostdown == pscostup ):
        roundup = ( random.uniform(0.0, 1.0) >= 0.5 )
    elif(  pscostdown > pscostup):
        roundup = True
    else:
        roundup = False

    if( roundup ):
      pscostquot = math.sqrt(candsfrac) * (1.0 + pscostdown) / (1.0 + pscostup)
    else:
      pscostquot = math.sqrt(1.0 - candsfrac) * (1.0 + pscostup) / (1.0 + pscostdown)

    if( isBinary and (not(mayrounddown or mayroundup) ) ):
      pscostquot = 1000.0 * pscostquot

    assert(pscostquot >= 0)
    
    score = pscostquot

    return (score, roundup)