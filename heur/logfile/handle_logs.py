import os
import re
import numpy as np
import json

def get_unsolved_primalbound(path,keyword):
    with open(path) as file:
        content = file.read()

    input_string = content
    lines = input_string.strip().split("\n")

    # Initialize variables to store the desired line containing keyword
    desired_line = ""
    is_find = False

    # Iterate through each line in reverse order to find the last line containing keyword
    for line in reversed(lines):
        if keyword in line:
            is_find = True
            desired_line = line
            break
    
    if(not is_find):
        print("NOooooo:",keyword)
        return (is_find,0)
    
    split_values = desired_line.split("|")

    # Extract the relevant fields from the split values

    primal_bound = split_values[-3].strip()  # '6.520716e+03'

    return (is_find, float(primal_bound))

def extract_info(text):
    info_dict = {}
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            info_dict[key.strip()] = value.strip()
    return info_dict

# use regular expression to get the dual bound/ primal bound
def get_solved_bestsol(path):
    
    with open(path) as file:
        content = file.read()

    position = 0
    position = content.find("SCIP Status ", position)

    extracted_text = content[position:]

    info_dictionary = extract_info(extracted_text)
    
    result = re.search(r'(.+?)\s*\(', info_dictionary["Primal Bound"])

    if result:
        pb = result.group(1)
        return float(pb)
    else:
        print("no matching contents")
        return float(info_dictionary["Primal Bound"])


epsilon = 1e-10

t = "train20"
# cauctions, facilities, indset, setcover, miplib, loadbalance
name = "miplib"
# heurs = [ 'coefdiving', 'coef2diving', 'distributiondiving', 'farkasdiving', 'fracdiving','frac2diving','linesearchdiving','linesearch2diving','pscostdiving','pscost2diving','veclendiving','veclen2diving','feaspump', 'rounding', 'objpscostdiving', 'rootsoldiving']
# heurs = [ 'coefdiving', 'coef2diving', 'distributiondiving', 'farkasdiving', 'fracdiving','frac2diving','linesearchdiving','linesearch2diving','pscostdiving','pscost2diving','veclendiving','veclen2diving']
heurs = [ 'coefdiving', 'distributiondiving', 'farkasdiving', 'fracdiving','linesearchdiving','pscostdiving','veclendiving','myheurdiving_mulgpt351','myheur3diving_mulclaude31','myheur3diving']




if __name__=="__main__":
    
    for heur in heurs:
        if( (name=='indset' or name == 'loadbalance') and heur=='farkasdiving'):
            continue
        print("\n")

        keyword = heur[:6]

        solved_logdir = '/home/yyzhou/LLM4Heur/heur/logfile/logs/'+ name +'/solved/'+ t
        unsolved_logdir = '/home/yyzhou/LLM4Heur/heur/logfile/logs/'+name+'/unsolved/'+ t +'/' + heur

        
        print(name,heur)

        unsolved_logfiles = os.listdir(unsolved_logdir)
        unsolved_logfiles.sort()
        n_ins = len(unsolved_logfiles)
        # n_ins = min(500,n_ins)

        data_abs = []
        data_rel = []
        data_dict = {}
        for log in unsolved_logfiles:
            
            unsolved_logpath = unsolved_logdir + '/'+ log
            solved_logpath = solved_logdir + '/'+ log

            is_find, primal_bound = get_unsolved_primalbound(unsolved_logpath,keyword)
            if(name == "miplib" and t == "train20"):
                with open('/home/yyzhou/LLM4Heur/heur/logfile/logs/miplib/solved/train20.json', 'r') as f:
                    data = json.load(f)
                    bestsol = data[log[:-11]]
            else: 
                bestsol = get_solved_bestsol(solved_logpath)
            
            
            if(is_find):
                data_abs.append( abs(primal_bound-bestsol) )
                data_rel.append( 100 * abs(primal_bound-bestsol) / (bestsol+epsilon) )
                data_dict[log[:-4]]  =  abs(primal_bound-bestsol)
            else:
                data_dict[log[:-4]]  = 1e8  
            
        mean_abs,mean_rel = np.mean(data_abs), np.mean(data_rel)
        std_abs,std_rel = np.std(data_abs), np.std(data_rel)
        SEM_abs,SEM_rel = std_abs / np.sqrt(len(data_abs)), std_rel / np.sqrt(len(data_rel))
        print("number of valid data:",len(data_rel))
        print("mean_abs:",mean_abs,"; std_abs:",std_abs,"; SEM_abs:", SEM_abs)
        print("mean_rel:",mean_rel,"%; std_rel:",std_rel,"; SEM_rel:", SEM_rel)

        print(data_dict)

