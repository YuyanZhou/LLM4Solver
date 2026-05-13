from EA import MyLLM, AGIndividual, EAMethods
from eval import eval_heur
import random
import datetime
import os



def EQ(num1,num2):
    return abs(num1-num2) < 1e-6



def run(n_round=10, n_pop=10, instance_name = "cauctions", dataset = "train50", model = "gpt-3.5-turbo", valid_dataset = "valid", DIVEING_IND = 1 ):

    background_prompt = '''
    Mixed Integer Linear Programming (MILP) is a type of mathematical optimization or decision-making method that is used to find the best or optimal solution from a set of possible solutions, considering both linear and discrete decision variables. It is an extension of the well-known Linear Programming (LP) paradigm, which deals only with continuous variables.

    ​Definition (Mixed Integer Linear Programming): Given a matrix $A \in \mathbb{R}^{m \times n}$, vectors $b \in \mathbb{R}^m$, and $c \in \mathbb{R}^n$, and a subset $I \subset N = \{1,2,...,n\}$, the *mixed integer linear programming* $\mathbf{MILP} = (A,b,c,I)$ is to solve $c^{*} = min\{c^T x| Ax \leq b, x \in \mathbb{R}^n, x_j \in \mathbb{Z}  \text{ for all } j \in I\}$. The vectors in the set $X_{MILP} = \{c^Tx|Ax\leq b,x_j\in\mathbb{Z} \text{ for all }j \in I\}$ are called *feasible solutions* of MILP. The bounds of variables are denoted by $l_j \leq x_j \leq u_j$ with $l_j,u_j \in \mathbb{R} \cup \{\pm \infty \}$

    ​Primal heuristics of MILP: Primal heuristics in the context of Mixed Integer Linear Programming (MILP) refer to methods or strategies used to find a feasible solution to the problem, typically as an initial step in the solution process. These heuristics are particularly useful when dealing with large and complex MILP problems where finding an optimal solution may be computationally expensive or time-consuming. The term "primal" refers to the original problem formulation, as opposed to the "dual" which is another way of looking at the problem.

    Diving heuristics: Diving heuristics are one of the most important categories of primal heuristics. Diving heuristics start from the current LP solution and iteratively fix an integer variable to an integral value and resolve the LP. 

    The pseudo-code of the Generic Diving Heuristic is as follows:

        Algorithm: Generic Diving Heuristic 
    Input: Optimal LP solution $\breve{x}$ of the current subproblem. 
    Output: If available, one or more feasible integral solutions. 
    Require: s, a scoring function to select variables for bound tightening
    1. Set $\tilde{x} \coloneqq \breve{x}$. 
    2. d = 1
    3. while $d \leq d_{max}$ do
    4. ​	If $F \coloneqq \{j \in I | \tilde{x}_j \notin \mathbb{Z}\} = \emptyset$, stop and return the feasible integral solution $\tilde{x}$. 
    5. ​	Apply the simple rounding heuristic on $\tilde{x}$ to potentially produce an intermediate feasible integral solution. 
    6. ​	Choose a fractional variable $x_j, j=argmax_{j\in F}  s_j$, and a rounding direction. 
    7. ​	If down rounding is selected, tighten $\tilde{u}_j \coloneqq \lfloor \tilde{x}_j \rfloor$. Otherwise, tighten $\tilde{l}_j \coloneqq \lceil \tilde{x}_j \rceil $. 
    8. ​	Call domain propagation to propagate the tightened bound. 
    9. ​	Resolve the LP relaxation with the new bounds. 
    10. ​	(optional) If the LP is infeasible, undo the previous propagations, apply the opposite rounding, propagate, and resolve the LP again.
    11. ​	If the LP is still infeasible, stop with a failure. Otherwise, let $\tilde{x}$ be the new optimal solution.
    12. ​	d = d + 1

    ​You need to understand the above contents, especially the generic diving heuristic, and the next task will be closely related to the diving heuristic. 
    '''

    features_description = '''
    "mayrounddown" and "mayroundup" (bool, indicate whether it is possible to round variable down/up and stay feasible, it should be penalized because we need more exploration); "candsfrac" (float, fractional part of solution value of variable); "candsol" (float, solution value of variable in LP relaxation solution); "nlocksdown" and "nlocksup" (int, the number of locks for rounding down/up of a special type); "obj" (float, objective function value of variable); "objnorm" (float, the Euclidean norm of the objective function vector); "pscostdown" and "pscostup" (float, the variable's pseudo cost value for the given change of the variable's LP value); "rootsolval" (float, the solution of the variable in the last root node's relaxation, if the root relaxation is not yet completely solved, zero is returned); "nNonz" (int, the number of nonzero entries in variable); "isBinary" (bool, TRUE if the variable is of binary type).
    '''

    inout_format_description = '''
    Provide a brief description of the new score function's logic and its corresponding Python code. The description must start with '<start_des>' and end with '</end_des>'. The code must start with '<start_code>' and end with '</end_code>'. The code score function must called 'myheurdiving' that takes 13 inputs 'mayrounddown', 'mayroundup', 'candsfrac', 'candsol', 'nlocksdown', 'nlocksup', 'obj', 'objnorm', 'pscostdown', 'pscostup', 'rootsolval', 'nNonz' and 'isBinary'. The function must output the 'score' and 'roundup', where 'score' is a float type indicating the variable's score, the more the better, and the 'roundup' is a bool type indicating whether we should round the variable up, True for rounding up.
    '''

    instruction = '''
    Be creative and do not give additional explanations.
    '''

    init_prompt = '''
    Please focus on line 6 of the Generic Diving Heuristic. You should create a totally new Python scoring function for me (different from the heuristics in the literature) to choose the fractional variable and corresponding rounding direction using the information of the LP relaxation and objective function. The function is used for every variable to decide the variable's score and rounding direction.
    '''

    init_prompt_suggestion = '''
    There is(are) 1 suggestion(s): 1) you should first decide the rounding direction and the determine the score of the corresponding variable.
    '''

    mutation_prompt = '''
    Please focus on line 6 of the Generic Diving Heuristic. I have a score function with its code to get the variable's score and its rounding direction. Motivated by the algorithm, you should create a different new Python score function.
    '''

    crossover_prompt = '''
    Please focus on line 6 of the Generic Diving Heuristic. I have some score functions with their code to get the variable's score and the rounding direction. Motivated by these functions, you should combine them and create 1 different new Python score function(s).
    '''

    cauc_init_ag_1 = '''
<start_des>
The `myheurdiving` function evaluates whether to round a fractional MILP variable up or down by computing scores for both possibilities. The function assesses several factors: the proximity of the variable to integer values, the variable's potential impact on the objective function, the structural importance of the variable, and the past difficulty in changing this variable's value (expressed through pseudo costs). Additional penalties are incorporated for feasibility constraints associated with rounding directions, and a dynamic scaling factor based on the root node's relaxation solution to prioritize variables closer to their most recent feasible values. The function prioritizes exploration by heavily penalizing choices that are deemed less feasible, thereby encouraging a broader search in the feasible space, which is crucial for solving complex MILP problems effectively.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize scores for rounding directions
    score_down = 0
    score_up = 0
    roundup = False

    # Adjust scores based on the variable's contribution to the objective and structural influence
    influence_on_objective = obj / objnorm
    structural_influence = 0.05 * nNonz

    # Exploration adjustments based on root node relaxation solutions
    root_adjustment = abs(rootsolval - candsol) / (abs(rootsolval) + 1)  # Avoid division by zero

    # Calculating scores for rounding down and up
    if mayrounddown:
        score_down = (1 - candsfrac) * influence_on_objective - pscostdown - structural_influence - 0.2 * nlocksdown + root_adjustment
    if mayroundup:
        score_up = candsfrac * influence_on_objective + pscostup - structural_influence - 0.2 * nlocksup + root_adjustment

    # Bonus for binary variables
    if isBinary:
        score_down += 0.1
        score_up += 0.1

    # Decide on the rounding direction based on calculated scores
    if score_up > score_down:
        roundup = True
        score = score_up
    else:
        score = score_down

    return score, roundup
</end_code>
'''

    cauc_init_ag_2 = '''
<start_des>
The newly designed scoring function `myheurdiving` blends elements from previous algorithms to make informed rounding decisions. It integrates considerations of feasibility, objective function impact, structural complexity, and the need for exploration in MILP models. The function evaluates each variable's rounding potential based on its pseudo costs, feasibility of rounding directions, and the variable's structural impact (nonzero entries and locks). Special emphasis is given to binary variables due to their profound influence on problem structure. An innovative aspect of this function is the dynamic adjustment of scores based on the current solution's proximity to integral values and the exploration necessity, promoting diverse solution pathways and minimizing the repetitive exploration of similar solutions.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Base initialization of scores and rounding direction
    score_down = 0
    score_up = 0
    roundup = False

    # Objective and structural impact calculations
    obj_contrib_down = (1 - candsfrac) * (obj / objnorm)
    obj_contrib_up = candsfrac * (obj / objnorm)
    structural_impact = 0.02 * nNonz

    # Exploration necessity and feasibility considerations
    exploration_penalty_down = 0.05 * nlocksdown if mayrounddown else 0
    exploration_penalty_up = 0.05 * nlocksup if mayroundup else 0

    # Score calculations incorporating pseudo-costs, exploration, and feasibility
    if mayrounddown:
        score_down = obj_contrib_down - pscostdown - exploration_penalty_down - structural_impact
    if mayroundup:
        score_up = obj_contrib_up + pscostup - exploration_penalty_up - structural_impact

    # Special consideration for binary variables
    if isBinary:
        binary_bonus = 50
        score_down += binary_bonus
        score_up += binary_bonus

    # Decide the best rounding direction based on the calculated scores
    if score_up > score_down:
        roundup = True
        score = score_up
    else:
        score = score_down

    return score, roundup
</end_code>
'''

    cauc_init_ag_3 = '''
<start_des>
The new scoring function `myheurdiving` is crafted to strategically decide on the most effective rounding direction for a variable by utilizing a weighted scoring system that accounts for multiple aspects of the MILP model's dynamics. The function incorporates both the cost and benefit of rounding a variable up or down, adjusting for the impact on the objective function and overall feasibility. It evaluates the variable's contribution to the objective function, the closeness to an integer, the feasibility of rounding in either direction, and the structural complexity indicated by the number of non-zero entries and locks. A unique feature of this function is the adaptive exploration bonus, which slightly favors variables that are less explored in terms of rounding options, fostering a broader search of the solution space. Variables that are binary are given extra attention due to their critical influence on model behavior.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize rounding direction and base scores
    roundup = False
    score_down = 0
    score_up = 0

    # Adjust scores based on feasibility, pseudo costs, and exploration potential
    if mayrounddown:
        score_down = (abs(obj) / objnorm - pscostdown) * (1 + 0.05 / (1 + nlocksdown))
    if mayroundup:
        score_up = (abs(obj) / objnorm + pscostup) * (1 + 0.05 / (1 + nlocksup))

    # Include adjustments for closeness to integer and root node values
    if mayrounddown:
        score_down += (1 - candsfrac) * rootsolval * 10
    if mayroundup:
        score_up += candsfrac * rootsolval * 10

    # Determine the preferred rounding direction
    if score_up > score_down:
        roundup = True
        final_score = score_up
    else:
        final_score = score_down

    # Apply a special consideration for binary variables
    if isBinary:
        final_score += 50  # Significant bonus due to high sensitivity

    return final_score, roundup
</end_code>
'''

    cauc_init_ag_4 = '''
<start_des>
The new scoring function `myheurdiving` aims to balance between exploration and exploitation by considering various aspects of the variable's characteristics. It penalizes the feasibility of rounding directions to encourage exploration, rewards proximity to integer values and contribution to the objective function, and penalizes higher lock counts to maintain feasibility. Additionally, binary variables receive a significant bonus due to their critical role in solution dynamics. The new score function also takes into account the number of nonzero entries in the variable and the solution value in the last root node's relaxation, providing a comprehensive evaluation of the variable's importance and potential impact on the solution.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score and rounding direction
    score = 0
    roundup = False

    # Penalize feasibility of rounding directions to encourage exploration
    if mayrounddown or mayroundup:
        score -= 10

    # Reward proximity to integer values
    score += (1 - candsfrac) * 100

    # Reward contribution to objective function
    score += abs(obj) / objnorm

    # Penalize higher lock counts to maintain feasibility
    locks = max(nlocksdown, nlocksup)
    score -= locks * 5

    # Slight penalty if only one direction is feasible
    if not (mayroundup and mayrounddown):
        score *= 0.9

    # Binary variables get an extra score for critical rounding importance
    if isBinary:
        score += 100

    # Reward based on the number of nonzero entries and solution value in root node's relaxation
    score += nNonz * 10
    score += rootsolval * 20

    # Determine rounding direction based on feasibility and pseudo costs
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding

    return score, roundup
</end_code>

'''

    cauc_init_ag_5 = '''
<start_des>
The new scoring function `myheurdiving` is designed to optimally select a variable from the MILP solution for rounding by weighing its contribution to the objective, proximity to an integer value, and the impact on feasibility constraints. The function first determines the rounding direction based on the lower pseudo cost (`pscostdown` vs. `pscostup`), favoring the direction that causes fewer disruptions in the LP's feasibility and structure (indicated by the number of locks). The score is then calculated, balancing the objective function's urgency (weighted by its normalized contribution), the variable's closeness to an integer (emphasizing less fractional variables), and penalizing higher locks to minimize constraint violations. Variables that can only be rounded in one direction (due to feasibility) receive a slight penalty to encourage exploring more flexible options, and binary variables get a significant bonus due to their high sensitivity in solution dynamics.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine feasible rounding direction with lower pseudo cost
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding

    # Calculate the score
    score = 0
    direction_multiplier = -1 if roundup else 1
    score += abs(obj) / objnorm  # Normalize the objective contribution
    score += (1 - candsfrac) * 100  # Reward closeness to integer
    locks = nlocksup if roundup else nlocksdown
    score -= locks * 5  # Fewer locks is better, penalize higher lock numbers

    # Adjust the score based on feasibility of rounding direction
    if not (mayroundup and mayrounddown):
        score *= 0.9  # Slight penalty if only one direction is feasible

    # Binary variables get an extra score for critical rounding importance
    if isBinary:
        score += 100

    return score, roundup
</end_code>
'''

    cauc_init_ag_6 = '''
<start_des>
The new scoring function `myheurdiving` aims to balance between exploration and exploitation by considering various aspects of the variable's characteristics. It penalizes the feasibility of rounding directions to encourage exploration, rewards proximity to integer values and contribution to the objective function, and penalizes higher lock counts to maintain feasibility. Additionally, binary variables receive a significant bonus due to their critical role in solution dynamics.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score and rounding direction
    score = 0
    roundup = False

    # Penalize feasibility of rounding directions to encourage exploration
    if mayrounddown or mayroundup:
        score -= 10

    # Reward proximity to integer values
    score += (1 - candsfrac) * 100

    # Reward contribution to objective function
    score += abs(obj) / objnorm

    # Penalize higher lock counts to maintain feasibility
    locks = max(nlocksdown, nlocksup)
    score -= locks * 5

    # Slight penalty if only one direction is feasible
    if not (mayroundup and mayrounddown):
        score *= 0.9

    # Binary variables get an extra score for critical rounding importance
    if isBinary:
        score += 100

    # Determine rounding direction based on feasibility and pseudo costs
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding

    return score, roundup
</end_code>
'''

    cauc_init_ag_7 = '''
<start_des>
The new scoring function `myheurdiving` combines various aspects of the variable's characteristics to make an informed decision on variable selection for rounding in the MILP solution. It penalizes the feasibility of rounding directions to encourage exploration, rewards proximity to integer values, considers the variable's contribution to the objective function, penalizes higher lock counts to maintain feasibility, and provides a bonus for binary variables due to their critical role in solution dynamics. Additionally, it incorporates the number of nonzero entries in the variable to account for sparsity in the problem structure.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize score and rounding direction
    score = 0
    roundup = False

    # Penalize feasibility of rounding directions to encourage exploration
    if mayrounddown or mayroundup:
        score -= 10

    # Reward proximity to integer values
    score += (1 - candsfrac) * 100

    # Reward contribution to objective function
    score += abs(obj) / objnorm

    # Penalize higher lock counts to maintain feasibility
    locks = max(nlocksdown, nlocksup)
    score -= locks * 5

    # Slight penalty if only one direction is feasible
    if not (mayroundup and mayrounddown):
        score *= 0.9

    # Bonus for binary variables due to their critical role in solution dynamics
    if isBinary:
        score += 100

    # Incorporate sparsity of variable in the problem structure
    score += nNonz * 0.5

    # Determine rounding direction based on feasibility and pseudo costs
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding

    return score, roundup
</end_code>
'''

    cauc_init_ag_8 = '''
<start_des>The new scoring function, `myheurdiving`, combines various factors to evaluate each variable's desirability for rounding in a particular direction within the context of MILP. It considers the feasibility of rounding options, the variable's proximity to an integer value, its impact on the objective function, the structure of the problem indicated by the number of locks, and the variable's binary nature. The function aims to strike a balance between exploration and exploitation, favoring variables that offer significant improvements to the objective while maintaining feasibility and considering the problem's complexity.</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False
    
    # Penalize if only one rounding direction is feasible
    if not (mayroundup and mayrounddown):
        score -= 10
    
    # Calculate score based on proximity to integer and objective impact
    score += (1 - candsfrac) * 10  # Reward closeness to integer
    score += abs(obj) / objnorm  # Normalize the objective contribution
    
    # Adjust score based on the number of locks
    score -= (nlocksdown + nlocksup) * 5  # Penalize higher lock numbers
    
    # Reward binary variables for their importance
    if isBinary:
        score += 50
    
    # Determine rounding direction based on lower pseudo cost
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding
    
    return score, roundup
</end_code>

'''

    cauc_init_ag_9 = '''
<start_des>The new scoring function, `myheurdiving`, evaluates each variable's desirability for rounding based on various factors. It penalizes rounding options that restrict exploration, rewards proximity to integer values, considers the objective impact, penalizes high lock numbers, rewards binary variables, and selects rounding direction based on pseudo costs.</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False
    
    # Penalize if only one rounding direction is feasible
    if not (mayroundup and mayrounddown):
        score -= 20  # Increased penalty for restricting exploration
    
    # Reward closeness to integer and normalize objective contribution
    score += (1 - candsfrac) * 10  
    score += abs(obj) / objnorm  
    
    # Penalize higher lock numbers
    score -= (nlocksdown + nlocksup) * 5  
    
    # Reward binary variables
    if isBinary:
        score += 50
    
    # Determine rounding direction based on lower pseudo cost
    if pscostdown < pscostup and mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        return -float('inf'), False  # Return lowest score if no feasible rounding
    
    return score, roundup
</end_code>
'''

    cauc_init_ag_10 = '''
<start_des>The new scoring function `myheurdiving` is designed to systematically evaluate the potential impact of rounding a given MILP variable either up or down. It enhances decision-making by accounting for both the direct benefits of rounding (closeness to an integer, objective value impact) and the structural complexity of the problem (number of locks). Additionally, the function applies strategic consideration by assessing the trade-off between exploring new solutions (penalizing limited rounding options) and exploiting the known good paths (rewards for rounding based on pseudo costs and root solution values). This holistic approach aims to provide a robust heuristic that balances immediacy in solution improvement with long-term solution exploration.</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0
    roundup = False

    # Encourage exploration by penalizing the lack of rounding options
    if not (mayrounddown and mayroundup):
        score -= 20

    # Reward variables that are close to integer values and have a significant objective impact
    score += (1 - candsfrac) * 10  # Reward for closeness to integer value
    score += abs(obj) / objnorm  # Normalize the impact on the objective

    # Incorporate problem complexity via lock numbers
    score -= (nlocksdown + nlocksup) * 5  # Penalize higher lock numbers

    # Higher score for binary variables due to strategic importance
    if isBinary:
        score += 30

    # Decision on rounding direction based on pseudo costs and historical performance at root node
    if (pscostdown < pscostup and mayrounddown):
        roundup = False
    elif (pscostdown >= pscostup and mayroundup):
        roundup = True
    else:
        # If no rounding direction is feasible, return the lowest possible score
        return -float('inf'), roundup

    return score, roundup
</end_code>
'''

    setc_init_ag_1 = '''
<start_des>
The new scoring function, `myheurdiving`, integrates various aspects of a MILP variable's behavior in the LP relaxation to determine both the optimal rounding direction and its associated score. The function assesses feasibility (whether rounding down or up is allowed), the impact of rounding on the objective (using pseudo costs), and constraints on the variable's values (expressed through lock counts). The function also considers the variable's fractional part, its overall contribution to the objective (scaled by the pseudo costs), and additional penalties or benefits based on its binary nature and the presence of constraint locks. The function calculates separate scores for rounding down and up, comparing these to decide the best direction. It prioritizes rounding to the nearest integer, adjusts for the feasibility of each direction, and enhances the score for binary variables to encourage integer completeness.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize scores
    score_down = 0
    score_up = 0

    # Calculate scores for rounding down and up
    if mayrounddown:
        score_down = (1 - candsfrac) * (10 / (1 + pscostdown)) - nlocksdown * 2
    else:
        score_down = -1e6  # Penalize rounding down when not feasible

    if mayroundup:
        score_up = candsfrac * (10 / (1 + pscostup)) - nlocksup * 2
    else:
        score_up = -1e6  # Penalize rounding up when not feasible

    # Adjust scores for binary variables
    if isBinary:
        score_down += 20  # Enhance score for binary variables
        score_up += 20

    # Determine the best rounding direction
    if score_up > score_down:
        roundup = True
        final_score = score_up
    else:
        roundup = False
        final_score = score_down

    return final_score, roundup
</end_code>
'''

    setc_init_ag_2 = '''
<start_des>
The new scoring function, `myheurdiving`, integrates various aspects of a MILP variable to determine the optimal rounding direction and score its potential impact on the overall solution's quality. The function first decides the rounding direction based on feasibility and the lesser increase in objective function cost. The score computation is multifaceted, including factors such as the urgency to move the variable closer to an integer (more urgency for values closer to 0.5), impact on the objective (higher weight for lower objective contribution), structural constraints due to locks, and the variable's distance from its root solution value, promoting decisions that keep the solution trajectory stable. Special emphasis is placed on binary variables due to their significant leverage in solution space. This approach ensures the variable selection is not only feasible but also strategically optimal.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Decide rounding direction based on feasibility and cost
    if mayrounddown and mayroundup:
        if (1 - candsfrac) * pscostup < candsfrac * pscostdown:
            roundup = True
        else:
            roundup = False
    elif mayroundup:
        roundup = True
    elif mayrounddown:
        roundup = False
    else:
        roundup = False  # Default to prevent infeasibility when both directions are infeasible

    # Compute the score considering multiple factors
    score = 0
    if roundup:
        distance_to_integer = 1 - candsfrac
        pseudo_cost = pscostup
        lock_penalty = nlocksup
    else:
        distance_to_integer = candsfrac
        pseudo_cost = pscostdown
        lock_penalty = nlocksdown

    # Incorporating structural integrity and objective impact
    score += 10 / (1 + pseudo_cost) * (1 - distance_to_integer) * (10 / (1 + lock_penalty))
    stability = 0.1 * (rootsolval - candsol)
    score += stability

    # Additional scoring for binary variables
    if isBinary:
        score *= 1.5  # Significant boost for binaries

    return score, roundup
</end_code>

'''
    
    setc_init_ag_3 = '''
<start_des>
The new scoring function for the generic diving heuristic, `myheurdiving`, determines the rounding direction and score of a variable based on various features reflecting its characteristics in the LP relaxation and its impact on the objective function. The logic starts by determining the preferred rounding direction based on feasibility and the variable's fractional part. If both directions are feasible, the direction that minimizes the increase in objective function cost due to rounding is preferred. The score computation integrates multiple factors: the fractional part's distance from the nearest integer (to prioritize variables closer to an integer value), the pseudo costs which estimate the change in objective function value per unit change in variable value, and a penalty for variables locked significantly in one direction, which could indicate constraints that limit flexibility. Additional complexity and influence are considered through factors like the number of non-zero entries in the variable's constraint matrix, and special handling for binary variables to encourage their completion to integer values. The scoring is designed to prioritize higher values for more impactful variables on the solution.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determining the rounding direction based on feasibility and impact
    if mayrounddown and mayroundup:
        # Choose rounding direction based on lesser pseudo cost and closeness to integer
        if (1 - candsfrac) * pscostup < candsfrac * pscostdown:
            roundup = True
        else:
            roundup = False
    elif mayrounddown:
        roundup = False
    elif mayroundup:
        roundup = True
    else:
        # Neither rounding is feasible, handle as special case
        roundup = False  # Default to false to prevent infeasibility

    # Scoring function based on several features
    distance_to_integer = 1 - candsfrac if roundup else candsfrac
    pseudo_cost = pscostup if roundup else pscostdown
    lock_penalty = nlocksup if roundup else nlocksdown

    # Calculate the score, higher is better
    score = (1 / (1 + pseudo_cost)) * (1 - distance_to_integer) * (1 / (1 + lock_penalty)) * 100
    if isBinary:
        score *= 1.2  # Boost the score slightly for binary variables

    return score, roundup
</end_code>
'''
    
    setc_init_ag_4 = '''
<start_des>
The new scoring function, `myheurdiving`, is designed to effectively prioritize variables for rounding in a Mixed Integer Linear Programming scenario. It considers both feasibility and impact on the objective function. The decision on the rounding direction is first determined based on the available options (mayrounddown, mayroundup) and the associated costs. The scoring system emphasizes the trade-off between reaching an integer value and minimizing disruptions to the objective value. This function integrates multiple features such as the proximity to integer values, pseudo costs, and the degree of variable locking, thus refining the selection process. Additional emphasis is given to binary variables, recognizing their pivotal role in reaching integer solutions. The flexibility of rounding options is also assessed, rewarding less restricted moves to foster exploration over exploitation, which is crucial in large variable spaces.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine the rounding direction based on available feasibility and lower pseudo cost increase
    if mayrounddown and mayroundup:
        if (1 - candsfrac) * pscostup < candsfrac * pscostdown:
            roundup = True
        else:
            roundup = False
    elif mayroundup:
        roundup = True
    else:
        roundup = False  # Defaults to False if both directions are not possible

    # Score calculation integrates distance to nearest integer, pseudo costs, and the number of locks
    distance_to_integer = 1 - candsfrac if roundup else candsfrac
    pseudo_cost = pscostup if roundup else pscostdown
    flexibility_penalty = (nlocksup if roundup else nlocksdown) / (nNonz + 1)  # Penalize less flexibility to encourage exploration

    # Construct the score: better scores for less cost, closer to integer, and more flexibility
    score = ((1 / (1 + pseudo_cost)) * (1 - distance_to_integer) / (1 + flexibility_penalty)) * 100
    if isBinary:
        score *= 1.5  # Increase score for binary variables due to their significant impact

    return score, roundup
</end_code>

'''
    
    setc_init_ag_5 = '''
<start_des>
The new scoring function, `myheurdiving`, synthesizes insights from previous algorithms to optimize variable selection for rounding in MILP, focusing on maximizing exploration and impact on the objective function. It determines the rounding direction based on feasibility and desired exploration levels by considering both pseudo costs and the potential impact of each decision. The score calculation balances the proximity to integer values, pseudo costs, and lock counts to weigh the trade-offs between achieving feasible solutions and exploring potentially better but less obvious alternatives. Binary variables receive a special emphasis due to their significant influence on solution structure. The function adjusts scores based on the number of non-zero constraint matrix entries to reflect complexity and modifies scores to encourage choices that are less immediately obvious, thereby enhancing exploration in variable-heavy scenarios.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction for maximal exploration and minimal cost
    if mayrounddown and mayroundup:
        roundup = (1 - candsfrac) * pscostup < candsfrac * pscostdown
    elif mayroundup:
        roundup = True
    else:
        roundup = False  # Default to down if up is not possible

    # Calculate score using a composite measure
    distance_to_integer = 1 - candsfrac if roundup else candsfrac
    pseudo_cost = pscostup if roundup else pscostdown
    lock_penalty = nlocksup if roundup else nlocksdown

    score = (1 - distance_to_integer) * (1 / (1 + pseudo_cost)) * 100 / (1 + lock_penalty / (nNonz + 1))
    if isBinary:
        score *= 1.1  # Higher weight for binary variables

    # Encourage more complex variables to explore different parts of the solution space
    if nNonz > 0:
        score *= (1 + 0.05 / nNonz)  # Modify score based on complexity

    return score, roundup
</end_code>
'''
    
    setc_init_ag_6 = '''
<start_des>
The new scoring function `myheurdiving` incorporates comprehensive criteria to evaluate the desirability and feasibility of rounding a MILP variable up or down. The function integrates the potential rounding direction's feasibility, the variable's impact on the objective function, and other characteristics like the variable's locks and non-zero count in the constraint matrix. The function computes a score for each rounding direction based on feasibility, impact on the objective function (pseudo costs), distance from integer (closeness), and penalization for variable locking. A higher score reflects a more favorable rounding choice. Additionally, binary variables receive a boost due to their integral nature. The function selects the rounding direction with the highest score and outputs both the score and the chosen direction.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Initialize scores
    score_down = score_up = 0

    # Calculating scores for rounding down and up
    if mayrounddown:
        score_down = ((1 - candsfrac) * objnorm) - (pscostdown * nlocksdown) + (candsol * 10)
    else:
        score_down = -1e6  # large penalty for infeasible rounding

    if mayroundup:
        score_up = (candsfrac * objnorm) - (pscostup * nlocksup) + (candsol * 10)
    else:
        score_up = -1e6  # large penalty for infeasible rounding

    # Additional scoring for binary variables
    if isBinary:
        score_down *= 1.1
        score_up *= 1.1

    # Determine the better rounding direction
    if score_up > score_down:
        return score_up, True  # Round up is better
    else:
        return score_down, False  # Round down is better
</end_code>
'''

    setc_init_ag_7 = '''
<start_des>
The proposed scoring function `myheurdiving` integrates insights from previous algorithms to refine decision-making in the rounding process of MILP solutions. The function emphasizes feasibility, influence on the objective function, and the overall structure of the problem constraints. The determination of the rounding direction hinges on minimizing the pseudo cost while considering the proximity to the variable's root solution value. The score calculation incorporates the urgency of rounding (distance from the nearest integer), feasibility of the rounding direction, and the expected impact on the objective function due to rounding. The complexity of the variable in the constraint matrix and a special emphasis on binary variables are considered to balance between quick feasible solutions and optimal ones. A higher score suggests a more desirable variable to round at the given step, facilitating faster convergence to an integer solution.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction using feasibility, root solution alignment, and lesser pseudo cost
    if isBinary:
        roundup = candsol > 0.5
    elif mayrounddown and mayroundup:
        if abs(candsol - rootsolval) < 0.5:
            roundup = pscostup < pscostdown
        else:
            roundup = pscostup > pscostdown
    elif mayroundup:
        roundup = True
    elif mayrounddown:
        roundup = False
    else:
        roundup = False  # Default when neither is feasible

    # Score calculation considering urgency, impact, and constraint complexity
    distance_to_integer = 1 - candsfrac if roundup else candsfrac
    pseudo_cost = pscostup if roundup else pscostdown
    lock_penalty = nlocksup if roundup else nlocksdown
    norm_adjusted_obj = obj / (1 + objnorm)  # Adjust objective with norm to normalize its scale

    # Final score formula
    score = (1 - distance_to_integer) * norm_adjusted_obj - (pseudo_cost + 0.1 * lock_penalty)
    if isBinary:
        score *= 1.1  # Slightly higher weight for binary variables to encourage quick feasibility

    return score, roundup
</end_code>
'''

    setc_init_ag_8 = '''
<start_des>
The new scoring function `myheurdiving` incorporates elements from the provided algorithms, emphasizing variable selection and rounding direction determination, while balancing exploration and optimization in the MILP diving heuristic. The function evaluates rounding feasibility, the fractional part of the variable, its influence on the objective function, and constraints related to its values. The score is formulated by integrating the fractional distance to the nearest integer, the pseudo costs, lock counts, and the variable's characteristics, with modifications to encourage exploration and optimize impact. A special focus is given to enhancing the decision process for binary variables and those variables significantly affecting the objective function through their root solution values.
</start_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine initial rounding feasibility and select pseudo costs and locks accordingly
    if mayrounddown and mayroundup:
        rounding_bias = 0.1  # Encourage exploring less obvious rounding directions
        if (1 - candsfrac) * pscostup < candsfrac * pscostdown:
            roundup = True
            score = (1 - candsfrac) * (10 / (1 + pscostup)) - (nlocksup * 2) - rounding_bias
        else:
            roundup = False
            score = candsfrac * (10 / (1 + pscostdown)) - (nlocksdown * 2) - rounding_bias
    elif mayroundup:
        roundup = True
        score = candsfrac * (10 / (1 + pscostup)) - (nlocksup * 2)
    elif mayrounddown:
        roundup = False
        score = (1 - candsfrac) * (10 / (1 + pscostdown)) - (nlocksdown * 2)
    else:
        # If no rounding is feasible, choose the lesser penalty path
        roundup = False
        score = -1e6

    # Modify score for binary variables significantly
    if isBinary:
        score += 20

    # Additional adjustments based on the root solution value
    if rootsolval != 0:
        score += rootsolval * 0.1

    # Penalize complex variables with many constraints to encourage simplicity
    score -= nNonz * 0.05

    return score, roundup
</end_code>
'''

    setc_init_ag_9 = '''
<start_des>
The scoring function `myheurdiving` is designed to evaluate the desirability of rounding each variable up or down in a MILP problem based on a set of features provided for each variable. The function considers whether rounding up or down is feasible, the objective contribution of the variable, its distance from being integral, and other contextual factors. The choice of rounding direction (up or down) is initially determined by which direction has a lower pseudo cost, suggesting fewer side effects on the LP's feasibility and optimality. If both directions are feasible, the direction that moves the variable towards its root node solution is preferred, assuming it results in a closer alignment with the higher-level solution structure of the problem.

The score for each variable is computed by weighing the fractional part of the variable (indicating its urgency for rounding), the pseudo costs for changes, and the potential improvement in the objective function. A penalty is added based on the number of locks, which indicates constraints that would be affected by rounding, thereby capturing the complexity and potential impact of changing this variable. Binary variables are handled differently, emphasizing rapid integer feasibility due to their limited range.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Decide the rounding direction
    if isBinary and candsol > 0.5:
        roundup = True
    elif isBinary and candsol <= 0.5:
        roundup = False
    else:
        if mayrounddown and mayroundup:
            if abs(candsol - rootsolval) < 0.5:
                roundup = pscostup > pscostdown
            else:
                roundup = pscostup < pscostdown
        elif mayroundup:
            roundup = True
        elif mayrounddown:
            roundup = False
        else:
            roundup = pscostup < pscostdown  # Default to the direction with lesser impact

    # Compute the score
    if roundup:
        score = (1 - candsfrac) * obj - pscostup - nlocksup
    else:
        score = candsfrac * obj - pscostdown - nlocksdown

    # Apply penalties based on the complexity and feasibility
    score -= (nlocksdown + nlocksup) * 0.1  # Lower scores for variables with many dependencies

    return score, roundup
</end_code>

'''

    setc_init_ag_10 = '''
<start_des>
The new scoring function, `myheurdiving`, blends concepts from previous iterations to optimize rounding decisions in MILP based on a strategic evaluation of feasibility, constraint complexity, and the impact on the objective function. It aims to strike a balance between feasible solutions and exploring beneficial rounding opportunities by evaluating the impact of rounding up versus down. The direction for rounding is chosen based on a combination of feasibility, proximity to the integer value, and the least negative impact on the objective function through pseudo costs. This function also considers the structure of the problem by adjusting the score according to the complexity of the variable's involvement in constraints. A higher score is given to variables that have a lower pseudo cost, nearer proximity to integer values, and lower lock penalties, making them more appealing for rounding. This tailored approach ensures that the heuristic not only strives for feasibility but also nurtures exploration, especially in densely connected variables.
</end_des>

<start_code>
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    # Determine rounding direction based on feasibility and minimal pseudo cost impact
    if mayrounddown and mayroundup:
        roundup = pscostup < pscostdown if abs(candsol - rootsolval) < 0.5 else candsol > 0.5
    elif mayroundup:
        roundup = True
    elif mayrounddown:
        roundup = False
    else:
        roundup = False  # Default when neither is feasible

    # Calculate score emphasizing proximity to integer, lower pseudo cost, and lower lock penalties
    distance_to_integer = abs(candsol - round(candsol))
    pseudo_cost = pscostup if roundup else pscostdown
    lock_penalty = nlocksup if roundup else nlocksdown
    objective_impact = obj / (1 + objnorm)  # Normalize the influence of the objective function

    # Incorporate complexity and binary preference
    complexity_factor = 1 / (1 + 0.05 * nNonz) if nNonz else 1  # Less weight for more complex variables
    binary_boost = 1.1 if isBinary else 1  # Additional boost for binary variables

    # Final score formula
    score = ((1 - distance_to_integer) * objective_impact - pseudo_cost - lock_penalty) * complexity_factor * binary_boost

    return score, roundup
</end_code>
'''


    # init_pop = [setc_init_ag_1,setc_init_ag_2,setc_init_ag_3,setc_init_ag_4,setc_init_ag_5,setc_init_ag_6,setc_init_ag_7,setc_init_ag_8,setc_init_ag_9,setc_init_ag_10]


    # give the prompts to init ea_methods
    llm = MyLLM(model=model)
    ea_methods = EAMethods(llm, background_prompt, features_description, inout_format_description, instruction, init_prompt, init_prompt_suggestion, mutation_prompt, crossover_prompt)
    
    init_pop = []
    populations = []
    
    current_datetime = datetime.datetime.now()
    time_stamp = current_datetime.strftime("%Y%m%d%H%M")
    info_path = "/home/yyzhou/LLM4Heur/tmp/EA_" + instance_name[:4] + "/" + time_stamp + ".txt"
    info_dir = "/home/yyzhou/LLM4Heur/tmp/EA_" + instance_name[:4]
    if not os.path.exists(info_dir):
        os.makedirs(info_dir)

    
    # initialization with init pop
    for init_ag_content in init_pop:

        init_ag_individual = AGIndividual(content=init_ag_content,evaluated=False,score=-10e8,llm=llm)
        mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(init_ag_individual.code, instance_name, dataset, diving_ind=DIVEING_IND)
        init_ag_individual.set_score( -mean_rel )

        populations.append(init_ag_individual)

    # initialization without init pop
    while( len(populations) < n_pop):

        ag_individual = ea_methods.initialization()
        mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(ag_individual.code, instance_name, dataset, diving_ind=DIVEING_IND)

        ag_individual.set_score( -mean_rel )

        populations.append(ag_individual)

    populations.sort(key=lambda x:x.get_score())
    while( len(populations) > n_pop):
        populations.pop(0)
    
    s = ""
    for alg in populations:
        score = alg.get_score()
        s = s + "-------------------\n" \
            + "score:" + str(-score) + "\n" \
            + alg.get_content() +"\n\n"
        
    round_info = "round:" + str(0) +"\n"
    
    with open(info_path, 'a') as file:
        file.write(round_info)
        file.write(s)


    for i in range(n_round):

        print("round:",i)
        print("\n")
        

        added_individuals = []
        
        for j in range(n_pop):

            # immigrant
            print("immigrant")
            immigrant_individual = ea_methods.initialization()
            mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(immigrant_individual.code, instance_name, dataset, diving_ind=DIVEING_IND)

            immigrant_individual.set_score( -mean_rel )
            
            added_individuals.append(immigrant_individual)

            # selection            
            p_individuals = ea_methods.selection(populations)

            # crossover
            print("crossover")
            s_individual_1 = ea_methods.crossover(p_individuals[0], p_individuals[1])

            if( s_individual_1.get_code() == p_individuals[0].get_code() or s_individual_1.get_code() == p_individuals[1].get_code() ):
                score = p_individuals[0].get_score() if s_individual_1.get_code() == p_individuals[0].get_code() else p_individuals[1].get_score()
                s_individual_1.set_score(score)
            
            else:
                mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(s_individual_1.code, instance_name, dataset, diving_ind=DIVEING_IND)
                s_individual_1.set_score( -mean_rel )
                
                if(  ( EQ(s_individual_1.get_score(), p_individuals[0].get_score()) or EQ(s_individual_1.get_score(), p_individuals[1].get_score()) ) and random.uniform(0.0,1.0)>0.1 ):
                    pass
                else:
                    added_individuals.append(s_individual_1)

            # mutation
            print("mutation")
            s_individual_2 = ea_methods.mutation(s_individual_1, prob=1)
            
            if( s_individual_1.get_code() == s_individual_2.get_code() ):
                pass
            else:
                mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(s_individual_2.code, instance_name, dataset, diving_ind=DIVEING_IND)
                s_individual_2.set_score( -mean_rel )

                if(  EQ( s_individual_1.get_score(), s_individual_2.get_score() ) and random.uniform(0.0,1.0)>0.1):
                    added_individuals.append( s_individual_2)
            

        for item in added_individuals:
            populations.append(item)
        
        populations.sort(key=lambda x:x.get_score())
        while( len(populations) > n_pop):
            populations.pop(0)
        
        s = ""
        for alg in populations:
            score = alg.get_score()
            s = s + "-------------------\n" \
                + "score:" + str(-score) + "\n" \
                + alg.get_content() +"\n\n"
            
        round_info = "round:" + str(i+1) +"\n"
        
        with open(info_path, 'a') as file:
            file.write(round_info)
            file.write(s)
    
    valid_pop = populations[-int(n_pop/2):]
    s = ""
    for alg in valid_pop:
        mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = eval_heur(alg.code, instance_name, valid_dataset, diving_ind=DIVEING_IND)
        s = s + "-------------------\n" \
        + "score:" + str(mean_rel) + "\n" \
        + alg.get_content() +"\n\n"
    
    valid_info = "valid:+++++++++++++++++"
    with open(info_path, 'a') as file:
        file.write(valid_info)
        file.write(s)

    
if __name__ == "__main__":
    run(n_round=30, n_pop=15, instance_name="cauctions", dataset="train50", model = "gpt-3.5-turbo", DIVEING_IND=3)
        