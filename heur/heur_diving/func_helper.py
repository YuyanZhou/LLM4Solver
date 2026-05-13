
def coefdiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    path = "/home/yyzhou/LLM4Heur/heur/heur_diving/diving.py"
    with open(path, 'r') as file:
        contents = file.read()

    function_dict = {}
    exec(contents, function_dict)

    heurdiving = function_dict['coefdiving']

    return heurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)

def fracdiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    path = "/home/yyzhou/LLM4Heur/heur/heur_diving/diving.py"
    with open(path, 'r') as file:
        contents = file.read()

    function_dict = {}
    exec(contents, function_dict)

    heurdiving = function_dict['fracdiving']

    return heurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)

def pscostdiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    path = "/home/yyzhou/LLM4Heur/heur/heur_diving/diving.py"
    with open(path, 'r') as file:
        contents = file.read()

    function_dict = {}
    exec(contents, function_dict)

    heurdiving = function_dict['pscostdiving']

    return heurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)

def linesearchdiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    path = "/home/yyzhou/LLM4Heur/heur/heur_diving/diving.py"
    with open(path, 'r') as file:
        contents = file.read()

    function_dict = {}
    exec(contents, function_dict)

    heurdiving = function_dict['linesearchdiving']

    return heurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)

def veclendiving_helper(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    path = "/home/yyzhou/LLM4Heur/heur/heur_diving/diving.py"
    with open(path, 'r') as file:
        contents = file.read()

    function_dict = {}
    exec(contents, function_dict)

    heurdiving = function_dict['veclendiving']

    return heurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary)
