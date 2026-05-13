import os
import json

def myheurdiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):   
    try:
        path = "/home/yyzhou/LLM4Heur/tmp/diving.py"
        with open(path, 'r') as file:
            contents = file.read()

        function_dict = {}
        exec(contents, function_dict)

        myheurdiving = function_dict['myheurdiving']
        score, roundup = myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)
        assert((type(score) == float) or (type(score) == int))
        assert( (type(roundup) == bool) or (type(roundup) == int) )
        return score, roundup
    except Exception as e:
        # set the state to decide whether the heur is executable or not, it may be init in /home/yyzhou/LLM4Heur/LLMandEA/eval.py
        
        state = {
            "heur_executable": False,
            "error": str(e)
        }
        with open('/home/yyzhou/LLM4Heur/tmp/state.json', 'w') as f:
            json.dump(state, f, indent=4)
        return 0, 1

def myheur2diving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    try:
        path = "/home/yyzhou/LLM4Heur/tmp/diving2.py"
        with open(path, 'r') as file:
            contents = file.read()

        function_dict = {}
        exec(contents, function_dict)

        myheurdiving = function_dict['myheurdiving']
        score, roundup = myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)
        assert((type(score) == float) or (type(score) == int))
        assert( (type(roundup) == bool) or (type(roundup) == int) )
        return score, roundup
    except Exception as e:
        # set the state to decide whether the heur is executable or not, it may be init in /home/yyzhou/LLM4Heur/LLMandEA/eval.py
        state = {
            "heur_executable": False,
            "error": str(e)
        }
        with open('/home/yyzhou/LLM4Heur/tmp/state2.json', 'w') as f:
            json.dump(state, f, indent=4)
        return 0, 1

def myheur3diving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    try:
        path = "/home/yyzhou/LLM4Heur/tmp/diving3.py"
        with open(path, 'r') as file:
            contents = file.read()

        function_dict = {}
        exec(contents, function_dict)

        myheurdiving = function_dict['myheurdiving']
        score, roundup = myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)
        assert((type(score) == float) or (type(score) == int))
        assert( (type(roundup) == bool) or (type(roundup) == int) )
        return score, roundup
    except Exception as e:
        # set the state to decide whether the heur is executable or not, it may be init in /home/yyzhou/LLM4Heur/LLMandEA/eval.py
        state = {
            "heur_executable": False,
            "error": str(e)
        }
        with open('/home/yyzhou/LLM4Heur/tmp/state3.json', 'w') as f:
            json.dump(state, f, indent=4)
        return 0, 1
    
def myheur4diving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    try:
        path = "/home/yyzhou/LLM4Heur/tmp/diving4.py"
        with open(path, 'r') as file:
            contents = file.read()

        function_dict = {}
        exec(contents, function_dict)

        myheurdiving = function_dict['myheurdiving']
        score, roundup = myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)
        # print("score type:",type(score))
        assert((type(score) == float) or (type(score) == int))
        assert( (type(roundup) == bool) or (type(roundup) == int) )
        return score, roundup
    
    except Exception as e:
        # set the state to decide whether the heur is executable or not, it may be init in /home/yyzhou/LLM4Heur/LLMandEA/eval.py
        state = {
            "heur_executable": False,
            "error": str(e)
        }
        with open('/home/yyzhou/LLM4Heur/tmp/state4.json', 'w') as f:
            json.dump(state, f, indent=4)
        return 0, 1
