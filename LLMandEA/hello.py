from eval import eval_heur
import pandas as pd

pscost_heur_text = '''
import random
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
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

    # if( isBinary and (not(mayrounddown or mayroundup) ) ):
    #   pscostquot = 1000.0 * pscostquot

    assert(pscostquot >= 0)
    
    score = pscostquot

    return (score, roundup)
'''

coef_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
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
'''

frac_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
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

'''

linesearch_heur_text = '''
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
'''

veclen_heur_text = '''
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
'''




pscost_mo_heur_text = '''
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Normalize candsfrac between 0.1 and 0.9
    candsfrac = max(min(candsfrac, 0.9), 0.1)
    
    # Initialize the score
    score = 0.0
    
    # Consider whether rounding up/down is feasible
    if mayrounddown and mayroundup:
        score += 1.0
    elif mayrounddown:
        score += 0.8
    elif mayroundup:
        score += 0.6
    
    # Consider the fractional part of the solution value
    score += candsfrac
    
    # Consider the objective function value
    score += obj
    
    # Consider the objective function norm
    score += objnorm
    
    # Consider the variable's pseudo cost values
    score += max(pscostdown, pscostup)
    
    # Consider the difference between root solution value and current solution value
    score += abs(rootsolval - candsol)
    
    # Consider the number of locks for rounding down/up
    score -= min(nlocksdown, nlocksup) * 0.1
    
    # Consider the number of non-zero entries in the variable
    score += nNonz * 0.2
    
    # If the variable is binary and cannot be rounded, penalize heavily
    if isBinary and not (mayrounddown or mayroundup):
        score -= 1000.0
    
    # Determine the rounding direction based on the score
    roundup = score >= 0.0
    
    return (score, roundup)

'''

kimi_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the base score
    base_score = abs(candsfrac) * (abs(candsol - rootsolval) + obj)
    
    # Adjust the score based on the number of locks and pseudo costs
    locks_score = -(nlocksdown + nlocksup) * 0.1
    pscost_score = (pscostdown - pscostup) * 0.01
    
    # Increase the score for binary variables
    binary_score = 0.2 if isBinary else 0
    
    # Calculate the total score
    score = base_score + locks_score + pscost_score + binary_score
    
    # Normalize the score by the objective function norm
    normalized_score = score / objnorm
    
    # Determine the rounding direction based on the pseudo costs and locks
    roundup = (pscostup - pscostdown) > 0
    
    return normalized_score, roundup
'''

gpt35_des = '''
<strat_des>
The new algorithm employs a scoring function, 'myheurdiving', to select the fractional variable and corresponding rounding direction. It utilizes 13 features derived from the LP relaxation and objective function to compute the variable's score. The scoring function aims to maximize the potential improvement in the objective function while considering the feasibility of rounding options.
</end_des>

'''

gpt35_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False

    # Feature weights for scoring function
    weights = {
        "mayrounddown": 0.1,
        "mayroundup": 0.1,
        "candsfrac": 0.2,
        "candsol": 0.1,
        "nlocksdown": 0.05,
        "nlocksup": 0.05,
        "obj": 0.15,
        "objnorm": 0.1,
        "pscostdown": 0.05,
        "pscostup": 0.05,
        "rootsolval": 0.05,
        "nNonz": 0.05,
        "isBinary": 0.1
    }

    # Calculate score based on feature weights
    score += weights["mayrounddown"] if mayrounddown else 0
    score += weights["mayroundup"] if mayroundup else 0
    score += weights["candsfrac"] * candsfrac
    score += weights["candsol"] * candsol
    score += weights["nlocksdown"] * nlocksdown
    score += weights["nlocksup"] * nlocksup
    score += weights["obj"] * obj
    score += weights["objnorm"] * objnorm
    score += weights["pscostdown"] * pscostdown
    score += weights["pscostup"] * pscostup
    score += weights["rootsolval"] * rootsolval
    score += weights["nNonz"] * nNonz
    score += weights["isBinary"] if isBinary else 0

    # Determine rounding direction
    if mayroundup and (not mayrounddown or score < 0):
        roundup = True

    return score, roundup

'''

gpt35_mo_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False

    # Feature weights for scoring function
    weights = {
        "mayrounddown": 0.15,
        "mayroundup": 0.15,
        "candsfrac": 0.1,
        "candsol": 0.1,
        "nlocksdown": 0.05,
        "nlocksup": 0.05,
        "obj": 0.1,
        "objnorm": 0.1,
        "pscostdown": 0.05,
        "pscostup": 0.05,
        "rootsolval": 0.05,
        "nNonz": 0.05,
        "isBinary": 0.1
    }

    # Calculate score based on feature weights
    score += weights["mayrounddown"] if mayrounddown else 0
    score += weights["mayroundup"] if mayroundup else 0
    score += weights["candsfrac"] * candsfrac
    score += weights["candsol"] * candsol
    score += weights["nlocksdown"] * nlocksdown
    score += weights["nlocksup"] * nlocksup
    score += weights["obj"] * obj
    score += weights["objnorm"] * objnorm
    score += weights["pscostdown"] * pscostdown
    score += weights["pscostup"] * pscostup
    score += weights["rootsolval"] * rootsolval
    score += weights["nNonz"] * nNonz
    score += weights["isBinary"] if isBinary else 0

    # Determine rounding direction
    if mayroundup and (not mayrounddown or score < 0):
        roundup = True

    return score, roundup

'''

gpt35b_heur_text = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score and rounding direction
    score = 0.0
    roundup = False
    
    # Custom scoring function based on provided features
    # Add your scoring logic here
    score += obj * objnorm  # Consider objective value and its norm
    score += 0.5 * (pscostdown + pscostup)  # Include pseudo costs
    score += nNonz  # Consider the number of nonzero entries
    if mayroundup and mayrounddown:
        score += 0.1 * (nlocksup + nlocksdown)  # Penalize if variable can't be locked for rounding
    if isBinary:
        score += 10.0  # Give a boost if the variable is binary
    
    # Determine rounding direction based on candidate values
    if candsfrac >= 0.5 and mayroundup:
        roundup = True
    elif candsfrac < 0.5 and mayrounddown:
        roundup = False
    
    return score, roundup
'''



random_code = '''
import random
random.seed(111)
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = random.uniform(1.0,10.0)
    score = score / 0
    roundup = (random.randint(1,10) > 5)

    return score, roundup
'''



kimi1_des = '''
The new scoring function, named myheurdiving, aims to select a fractional variable and determine the rounding direction based on a combination of factors that reflect the variable's current state, its impact on the objective function, and its potential for moving towards feasibility. The score is calculated by considering the urgency to fix the variable (based on the number of locks and pseudo costs), the desirability of rounding in a particular direction (based on the fractional part and the current solution), and the variable's binary status. The rounding direction is determined by the sign of the fractional part and the urgency factors. The higher the score, the more favorable it is to fix the variable, and the roundup boolean indicates the preferred rounding direction.
'''

kimi1_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate urgency score based on locks and pseudo costs
    urgency_score = nlocksdown * pscostdown + nlocksup * pscostup
    
    # Determine the desirability of rounding based on the fractional part and the current solution
    desirability = candsfrac * (objnorm - abs(obj)) / (candsol + 1e-6)  # Avoid division by zero
    
    # Factor in the binary status of the variable
    binary_factor = 2.0 if isBinary else 1.0
    
    # Calculate the overall score
    score = urgency_score + desirability * binary_factor
    
    # Determine the rounding direction: prefer rounding up if the fractional part is positive, otherwise rounding down
    roundup = candsfrac >= 0
    
    # Return the score and the rounding direction
    return score, roundup
'''

kimi2_des = '''
The new scoring function, named myheurdiving, aims to select the most promising fractional variable and its rounding direction based on a set of 13 features derived from the LP relaxation and objective function. The logic behind the scoring function is to prioritize variables that have a higher potential to reduce the objective function value when rounded and to consider the ease of rounding without losing feasibility. The function will output a score and a boolean value indicating whether to round up.
'''

kimi2_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the base score based on the fractional part and the current LP solution
    base_score = candsfrac * (candsol - rootsolval)
    
    # Factor in the number of locks, giving more weight to variables that are less constrained
    down_lock_multiplier = 1 + nlocksdown / nNonz
    up_lock_multiplier = 1 + nlocksup / nNonz
    
    # Calculate the score for rounding down and up separately
    score_down = base_score * (1 - down_lock_multiplier) + pscostdown
    score_up = base_score * (1 + up_lock_multiplier) - pscostup
    
    # Determine the better rounding direction based on the calculated scores
    if score_down > score_up:
        score = score_down
        roundup = False
    else:
        score = score_up
        roundup = True
    
    # Adjust the score based on the objective function value and its norm
    score *= (1 - obj / objnorm)
    
    # Give a bonus to binary variables as they have less flexibility
    if isBinary:
        score *= 2
    
    return score, roundup
'''

kimi3_des = '''
The new scoring function, named myheurdiving, aims to prioritize variables that have a higher potential impact on the objective function while considering the ease of rounding and the variable's historical behavior in the solution process. The score is calculated based on the potential change in the objective function (both in terms of value and norm), the pseudo costs for rounding up or down, and the variable's binary status. The rounding direction is determined by the variable's current fractional part and the number of locks for each direction. The score is designed to be higher for variables that could lead to a better solution and are easier to fix. The roundup decision is based on the comparison between the potential cost of rounding up and down.
'''

kimi3_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the base score based on the objective function impact
    base_score = obj / objnorm

    # Adjust the score based on the pseudo costs
    pseudo_cost_factor = (pscostdown - pscostup) / (pscostdown + pscostup + 1e-9)

    # Factor in the binary variable type, giving them higher priority
    binary_factor = 2.0 if isBinary else 1.0

    # Consider the ease of rounding based on the number of locks and the fractional part
    rounding_factor = 1.0 - abs(candsfrac)

    # Combine all factors to calculate the final score
    score = base_score + pseudo_cost_factor * rounding_factor * binary_factor

    # Determine the rounding direction based on the number of locks and the fractional part
    roundup = False
    if candsfrac > 0 and (not mayrounddown or nlocksdown > nlocksup):
        roundup = True

    return score, roundup
'''

kimi4_des = '''
The new scoring function, myheurdiving, aims to prioritize variables that have a significant impact on the objective function while considering the ease of rounding and the potential for improving the solution. The score is calculated based on the variable's fractional part, its current LP solution value, the number of locks preventing rounding, the objective function value, the pseudo costs for rounding down and up, and the variable's binary status. The roundup boolean determines whether it is more favorable to round up the variable rather than down.

The scoring function gives more weight to variables with a larger impact on the objective function and a higher pseudo cost for the chosen rounding direction. It also considers the number of locks, which can indicate how often a variable has been rounded in a certain direction in previous iterations, potentially guiding the search away from frequently chosen, suboptimal roundings. The binary status is used to give a higher score to binary variables, as they must be rounded to 0 or 1, and the direction of rounding is inherently determined by their current solution value.
'''

kimi4_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the base score based on the objective function impact and pseudo costs
    base_score = obj / objnorm
    pscost_diff = pscostdown - pscostup  # Difference in pseudo costs for down and up rounding

    # Adjust the score based on the fractional part and the number of locks
    adjust_score = (1 - candsfrac) * (nlocksdown + nlocksup)

    # Give a higher score to binary variables as they have less rounding flexibility
    binary_score = 2 if isBinary else 1

    # Calculate the final score
    score = base_score + adjust_score + pscost_diff * binary_score

    # Determine the rounding direction based on the current solution and the possibility of rounding
    roundup = candsol >= 0.5 if mayroundup else candsol <= -0.5 if mayrounddown else False

    return score, roundup
'''



gpt351_des = '''
The new algorithm aims to dynamically assess the importance of each variable in contributing to the objective function and feasibility of the MILP problem. It considers various factors such as the fractional part of the solution value, the objective function value, the number of locks for rounding, the pseudo cost, and the variable type. The scoring function combines these features to prioritize variables for rounding and determines the rounding direction based on their potential impact on the objective and feasibility.
'''

gpt351_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Feature weights
    weight_candsfrac = 0.5
    weight_obj = 1.0
    weight_nlocks = 0.3
    weight_pscost = 0.7
    weight_nNonz = 0.2
    weight_isBinary = 0.5
    
    # Calculate score based on features
    score += weight_candsfrac * candsfrac
    score += weight_obj * obj
    score -= weight_nlocks * (nlocksdown + nlocksup)
    score -= weight_pscost * (pscostdown + pscostup)
    score -= weight_nNonz * nNonz
    score += weight_isBinary if isBinary else 0.0
    
    # Determine rounding direction
    if mayroundup and mayrounddown:
        roundup = True if obj > 0 else False
    elif mayroundup:
        roundup = True
    elif mayrounddown:
        roundup = False
    
    return score, roundup

'''

gpt351_mu_des = '''
The new score function considers various features such as the fractional part of the solution value, the objective function value, the number of locks for rounding, the pseudo cost, the Euclidean norm of the objective function vector, the solution value in the previous root node relaxation, the number of nonzero entries in the variable, and the variable type. The scoring function combines these features to prioritize variables for rounding and determines the rounding direction based on their potential impact on the objective and feasibility, penalizing more exploratory rounding options.

'''

gpt351_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Feature weights
    weight_candsfrac = 0.5
    weight_obj = 1.0
    weight_nlocks = 0.3
    weight_pscost = 0.7
    weight_objnorm = 0.4
    weight_rootsolval = 0.6
    weight_nNonz = 0.2
    weight_isBinary = 0.5
    
    # Calculate score based on features
    score += weight_candsfrac * candsfrac
    score += weight_obj * obj
    score -= weight_nlocks * (nlocksdown + nlocksup)
    score -= weight_pscost * (pscostdown + pscostup)
    score += weight_objnorm * objnorm
    score += weight_rootsolval * rootsolval
    score -= weight_nNonz * nNonz
    score += weight_isBinary if isBinary else 0.0
    
    # Determine rounding direction
    if mayroundup and mayrounddown:
        roundup = True if obj > 0 else False
    elif mayroundup:
        roundup = True
    elif mayrounddown:
        roundup = False
    
    return score, roundup

'''

