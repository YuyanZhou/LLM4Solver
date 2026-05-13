import os
import re
import pyscipopt
import datetime
import numpy as np
import shutil
import json

heur = "myheurdiving"
# t = "test"


def get_unsolved_primalbound(path,keyword,state_path):
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
    
    if "violation" in content:
        is_find = False
        state = {
            "heur_executable": False
        }
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=4)

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
    
    with open(path, 'r') as file:
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

def extract_code(text):
    pattern = r'<start_code>(.*?)</end_code>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:#
        return text

def solve_problems_and_generate_logs(name,t,diving_ind):
    
    path_to_instances = "/home/yyzhou/LLM4Heur/dataset/instances/" + name + "/" + t

    instance_list = os.listdir(path_to_instances)

    current_datetime = datetime.datetime.now()
    time_stamp = current_datetime.strftime("%Y%m%d%H%M")
    log_dir = "/home/yyzhou/LLM4Heur/tmp/logs" + "/" + name + "/" + time_stamp
    
    while(os.path.exists(log_dir)):
        log_dir = log_dir + "a"

    os.makedirs(log_dir)  

    i = 1
    for instance in instance_list:
        

        path_to_one_instance = path_to_instances + "/" + instance
            
        logfile = log_dir + "/" + instance + ".log"

        model = pyscipopt.Model("Heuristic_Example")
        model.readProblem(path_to_one_instance)
        model.setLogfile(logfile)

        print(i,end='\r')
        i = i+1

        model.setSeparating(pyscipopt.SCIP_PARAMSETTING.OFF)  # close cutting planes
        model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
        
        if diving_ind == 1:
            model.includeMyheurdiving()
            freq_param = 'heuristics/myheurdiving/freq'
            freqofs_param = 'heuristics/myheurdiving/freqofs'
        elif diving_ind == 2:
            model.includeMyheur2diving()
            freq_param = 'heuristics/myheur2diving/freq'
            freqofs_param = 'heuristics/myheur2diving/freqofs'
        elif diving_ind == 3:
            model.includeMyheur3diving()
            freq_param = 'heuristics/myheur3diving/freq'
            freqofs_param = 'heuristics/myheur3diving/freqofs'
        else:
            model.includeMyheur4diving()
            freq_param = 'heuristics/myheur4diving/freq'
            freqofs_param = 'heuristics/myheur4diving/freqofs'
        
        model.setParam(freq_param,1)
        model.setParam(freqofs_param,0)

        model.setParam('limits/nodes',1)
        model.setParam('limits/totalnodes',1)

        model.setParam('limits/time', 360)

        model.hideOutput()
        model.optimize() 

        

    return log_dir


def get_data(name,t, log_dir, state_path):
    keyword = heur[:6]
    epsilon = 1e-6

    solved_logdir = '/home/yyzhou/LLM4Heur/heur/logfile/logs/'+ name +'/solved/'+ t

    unsolved_logdir = log_dir

    print(name,heur)

    solved_logfiles = os.listdir(solved_logdir)
    n_ins = len(solved_logfiles)

    data_abs = []
    data_rel = []
    


    for ins_logfile in solved_logfiles:
        unsolved_logpath = unsolved_logdir + '/' + ins_logfile
        solved_logpath = solved_logdir + '/' +ins_logfile

        is_find, primal_bound = get_unsolved_primalbound(unsolved_logpath,keyword, state_path)
        bestsol = get_solved_bestsol(solved_logpath)
        
        if(is_find):
            data_abs.append( abs(primal_bound-bestsol) )
            data_rel.append( 100 * abs(primal_bound-bestsol) / (bestsol+epsilon) )        


    mean_abs,mean_rel = np.mean(data_abs), np.mean(data_rel)
    std_abs,std_rel = np.std(data_abs), np.std(data_rel)
    SEM_abs,SEM_rel = std_abs / np.sqrt(len(data_abs)), std_rel / np.sqrt(len(data_rel))

    with open(state_path, 'r') as f:
        state = json.load(f)
    
    if(state["heur_executable"]):
        return (len(data_rel), mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel)
    else:
        print("violation")
        return (len(data_rel), 10e8, 0, 0, 10e8, 0, 0)
    
    # return (len(data_rel), mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel)

def eval_heur(heur_text,instance_name, t = "train10", diving_ind = 1):# diving_ind是表示使用第几个diving文件，diving1用于演化，diving2用于评估
    
    # assert(heur in heur_text)# heur = "myheurdiving"
    
    file_dir = '/home/yyzhou/LLM4Heur/tmp/'
    if(diving_ind == 1):
        file_path = file_dir + 'diving.py'
        state_path = file_dir + 'state.json'
    elif(diving_ind == 2):
        file_path = file_dir + 'diving2.py'
        state_path = file_dir + 'state2.json'
    elif(diving_ind ==3):
        file_path = file_dir + 'diving3.py'
        state_path = file_dir + 'state3.json'
    else:
        file_path = file_dir + 'diving4.py'
        state_path = file_dir + 'state4.json'
    
    

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
        file.write(extract_code(heur_text))

    # set the state to decide whether the heur is executable or not, it may be changed in /home/yyzhou/LLM4Heur/tmp/func_helper.py
    state = {
        "heur_executable": True
    }
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=4)


    log_dir = solve_problems_and_generate_logs(instance_name, t, diving_ind)


    with open(state_path, 'r') as f:
        state = json.load(f)
    
    if(state["heur_executable"]):
        (num_valid, mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel) = get_data(instance_name, t, log_dir, state_path)

        print("number of valid data:",num_valid)
        print("mean_abs:",mean_abs,"; std_abs:",std_abs,"; SEM_abs:", SEM_abs)
        print("mean_rel:",mean_rel,"%; std_rel:",std_rel,"; SEM_rel:", SEM_rel)
    
    else:
        print("the heur is not executable")
        print("the error is:",state["error"])
        mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel = 10e8, 0, 0, 10e8, 0, 0

    return mean_abs, std_abs, SEM_abs, mean_rel, std_rel, SEM_rel

if __name__ == "__main__":

    code = '''
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    score = 0.5 * candsfrac / (pscostdown + pscostup + 1) * (1 + nlocksdown) * (1 + nlocksup) * (obj + objnorm) * (1 + nNonz) * (1 if isBinary else 0.5)
    
    if mayrounddown or mayroundup:
        score -= 0.1
        
    if rootsolval > 0:
        score += rootsolval * 0.5
    
    roundup = True if candsol > 0.5 else False
    
    return score, roundup

'''

    eval_heur(code,instance_name="indset",t="train10",diving_ind=4)






    