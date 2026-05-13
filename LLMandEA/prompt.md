<inout format description> = Provide a brief description of the new score function's logic and its corresponding Python code. The description must start with '<start_des>' and end with '</end_des>'. The code must start with '<start_code>' and end with '</end_code>'. The code score function must called 'myheurdiving' that takes 13 inputs 'mayrounddown', 'mayroundup', 'candsfrac', 'candsol', 'nlocksdown', 'nlocksup', 'obj', 'objnorm', 'pscostdown', 'pscostup', 'rootsolval', 'nNonz' and 'isBinary'. The function must output the 'score' and 'roundup', where 'score' is a float type indicating the variable's score, the more the better, and the 'roundup' is a bool type indicating whether we should round the variable up, True for rounding up. 

​<instruction> = Be creative and do not give additional explanations.

<features description> = "mayrounddown" and "mayroundup" (bool, indicate whether it is possible to round variable down/up and stay feasible, it should be penalized because we need more exploration); "candsfrac" (float, fractional part of solution value of variable); "candsol" (float, solution value of variable in LP relaxation solution); "nlocksdown" and "nlocksup" (int, the number of locks for rounding down/up of a special type); "obj" (float, objective function value of variable); "objnorm" (float, the Euclidean norm of the objective function vector); "pscostdown" and "pscostup" (float, the variable's pseudo cost value for the given change of the variable's LP value); "rootsolval" (float, the solution of the variable in the last root node's relaxation, if the root relaxation is not yet completely solved, zero is returned); "nNonz" (int, the number of nonzero entries in variable); "isBinary" (bool, TRUE if the variable is of binary type). 

------------
<background prompt>
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

-------------

**Initialization** prompt: 

​<init prompt> = Please focus on line 6 of the Generic Diving Heuristic. You should create a totally new Python scoring function for me (different from the heuristics in the literature) to choose the fractional variable and corresponding rounding direction using the information of the LP relaxation and objective function. The function is used for every variable to decide the variable's score and rounding direction. 
Specifically, you have 13 features to use in the score function: <features description>

<init prompt suggestions> = There is(are) 1 suggestion(s): 1) you should first decide the rounding direction and the determine the score of the corresponding variable.

<inout format description>
<instruction>

----------------

**Mutation** prompt:

​<mutation prompt> = Please focus on line 6 of the Generic Diving Heuristic. I have a score function with its code to get the variable's score and its rounding direction. Motivated by the algorithm, you should create a different new Python score function.

​The score function and the corresponding code are:
<algorithm description>
<code>

​Motivated by the above algorithm, you should create a different new Python score function provided using the following 13 features: <features description>

<inout format description>
<instruction>

-----------------

**Crossover** prompt:

<crossover prompt> = ​Please focus on line 6 of the Generic Diving Heuristic. I have some score functions with their code to get the variable's score and the rounding direction. Motivated by these functions, you should combine them and create 1 different new Python score function(s).

​The first algorithm and the corresponding code is:
<algorithm description>
<code>
​The second algorithm and the corresponding code is:
<algorithm description>
<code>

​Motivated by these functions, you should combine them and create 1 different new Python score function(s) using the following 13 features: <features description>

<inout format description>
<instruction>