gpt352_des = '''
The new algorithm aims to create a scoring function that intelligently selects fractional variables and determines the rounding direction based on various features provided by the LP relaxation and objective function. It combines multiple factors such as the potential for rounding, fractional part of the solution value, objective function value, pseudo cost, and other characteristics to prioritize variables for rounding. The algorithm assesses each variable's potential contribution to achieving feasible integral solutions and adjusts rounding directions accordingly to enhance solution quality.
'''

gpt352_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Feature weights for scoring
    weight_mayround = 0.2
    weight_candsfrac = 0.15
    weight_candsol = 0.1
    weight_nlocks = 0.1
    weight_obj = 0.15
    weight_pscost = 0.1
    weight_rootsolval = 0.05
    weight_nNonz = 0.05
    
    # Scoring calculation
    score += weight_mayround * (mayrounddown + mayroundup)
    score += weight_candsfrac * (1.0 - abs(candsfrac - round(candsfrac)))
    score += weight_candsol * (1.0 - abs(candsol - round(candsol)))
    score += weight_nlocks * ((nlocksdown + nlocksup) / (nlocksdown + nlocksup + 1))  # Avoid division by zero
    score += weight_obj * (1.0 - abs(obj))
    score += weight_pscost * (min(pscostdown, pscostup) / max(pscostdown, pscostup + 0.1))  # Avoid division by zero
    score += weight_rootsolval * (1.0 - abs(rootsolval))
    score += weight_nNonz * (1.0 - (nNonz / 10))  # Normalize nNonz
    
    # Determine rounding direction based on objective value
    if obj > 0:
        roundup = True
    
    return score, roundup

'''

gpt352_mu_des = '''
The new score function aims to combine various features provided by the LP relaxation and objective function to intelligently prioritize variables for rounding. It penalizes variables that can be easily rounded to maintain feasibility, emphasizes the fractional part and solution value of the variable, considers the number of locks for rounding down/up, evaluates the objective function value and its Euclidean norm, incorporates pseudo cost values for potential changes, includes the solution value in the last root node's relaxation, normalizes the number of nonzero entries in the variable, and checks if the variable is of binary type.

'''

gpt352_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Feature weights for scoring
    weight_mayround = 0.2
    weight_candsfrac = 0.15
    weight_candsol = 0.1
    weight_nlocks = 0.1
    weight_obj = 0.15
    weight_pscost = 0.1
    weight_rootsolval = 0.05
    weight_nNonz = 0.05
    weight_isBinary = 0.05
    
    # Scoring calculation
    score += weight_mayround * (mayrounddown + mayroundup)
    score += weight_candsfrac * (1.0 - abs(candsfrac - round(candsfrac)))
    score += weight_candsol * (1.0 - abs(candsol - round(candsol)))
    score += weight_nlocks * ((nlocksdown + nlocksup) / (nlocksdown + nlocksup + 1))
    score += weight_obj * (1.0 - abs(obj))
    score += weight_pscost * (min(pscostdown, pscostup) / max(pscostdown, pscostup + 0.1))
    score += weight_rootsolval * (1.0 - abs(rootsolval))
    score += weight_nNonz * (1.0 - (nNonz / 10))
    score += weight_isBinary if isBinary else 0
    
    # Determine rounding direction based on objective value
    if obj > 0:
        roundup = True
    
    return score, roundup

'''

gpt353_des = '''
The new algorithm's logic involves weighing the importance of various features to select the fractional variable and its rounding direction. It prioritizes variables that have higher potential impact on improving the objective function value or feasibility. The scoring function balances between the fractional part of the solution, the potential contribution to the objective function, the number of locks, and the variable type, among other factors.
'''

gpt353_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Weighted sum of features
    score += 0.3 * objnorm
    score += 0.2 * (pscostdown + pscostup)
    score += 0.15 * nNonz
    score += 0.1 * (nlocksdown + nlocksup)
    
    # Handling fractional part
    if mayrounddown and mayroundup:
        if candsfrac > 0.5:
            roundup = True
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    
    return score, roundup

'''

gpt353_mu_des = '''
The new score function aims to prioritize variables based on their potential impact on improving the objective function value or feasibility while considering various features. It penalizes the possibility of rounding variables down or up too early to promote more exploration. The scoring is a weighted sum of features including fractional part, solution value, number of locks, objective function value, Euclidean norm of the objective function vector, pseudo cost, root solution value, number of nonzero entries, and variable type.

'''

gpt353_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
    
    # Weighted sum of features
    score += 0.2 * obj
    score += 0.15 * objnorm
    score += 0.1 * (pscostdown + pscostup)
    score += 0.1 * nNonz
    score += 0.1 * (nlocksdown + nlocksup)
    
    # Handling fractional part
    if mayrounddown and mayroundup:
        if candsfrac > 0.6:
            roundup = True
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    
    return score, roundup
'''

gpt354_des = '''
The new score function aims to intelligently select the fractional variable and its corresponding rounding direction based on a combination of features related to the LP relaxation solution and objective function. It prioritizes variables that have a higher potential to improve the objective function value while considering constraints and feasibility. Additionally, it penalizes variables that have limited rounding options or exhibit characteristics that hinder exploration.
'''

gpt354_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score
    score = 0.0
    
    # Determine rounding direction based on the difference between candsfrac and 0.5
    roundup = candsfrac >= 0.5
    
    # Calculate score based on features
    score += obj / (1 + objnorm)  # Higher objective function value contributes positively to the score
    score -= (mayrounddown + mayroundup) * 0.5  # Penalize if rounding options are limited
    
    # Adjust score based on rounding direction and other features
    if roundup:
        score += pscostup * 0.2  # Higher pseudo cost for rounding up contributes positively
        score += (1 - candsfrac) * 0.1  # Higher fractional part contributes positively
        score -= nlocksdown * 0.3  # Penalize if there are locks for rounding down
    else:
        score += pscostdown * 0.2  # Higher pseudo cost for rounding down contributes positively
        score += candsfrac * 0.1  # Higher fractional part contributes positively
        score -= nlocksup * 0.3  # Penalize if there are locks for rounding up
    
    # Further adjustments based on additional features
    if rootsolval > 0:
        score += (candsol - rootsolval) * 0.5  # Positive contribution if current solution deviates from root node solution
    else:
        score += rootsolval * 0.1  # Penalize if root solution value is zero
    
    # Adjust score based on the type of variable
    if isBinary:
        score += 0.5  # Give a bonus for binary variables
    
    return score, roundup

'''

gpt354_mu_des = '''
The new score function intelligently selects the fractional variable and its rounding direction based on a combination of features related to the LP relaxation solution and objective function. It prioritizes variables with higher potential to improve the objective function value while penalizing limited rounding options and constraints that hinder exploration.

'''

gpt354_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score
    score = 0.0
    
    # Determine rounding direction based on the fractional part of the variable
    roundup = candsfrac >= 0.5
    
    # Calculate score based on features
    score += obj / (1 + objnorm)  # Higher objective function value contributes positively to the score
    score -= (mayrounddown + mayroundup) * 0.5  # Penalize limited rounding options
    
    # Adjust score based on rounding direction and other features
    if roundup:
        score += pscostup * 0.2  # Higher pseudo cost for rounding up contributes positively
        score += (1 - candsfrac) * 0.1  # Higher fractional part contributes positively
        score -= nlocksdown * 0.3  # Penalize locks for rounding down
    else:
        score += pscostdown * 0.2  # Higher pseudo cost for rounding down contributes positively
        score += candsfrac * 0.1  # Higher fractional part contributes positively
        score -= nlocksup * 0.3  # Penalize locks for rounding up
    
    # Further adjustments based on additional features
    if rootsolval > 0:
        score += (candsol - rootsolval) * 0.5  # Positive contribution if solution deviates from root node solution
    else:
        score += rootsolval * 0.1  # Penalize if root solution value is zero
    
    # Adjust score based on the type of variable
    if isBinary:
        score += 0.5  # Give a bonus for binary variables
    
    return score, roundup
'''




glm41_des = '''
The logic of the new score function ‘myheurdiving’ is based on the idea that variables with a larger fractional part (‘candsfrac’) are more in need of rounding. The function also takes into account the number of locks for rounding down (‘nlocksdown’) and up (‘nlocksup’), penalizing variables that have more locks in one direction. The objective function value (‘obj’) is used to give preference to variables that have a higher impact on the objective. Additionally, the pseudo costs (‘pscostdown’ and ‘pscostup’) are considered to favor variables that are more likely to lead to a better solution when rounded. The function also gives a boost to binary variables (‘isBinary’) since they are more critical in many MILP problems. The score is computed as a weighted sum of these factors, and the ‘roundup’ decision is made based on comparing the pseudo costs and the direction with fewer locks. 
'''

glm41_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Weighting factors
    w_frac = 1.5
    w_locks = 0.8
    w_obj = 1.0
    w_pscost = 1.2
    w_binary = 1.1

    # Calculate the score based on the fractional part
    score = w_frac * candsfrac

    # Penalize based on the number of locks
    score -= w_locks * (nlocksdown + nlocksup)

    # Incorporate the objective function value
    score += w_obj * (obj / objnorm)

    # Consider pseudo costs
    score += w_pscost * (pscostdown if mayrounddown else 0)
    score -= w_pscost * (pscostup if mayroundup else 0)

    # Give a bonus to binary variables
    if isBinary:
        score *= w_binary

    # Determine the rounding direction
    roundup = pscostup < pscostdown or (pscostup == pscostdown and nlocksdown > nlocksup)

    return score, roundup

'''

glm42_des = '''
The logic of the new score function ‘myheurdiving’ is designed to prioritize variables that have a significant impact on the objective function and are likely to lead to a feasible solution with minimal impact on the overall solution quality. The function penalizes variables that cannot be rounded in both directions due to feasibility constraints, as these may require additional exploration. It also takes into account the pseudo costs associated with rounding in each direction, the number of locks that prevent rounding, and the norm of the objective function vector, which gives an indication of the scale of the objective function coefficients.

The score is calculated by considering the following components:

The absolute value of the objective function coefficient, as a measure of the variable’s impact on the objective.
The pseudo costs for rounding up and down, with a preference for the direction with the lower pseudo cost.
A penalty for each lock that prevents rounding in a particular direction.
A penalty for variables that are not binary, as binary variables are often more critical in integer programming.
A factor that encourages rounding of variables with a fractional part close to 0.5, as these are more likely to have a significant impact on the solution.
The rounding direction is determined by comparing the pseudo costs and considering the feasibility of rounding in each direction. The function outputs a score and a boolean indicating whether to round up or down.
'''

glm42_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Penalize variables that cannot be rounded in both directions
    if not mayrounddown and not mayroundup:
        return -float('inf'), False

    # Calculate the impact of the variable on the objective
    obj_coeff_weight = abs(obj) / objnorm

    # Calculate the pseudo cost component, favoring the direction with lower pseudo cost
    pseudo_cost_diff = pscostup - pscostdown
    rounding_up = pscostdown < pscostup

    # Penalize variables with locks
    lock_penalty = nlocksdown + nlocksup

    # Penalize non-binary variables
    binary_penalty = 0 if isBinary else 1

    # Encourage rounding variables with a fractional part close to 0.5
    fractional_encouragement = 1 - abs(candsfrac - 0.5)

    # Calculate the score
    score = (obj_coeff_weight + pseudo_cost_diff - lock_penalty - binary_penalty) * fractional_encouragement

    return score, rounding_up

'''




gpt41_des = '''
The new scoring function, 'myheurdiving', uses a combination of factors derived from the variable's properties in the linear programming relaxation and its impact on the objective function. The score is computed based on the fractional part of the variable's solution, the feasibility of rounding directions, the pseudo costs, and the objective function value. The function prioritizes variables that have a significant impact on the objective function and where a feasible rounding direction exists. The score is increased by the pseudo cost for the feasible direction, adjusted by the number of locks, and normalized by the objective function norm. The rounding direction is determined based on which direction has a lesser impact on the objective function (lower pseudo cost) and fewer locks, favoring 'roundup' for binary variables close to their upper bound.
'''

gpt41_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the base score based on the objective impact and feasibility
    score = 0
    roundup = False

    # Adjust score based on rounding feasibility and pseudo costs
    if mayrounddown and mayroundup:
        # Choose rounding direction based on lower pseudo cost and number of locks
        if (pscostdown + nlocksdown) < (pscostup + nlocksup):
            score = (1 - candsfrac) * obj - pscostdown / objnorm
            roundup = False
        else:
            score = candsfrac * obj - pscostup / objnorm
            roundup = True
    elif mayrounddown:
        score = (1 - candsfrac) * obj - pscostdown / objnorm
        roundup = False
    elif mayroundup:
        score = candsfrac * obj - pscostup / objnorm
        roundup = True

    # Additional heuristic for binary variables
    if isBinary:
        if candsol > 0.5:
            roundup = True
        else:
            roundup = False

    return score, roundup

'''

gpt42_des = '''
The new scoring function 'myheurdiving' leverages a combination of mathematical heuristics and pragmatic decision-making based on the characteristics of the LP relaxation solution and variable attributes. This function assesses whether rounding up or down yields a higher score based on feasibility, influence on the objective function, and other problem-specific criteria. The logic is to maximize the decrease in the objective function while ensuring that the rounding maintains feasibility. If rounding up is feasible and aligns with decreasing the objective value more effectively or with fewer locks, it's preferred. Otherwise, rounding down is considered. The score is influenced by the pseudo costs which estimate the impact on the objective function, the proximity to the binary threshold for binary variables, and the number of locks which signify potential constraints.
'''

gpt42_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Decide rounding direction based on feasibility and expected impact on the objective
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    else:
        # If both directions are feasible, choose based on lesser locks and lower pseudo cost
        if pscostup < pscostdown:
            roundup = True
        else:
            roundup = False

    # Calculate score based on chosen rounding direction
    if roundup:
        score = -pscostup + obj - (nlocksup * 0.1) + (1 - candsfrac) * 100
    else:
        score = -pscostdown + obj - (nlocksdown * 0.1) + candsfrac * 100

    # Enhance the score for binary variables closer to their bounds
    if isBinary:
        if roundup:
            score += (1 - candsol) * 50  # Prefer rounding up closer to 1 for binaries
        else:
            score += candsol * 50       # Prefer rounding down closer to 0 for binaries

    return score, roundup

'''

