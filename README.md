# LLM4Solver

**Large Language Model for Efficient Algorithm Design of Combinatorial Optimization Solver**

## Overview

This project explores the use of Large Language Models (LLMs) combined with Evolutionary Algorithms (EA) to automatically design and optimize primal heuristics (specifically diving heuristics) for Mixed Integer Linear Programming (MILP) solvers. The core idea is to leverage LLMs (such as GPT-3.5, GPT-4, Claude-3, GLM-4) as "code generators" within an evolutionary framework, where each individual in the population is a scoring function for a diving heuristic, and the EA operators (initialization, mutation, crossover) are implemented via LLM prompts.

## Project Purpose

Traditional MILP solvers (like SCIP) rely on hand-crafted heuristics designed by domain experts. This project aims to:

1. **Automatically discover novel diving heuristic scoring functions** using LLMs as creative algorithm designers.
2. **Evolve and improve these functions** through an evolutionary process (selection, crossover, mutation) guided by actual solver performance.
3. **Evaluate the generated heuristics** on diverse MILP benchmark instances and compare against classical baselines (coefdiving, fracdiving, pscostdiving, linesearchdiving, veclendiving, etc.).
4. **Explore multi-objective optimization** (via NSGA-II) to find Pareto-optimal heuristics across different problem families.

## Architecture

```
LLM4Solver/
├── LLMandEA/          # Core: LLM + Evolutionary Algorithm framework
│   ├── EA.py          # LLM wrapper, Individual representation, EA operators
│   ├── eval.py        # Evaluation: runs generated heuristics on SCIP and measures quality
│   ├── runEA.py       # Single-instance EA runner (single-objective)
│   ├── runEA2.py      # Multi-instance EA runner (aggregated score across 4 benchmarks)
│   ├── runEA3.py      # Multi-instance evaluation without evolution (batch evaluation)
│   ├── runNSGA2.py    # Multi-objective EA runner using NSGA-II
│   ├── run_miplib.py  # Testing on MIPLIB benchmark instances
│   ├── run_nnverify.py    # Testing on neural network verification instances
│   ├── run_nnverify2.py   # Additional NN verification experiments
│   ├── run_loadbalance.py # Testing on load balancing instances
│   ├── run_valid_lb.py    # Validation on load balancing instances
│   ├── prompt.md      # Documentation of all prompt templates used
│   └── test/          # Prompt testing
├── heur/              # Heuristic implementations and baselines
│   ├── heur_diving/   # Reference implementations of classical diving heuristics
│   │   ├── diving.py      # coefdiving, fracdiving, pscostdiving, linesearchdiving, veclendiving
│   │   └── func_helper.py # Helper functions for calling diving heuristics
│   ├── heur_rounding.py   # Full implementation of SCIP rounding heuristic in Python
│   ├── rounding.py        # Simple rounding heuristic prototype
│   ├── baselines/     # Baseline solvers for comparison
│   │   ├── baseline.py    # Run SCIP with default settings on benchmarks
│   │   └── handle_logs.py # Parse log files for results
│   └── logfile/       # Log file processing utilities
│       ├── solved.py      # Process logs for fully solved instances
│       ├── unsolved.py    # Process logs for unsolved instances
│       ├── heursolved.py  # Process logs for heuristic-solved instances
│       └── handle_logs.py # General log file handler
└── tmp/               # Temporary files, experiment results, and generated heuristics
    ├── diving.py ~ diving4.py    # Runtime slots for generated heuristic code
    ├── state.json ~ state4.json  # Execution state tracking
    ├── func_helper.py            # Dynamic code loader (used by modified SCIP)
    ├── EA_cauc/       # EA results for Combinatorial Auctions
    ├── EA_setc/       # EA results for Set Cover
    ├── EA_faci/       # EA results for Facility Location
    ├── EA_inds/       # EA results for Independent Set
    ├── EA_mul/        # Multi-objective results with plots
    └── EA_mul2/       # Additional multi-objective results
```

## How It Works

### 1. Individual Representation (`EA.py` - `AGIndividual`)

Each individual in the EA population consists of:
- **Description**: A natural language explanation of the scoring function's logic (enclosed in `<start_des>...</end_des>` tags)
- **Code**: A Python function `myheurdiving(...)` that takes 13 features and returns `(score, roundup)` (enclosed in `<start_code>...</end_code>` tags)
- **Score**: Performance metric obtained from evaluation

