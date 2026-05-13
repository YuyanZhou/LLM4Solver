
from pyscipopt import Model, Heur, SCIP_RESULT, SCIP_PARAMSETTING, SCIP_HEURTIMING
from pyscipopt.scip import is_memory_freed
import pyscipopt
import os

import pyscipopt as scip
import os
import sys

import re

import random


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
This scoring function aims to balance exploration and exploitation by considering the objective value contribution, fractional part, pseudo-costs, feasibility constraints, variable characteristics, and proximity to the root solution. It encourages exploration by penalizing variables with restricted rounding directions and prioritizes variables with larger objective coefficients, significant fractional parts, and fewer locks in the preferred rounding direction. The rounding direction is determined based on objective value, pseudo-costs, and feasibility. The score is boosted for binary variables, variables with more nonzero entries, and variables closer to the root solution value.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction
    if obj > 0:
        roundup = True if (pscostup <= pscostdown or (pscostup == pscostdown and mayroundup)) else False
    else:
        roundup = False if (pscostdown <= pscostup or (pscostdown == pscostup and mayrounddown)) else True

    # Calculate score
    if roundup and not mayroundup:
        score = -math.inf  # Penalty for restricting exploration
    elif not roundup and not mayrounddown:
        score = -math.inf  # Penalty for restricting exploration
    else:
        if roundup:
            score = obj * candsfrac / objnorm
        else:
            score = obj * (1 - candsfrac) / objnorm

        score *= (1 + nNonz / 18)  # Bonus for variables with more nonzero entries
        score *= (1 + (1 - abs(rootsolval - candsol)) * 2.5)  # Bonus for variables close to root solution

        # Penalty for variables with locks in the preferred direction
        if roundup and nlocksup > 0:
            score *= 0.5 ** nlocksup
        elif not roundup and nlocksdown > 0:
            score *= 0.5 ** nlocksdown

        if isBinary:
            score *= 1.4  # Prioritize binary variables

    return score, roundup
</end_code>
'''

setc_gpt4_1010_train50 = '''
<start_des>
The new scoring function, `myheurdiving`, optimizes variable rounding decisions by considering various factors such as feasibility, proximity to integer values, objective impact, pseudo cost, structural complexity, and binary nature. It penalizes rounding options that limit exploration while favoring variables closer to integer values with lower pseudo costs and fewer constraints. The function encourages strategic rounding decisions that balance feasibility with objective improvement, promoting the exploration of potentially impactful solutions.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Assess feasibility and pseudo cost impacts for rounding decisions
    feasible_down = mayrounddown and pscostdown < pscostup
    feasible_up = mayroundup and pscostup < pscostdown
    
    # Calculate base score components based on proximity to integer and objective impact
    base_score = obj / (1 + objnorm)  # Normalizing by objective function norm
    proximity_score = 1 - abs(candsfrac)  # Closer to integer, higher score
    
    # Initialize scores for both directions
    score_down = float('-inf') if not feasible_down else base_score - pscostdown + proximity_score - (nlocksdown * 0.05)
    score_up = float('-inf') if not feasible_up else base_score - pscostup + proximity_score - (nlocksup * 0.05)
    
    # Factor in binary variable adjustment and complexity
    if isBinary:
        score_down *= 1.05  # Slight boost for binary variables
        score_up *= 1.05
    complexity_adjustment = 1 / (1 + 0.05 * nNonz)  # Reduce score for complex variables
    score_down *= complexity_adjustment
    score_up *= complexity_adjustment
    
    # Determine best scoring direction
    if score_down > score_up:
        return score_down, False  # Round down is better
    else:
        return score_up, True  # Round up is better
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
This scoring function aims to balance fractional closeness, objective importance, diversity promotion, and exploration encouragement. It favors variables closer to integers, with higher objective contributions, and greater diversity from the root solution. Penalties are applied for locks, pseudo-costs, and non-zeros. The rounding direction is determined by fractional value, objective coefficient, and pseudo-costs, with a bonus for binary variables. Exploration is encouraged by favoring variables with fewer locks.
</end_des>

<start_code>
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    roundup = False
    if obj > 0:
        roundup = candsfrac < 0.5 or (pscostup < pscostdown and pscostup < abs(obj))
    else:
        roundup = candsfrac > 0.5 or (pscostdown < pscostup and pscostdown < abs(obj))

    exploration_bonus = (nlocksdown + nlocksup) * 0.3

    fractional_score = abs(min(candsfrac, 1 - candsfrac) - 0.5) * 0.7
    objective_score = abs(obj) / (objnorm + 1e-6) * 0.6
    diversity_score = abs(candsol - rootsolval) * 0.5
    locks_penalty = (nlocksdown + nlocksup) * 0.2
    pscost_penalty = pscostup if roundup else pscostdown
    pscost_penalty *= 0.3
    nonzeros_penalty = nNonz * 0.1

    score = fractional_score + objective_score + diversity_score + exploration_bonus - locks_penalty - pscost_penalty - nonzeros_penalty

    if isBinary:
        score *= 1.1

    return score, roundup