gpt43_des = '''
The new scoring function myheurdiving selects a rounding direction and calculates a score for a variable based on a variety of factors from the LP relaxation and the problem's structure. The decision on whether to round up or down is determined first by checking feasibility constraints for rounding directions (mayrounddown, mayroundup). If both directions are feasible, the function prioritizes rounding to the nearest integer. The scoring mechanism combines the fractional part's closeness to the nearest integer, adjusted by the variable's impact on the objective and other penalties or boosts like pseudo costs and locks, ensuring that variables causing significant change upon rounding are prioritized or avoided based on strategic need. The function returns both the score and the chosen rounding direction.
'''

gpt43_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    else:
        # Prefer rounding to the nearest integer if both directions are feasible
        roundup = candsfrac >= 0.5
    
    # Calculate score based on various factors
    distance_to_int = min(candsfrac, 1 - candsfrac)  # Distance to the nearest integer
    obj_impact = (obj / objnorm) if objnorm != 0 else obj  # Normalized objective impact
    
    if roundup:
        score = (1 - candsfrac) * obj_impact  # Weight by distance to next integer and impact on objective
        score -= pscostup  # Subtract pseudo cost of rounding up
        score -= nlocksup * 0.1  # Penalize based on locks that discourage rounding up
    else:
        score = candsfrac * obj_impact
        score -= pscostdown
        score -= nlocksdown * 0.1
    
    # Adjust score for binary variables as they are often more critical
    if isBinary:
        score *= 1.5
    
    return score, roundup

'''

gpt44_des = '''
The new scoring function, myheurdiving, evaluates each variable based on its characteristics such as feasibility of rounding, impact on the objective function, and behavior under previous relaxations. The decision on rounding direction is initially based on the feasibility (mayroundup, mayrounddown) and the variable's potential impact on cost (pscostup, pscostdown). The score itself is a weighted sum where the fractional part of the variable, its significance in the objective function (normalized by the Euclidean norm of the objective vector), and its behavior in past solutions are key components. Binary variables are handled with a bias towards rounding to 1 due to their nature. Locks on rounding directions are used to penalize or favor certain directions based on past difficulties in rounding.
'''

gpt44_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if mayrounddown and mayroundup:
        # Choose direction based on the least pseudo cost and feasibility
        roundup = pscostup < pscostdown
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        # Fallback if neither direction is feasible
        roundup = pscostup < pscostdown

    # Calculate score considering all factors
    direction_bias = -1 if roundup else 1  # Favor lower pseudo costs
    lock_penalty = (nlocksup if roundup else nlocksdown) * 0.5  # Penalize based on locks
    obj_impact = (obj / objnorm) * (candsol if roundup else -candsol)  # Impact of obj in chosen direction
    fractional_bias = candsfrac if roundup else (1 - candsfrac)  # Favor rounding towards whole numbers
    historical_bias = rootsolval * 0.2  # Weight by root solution value
    binary_bias = 0.2 if isBinary and roundup else 0  # Extra push for binary variables to 1

    score = obj_impact + fractional_bias + historical_bias + binary_bias - lock_penalty + direction_bias * (pscostup if roundup else pscostdown)

    return score, roundup

'''

gpt41_mu_des = '''
The new scoring function, 'myheurdiving', takes into consideration multiple factors such as the feasibility of rounding directions, fractional part of the solution value, objective function impact, pseudo costs, and binary variable properties. The score is calculated based on the impact of the variable on the objective function, the pseudo costs associated with rounding in different directions, the number of locks for rounding down and up, and the objective function norm. The function also includes a heuristic for binary variables, favoring 'roundup' for values close to their upper bound.

'''

gpt41_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False

    # Adjust score based on rounding feasibility and pseudo costs
    if mayrounddown and mayroundup:
        if (pscostdown + nlocksdown) < (pscostup + nlocksup):
            score = (1 - candsfrac) * obj - pscostdown / objnorm
            roundup = False
        else:
            score = candsfrac * obj - pscostup / objnorm
            roundup = True
    elif mayrounddown:
        score = (1 - candsfrac) * obj - pscostdown / objnorm
        roundup = False
    elif mayroundup:
        score = candsfrac * obj - pscostup / objnorm
        roundup = True

    # Additional heuristic for binary variables
    if isBinary:
        if candsol > 0.5:
            roundup = True
        else:
            roundup = False

    return score, roundup
'''

gpt42_mu_des = '''
The new score function 'myheurdiving' evaluates the feasibility and impact of rounding a variable up or down based on various factors such as pseudo cost, objective function value, number of locks, solution value, etc. It penalizes actions that limit exploration (mayrounddown/mayroundup) and rewards actions that contribute positively to reducing the objective value while maintaining feasibility. The score calculation incorporates the characteristics of the variable, including binary nature, proximity to bounds, and sparsity, to make an informed decision on the rounding direction.

'''

gpt42_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Decide rounding direction based on various factors
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    else:
        # Choose based on a weighted combination of factors
        if pscostup / (1 + nlocksup) >= pscostdown / (1 + nlocksdown):
            roundup = True
        else:
            roundup = False

    # Calculate score with consideration of variable characteristics
    score = -pscostup + obj - (nlocksup * 0.1) - (rootsolval * 10) + (objnorm / (1 + nNonz))

    # Adjust score for binary variables towards their bounds
    if isBinary:
        if roundup:
            score += (1 - candsol) * 50 
        else:
            score += candsol * 50

    return score, roundup
'''

gpt43_mu_des = '''
The new scoring function myheurdiving penalizes rounding directions if they are feasible, encourages exploration by penalizing variables that can be easily rounded, and prioritizes variables that have a significant impact on the objective. It adjusts the score based on the distance to the nearest integer, the impact on the objective function, pseudo costs, locks, the variable type, and other relevant factors.

'''

gpt43_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    else:
        # Prefer rounding to the nearest integer if both directions are feasible
        roundup = candsfrac >= 0.5
    
    # Calculate score based on various factors
    distance_to_int = min(candsfrac, 1 - candsfrac)  # Distance to the nearest integer
    obj_impact = (obj / objnorm) if objnorm != 0 else obj  # Normalized objective impact
    
    if roundup:
        score = (1 - candsfrac) * obj_impact  # Weight by distance to next integer and impact on objective
        score -= pscostup  # Subtract pseudo cost of rounding up
        score -= nlocksup * 0.1  # Penalize based on locks that discourage rounding up
    else:
        score = candsfrac * obj_impact
        score -= pscostdown
        score -= nlocksdown * 0.1
    
    # Adjust score for binary variables as they are often more critical
    if isBinary:
        score *= 1.5
    
    return score, roundup
'''

gpt44_mu_des = '''
The new scoring function, myheurdiving, evaluates each variable based on a combination of factors including the feasibility of rounding, impact on the objective function, historical behavior, and characteristics specific to binary variables. The function penalizes directions that limit exploration and favor directions that contribute positively to the objective value. It considers the fractional part of the solution, the objective function's normalized impact, pseudo cost values, previous rounding locks, as well as the historical solution value and the variable's uniqueness based on the number of nonzero entries.

'''

gpt44_mu_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if mayrounddown and mayroundup:
        # Choose direction balancing feasibility and impact
        roundup = pscostup < pscostdown and nlocksdown == 0
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        # Fallback to avoid infeasibility
        roundup = pscostup < pscostdown

    # Calculate score considering various factors
    direction_bias = -1 if roundup else 1
    lock_penalty = (nlocksup if roundup else nlocksdown) * 0.5
    obj_impact = (obj / objnorm) * (candsol if roundup else -candsol)
    fractional_bias = candsfrac if roundup else (1 - candsfrac)
    historical_bias = rootsolval * 0.2
    binary_bias = 0.2 if isBinary and roundup else 0
    uniqueness_bias = 0.1 / (nNonz + 1)  # Penalize highly unique variables

    score = obj_impact + fractional_bias + historical_bias + binary_bias - lock_penalty + direction_bias * (pscostup if roundup else pscostdown) - uniqueness_bias

    return score, roundup
'''




claude31_des = '''
The score function aims to prioritize variables with a high potential impact on the objective function while considering feasibility and exploration. The rounding direction is first determined based on the pseudo-cost values and objective function coefficients. The variable's score is then calculated by combining factors such as the fractional part, objective coefficient, and number of non-zero entries, with penalties for variables that cannot be rounded in the chosen direction. The goal is to select variables that can significantly improve the objective while maintaining feasibility and promoting exploration of the solution space.
'''

claude31_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction based on pseudo-costs and objective coefficient
    if pscostup < pscostdown and obj >= 0:
        roundup = True
    elif pscostup > pscostdown and obj <= 0:
        roundup = False
    else:
        roundup = obj >= 0

    # Calculate score
    if roundup:
        if not mayroundup:
            score = -1e9  # Penalize variables that cannot be rounded up
        else:
            score = candsfrac * obj * nNonz / (objnorm + 1e-9)  # Higher score for larger fractional part, objective coefficient, and non-zero entries
            score -= nlocksup  # Penalize variables with more locks for rounding up
    else:
        if not mayrounddown:
            score = -1e9  # Penalize variables that cannot be rounded down
        else:
            score = (1 - candsfrac) * abs(obj) * nNonz / (objnorm + 1e-9)  # Higher score for smaller fractional part, larger objective coefficient, and more non-zero entries
            score -= nlocksdown  # Penalize variables with more locks for rounding down

    return score, roundup
'''

claude32_des = '''
The scoring function first determines the rounding direction based on the objective coefficient, pseudo costs, and fractional part of the variable's solution value. It then calculates the score by considering the number of potential locks, the Euclidean norm of the objective coefficients, and whether the variable is binary or not. The score is higher for variables that are closer to being integral, have fewer potential locks, and have a larger objective coefficient norm if the variable is binary. This aims to prioritize variables that are closer to being integral and have a larger impact on the objective value.
'''

claude32_code = '''
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    roundup = False
    
    # Determine rounding direction based on objective, pseudo costs, and fractional part
    if obj < 0 and pscostdown < pscostup:
        roundup = False
    elif obj > 0 and pscostup < pscostdown:
        roundup = True
    else:
        roundup = candsfrac > 0.5
    
    # Calculate score
    if roundup:
        lockpenalty = nlocksup
        frac = 1 - candsfrac
    else:
        lockpenalty = nlocksdown
        frac = candsfrac
    
    if isBinary:
        score = frac * (1 + objnorm) / (1 + lockpenalty)
    else:
        score = frac / (1 + lockpenalty)
    
    return score, roundup
'''

claude33_des = '''
The new score function 'myheurdiving' is designed to balance exploration and exploitation. It first determines the rounding direction by considering the fractional part of the variable's solution, the number of locks for rounding up/down, and the pseudo-costs. If rounding up is preferred, the score prioritizes variables with larger objective coefficients and solution values, but penalizes variables with larger pseudo-costs for rounding up. If rounding down is preferred, the score prioritizes variables with smaller objective coefficients and solution values, but penalizes variables with larger pseudo-costs for rounding down. Additional factors like the number of non-zeros and whether the variable is binary are also considered.
'''

claude33_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if candsfrac > 0.5 or (candsfrac == 0.5 and nlocksup < nlocksdown) or (candsfrac == 0.5 and nlocksup == nlocksdown and pscostup < pscostdown):
        roundup = True
        score = obj * candsol / objnorm - pscostup * (1 - candsfrac) * (1 + isBinary) - (1 - mayroundup) * 1e6
    else:
        roundup = False
        score = -obj * candsol / objnorm - pscostdown * candsfrac * (1 + isBinary) - (1 - mayrounddown) * 1e6
    
    score += (1 - abs(candsfrac - 0.5)) * 100 + nNonz * 0.1
    
    return score, roundup
'''

claude34_des = '''
The proposed score function first determines the rounding direction based on the 'mayrounddown' and 'mayroundup' features, which indicate whether it is possible to round the variable down or up while maintaining feasibility. If both rounding directions are possible, the function considers the 'candsfrac' feature, which represents the fractional part of the variable's solution value in the LP relaxation. The function favors rounding the variable in the direction that reduces the fractional part, as this is likely to lead to a more integer-feasible solution.

Additionally, the function incorporates the 'nlocksdown' and 'nlocksup' features, which represent the number of locks for rounding the variable down or up. The function penalizes variables with a higher number of locks, as rounding these variables may be more difficult and lead to infeasibility.

The function also considers the objective function information, including the 'obj' feature (the objective function value of the variable) and the 'objnorm' feature (the Euclidean norm of the objective function vector). The function favors variables with a higher objective function value and a lower Euclidean norm, as these variables are likely to have a greater impact on the overall objective function.

Finally, the function takes into account the 'pscostdown' and 'pscostup' features, which represent the variable's pseudo-cost value for the given change in the variable's LP value. The function favors variables with a higher pseudo-cost value, as these variables are likely to have a more significant impact on the overall solution quality.
'''

claude34_code = '''
import numpy as np

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine the rounding direction
    if mayrounddown and mayroundup:
        roundup = candsfrac >= 0.5
    elif mayrounddown:
        roundup = False
    else:
        roundup = True
    
    # Calculate the score
    score = obj / objnorm
    score -= nlocksdown * 0.1
    score -= nlocksup * 0.1
    score += pscostdown if not roundup else pscostup
    
    return score, roundup
'''

ea_cauc1_des = '''
The new score function evaluates the variable's potential rounding direction and score by considering various factors such as limited rounding options, fractionality of the solution value, impact on the objective function, locking constraints, pseudo cost values, previous solution value, number of non-zero entries, and variable type. It aims to strike a balance between exploration and exploitation by penalizing constrained variables, incentivizing impactful variables, and rewarding binary variables.
'''