### 2. EA Operators via LLM (`EA.py` - `EAMethods`)

- **Initialization**: LLM generates a novel scoring function from scratch given a background prompt about MILP diving heuristics
- **Mutation**: LLM is shown an existing scoring function and asked to create a different variant
- **Crossover**: LLM is shown two parent functions and asked to combine them into a new function
- **Selection**: Roulette-wheel selection based on fitness scores

### 3. Evaluation (`eval.py`)

Generated heuristic code is:
1. Written to a temporary file (`diving.py`)
2. Loaded dynamically by a modified PySCIPOpt diving heuristic plugin
3. Run on MILP instances with SCIP (node limit = 1, all other heuristics disabled)
4. Evaluated by comparing the heuristic's primal bound against the known optimal solution
5. Scored using mean relative error (lower is better)

### 4. Diving Heuristic Scoring Function

The generated function `myheurdiving` takes 13 features for each fractional variable:

| Feature | Type | Description |
|---------|------|-------------|
| `mayrounddown` | bool | Can the variable be rounded down feasibly? |
| `mayroundup` | bool | Can the variable be rounded up feasibly? |
| `candsfrac` | float | Fractional part of the LP solution value |
| `candsol` | float | LP relaxation solution value |
| `nlocksdown` | int | Number of down-rounding locks |
| `nlocksup` | int | Number of up-rounding locks |
| `obj` | float | Objective function coefficient |
| `objnorm` | float | Euclidean norm of objective vector |
| `pscostdown` | float | Pseudo-cost for rounding down |
| `pscostup` | float | Pseudo-cost for rounding up |
| `rootsolval` | float | Solution value in root node relaxation |
| `nNonz` | int | Number of nonzero entries |
| `isBinary` | bool | Whether the variable is binary |

It returns:
- `score` (float): Higher means the variable is more preferred for rounding
- `roundup` (bool): True = round up, False = round down

## Benchmark Instances

The project evaluates on several MILP problem families:

- **Combinatorial Auctions** (`cauctions`): Winner determination in combinatorial auctions
- **Set Cover** (`setcover`): Minimum cost set cover problems
- **Facility Location** (`facilities`): Capacitated facility location problems
- **Independent Set** (`indset`): Maximum independent set problems
- **MIPLIB**: Standard mixed-integer programming benchmark library
- **Load Balancing** (`loadbalance`): Load balancing optimization problems
- **NN Verification** (`nnverify`): Neural network verification via MILP encoding

Each family has `train`, `valid`, and `test` splits for proper evaluation methodology.

## LLM Models Used

- GPT-3.5-turbo / GPT-3.5-turbo-16k
- GPT-4
- Claude-3-Sonnet
- GLM-4 (ZhipuAI)

## Dependencies

- `pyscipopt` - Python interface for SCIP solver (modified to support custom diving heuristics)
- `numpy` - Numerical computation
- `requests` - LLM API calls
- `zhipuai` - ZhipuAI SDK (for GLM-4)
- `matplotlib` - Visualization (for NSGA-II Pareto fronts)

## Key Results Storage

- Evolution logs are stored in `tmp/EA_<problem>/` with timestamps
- Each log file records the population state at each generation (score + code for each individual)
- Validation results are appended at the end of each run
- NSGA-II results include Pareto front visualizations

## Running Experiments

```bash
# Single-objective EA on Combinatorial Auctions
cd LLMandEA
python runEA.py

# Multi-instance evaluation
python runEA2.py

# Multi-objective (NSGA-II)
python runNSGA2.py <diving_ind> <model_name>

# Test on MIPLIB (parallel execution)
python run_miplib.py <worker_id> <total_workers>

# Test on NN Verification
python run_nnverify.py <worker_id> <total_workers>
```

## Research Context

This work is part of the emerging research direction of using LLMs for algorithm design and optimization, specifically:
- **LLM as Algorithm Designer**: Using LLMs to generate novel algorithmic components
- **Evolutionary Prompt Engineering**: EA operators implemented through structured prompts
- **Automated Heuristic Design**: Replacing manual heuristic tuning with automated search
- **Code-as-Individual**: Each EA individual is executable code, bridging natural language reasoning with programmatic evaluation