</end_code>
'''

cauc_gpt4_1010_train50 = '''
<start_des>
The `myheurdiving` function is designed to make strategic rounding decisions for MILP variables by weighing factors such as feasibility, proximity to integer values, and their impact on the objective function. It introduces a refined scoring system that values binary characteristics, the variable's contribution to the objective relative to its norm, and penalizes situations with restricted rounding options to foster a more exhaustive exploration of the solution space. The function also accounts for variable sparsity, emphasizing less populated variables, and integrates pseudo costs to guide the rounding direction. This balanced approach aims to enhance the solver's ability to explore and exploit viable solutions effectively, especially under complex MILP scenarios.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False

    # Rewarding proximity to integer values and binary status
    score += 50 if isBinary else (1 - candsfrac) * 15

    # Influence of objective function's normalized value
    score += (abs(obj) / objnorm) * 15

    # Penalize limited rounding options to encourage exploration
    if not mayrounddown or not mayroundup:
        score -= 25

    # Considering locks and sparsity in variable involvement
    score -= (nlocksdown + nlocksup) * 3.5
    score += 0.1 * (10 - nNonz) if nNonz < 10 else 0

    # Determine the rounding direction based on the pseudo costs and feasibility
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Ensure avoidance of infeasible directions

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

pscost_diving = '''
<start_code>
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

    if( isBinary and (not(mayrounddown or mayroundup) ) ):
      pscostquot = 1000.0 * pscostquot

    assert(pscostquot >= 0)
    
    score = pscostquot

    return (score, roundup)
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


def extract_code(text):
    pattern = r'<start_code>(.*?)</end_code>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        print("No code found between <start_code> and </end_code>.")
        code = "No code found between <start_code> and </end_code>."
        return code


seed = 3
random.seed(seed)

ind = int(sys.argv[1])
ind_total = int(sys.argv[2])

DIVING_IND = 4

name = "nnverify"
names = ["cauctions","facilities","indset","setcover","miplib","loadbalance","nnverify"]
heurs = ['coefdiving','distributiondiving','farkasdiving','fracdiving','linesearchdiving','pscostdiving','veclendiving']
confs = [3, 5, 7, 0, 3, 3, 4]

ds = ["test"]

for t in ds:

    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    instance_list.sort()

    num = int( len(instance_list) / ind_total )

    start = (ind-1)*num
    end = ind * num if ind < ind_total else len(instance_list)

    my_diving = extract_code(setc_gpt35_1010_train50)
    my_diving_info = "setc_gpt35"

    for instance in instance_list[start:end]:
        print(instance)
        path_to_one_instance = path_to_instances + "/" + instance

        log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/nnverify/"+ my_diving_info +"solved/"+ t + "/seed" +str(seed) # 2
        # log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/nnverify/tunescipsolved/"+t+"/seed"+str(seed) # 8
        # log_dir = "/home/yyzhou/LLM4Heur/heur/logfile/logs/nnverify/scipsolved/"+t+"/seed"+str(seed) # 10
        if( not os.path.exists(log_dir) ):
            os.makedirs(log_dir)

        logfile = log_dir + "/" + instance + ".log"

        model = scip.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        model.setParam('limits/time', 600)
        

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
        
        model.setParam(freq_param,1)
        model.setParam(freqofs_param,0)
        
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
        
        
        # turn off the other diving heur
        
        model.setParam('heuristics/coefdiving/freq',-1)
        model.setParam('heuristics/fracdiving/freq',-1)
        model.setParam('heuristics/distributiondiving/freq',-1)
        model.setParam('heuristics/farkasdiving/freq',-1)
        model.setParam('heuristics/linesearchdiving/freq',-1)
        model.setParam('heuristics/veclendiving/freq',-1)
        model.setParam('heuristics/pscostdiving/freq',-1)
            
        # for conf,heur in zip(confs,heurs):
        #     freq_param = 'heuristics/'+ heur +'/freq'
        #     freqofs_param = 'heuristics/'+heur+'/freqofs'

        #     default_freq = model.getParam(freq_param)
        #     if(default_freq == -1):
        #         default_freq = 1
        #     default_freqofs = model.getParam(freqofs_param)

        #     id1 = conf % 4
        #     id2 = int(conf/4)

        #     if id1==0:
        #         model.setParam(freq_param,-1)
        #     elif id1==1:
        #         model.setParam(freq_param,int(default_freq/2))
        #     elif id1==2:
        #         model.setParam(freq_param,int(default_freq))
        #     else:
        #         model.setParam(freq_param,int(default_freq*2))
            
        #     if id2==0:
        #         model.setParam(freqofs_param,0)
        #     else:
        #         model.setParam(freqofs_param,default_freqofs)


        

        model.hideOutput()
        # before optimize, check /home/yyzhou/scipoptsuite-9.0.0/scip/src/scip/scipdefplugins.c
        model.optimize()