ea_cauc1_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    
    # Penalize limited rounding options
    if not mayrounddown or not mayroundup:
        score -= 100
    
    # Determine rounding direction based on the fractional part
    roundup = candsfrac >= 0.5
        
    # Calculate score based on the given features
    score += candsfrac * 10
    score += obj / objnorm * 50
    score -= nlocksdown + nlocksup * 5
    score -= pscostdown + pscostup * 30
    
    if rootsolval == 0:
        score -= 10
    
    score -= nNonz * 5
    
    # Reward binary variables
    if isBinary:
        score += 20

    return score, roundup
'''

ea_cauc2_des = '''
The new score function calculates the variable's score by considering a weighted combination of different features. It penalizes variables with high fractional parts, pseudo cost values, and low locking constraints, while prioritizing variables with high objective function values, Euclidean norm, and number of nonzero entries. It also takes into account whether the variable is binary and the solution value in the last root node's relaxation.
'''

ea_cauc2_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.5 * candsfrac / (pscostdown + pscostup + 1) * (1 + nlocksdown) * (1 + nlocksup) * (obj + objnorm) * (1 + nNonz) * (1 if isBinary else 0.5)
    
    if mayrounddown or mayroundup:
        score -= 0.1
        
    if rootsolval > 0:
        score += rootsolval * 0.5
    
    roundup = True if candsol > 0.5 else False
    
    return score, roundup
'''

ea_cauc3_des = '''
The new score function for the diving heuristic evaluates variable score based on various factors such as fractional part, objective function impact, pseudo cost values, solution values, and data characteristics like binary nature and number of non-zero entries. It encourages simplicity, penalizes complexity, and favors feasible binary variables, aiming to strike a balance between exploration and exploitation in the rounding decision process.

'''

ea_cauc3_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = candsfrac - 0.5*(mayrounddown + mayroundup)
    score -= obj/(1+objnorm)
    score -= (0.5*pscostdown + 0.5*pscostup)                                                      
    score -= min(rootsolval * 0.4, 6)
    score -= 5/nNonz
    score += 100 if isBinary else -50                                               
                                                    
    roundup = True if candsfrac >= 0.3 else False                                            
    
    return score, roundup
'''

ea_cauc4_des = '''
The logic of the new score function is as follows:
1. Initialize the score to zero.
2. If the variable is not binary or not feasible to be rounded down or up (mayrounddown=False and mayroundup=False), penalize the variable by subtracting a large value from the score.
3. If the variable is fractional (candsfrac > 0) and mayrounddown or mayroundup is True:
    a. Calculate the fractional score by multiplying the absolute value of the fractional part with the square root of the number of locks for rounding down/up.
    b. Add the fractional score to the variable's score.
4. If the variable is binary (isBinary=True):
    a. If the variable has more locks for rounding down (nlocksdown) than rounding up (nlocksup), set the roundup to False.
    b. Otherwise, set the roundup to True.
5. If the variable is not binary:
    a. If the pseudo cost value for rounding down (pscostdown) is greater than the pseudocost value for rounding up (pscostup), set the roundup to False.
    b. Otherwise, set the roundup to True.
6. Return the variable's score and the roundup value.
'''

ea_cauc4_code = '''
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
  
    if not isBinary or (not mayrounddown and not mayroundup):
        score -= 1000000.0 # Penalize variables that cannot be rounded down or up

    if candsfrac > 0 and (mayrounddown or mayroundup):
        frac_score = abs(candsfrac) * math.sqrt(nlocksdown + nlocksup) # Calculate the fractional score
        score += frac_score

    if isBinary:
        if nlocksdown > nlocksup:
            roundup = False
        else:
            roundup = True
    else:
        if pscostdown > pscostup:
            roundup = False
        else:
            roundup = True

    return score, roundup
'''

ea_cauc5_des = '''
The new score function penalizes variables that are easily roundable, have high objective values, or binary variables that are not at extreme values. It prioritizes variables with high fractional parts and low pseudo costs, considering the number of locks, the Euclidean norm of the objective function vector, the solution value in the last root node's relaxation, and the number of nonzero entries in the variable. The function aims to balance exploration and exploitation while taking into account various factors that contribute to the variable's importance in the MILP problem.

'''

ea_cauc5_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, 
                 obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = 0
    
    # Penalize easily roundable variables
    if candsfrac < 0.5:
        score -= candsfrac
    if candsfrac == 1:
        score -= 0.2
    if candsfrac == 0:
        score += 0.2
    
    # Penalize high objective values
    if obj > 0.5:
        score -= 0.5 * obj
    
    # Penalize binary variables not at extreme values
    if isBinary and (candsol != 0 and candsol != 1):
        score -= 0.5
        
    # Prioritize variables with high fractional parts
    score += candsfrac
    
    # Consider the number of locks
    score -= nlocksdown * 0.05
    score -= nlocksup * 0.05
    
    # Consider the Euclidean norm of the objective function vector
    if objnorm > 1:
        score += 0.2
    
    # Consider the solution value in the last root node's relaxation
    if rootsolval != 0:
        score += rootsolval
    
    # Consider the number of non-zero entries in the variable
    if nNonz > 0:
        score += nNonz * 0.1
    
    roundup = True if score > 0 else False   # Rounding direction based on the calculated score
    
    return score, roundup
'''



ea_setc1_des = '''
The new scoring function penalizes variables with limited rounding options, high fractional parts, low pseudo costs, and lower objective function norms, while rewarding variables with high objective function values, a higher number of non-zero entries, and binary type variables. It considers the potential exploration needed for variables that can be rounded up or down while also prioritizing variables with significant impact on the objective function and non-zero entries.

'''

ea_setc1_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = (obj + nNonz + 1/pscostup) - (1/candsfrac + pscostdown + 1/objnorm) * (nlocksdown + nlocksup)
    
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    elif mayrounddown and mayroundup:
        roundup = score > 0
    
    return score, roundup
'''

ea_setc2_des = '''
The new scoring function penalizes variables with limited rounding options, high fractional parts, low pseudo costs, and lower objective function norms, while rewarding variables with high objective function values, a higher number of non-zero entries, and binary type variables. It considers the potential exploration needed for variables that can be rounded up or down while also prioritizing variables with significant impact on the objective function and non-zero entries. Additionally, it incorporates the information from the previous root node relaxation solution to adjust the score accordingly.

'''

ea_setc2_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    if rootsolval == 0:
        rootsolval = 0.01  # Avoid division by zero
    
    score = (obj * rootsolval + nNonz) * 1/(pscostup + 1) - (1/candsfrac + pscostdown + 1/objnorm) * (nlocksdown + nlocksup)
    
    if mayroundup and not mayrounddown:
        roundup = True
    elif mayrounddown and not mayroundup:
        roundup = False
    elif mayrounddown and mayroundup:
        roundup = score > 0
    
    return score, roundup
'''

ea_setc3_des = '''

The new score function prioritizes variables based on their likelihood of becoming feasible integral solutions. It combines features such as the fractional part of the solution value, the number of locks for each rounding direction, the variable's significance in the objective function, the pseudo cost values, the solution value in the last root node's relaxation, the number of nonzero entries in the variable, and whether the variable is binary. It also penalizes variables that have limited rounding options to encourage more exploration and adds a penalty for having a high objective value to balance exploration and exploitation.

'''

ea_setc3_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine the rounding direction
    if mayrounddown and not mayroundup:
        roundup = False
    elif mayroundup and not mayrounddown:
        roundup = True
    else:
        roundup = obj > 0  # Choose rounding direction based on the sign of the objective function value

    # Calculate the score with penalty for limited rounding options and high objective value
    rounding_penalty = 0.1 if (not mayrounddown and not mayroundup) else 0.05  # Penalty for limited rounding options
    score = (candsfrac * objnorm) / (1 + nlocksdown + nlocksup) + (0.5 * (pscostdown + pscostup)) + rootsolval + (0.1 * nNonz) - obj * rounding_penalty + (5 if isBinary else 0) / (1 + objnorm)

    return score, roundup
'''

ea_setc4_des = '''
The new score function prioritizes variables that have a high likelihood of becoming feasible integral solutions by penalizing limited rounding options, prioritizing variables with a high fractional part and those with a high number of locks preventing rounding. It also considers the variable's significance in the objective function, the pseudo cost values, the solution value in the last root node's relaxation, the number of nonzero entries in the variable, and whether the variable is binary. The function combines these features to calculate a score that reflects the potential for the variable to contribute to a feasible integral solution.

'''

ea_setc4_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = ((candsfrac * objnorm) / (1 + nlocksdown + nlocksup) + pscostdown + pscostup) - (1 if mayrounddown or mayroundup else 0)
    roundup = candsfrac > 0.5 or mayroundup

    return score, roundup
'''

ea_faci1_des = '''
The new score function combines multiple factors such as the feasibility of rounding, fractional solution value, objective function value, pseudo costs, number of locks, Euclidean norm of the objective function vector, number of nonzero entries in the variable, and type of variable to determine the best score and rounding direction. It penalizes variables that are hard to round down/up feasibly while considering the impact on the objective function and the overall problem.
'''

ea_faci1_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    penalty = 0.0
    
    # Penalize if rounding down or up is not possible
    if not mayrounddown:
        penalty += 0.5
    if not mayroundup:
        penalty += 0.5

    # Calculate score based on a combination of factors
    score = (candsfrac / (nNonz + 1)) * (obj / (abs(pscostdown) + abs(pscostup) + 1)) - penalty * 0.2

    # Determine rounding direction based on score
    roundup = False
    if score > 0:
        roundup = True

    return score, roundup
'''

ea_faci2_des = '''
The new score function's logic is as follows:

1. If 'mayrounddown' is False or 'mayroundup' is False, penalize the variable by setting its score to a very low value (-inf).
2. Otherwise, calculate the score based on the following factors:
   a. Penalize the variable if its fractional part 'candsfrac' is close to 0 or 1, as it indicates that rounding may not significantly improve the feasibility.
   b. Penalize the variable if its solution value 'candsol' is close to its lower or upper bound, as it indicates less room for rounding.
   c. Penalize the variable if it has a high number of locks for rounding down 'nlocksdown' or rounding up 'nlocksup', as it suggests that previous rounding directions did not lead to feasible solutions.
   d. Increase the score if the variable's objective function value 'obj' is large compared to other variables, as it indicates that maximizing the variable may improve the overall objective function value.
   e. Increase the score if the Euclidean norm of the objective function vector 'objnorm' is high, as it indicates that maximizing the variable may have a significant impact on the objective function.
   f. Increase the score if the variable's pseudo cost value 'pscostdown' or 'pscostup' is high, as it suggests that the variable has a significant impact on the LP relaxation solution.
   g. Increase the score if the variable's solution value in the last root node's relaxation 'rootsolval' is close to 1, as it indicates that rounding the variable up may lead to a closer feasible integral solution.
   h. Increase the score if the variable has a high number of nonzero entries 'nNonz', as it suggests that the variable plays a crucial role in the problem.
   i. Increase the score if the variable is binary 'isBinary', as it indicates that rounding the variable may lead to a feasible integral solution.
'''

ea_faci2_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm,
                 pscostdown, pscostup, rootsolval, nNonz, isBinary):

    if not mayrounddown or not mayroundup:
        score = float('-inf')
        roundup = False
    else:
        score = 0
        roundup = True

        if 0.01 <= candsfrac <= 0.99:
            score -= 0.01

        if 0.95 * candsol <= candsol <= 1.05 * candsol:
            score -= 0.1

        score -= 0.1 * (nlocksdown + nlocksup)

        score += obj

        score += 0.1 * objnorm

        score += 0.1 * (pscostdown + pscostup)

        if 0.95 <= rootsolval <= 1.05:
            score += 0.1

        score += 0.05 * nNonz

        if isBinary:
            score += 0.1

    return score, roundup
'''

ea_faci3_des = '''
The new score function's logic aims to consider multiple factors to determine the variable's score and rounding direction. It penalizes variables that may be rounded down/up and stay feasible while prioriti
zing variables with a larger fractional part and a smaller number of locks for rounding down/up. The function also takes into account the objective function value, objective function vector norm, pseudo cos
t values, solution value in the last root node's relaxation, number of nonzero entries, and binary type indicator to calculate the score. Based on the score, the function determines whether to round the variable up or not.
'''

ea_faci3_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 0.5  # Penalty term for variables that may be rounded down/up and stay feasible
    score = candsfrac - penalty*(mayrounddown + mayroundup) + (1 / (nlocksdown + 1)) + (1 / (nlocksup + 1)) + obj + (1 / (objnorm + 1)) + (1 / (pscostdown + 1)) + (1 / (pscostup + 1)) + rootsolval + (1 / (nNonz + 1))

    if isBinary:
        score += 1

    roundup = candsol >= 0.5   

    return score, roundup
'''

ea_faci4_des = '''
The logic of the new score function is to prioritize variables that have a lower fractional part and a higher solution value in the LP relaxation. It penalizes variables that have a high number of locks for rounding down/up and variables that are binary or have a low number of nonzero entries. The score is also influenced by the objective function value and its Euclidean norm. The function calculates the score for each variable and determines the rounding direction based on the score.

The scoring function can be implemented using the following steps:
1. Initialize the score as zero.
2. If 'mayrounddown' or 'mayroundup' is False, return score as -infinity.
3. If 'candsfrac' is zero, return score as -infinity.
4. If 'nlocksdown' or 'nlocksup' is greater than zero, return score as -infinity.
5. Calculate the score as follows:
   - Add 'candsfrac' to the score.
   - Subtract 'candsol' from the score.
   - Multiply 'obj' by 'objnorm' and add it to the score.
   - Divide 'pscostdown' by 'pscostup' and subtract it from the score.
   - Subtract 'rootsolval' from the score.
   - Subtract 'nNonz' from the score.
   - If 'isBinary' is True, subtract 100 from the score.
