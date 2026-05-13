import re
import requests
import json
import numpy as np
from zhipuai import ZhipuAI

import random

from eval import eval_heur

class MyLLM:
    def __init__(self, model = "gpt-3.5-turbo"):
        self.model = model


    def response(self, prompt):
        a = 0
        while a < 3:
            try:
                if(self.model == "glm-4"):
                    return self._response_glm(prompt)
                elif(self.model[:3] == "gpt"):
                    return self._response_qdd35(prompt)

                return self._response_qdd(prompt)
            except:
                a = a + 1
        return "no response"        

    

    def _response_glm(self, prompt):
        client = ZhipuAI(api_key="YOUR_ZHIPUAI_API_KEY_HERE")

        response = client.chat.completions.create(
            model="glm-4",  
            messages=[
                {"role": "user", "content": prompt },
            ],
        )

        return response.choices[0].message.content

    def _response_qdd35(self, prompt):
        model = self.model
        
        url = "https://35.aigcbest.top/v1/chat/completions"

        payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        })

       
        headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer sk-YOUR_API_KEY_HERE',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
        }

        resp = requests.request("POST", url, headers=headers, data=payload).json()
        resp_content = resp['choices'][0]['message']['content']

        return resp_content

    def _response_qdd(self, prompt):
        model = self.model
        
        url = "https://api.aigcbest.top/v1/chat/completions"

        payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # "temperature": self.temper,
        })

        headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer sk-YOUR_API_KEY_HERE',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
        }

        resp = requests.request("POST", url, headers=headers, data=payload).json()
        resp_content = resp['choices'][0]['message']['content']

        return resp_content

    def _response_shellapi(self, prompt):
        model = self.model
        url = "https://api.gptplus5.com/v1/chat/completions"

        payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        })

        headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer sk-YOUR_API_KEY_HERE',
        'Content-Type': 'application/json'
        }

        resp = requests.request("POST", url, headers=headers, data=payload).json()
        resp_content = resp['choices'][0]['message']['content']

        return resp_content

    def _response_api2d(self, prompt):

        model = "gpt-3.5-turbo"
        
        url = "https://openai.api2d.net/v1/chat/completions"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer fk-YOUR_FORWARD_KEY_HERE' 
        }
        data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        # "temperature": self.temper,
        }
        
        resp = requests.post(url, headers=headers, json=data).json()
        print(resp)
        resp_content = resp['choices'][0]['message']['content'] 
        
        return resp_content

class AGIndividual:
    
    def __init__(self, content, evaluated, score, llm):

        print(content)
        self.llm = llm

        self.content = content
        self.description = self.extract_description(content)
        self.code = self.extract_code(content)
        self.evaluated = evaluated # indicate whether the individual is evaluated
        self.score = score # the score of the individual, before evaluated it is useless and set to -inf

    def extract_description(self, text):

        pattern = r'<start_des>(.*?)</end_des>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            llm = self.llm
            print("No des found between <start_des> and </end_des>.")
            prompt = " \" " + text + " \" \n\n " + "extract and only return the description of the above contents."
            des = llm.response(prompt)
            print(des)
            return des

    def extract_code(self, text):
        
        pattern = r'<start_code>(.*?)</end_code>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            print("No code found between <start_code> and </end_code>.")
            code = "No code found between <start_code> and </end_code>."
            return code

    def get_description(self):
        return self.description
    
    def get_code(self):
        return self.code
    
    def get_content(self):
        return self.content

    def get_score(self):
        if(self.evaluated):
            return self.score
        assert self.evaluated, "this algorithm is not evaluated yet"
    
    def set_score(self, score):
        self.evaluated = True
        self.score = score


class EAMethods:

    def __init__(self, llm, background_prompt, features_description, inout_format_description, instruction, init_prompt, init_prompt_suggestion, mutation_prompt, crossover_prompt ):
        '''
        reference to ./prompt.md to know the meaning of every prompt
        '''

        self.llm = llm
        # some prompts that init, mutation, crossover all will use
        self.background_prompt = background_prompt
        self.features_description = features_description
        self.inout_format_description = inout_format_description
        self.instruction = instruction
        # init prompts
        self.init_prompt = init_prompt
        self.init_prompt_suggestion = init_prompt_suggestion
        # mutation prompts
        self.mutation_prompt = mutation_prompt
        # crossover prompts
        self.crossover_prompt = crossover_prompt


    def initialization(self, code = None, description = None):
        # give code and description to initialize
        if((code is not None) and (description is not None)):
            content = "<start_des>\n" + description + "\n</end_des> \n \n <start_code>\n" + code +"\n</end_code>"
            ag_individual = AGIndividual(content, evaluated=False, score= -np.inf, llm=self.llm)
            
            return ag_individual
        
        # no code or description to initialize
        else:
            llm = self.llm
            prompt = self.background_prompt + "\n" \
                    + self.init_prompt + "\n" \
                    + "Specifically, you have 13 features to use in the score function: " + self.features_description +"\n" \
                    + self.init_prompt_suggestion + "\n" \
                    + self.inout_format_description + "\n" \
                    + self.instruction + "\n"
            
            content = llm.response(prompt)
            
            ag_individual = AGIndividual(content, evaluated=False, score= -np.inf, llm=llm)
            
            return ag_individual

    def selection(self, ag_list, l=2):

        scores = [ag.get_score() for ag in ag_list]

        max_abs_score = max(abs(score) for score in scores)
        processed_scores = [max_abs_score + score + 1 if score < 0 else score for score in scores]
        total_score = sum(processed_scores)
        probabilities = [score / total_score for score in processed_scores]

        selected_indices = random.choices(range(len(ag_list)), weights=probabilities, k=l)
        selected_elements = [ag_list[i] for i in selected_indices]

        return selected_elements

    def mutation(self, ag_individual: AGIndividual, prob=0.2):
        
        llm = self.llm
        # do not mutation with probability (1-prob)
        if( random.uniform(0.0, 1.0) > prob):
            return ag_individual

        prompt = self.background_prompt + "\n\n" \
            + self.mutation_prompt + "\n\n" \
            + "The score function and the corresponding code are:\n" \
            + ag_individual.get_content() + "\n"\
            + "Motivated by the above algorithm, you should create a different new Python score function provided using the following 13 features: "\
            + self.features_description +"\n\n"\
            + self.inout_format_description +"\n\n"\
            + self.instruction

        content = llm.response(prompt)
        new_ag_individual = AGIndividual(content, evaluated=False, score= -np.inf, llm=llm)
            
        return new_ag_individual

    def crossover(self, ag_individual_1: AGIndividual, ag_individual_2: AGIndividual, prob=1.0):
        
        llm = self.llm

        # do not crossover with probability (1-prob)
        if( random.uniform(0.0, 1.0) > prob):
            return random.sample([ag_individual_1,ag_individual_2], 1)
        
        prompt = self.background_prompt + "\n\n" \
                + self.crossover_prompt + "\n\n" \
                + "The first algorithm and the corresponding code is:\n"\
                + ag_individual_1.get_content() + "\n" \
                + "The second algorithm and the corresponding code is:\n"\
                + ag_individual_2.get_content() + "\n" \
                + "Motivated by these functions, you should combine them and create 1 different new Python score function(s) using the following 13 features: "\
                + self.features_description + "\n\n"\
                + self.inout_format_description +"\n\n"\
                + self.instruction
        
        content = llm.response(prompt)
        new_ag_individual = AGIndividual(content, evaluated=False, score= -np.inf, llm=llm)
            
        return new_ag_individual
    


        