6. Determine the rounding direction (roundup) based on 'candsfrac' and 'candsol'. If 'candsfrac' is greater than 0.5, set 'roundup' to False, otherwise set it to True.
7. Return the score and roundup.
'''

ea_faci4_code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    
    if not mayrounddown or not mayroundup:
        return -float('inf'), False
    if candsfrac == 0:
        return -float('inf'), False
    if nlocksdown > 0 or nlocksup > 0:
        return -float('inf'), False

    score += candsfrac
    score -= candsol
    score += obj * objnorm
    score -= pscostdown / pscostup
    score -= rootsolval
    score -= nNonz
    if isBinary:
        score -= 100

    roundup = False if candsfrac > 0.5 else True
    
    return score, roundup
'''



setc_gpt3516k_1010_train50 = '''
<start_des>
The new score function is designed to prioritize variables that have a higher probability of rounding up and contribute more to improving the objective function. The score is determined by a combination of several factors: the fractional part of the solution value, the number of locks for rounding down and rounding up, the normalized objective function value, the pseudo cost for rounding up, the number of nonzero entries in the variable, and whether the variable is binary. The score is penalized if it is not possible to round the variable down or if rounding up is not beneficial. The rounding direction is determined based on whether rounding up is more advantageous or rounding down is not allowed.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    
    if mayroundup and not mayrounddown:
        score -= 1
    
    score += candsfrac * 10
    
    if obj > 0:
        score += objnorm
    
    score += nlocksup * 0.5
    
    if pscostup != 0:
        score += 1 / pscostup
    
    score += nNonz * 0.1
    
    if isBinary and obj > 0:
        score += 1
    
    if score < 0:
        score = 0
    
    roundup = True if score > 0 else False
    
    return score, roundup
</end_code>
'''

setc_gpt35_1010_train50 = '''
<start_des>
The new score function 'myheurdiving' prioritizes variables that have a high fractional part of the solution value, a high number of locks for rounding, a lower pseudo cost value for rounding, a low number of nonzero entries, and a non-binary type. The objective function value and its Euclidean norm are also considered in the scoring. Variables with a high root node relaxation value are penalized. The function determines the rounding direction based on these features to guide the diving heuristic towards selecting promising variables for rounding towards an integral solution.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = candsfrac * (1 + nlocksdown + nlocksup) / (1 + pscostdown + pscostup) / (1 + nNonz) * objnorm / max(1, rootsolval)
    
    roundup = True if candsfrac >= 0.5 or (mayroundup and not mayrounddown) else False
    
    return score, roundup
</end_code>

'''

setc_claude3son_1010_train50 = '''
<start_des>
The scoring function considers both the objective function impact and the feasibility impact when deciding the variable to round and the rounding direction. If rounding down is feasible, it prioritizes variables with larger objective coefficients, smaller fractional parts, and lower pseudo-costs for rounding down. If rounding up is feasible, it prioritizes variables with smaller objective coefficients, larger fractional parts, and lower pseudo-costs for rounding up. The function also penalizes variables with more locks (nlocksdown or nlocksup) to encourage exploration.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if mayrounddown:
        scoredown = obj / objnorm - candsfrac - pscostdown / 1000 - nlocksdown / 100
    else:
        scoredown = -1e9
    
    if mayroundup:
        scoreup = -obj / objnorm + candsfrac - pscostup / 1000 - nlocksup / 100
    else:
        scoreup = -1e9
    
    if scoredown > scoreup:
        score = scoredown
        roundup = False
    else:
        score = scoreup
        roundup = True
    
    return score, roundup
</end_code>
'''

setc_gpt4_1010_train50 = '''
<start_des>
The new `myheurdiving` function is designed to streamline decision-making in MILP diving heuristics by balancing multiple aspects of variables and their situational contexts. It leverages both the fractional part of the variable's solution and its proximity to the root relaxation, allowing for strategic rounding decisions that account for potential future solutions. The function also integrates constraint-based penalties, factoring in the difficulty of locking constraints to balance feasibility against objective optimization. Special treatment for binary variables expedites rounding, while the overall scoring system synthesizes urgency, constraint influence, and exploration needs, aiming for an efficient and directed solution path.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction based on various factors
    if isBinary:
        roundup = candsol > 0.5
    else:
        if mayrounddown and mayroundup:
            roundup = pscostup < pscostdown if candsfrac < 0.5 else True
        elif mayrounddown:
            roundup = False
        elif mayroundup:
            roundup = True
        else:
            roundup = pscostup < pscostdown
    
    # Proximity to integer and penalty for rounding direction
    distance_to_integer = min(abs(candsol - int(candsol)), abs(candsol - (int(candsol) + 1)))
    feasibility_penalty = (nlocksdown if not roundup else nlocksup) * 0.1

    # Constraint influence scaled by normalized objective
    constraint_influence = nNonz / (1 + objnorm + 0.01 * obj)
    
    # Final score combines distance, influence, and penalties
    score = (1 - distance_to_integer) * constraint_influence - (feasibility_penalty + (pscostup if roundup else pscostdown))
    if isBinary:
        score *= 1.25  # Prioritize binary rounding
    
    return score, roundup
</end_code>
'''

cauc_gpt3516k_1010_train50 = '''
<start_des>
The logic of the new score function is as follows:
1. Initialize the score to zero.
2. If the variable is not binary or not feasible to be rounded down or up (mayrounddown=False and mayroundup=False), penalize the variable by subtracting a large value from the score.
3. If the variable is fractional (candsfrac > 0) and mayrounddown or mayroundup is True:
    a. Calculate the fractional score by multiplying the absolute value of the fractional part with the square root of the number of locks for rounding down/up.
    b. Add the fractional score to the variable's score.
4. If the variable is binary (isBinary=True):
    a. If the variable has more locks for rounding down (nlocksdown) than rounding up (nlocksup), set the roundup to False.
    b. Otherwise, set the roundup to True.
5. If the variable is not binary:
    a. If the pseudo cost value for rounding down (pscostdown) is greater than the pseudocost value for rounding up (pscostup), set the roundup to False.
    b. Otherwise, set the roundup to True.
6. Return the variable's score and the roundup value.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
  
    if not isBinary or (not mayrounddown and not mayroundup):
        score -= 1000000.0 # Penalize variables that cannot be rounded down or up

    if candsfrac > 0 and (mayrounddown or mayroundup):
        frac_score = abs(candsfrac) * math.sqrt(nlocksdown + nlocksup) # Calculate the fractional score
        score += frac_score

    if isBinary:
        if nlocksdown > nlocksup:
            roundup = False
        else:
            roundup = True
    else:
        if pscostdown > pscostup:
            roundup = False
        else:
            roundup = True

    return score, roundup
</end_code>
'''

cauc_gpt35_1010_train50 = '''
<start_des>
The new score function penalizes variables that are easily roundable, have high objective values, or binary variables that are not at extreme values. It prioritizes variables with high fractional parts and low pseudo costs, considering the number of locks, the Euclidean norm of the objective function vector, the solution value in the last root node's relaxation, and the number of nonzero entries in the variable. The function aims to balance exploration and exploitation while taking into account various factors that contribute to the variable's importance in the MILP problem.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, 
                 obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = 0
    
    # Penalize easily roundable variables
    if candsfrac < 0.5:
        score -= candsfrac
    if candsfrac == 1:
        score -= 0.2
    if candsfrac == 0:
        score += 0.2
    
    # Penalize high objective values
    if obj > 0.5:
        score -= 0.5 * obj
    
    # Penalize binary variables not at extreme values
    if isBinary and (candsol != 0 and candsol != 1):
        score -= 0.5
        
    # Prioritize variables with high fractional parts
    score += candsfrac
    
    # Consider the number of locks
    score -= nlocksdown * 0.05
    score -= nlocksup * 0.05
    
    # Consider the Euclidean norm of the objective function vector
    if objnorm > 1:
        score += 0.2
    
    # Consider the solution value in the last root node's relaxation
    if rootsolval != 0:
        score += rootsolval
    
    # Consider the number of non-zero entries in the variable
    if nNonz > 0:
        score += nNonz * 0.1
    
    roundup = True if score > 0 else False   # Rounding direction based on the calculated score
    
    return score, roundup
</end_code>

'''

cauc_claude3son_1010_train50 = '''
<start_des>
The scoring function aims to prioritize variables that have a significant impact on the objective function and can potentially lead to a feasible integral solution. It considers various features to determine the rounding direction and the corresponding score for each variable. The logic is as follows:

1. If the variable is binary, favor the direction that moves the fractional value closer to the corresponding integral value.
2. For non-binary variables, prioritize the direction that has a lower pseudo-cost and fewer locks.
3. Assign a higher score to variables with a larger absolute objective coefficient and a fractional value closer to the midpoint (0.5).
4. Penalize variables that cannot be rounded in either direction by assigning a lower score.
</end_des>

<start_code>   # 1              2               3       4           5           6       7   8           9           10      11          12      13
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False

    if isBinary:
        if candsfrac < 0.5:
            roundup = False
        else:
            roundup = True
        score = abs(obj) * (1 - abs(candsfrac - (0 if not roundup else 1)))
    else:
        if pscostdown < pscostup and nlocksdown <= nlocksup:
            roundup = False
        else:
            roundup = True
        score = abs(obj) * (1 - abs(candsfrac - 0.5))

    if not mayrounddown and not mayroundup:
        score *= 0.1

    return score, roundup
</end_code>
'''

cauc_gpt4_1010_train50 = '''
<start_des>
The new diving heuristic scoring function aims to prioritize variables with larger objective coefficients and fractional values closer to 0.5, while also considering the pseudo-costs and number of locks. The rounding direction is chosen based on the objective coefficient sign and the fractional value, favoring rounding down for positive coefficients and up for negative coefficients. Additionally, binary variables and variables with fewer nonzero entries are preferred.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = abs(obj) / objnorm
    roundup = False

    if obj > 0:
        score *= (1 - candsfrac) + 0.5 * (1 - math.exp(-pscostdown))
    else:
        score *= candsfrac + 0.5 * (1 - math.exp(-pscostup))
        roundup = True

    score *= (1 + isBinary) / (1 + nNonz)
    score *= (1 + abs(candsfrac - 0.5))
    score *= (1 + (nlocksdown + nlocksup) ** 0.5)

    return score, roundup
</end_code>
'''

faci_gpt3516k_1010_train10 = '''
<start_des>
The logic of the new score function is to prioritize variables that have a lower fractional part and a higher solution value in the LP relaxation. It penalizes variables that have a high number of locks for rounding down/up and variables that are binary or have a low number of nonzero entries. The score is also influenced by the objective function value and its Euclidean norm. The function calculates the score for each variable and determines the rounding direction based on the score.

The scoring function can be implemented using the following steps:
1. Initialize the score as zero.
2. If 'mayrounddown' or 'mayroundup' is False, return score as -infinity.
3. If 'candsfrac' is zero, return score as -infinity.
4. If 'nlocksdown' or 'nlocksup' is greater than zero, return score as -infinity.
5. Calculate the score as follows:
   - Add 'candsfrac' to the score.
   - Subtract 'candsol' from the score.
   - Multiply 'obj' by 'objnorm' and add it to the score.
   - Divide 'pscostdown' by 'pscostup' and subtract it from the score.
   - Subtract 'rootsolval' from the score.
   - Subtract 'nNonz' from the score.
   - If 'isBinary' is True, subtract 100 from the score.
6. Determine the rounding direction (roundup) based on 'candsfrac' and 'candsol'. If 'candsfrac' is greater than 0.5, set 'roundup' to False, otherwise set it to True.
7. Return the score and roundup.

</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    
    if not mayrounddown or not mayroundup:
        return -float('inf'), False
    if candsfrac == 0:
        return -float('inf'), False
    if nlocksdown > 0 or nlocksup > 0:
        return -float('inf'), False

    score += candsfrac
    score -= candsol
    score += obj * objnorm
    score -= pscostdown / pscostup
    score -= rootsolval
    score -= nNonz
    if isBinary:
        score -= 100

    roundup = False if candsfrac > 0.5 else True
    
    return score, roundup
</end_code>

'''

faci_gpt35_1010_train10 = '''
<start_des>
The new score function calculates the variable's score by balancing various factors such as the fractional part of the solution value, LP relaxation solution value, number of locks for rounding, objective function value, Euclidean norm of the objective function vector, pseudo cost values, solution value in the last root node's relaxation, number of non-zero entries, and whether the variable is binary. It penalizes limited rounding possibilities for exploration, rewards higher objective values, promotes feasible solution exploration, and adjusts the score based on the specified features.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    roundup = True if candsfrac >= 0.5 else False
    
    # Calculate the score based on the 13 features
    score = (candsfrac * 0.1) - ((nlocksdown + nlocksup) * 0.2) + (obj * 0.25) - (objnorm * 0.1) - ((pscostdown + pscostup) * 0.25) + (rootsolval * 0.15) + (nNonz * 0.1)
    
    # Penalize limited rounding possibilities for more exploration
    score -= 0.15 if not mayrounddown else 0.1
    score -= 0.15 if not mayroundup else 0.1
    
    # Reward binary variables
    score += 0.3 if isBinary else 0.15
    
    return score, roundup
</end_code>

'''

faci_claude3son_1010_train10 = '''
<start_des>
The scoring function aims to strike a balance between exploration and exploitation by considering objective contribution, fractional value, pseudo-costs, variable type, and rounding potential. It determines the rounding direction based on the objective contribution, fractional value, and pseudo-costs. The score incorporates the chosen rounding direction, objective contribution weighted by the fractional value, pseudo-costs, the number of locks, variable type, and the number of nonzero entries. It prioritizes variables with larger objective contributions, fractional values closer to 0.5, lower pseudo-costs, fewer locks, and binary variables.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    if obj / objnorm < 0:
        roundup = (candsfrac < 0.5) and (pscostup < pscostdown)
    else:
        roundup = (candsfrac >= 0.5) and (pscostup <= pscostdown)

    # Calculate score
    if roundup:
        score = (obj / objnorm) * (1 - candsfrac) - pscostup - nlocksup * 0.2
    else:
        score = (obj / objnorm) * candsfrac - pscostdown - nlocksdown * 0.2

    # Prioritize variables with fractional values closer to 0.5
    score *= 1.8 * abs(candsfrac - 0.5)

    # Prioritize binary variables
    if isBinary:
        score *= 1.4

    # Incorporate the number of nonzero entries
    score *= (1 + nNonz / 10)

    # Penalize variables that cannot be rounded
    if roundup and not mayroundup:
        score = -math.inf
    elif not roundup and not mayrounddown:
        score = -math.inf

    return score, roundup
</end_code>

'''

faci_gpt4_1010_train10 = '''
score:0.62864772160614
<start_des>
The `myheurdiving` function introduced here utilizes a strategic balance between exploring and exploiting in the context of MILP by incorporating a decision-making process based on the variable's contribution to the objective function, the feasibility of rounding, and the complexity of the decision space as indicated by the number of locks. This function uniquely integrates a dynamic scoring adjustment based on the distance from the variable's current fractional value to its nearest integer, enhancing decision precision. It also considers the pseudo costs to estimate the impact of rounding on the LP's objective, combined with an exploration bonus or penalty based on feasibility and the variable type, especially emphasizing binary variables due to their pivotal role in solution space definition. The method strategically toggles rounding direction based on a combination of feasibility and potential objective improvement, aiming for an optimal balance between immediate solution quality and long-term search space exploration.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate the proximity score based on closeness to the nearest integer
    if candsfrac < 0.5:
        proximity_score = 1 - candsfrac
        roundup = mayrounddown
    else:
        proximity_score = candsfrac
        roundup = mayroundup

    # Determine feasibility and calculate penalties
    if not roundup:
        penalty = (0.1 * nNonz) + (0.05 * (nlocksdown if candsfrac < 0.5 else nlocksup))
        score = float('-inf') - penalty  # Strong penalty to foster exploration when rounding is not straightforward
        return score, roundup

    # Compute the normalized objective impact and adjust by pseudo costs and lock impacts
    base_score = (obj / objnorm) * proximity_score
    if roundup:
        score = base_score - (pscostup + nlocksup * 0.05) + (0.1 * rootsolval) - (0.05 * nNonz)
    else:
        score = base_score - (pscostdown + nlocksdown * 0.05) + (0.1 * rootsolval) - (0.05 * nNonz)

    # Apply a significant boost if the variable is binary, reflecting its importance
    if isBinary:
        score += 10  # Boost for binary variables, highlighting their critical role

    return score, roundup
</end_code>
'''

faci_llama3_1010_train10 = '''
<start_des>
The new score function, 'myheurdiving', combines the ideas from the two algorithms and incorporates the 13 features. It calculates a score for each variable based on the possibility of rounding down or up and staying feasible, the fractional part of the solution value, the objective function value, the number of locks, the pseudo cost value, the root solution value, the number of nonzero entries, and the binary variable type. The score is calculated as a weighted sum of these components, and the rounding direction is determined based on the fractional part and the objective function value.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty_down = 0.1 if mayrounddown else 0
    penalty_up = 0.1 if mayroundup else 0
    fraction_score = abs(candsfrac)
    obj_score = obj / objnorm
    pscost_score = max(pscostdown, pscostup)
    lock_score = nlocksdown + nlocksup
    rootsol_score = rootsolval
    nnonz_score = nNonz
    isBinary_score = isBinary
    
    if candsfrac > 0.5:
        roundup = True
        score = (fraction_score * obj_score * (1 + pscost_score)) - (penalty_down + penalty_up + lock_score) + rootsol_score
    else:
        roundup = False
        score = ((1 - fraction_score) * obj_score * (1 + pscost_score)) - (penalty_down + penalty_up + lock_score) + rootsol_score
    
    if isBinary:
        score *= 2
    
    return score, roundup
</end_code>
'''

inds_gpt3516k_1010_train50 = '''
<start_des>
The new score function assigns a base score of 0.0 to the variable. It then adds positive contributions to the score based on different features. It assigns a higher score to variables that have a larger fractional part of the solution value, as these variables have the potential to contribute a greater improvement to the solution. It assigns a higher score to variables with a larger solution value, as these variables may have a greater impact on the solution. It penalizes variables that have a higher number of locks for rounding down and up, as this indicates a more locked state. It assigns a higher score to variables with a higher objective function value and greater Euclidean norm, as these variables contribute more to the overall objective. It assigns a lower score to variables with higher pseudo cost values for rounding down and up. It considers the variable's solution value in the last root node's relaxation and assigns a nonzero score if the root relaxation is not yet completely solved. It assigns a lower score to variables with a higher number of nonzero entries, as these variables may not contribute significantly to the solution. Finally, it considers whether the variable is of binary type and determines whether to round the variable up or not based on the score.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False
     
    score += candsfrac * 3.0  # higher score for larger fractional part
    score += candsol * 0.7  # higher score for larger solution value
    score -= nlocksdown * 2.0  # penalize higher number of locks for rounding down
    score -= nlocksup * 2.0  # penalize higher number of locks for rounding up
    score += obj * 0.5  # higher score for higher objective function value
    score += objnorm * 0.4  # higher score for greater Euclidean norm
    score -= pscostdown * 0.2  # lower score for higher pseudo cost value for rounding down
    score -= pscostup * 0.2  # lower score for higher pseudo cost value for rounding up
     
    if rootsolval != 0:
        score += 0.3  # nonzero score if root relaxation is not completely solved
     
    score -= nNonz * 0.15  # lower score for higher number of nonzero entries
     
    if mayrounddown or mayroundup:
        score -= 0.5  # penalize if rounding down or up is possible
     
    if isBinary:
        roundup = True
     
    return score, roundup
</end_code>
'''

inds_gpt35_1010_train50 = '''
<start_des>
The new score function considers the given features to calculate the variable's score for informed rounding decisions. It penalizes limited rounding options, prioritizes variables with high fractional values and lower pseudo costs. It balances exploration and exploitation by factoring in the objective function value, its norm, solution values, the number of locks, nonzero entries, and binary type.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 0
    penalty += 10 if not mayrounddown else 0
    penalty += 10 if not mayroundup else 0
    
    score = objnorm - penalty + 0.5*candsfrac - (pscostdown + pscostup) - nlocksdown - nlocksup + obj + abs(rootsolval) - 0.1*nNonz - (0.5*isBinary)
    
    roundup = score > 0
    
    return abs(score), roundup
</end_code>
'''

inds_claude3son_1010_train50 = '''
<start_des>
The new score function considers multiple factors to determine the rounding direction and score for each fractional variable. It prioritizes rounding in the direction that minimizes the objective function value, while also considering the feasibility and impact on the remaining problem. The score is designed to encourage exploration by favoring variables with higher fractional parts and lower pseudo-costs, and to prioritize binary variables to exploit their potential impact.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    roundup = False
    score = 0.0

    # Determine rounding direction based on objective function
    if obj < 0:
        roundup = True
    elif obj > 0:
        roundup = False
    else:
        # If objective is zero, prefer rounding down
        roundup = False

    # Adjust score based on fractional part and pseudo-costs
    if roundup:
        score = candsfrac / (1e-9 + pscostup)
    else:
        score = (1 - candsfrac) / (1e-9 + pscostdown)

    # Penalize variables with fewer feasible rounding directions
    if not mayrounddown:
        score /= 2.0
    if not mayroundup:
        score /= 2.0

    # Prioritize binary variables
    if isBinary:
        score *= 2.0

    # Favor variables with higher objective coefficient
    score *= abs(obj) / objnorm

    # Encourage exploration by favoring variables with larger fractional parts
    score *= candsfrac * (1 - candsfrac)

    # Prioritize variables with fewer locks
    score *= 1.0 / (1 + nlocksdown + nlocksup)

    return score, roundup
</end_code>
'''

inds_gpt4_1010_train50 = '''
<start_des>
The new scoring function, `myheurdiving`, refines and adjusts its methodology to optimize the decision-making process for rounding in MILP scenarios. It evaluates both upward and downward rounding potential by considering the feasibility, direct impact on the objective, and the strategic influence of each rounding decision. The score calculation involves considering penalties for infeasibility and rewards for reducing the objective function while incorporating a complexity factor based on the variable's involvement in the model. Special attention is given to binary variables by assigning them additional score points, enhancing their prioritization due to their decisive nature in binary decisions. This function aims to balance between exploring new feasible regions (penalized if not feasible) and exploiting the current position to move towards optimality by dynamically comparing the potential outcomes of rounding decisions.
<end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Calculate penalties for infeasibility
    penalty_down = 2 if not mayrounddown else 1
    penalty_up = 2 if not mayroundup else 1

    # Base score calculations considering penalties
    score_down = (obj * (1 - candsfrac) - pscostdown * penalty_down + rootsolval * 3) / (nlocksdown + 1)
    score_up = (obj * candsfrac - pscostup * penalty_up + rootsolval * 3) / (nlocksup + 1)

    # Boost scores for binary variables
    if isBinary:
        score_down += 50
        score_up += 50

    # Decide the best rounding direction
    roundup = score_up > score_down

    # Normalize the score by considering the objective norm and the model's complexity
    final_score = (score_up if roundup else score_down) / (objnorm * (nNonz + 1))

    return final_score, roundup
</end_code>
'''

inds_llama3_1010_train50 = '''
<start_des>
The new score function, myheurdiving, assigns a score to each variable based on its fractional part, objective function value, and feasibility considerations. The function first determines the rounding direction by considering the feasibility of rounding up or down, and then calculates a score based on the fractional part, objective function value, and pseudo costs. The score is designed to prioritize variables with larger fractional parts, higher objective function values, and fewer locks.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if mayrounddown and mayroundup:
        if pscostdown > pscostup:
            roundup = False
        else:
            roundup = True
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        roundup = False
    
    score = candsfrac * objnorm * (1 + nlocksdown + nlocksup) * (1 - rootsolval) * (1 + nNonz * isBinary)
    score += obj * pscostdown if roundup else obj * pscostup
    return score, roundup
</end_code>

'''

cauc2_gpt4_1010_train50 = '''
<start_des>The new `myheurdiving` scoring function combines various factors to assess each variable's desirability for rounding within MILP problems. It strategically balances exploration and exploitation by penalizing limited rounding options while rewarding variables closer to integer values and those with significant objective contributions. It also considers the complexity of structural constraints and the importance of binary variables. The function utilizes pseudo costs and root node solution values for informed rounding direction decisions, ensuring a balanced approach to MILP problem-solving.</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False
    
    # Penalize limited rounding options to encourage exploration
    if not (mayrounddown and mayroundup):
        score -= 15  # Increased penalty for restricting exploration
    
    # Reward proximity to integer values to promote integrality
    score += (1 - candsfrac) * 12
    
    # Reward significant objective contributions
    score += abs(obj) / objnorm
    
    # Adjust score based on the number of locks
    score -= (nlocksdown + nlocksup) * 4
    
    # Incentivize binary variables due to significant impact
    if isBinary:
        score += 45
    
    # Reward for sparsity in problem structure
    score += (10 - nNonz) * 2
    
    # Utilize pseudo costs for informed rounding decisions
    if pscostdown < pscostup and mayrounddown:
        roundup = False
        score += pscostdown * 8  # Encourage down rounding with lower pseudo cost
    elif mayroundup:
        roundup = True
        score += pscostup * 8  # Encourage up rounding with lower pseudo cost
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding
    
    # Utilize root node solution value for enhanced decision making
    score += rootsolval * 7
    
    return score, roundup
</end_code>
'''

setc2_claude3 = '''
<start_des>
The scoring function aims to prioritize variables with a larger impact on the objective value while favoring rounding directions that lead to more exploration and diversification in the search tree. It considers the objective coefficient, fractional part of the solution value, pseudo-costs, and variable types to determine the rounding direction and score. Variables with a higher score have a higher priority for rounding.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction based on objective coefficient and fractional part
    if obj >= 0:
        roundup = candsfrac >= 0.5
    else:
        roundup = candsfrac < 0.5

    # Penalize if rounding in the chosen direction is not feasible
    if (roundup and not mayroundup) or (not roundup and not mayrounddown):
        penalty = 1e6
    else:
        penalty = 0

    # Compute score based on objective impact, fractional part, and pseudo-costs
    if roundup:
        score = obj * (1 - candsfrac) - pscostup
    else:
        score = -obj * candsfrac - pscostdown

    # Favor binary variables and variables with larger objective impact
    if isBinary:
        score *= 2
    score *= (1 + obj / objnorm)

    # Penalize locked variables to encourage exploration
    score -= (nlocksdown if roundup else nlocksup) * 1e3

    # Favor variables with larger fractional part for increased impact
    score *= candsfrac if roundup else (1 - candsfrac)

    # Penalize variables with the same value as the root relaxation solution
    if abs(candsol - rootsolval) < 1e-6:
        score -= 1e3

    return score - penalty, roundup
</end_code>
'''



mul_gpt351_4_16_1_2 = '''
<start_des>
The new score function 'myheurdiving' combines various factors to determine the variable's score. It penalizes variables with limited rounding options to encourage exploration. It assigns higher scores to variables with significant fractional parts, lower pseudo costs, higher objective function values, and lower impact on feasibility. The function aims to strike a balance between exploration and prioritizing variables that contribute most to the objective function with minimal feasibility impact.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = False

    # Penalize variables with limited rounding options
    if not mayrounddown or not mayroundup:
        score -= 0.5

    # Assign score based on fractional part of solution value
    score += candsfrac

    # Prioritize variables with lower pseudo costs
    score += min(pscostdown, pscostup)

    # Prioritize variables with higher objective function values
    score += obj / objnorm

    # Prioritize variables with lower impact on feasibility
    score -= (nlocksdown + nlocksup) / (nNonz + 1)

    # Determine rounding direction based on fractional part
    roundup = True if candsfrac >= 0.5 else False

    return score, roundup
</end_code>
'''

mul_gpt352_4_16_1_2 = '''
<start_des>
The new score function computes the variable's score by combining the importance of different features such as the objective function value, the feasibility of rounding, the fractional part of the solution value, the number of locks for rounding, the pseudo cost values, the Euclidean norm of the objective function vector, the root node solution v
alue, the number of nonzero entries, and the variable type. It penalizes variables that are difficult to round down/up while prioritizing variables with higher objective values and lower pseudo costs for potential solution improvement.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 0
    # Penalty for variables that cannot be rounded down/up
    if not mayrounddown:
        penalty += 0.5
    if not mayroundup:
        penalty += 0.5

    # Calculate the score based on various features
    score = obj + objnorm * (candsol + candsfrac) - max(pscostdown, pscostup) + 1/nNonz - nlocksdown - nlocksup - penalty

    # Determine the rounding direction based on the fractional part
    roundup = True if candsfrac >= 0.5 else False

    return score, roundup
</end_code>
'''

mul_gpt353_4_16_1_2 = '''
<start_des>
The new score function combines various factors like the feasibility of rounding, fractional and LP solution values, number of locks, objective function values, norm, pseudo cost values, root node solution value, number of non-zero entries, and variable type. It penalizes variables that can be easily rounded up/down to encourage exploration and prioritizes rounding directions that potentially improve the solution.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 0
    # Penalty for variables that can be rounded down/up
    if mayrounddown:
        penalty += 0.1
    if mayroundup:
        penalty += 0.1

    # Calculate the score based on various features
    score = (candsfrac / (abs(candsol) + 1)) * 0.5 + (obj / objnorm) * 0.3 + (pscostdown + pscostup) * 0.2 + rootsolval * 0.1 + nNonz * 0.1 - penalty

    # Determine the rounding direction based on the fractional part
    roundup = True if candsfrac > 0.5 else False

    return score, roundup
</end_code>
'''

mul_gpt354_4_16_1_2 = '''
<start_des>
The new score function 'myheurdiving' takes into account various factors to determine the score of a variable. It penalizes variables that can be easily rounded up/down to encourage exploration, while also considering the fractional part of the solution value, objective function impact, pseudo cost values, locks for rounding, objective function n
orm, root solution value, number of non-zero entries, and the variable type. The function aims to strike a balance between exploration and exploitation to improve solution quality effectively.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0

    if mayrounddown:
        score -= 0.4
    if mayroundup:
        score -= 0.4

    score += candsfrac * 0.4 
    score += abs(candsol) * 0.3
    score += obj / objnorm * 0.1
    score += (nlocksdown + nlocksup) * 0.2
    score += (pscostdown + pscostup) * 0.1
    score += rootsolval * 0.1
    score += nNonz * 0.1

    if isBinary:
        score += 0.5

    if candsfrac > 0.5:
        roundup = True
    else:
        roundup = False

    return score, roundup
</end_code>
'''


mul_gpt351_10_16_1_4 = '''
<start_des>
The new combined score function calculates the variable's score by considering various features such as the fractional part of the solution value, the objective function value, pseudo cost values, the number of locks for rounding, solution value in the last root node relaxation, and the number of nonzero entries in the variable. It penalizes limited rounding options, non-binary variables, and high pseudo cost values to promote exploration and avoid being stuck in local optima. The function aims to strike a balance between exploration and exploitation by incorporating these features into the scoring process.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 0
    
    # Determine rounding direction based on the fractional part
    roundup = True if candsfrac >= 0.5 else False
    
    # Calculate the score based on the combination of features
    score = 2 * candsfrac + 0.5 * obj / objnorm - (pscostup / (pscostdown + 1e-5)) - (nlocksup * 0.1) - (nlocksdown * 0.1) + (nNonz * 0.05) + rootsolval
    
    # Penalize limited rounding options, non-binary variables, and high pseudo cost values
    if not mayrounddown or not mayroundup or not isBinary:
        penalty += 1
    if pscostup > 0.5:
        penalty += 1
    
    # Adjust the score based on penalties
    score -= penalty
    
    return score, roundup
</end_code>
'''

mul_gpt352_10_16_1_4 = '''
<start_des>
The new score function calculates the score of a variable in a Mixed Integer Linear Programming context by considering various characteristics such as the fractional part of the solution value, the solution value itself, the objective function contribution, the pseudo cost values, the Euclidean norm of the objective function vector, the number of non-zero entries, and the binary nature of the variable. It penalizes limited rounding options, high pseudo cost values, and non-binary variables while aiming to balance exploration and improving the objective function value. The score is adjusted based on these factors to provide a balanced approach to selecting variables for rounding.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 2 if not mayrounddown else 1
    penalty += 2 if not mayroundup else 1
    
    score = (3 * candsfrac) + (1 / pscostup) - (nlocksdown * 0.1) - (nlocksup * 0.1) + (obj / objnorm) + (nNonz * 0.05)
    
    roundup = True if candsfrac >= 0.5 else False

    if not isBinary:
        penalty += 1
    if pscostup > 0.5:
        penalty += 1
    
    score -= penalty
    
    return score, roundup
</end_code>
'''

mul_gpt353_10_16_1_4 = '''
<start_des>
The new score function calculates the variable's score by combining penalties for limited rounding options and non-binary variables with prioritizing variables that have a high fractional part, significant objective function contributions, minimal lock counts, consistent solution values, a higher number of nonzero entries, and a lower pseudo cost for a positive change in the variable's LP value. It aims to strike a balance between exploration and exploitation, encouraging diverse rounded solutions while exploiting variables impacting the objective function in MILP.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    penalty = 1
    
    # Penalizing limited rounding options and non-binary variables
    penalty += 1 if not mayrounddown else 0.5
    penalty += 1 if not mayroundup else 0.5
    penalty += 1 if not isBinary else 0
    
    # Calculating the score based on various factors
    score = (candsfrac * 0.8) + (1 / max(nlocksdown, nlocksup)) + (obj / objnorm) + (rootsolval * 0.2) + (nNonz * 0.1) + (1 / pscostup)
    
    # Determining if we should round up based on fractional part
    roundup = candsfrac > 0.5
    
    if pscostdown > 0.6:
        penalty += 0.5
    
    score -= penalty
    
    return score, roundup
</end_code>
'''

mul_claude31_10_16_1_4 = '''
<start_des>
This score function encourages exploration by prioritizing variables that are close to being integer while considering the objective coefficient and potential impact. It favors variables that can be rounded in both directions and penalizes those that cannot. Variables closer to the root relaxation value are preferred, and binary variables are given a higher priority. Additionally, it considers the number of locks and pseudo-costs in the rounding direction.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Penalize if rounding is not possible
    if not mayrounddown and not mayroundup:
        return -1e10, False

    # Determine rounding direction based on fractional part and root relaxation value
    roundup = (rootsolval > candsol) if rootsolval != 0 else (candsfrac > 0.5)

    # Calculate fractional distance from closest integer and root relaxation value
    frac_dist_int = min(candsfrac, 1 - candsfrac)
    frac_dist_root = abs(candsol - rootsolval)

    # Calculate score based on objective function coefficient, fractional distances, locks, pseudo-costs, and potential impact
    score = abs(obj) * objnorm * (1 + frac_dist_int) * (1 + frac_dist_root)
    if roundup and mayroundup:
        score /= (1 + pscostup) * (1 + nlocksup)
        score *= (1 + nNonz)
    elif not roundup and mayrounddown:
        score /= (1 + pscostdown) * (1 + nlocksdown)
        score *= (1 + nNonz)
    else:
        score *= 0.9  # Encourage exploration by slightly penalizing variables that can only be rounded in one direction

    # Prioritize binary variables and larger objective coefficients
    if isBinary:
        score *= 1.2
    score *= (1 + 0.1 * abs(obj))

    return score, roundup
</end_code>
'''

mul_claude32_10_16_1_4 = '''
<start_des>
This score function prioritizes variables with higher objective coefficients and fractional values closer to 0 or 1. It encourages exploration by favoring variables that can be rounded in either direction, and exploitation by considering the magnitude of the objective coefficient. The function also penalizes variables with locks and high pseudo-costs, and rewards binary variables and those with more non-zero entries.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Penalize if rounding is not possible
    if not mayrounddown and not mayroundup:
        return -1e10, False

    # Calculate the distance from 0 or 1 (favoring fractional values closer to 0 or 1)
    frac_dist = min(candsfrac, 1 - candsfrac)

    # Determine rounding direction based on fractional part
    roundup = candsfrac > 0.5

    # Calculate score based on objective function coefficient, fractional distance, locks, pseudo-costs, and non-zero entries
    score = abs(obj) * objnorm * (1 - frac_dist)
    if roundup:
        score -= nlocksup + pscostup
    else:
        score -= nlocksdown + pscostdown

    # Encourage exploration by favoring variables that can be rounded in either direction
    if mayrounddown and mayroundup:
        score *= 1.5

    # Prioritize binary variables and variables with more non-zero entries
    if isBinary:
        score *= 2.0
    score *= (1 + 0.2 * nNonz)

    # Favor rounding towards the root relaxation solution if available
    if rootsolval != 0:
        score *= abs(candsol - rootsolval)

    return score, roundup
</end_code>
'''


mul_claude31_15_16_1_4 = '''
<start_des>
This score function considers the potential objective improvement, exploration of fractional values, diversification based on the number of locks, and prioritizes variables with a larger fractional part and higher objective coefficients. It aims to strike a balance between exploration, exploitation, and diversification to find high-quality solutions.
</end_des>

<start_code>
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
</end_code>
'''

mul_gpt351_20_16_1_4 = '''
<start_des>
The new score function penalizes limited rounding options to encourage exploration, prioritizes variables with high fractional values and low pseudo costs, considers the impact of the objective function value and Euclidean norm, incorporates historical solution values, adjusts for sparsity, and differentiates based on the binary nature of the variable for effective solution search.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Initialization
    score = 0.0
    roundup = False
    
    # Penalize limited rounding options to encourage exploration
    score -= 0.2 if mayrounddown or mayroundup else 0.0
    
    # Prioritize variables with high fractional values and low pseudo costs
    score += candsfrac  
    score += min(1 / (1 + (pscostdown + pscostup)), 1)
    
    # Consider the impact of objective function value and Euclidean norm
    score += (obj / max(1, objnorm)) * (1 - candsfrac) / (nNonz + 1)
    
    # Incorporate historical solution values
    score += rootsolval * 0.3
    
    # Penalize excessive sparsity
    if nNonz < 5:  
        score -= 0.2
    
    # Differentiate based on the binary nature of the variable
    score *= 1.5 if isBinary else 1.0
    
    # Determine rounding direction based on the score
    if candsfrac > 0.5:
        roundup = True
    
    return score, roundup
</end_code>

'''

mul_gpt352_20_16_1_4 = '''
<start_des>
The new score function penalizes limited rounding options, prioritizes variables with high fractional parts and low pseudo costs, considers the impact of the objective function value and Euclidean norm, penalizes excessive sparsity, incorporates the historical solution values, and adjusts for the binary nature of the variable. It encourages exploration while aiming for effective variable selection in finding feasible integral solutions.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Initialization
    score = 0.0
    roundup = False
    
    # Penalize limited rounding options to encourage exploration
    score -= 0.5 if mayrounddown or mayroundup else 0.0
    
    # Prioritize variables with high fractional parts and low pseudo costs
    score += candsfrac
    score += min(1 / (1 + (pscostdown + pscostup)), 1)
    
    # Consider impact of objective function value and Euclidean norm
    score += (obj / max(1, objnorm)) * (1 - candsfrac) / (nNonz + 1)
    
    # Penalize excessive sparsity
    if nNonz < 5:
        score -= 0.3
    
    # Consider historical solution values
    score += rootsolval * 0.2
    
    # Adjust for binary nature of variable
    score *= 1.3 if isBinary else 1.0
    
    # Determine rounding direction based on the score
    if candsfrac > 0.5:
        roundup = True
    
    return score, roundup
</end_code>
'''

mul_gpt353_20_16_1_4 = '''
<start_des>
The new score function aims to penalize easy rounding options, promote variables with high fractional parts, consider the impact of objective function values and pseudo costs, penalize limited rounding options, factor in historical solution values, encourage exploration for an efficient diving heuristic, and differentiate treatment based on binary or non-binary variables. Additionally, it introduces the concept of "lock-in" for rounding decisions.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Initialization
    score = 0.0
    roundup = False
    
    # Penalize easy rounding options
    score -= 0.2 if mayrounddown else 0.0
    score -= 0.2 if mayroundup else 0.0
    
    # Promote variables with high fractional parts
    score += candsfrac  
    
    # Evaluate impact of objective function and pseudo costs
    score += (obj / max(1, objnorm)) * (pscostdown + pscostup) * (1 - candsfrac) / (nNonz + 1)
    
    # Penalize limited rounding options
    score -= 0.5 if mayrounddown or mayroundup else 0.0
    
    # Consider historical solution values
    score += rootsolval * 0.3  
    
    # Encourage exploration
    if nNonz > 10:
        score += 0.5
    
    # Differentiate treatment based on binary or non-binary variables
    score *= 1.5 if isBinary else 1.0
    
    # Introduce lock-in for rounding decisions
    if nlocksdown >= 3 or nlocksup >= 3:
        score -= 0.3
    
    # Determine rounding direction based on the score
    if candsfrac > 0.5:
        roundup = True
    
    return score, roundup
</end_code>
'''

mul_gpt354_20_16_1_4 = '''
<start_des>
The new score function aims to balance exploration and exploitation strategies by penalizing easy rounding options, promoting variables with high fractional parts, considering the impact of the objective function value and pseudo costs, penalizing limited rounding options, factoring in historical solution values, and encouraging exploration for an efficient diving heuristic.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Initialization
    score = 0.0
    roundup = False
    
    # Penalize easy rounding options
    score -= 0.2 if mayrounddown else 0.0
    score -= 0.2 if mayroundup else 0.0
    
    # Promote variables with high fractional parts
    score += candsfrac  
    
    # Evaluate impact of objective function and pseudo costs
    score += (obj - objnorm) * (pscostdown + pscostup) * (1 - candsfrac) / (nNonz + 1)
    
    # Penalize limited rounding options
    score -= 1.0 if mayrounddown or mayroundup else 0.0
    
    # Consider historical solution values
    score += rootsolval * 0.3  
    
    # Encourage exploration
    if nNonz > 10:
        score += 0.5
    
    # Determine rounding direction based on the score
    if candsfrac > 0.5:
        roundup = True
    
    return score, roundup
</end_code>
'''

mul_gpt3516k1_20_16_1_4 = '''
<start_des>
The new score function's logic aims to prioritize variables that have a high potential for being rounded up while remaining feasible. It penalizes variables that can be rounded down to encourage more exploration and balanced rounding. The score calculation considers features such as the possibility of rounding down or up, the fractional part of the solution value, the solution value itself in the LP relaxation, the number of locks for rounding down and rounding up, the objective function value and its Euclidean norm, the variable's pseudo cost values, the solution value in the last root node's relaxation, the number of nonzero entries in the variable, and whether the variable is binary or not. The score is a weighted sum of these features, assigning higher weights to factors that have a positive impact on rounding up or the objective function value.

The rounding direction is determined based on the comparison between the fractional part of the solution value and the difference between the solution value and its rounded value. If the fractional part is greater than the absolute difference, it suggests that rounding up is more preferable. Therefore, the 'roundup' variable is set to True if the score indicates that rounding up is better, and False otherwise.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = (mayroundup * 0.2) - (mayrounddown * 0.5) + (candsfrac * 100) + (candsol * 10) + (nlocksup * 0.5) + (nlocksdown * 0.3) + (obj * 0.05) + (objnorm * 0.1) + (pscostup * 0.3) + (pscostdown * 0.2) + (rootsolval * 3) + (nNonz * 0.3) + (isBinary * 2)
    roundup = candsfrac > abs(candsol - round(candsol))
    return score, roundup
</end_code>
'''

mul_gpt3516k2_20_16_1_4 = '''
<start_des>
The logic of the new score function is as follows:
- The "mayrounddown" and "mayroundup" variables are multiplied by a negative weight to penalize them and encourage more exploration.
- The "candsfrac" variable, representing the fractional part of the solution value, receives a relatively high weight in the score calculation to prioritize variables with larger fractional parts that can be rounded up without making the solution infeasible.
- The "candsol" variable, representing the solution value in the LP relaxation, is included to prioritize variables that are close to their desired integral value.
- The "nlocksdown" and "nlocksup" variables, representing the number of locks for rounding down and rounding up, are considered to ensure a balanced rounding decision and avoid bias towards a particular direction.
- The "obj" variable, representing the objective function value, and the "objnorm" variable, representing the Euclidean norm of the objective function vector, are taken into account to give higher scores to variables that contribute more to the objective function.
- The "pscostdown" and "pscostup" variables, representing the variable's pseudo cost values, are considered in the score calculation as they reflect the sensitivity of the current solution to changes in the variable's value.
- The "rootsolval" variable, representing the solution value in the last root node's relaxation, provides historical information about the variable's behavior and is used to exploit past knowledge.
- The "nNonz" variable, representing the number of nonzero entries in the variable, is considered as it reflects the importance of the variable in the overall problem.
- The "isBinary" variable, indicating whether the variable is of binary type, receives a high weight in the score calculation as binary variables are often crucial in MILP problems.
</end_des>
<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = (mayrounddown*(-0.8) + mayroundup*(-0.8) + candsfrac*1000 + candsol*10 + nlocksdown*0.5 + nlocksup*0.5 + obj*0.2 + objnorm*0.2 + pscostdown*0.3 + pscostup*0.3 + rootsolval*100 + nNonz*10 + isBinary*2000)
    roundup = True if candsfrac > abs(candsol - round(candsol)) else False
    return score, roundup
</end_code>
'''

mul_gpt41_20_16_1_4 = '''
<start_des>
The `myheurdiving` function for MILP diving heuristic assigns scores to fractional variables for rounding decisions based on several considerations to ensure effective and informed rounding. It emphasizes exploration, solution quality, and the strategic importance of variables, incorporating factors like feasibility of rounding directions, variable proximity to integers, and influence on the overall objective. The function adjusts scores for both pseudo costs and the number of constraints a variable impacts when rounded up or down, with special attention to binary variables due to their pivotal role in solution feasibility. It also adjusts the score based on the deviation from the root solution, promoting variables closer to initial estimations to maintain solution stability.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = candsfrac >= 0.5  # Determines the initial rounding direction

    # Penalty for having both rounding options to promote more variable exploration
    if mayrounddown and mayroundup:
        score -= 0.3

    # Adding proximity to the nearest integer score
    proximity = 20 * (1 - abs(candsfrac - 0.5))
    score += proximity if roundup else -proximity

    # Influence on the objective function and solution quality
    score += 10 * candsol  # Reward higher solution values
    score += (obj / objnorm) * 3  # Normalize contribution to objective
    
    # Adjusting for pseudo costs
    score -= 0.7 * (pscostup if roundup else pscostdown)
    
    # Constraint influence through locks
    score -= 4 * (nlocksup if roundup else nlocksdown)

    # Adding a score for the number of nonzero entries to promote constraints satisfaction
    score += 3 * nNonz
    
    # Boost for binary variables
    if isBinary:
        score *= 1.5  # Increase importance for binary variables
    
    # Deviation from the root solution
    root_discrepancy = abs(candsol - rootsolval) * 7
    score += root_discrepancy if roundup else -root_discrepancy
    
    return score, roundup
</end_code>
'''

mul_gpt42_20_16_1_4 = '''
<start_des>
The newly designed `myheurdiving` function refines the scoring approach for MILP diving heuristics by intelligently evaluating variables based on their impact on solution feasibility and optimization potential. This function emphasizes enhanced exploration by penalizing choices where both rounding directions are feasible, thus encouraging decisions in scenarios with limited rounding flexibility. It integrates multiple aspects such as the fractional part of the variable, solution proximity to integer values, and the variable's past performance in rounding through pseudo costs. It also weighs in the variable's role in the objective function and its connectivity in the constraint matrix, prioritizing binary variables due to their significant leverage on feasibility. Overall, the function dynamically balances between exploring new feasible solutions and exploiting the best candidates for rounding to improve solution quality.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.0
    roundup = candsfrac > 0.5  # Favor rounding up if the fraction is greater than 0.5

    # Penalty for flexibility in rounding options, promoting exploration
    if mayrounddown and mayroundup:
        score -= 15

    # Bonus for contribution to the objective, normalized by objective vector norm
    score += 25 * candsol + 15 * (obj / objnorm)

    # Proximity to the nearest integer for the fractional part, applying a bonus or penalty based on the rounding direction
    proximity_bonus = 40 * min(candsfrac, 1 - candsfrac)
    score += proximity_bonus if roundup else -proximity_bonus

    # Adjustments based on pseudo costs which reflect the variable's historical rounding performance
    score -= 10 * (pscostup if roundup else pscostdown)

    # Reward for involvement in a higher number of constraints, indicating strategic importance
    score += 10 * nNonz

    # Enhanced influence for binary variables due to their pivotal role in achieving feasibility
    if isBinary:
        score *= 2.5

    # Impact of deviation from the root solution, adjusted for rounding direction
    root_discrepancy = abs(candsol - rootsolval) * 20
    score += root_discrepancy if roundup else -root_discrepancy

    # Locks impact, reducing score based on restrictions in rounding flexibility
    score -= 3 * (nlocksup if roundup else nlocksdown)

    return score, roundup
</end_code>
'''




mul2_claude31_20_16 = '''
<start_des>
The new score function combines the factors of fractional value proximity, objective coefficient, pseudo costs, number of locks, binary status, and nonzero entries. It prioritizes variables with fractional values closer to integers, larger objective coefficients, smaller pseudo costs, and fewer locks. The rounding direction is determined by the potential impact on the objective function and the fractional value. The score is adjusted based on the number of nonzero entries to encourage sparsity.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    roundup = False
    if isBinary:
        roundup = candsol > 0.5
    else:
        roundup = obj * (1 - candsfrac) < obj * candsfrac - pscostup + pscostdown

    # Calculate score
    if roundup:
        if mayroundup:
            score = (obj * candsfrac) / ((nNonz + nlocksup + 1) * (pscostup + 1))
        else:
            score = -(obj * candsfrac) / ((nNonz + nlocksup + 1) * (pscostup + 1))
    else:
        if mayrounddown:
            score = (obj * (1 - candsfrac)) / ((nNonz + nlocksdown + 1) * (pscostdown + 1))
        else:
            score = -(obj * (1 - candsfrac)) / ((nNonz + nlocksdown + 1) * (pscostdown + 1))

    return score, roundup
</end_code>
'''

tmp = '''
<start_des>
The new score function calculates the variable's score by considering various features such as the fractional value, solution value, number of locks, objective function value, objective function norm, pseudo cost values, root solution value, number of non-zero entries, and variable type. It penalizes variables that may require rounding to stay feasible, promotes exploration for better solutions, and gives higher importance to variables with lower fractional parts for effective rounding.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Determine rounding direction based on the fractional value
    roundup = candsfrac >= 0.5
    
    # Calculate score based on the combination of 13 features with penalties and prioritization
    score = (1 / (1 + abs(candsfrac - 0.5))) * (1 / (1 + candsol + 0.1)) * (1 / (1 + obj + 0.1)) * (1 / (1 + objnorm)) * (1 / (1 + max(pscostdown, pscostup))) * (1 / (1 + abs(nlocksdown - nlocksup))) * (1 / (1 + nNonz) + (1 / (1 + rootsolval+0.1)))
    
    # Penalize variables that may require rounding to stay feasible and promote exploration based on variable type
    if mayrounddown or mayroundup:
        score *= 0.85
    if isBinary:
        score *= 1.1
    
    # Give higher importance to lower fractional parts for effective rounding
    score *= (1 / (1 + candsfrac))
        
    return score, roundup
</end_code>
'''

tmp2 = '''
<start_des>
The new score function calculates the variable's score by considering multiple features such as the fractional value, solution value, number of locks for rounding, objective function value and norm, pseudo cost values, root solution value, number of non-zero entries, and the variable type. It penalizes rounding possibilities for feasibility and encourages exploration while giving priority to variables that are closer to being integral, contribute significantly to the objective function, have fewer locks, exhibit binary characteristics, and have lower pseudo cost values.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Determine the rounding direction based on the fractional value
    roundup = candsfrac >= 0.5
    
    # Calculate the score based on a combination of features with penalties and prioritizations
    score = (1 / (1 + abs(candsfrac - 0.5))) * (1 / (1 + candsol)) * (1 / (1 + obj)) * (1 / (1 + objnorm)) * (1 / (1 + max(pscostdown, pscostup))) * (1 / (1 + abs(nlocksdown - nlocksup))) * (1 / (1 + nNonz)) * (1 / (1 + rootsolval))
    
    # Penalize variables that may require rounding for feasibility and prioritize integral, significant, and binary type variables
    if mayrounddown:
        score *= 0.85
    if mayroundup:
        score *= 0.85
    if isBinary:
        score *= 1.1
    if pscostdown > pscostup:
        score *= 0.95
    
    return score, roundup
</end_code>
'''

tmp3 = '''
<start_des>
The new score function combines the factors of fractional value proximity, objective coefficient, pseudo costs, number of locks, binary status, and nonzero entries. It prioritizes variables with fractional values closer to integers, larger objective coefficients, smaller pseudo costs, and fewer locks. The rounding direction is determined by the potential impact on the objective function and the fractional value. The score is adjusted based on the number of nonzero entries to encourage sparsity.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    roundup = False
    if isBinary:
        roundup = candsol > 0.5
    else:
        roundup = obj * (1 - candsfrac) < obj * candsfrac - pscostup + pscostdown

    # Calculate score
    if roundup:
        if mayroundup:
            score = (obj * candsfrac) / ((nNonz + nlocksup + 1) * (pscostup + 1))
        else:
            score = -(obj * candsfrac) / ((nNonz + nlocksup + 1) * (pscostup + 1))
    else:
        if mayrounddown:
            score = (obj * (1 - candsfrac)) / ((nNonz + nlocksdown + 1) * (pscostdown + 1))
        else:
            score = -(obj * (1 - candsfrac)) / ((nNonz + nlocksdown + 1) * (pscostdown + 1))

    return score, roundup
</end_code>
'''

codes = [setc_gpt3516k_1010_train50,setc_gpt35_1010_train50, setc_claude3son_1010_train50,setc_gpt4_1010_train50,\
          cauc_gpt3516k_1010_train50, cauc_gpt35_1010_train50,cauc_claude3son_1010_train50,cauc_gpt4_1010_train50,\
        faci_gpt3516k_1010_train10, faci_gpt35_1010_train10, faci_claude3son_1010_train10,faci_gpt4_1010_train10,\
            inds_gpt3516k_1010_train50, inds_gpt35_1010_train50,inds_claude3son_1010_train50, inds_gpt4_1010_train50]

names = ["setcover","cauctions","facilities","indset","loadbalance","miplib"]

kimi_codes = [kimi1_code,kimi2_code,kimi3_code,kimi4_code]

gpt35_codes = [gpt351_code,gpt352_code,gpt353_code,gpt354_code]



for t in ["transfer3"]:
    abs_dict = {}
    rel_dict = {}
    for name in ["cauctions"]:
        lst1 = []
        lst2 = []
        for code in [mul_claude31_15_16_1_4]: 
            mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(code,name,t=t,diving_ind=2)
            s1 = str( round(mean_abs,2) ) + "(" + str( round(SEM_abs,2) ) + ")"
            s2 = str( round(mean_rel,2) ) + "(" + str( round(SEM_rel,2) ) + ")"

            lst1.append(s1)
            lst2.append(s2)


        abs_dict[name] = lst1
        rel_dict[name] = lst2

    df_abs = pd.DataFrame(abs_dict)
    df_rel = pd.DataFrame(rel_dict)

    abs_file = '/home/yyzhou/LLM4Heur/tmp/abs'+ t +'.xlsx'
    rel_file = '/home/yyzhou/LLM4Heur/tmp/rel'+ t +'.xlsx'

    # df_abs.to_excel(abs_file, index=False)
    # df_rel.to_excel(rel_file, index=False)
