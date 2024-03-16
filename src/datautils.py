#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import pandas as pd
from typing import *
from tqdm import tqdm
import logging
import tiktoken

ATTACKS_FOLDER_DIR="./attacks"
INPUTS_DIR="./inputs"
OP_FOLDER_DIR="./outputs"
TASK_FOLDER_DIR="./attacks"
BASE_PROMPTS_PATH="./Base Prompts/List of Base Prompts.xlsx"

def read_jsonl(path: str):
    data = []
    with open(path, "r") as f:
        for line in tqdm(f):
            data.append(json.loads(line.strip()))
    
    return data

# data loading pipeline for building the final prompts
class FinalPromptBuilder:
    """class for building final prompts"""
    def __init__(self, base_prompts_path: str=BASE_PROMPTS_PATH, 
                 attack_prompts_dir: str=ATTACKS_FOLDER_DIR,
                 inputs_dir: str=INPUTS_DIR):
        self.base_prompts_df = pd.read_excel(base_prompts_path)
        self.attack_prompts_dfs = {}
        self.user_inputs = {}
        self.supported_models = ["FLAN", "GPT3.5", "BLOOMHUB", "OPT"]
        self.conv_alias = {
            "BLOOM": "BLOOMHUB",
            "BLOOMHUB": "BLOOMHUB",
            "GPT-3": "GPT3.5",
            "mT5": "FLAN",
            "OPT": "OPT",
            "code": "GPT3.5",
            "FLAN": "FLAN",
            "gpt_turbo": "GPT3.5",
            "t_ada": "GPT3.5",
            "t_babbage": "GPT3.5",
            "t_curie": "GPT3.5",
            "t_davinci2": "GPT3.5"
        }
        self.task_mapping = {
            "codegenerate.csv": "Code Generation",
            "dialoguegenerate.csv": "Dialogue Generation", 
            "hateSpeech.csv": "Text Classification",
            "MT.csv": "Translation",
            "summarize.csv": "Summarization", 
        }
        self.list_of_tasks = list(self.task_mapping.values())
        
        for task in os.listdir(attack_prompts_dir):
            print(task)
            attack_path = os.path.join(attack_prompts_dir, task)
            self.attack_prompts_dfs[self.task_mapping[task]] = pd.read_csv(
                attack_path,
                encoding="unicode_escape"
            )

        for task in os.listdir(inputs_dir):
            """
            the input files are named after the task they are used for.
            eg. codegenerate.csv, dialoguegenerate.csv, hateSpeech.csv, MT.csv, summarize.csv
            each line contains a user input for the task
            """
            logging.info(f"Reading user inputs for task: {task}...")
            input_path = os.path.join(inputs_dir, task)
            self.user_inputs[self.task_mapping[task]] = pd.read_csv(
                input_path,
                encoding="utf-8"
            )
            logging.debug(f"Done reading user inputs for task: {task}...")
            logging.debug(f"Length of user inputs: {len(self.user_inputs[self.task_mapping[task]])}")

        self.base_prompts = {model_name: {} for model_name in self.supported_models}
        for rec in self.base_prompts_df.to_dict("records"):
            model_names = rec["Model Name"]
            for model_name in model_names.split(","):
                task_name = rec["Type of Task"]
                model_name = model_name.strip()
                model_name = self.conv_alias.get(model_name, model_name)
                base_prompt = rec["Base Prompt"]
                self.base_prompts[model_name][task_name] = base_prompt
        # self.user_inputs = {
        #     'codegenerate.csv': 'generate code for a function that takes a list of numbers and returns the sum of the numbers',
        #     'dialoguegenerate.csv': 'Hi, how are you doing?',
        #     'hateSpeech.csv': 'I hate you',
        #     'MT.csv': 'Translate English to Spanish: I am a student',
        #     'summarize.csv': 'The United States of America (USA), commonly known as the United States (U.S. or US) or America, is a country primarily located in North America, consisting of 50 states, a federal district, five major self-governing territories, 326 Indian reservations, and some minor possessions. At 3.8 million square miles (9.8 million square kilometers), it is the world\'s third or fourth-largest country by total area and is slightly smaller than the entire continent of Europe. With a population of over 328 million people, the U.S. is the third most populous country. The capital is Washington, D.C., and the most populous city is New York City. TL;DR.',
        # }
        
    def create_attack_prompt(self, base_prompt: str, rec: dict, user_input: str, task: str):
        prompt = {}
        if not isinstance(rec["Prompt"], str): return None
        if '{text input here}' in base_prompt:
                        prompt["final_prompt"] = base_prompt.replace(
                        "{text input here}", 
                        user_input+rec['Prompt'],
                        )
        else:
            prompt["final_prompt"] = f"""{base_prompt}"""+" "+f"""{user_input+rec['Prompt']}"""
        prompt["attack_prompt"] = rec['Prompt']
        prompt["base_prompt"] = base_prompt
        prompt["task_name"] = task
        prompt["agent"] = rec.get('Agent', "unknown")
        prompt["linguistic_level"] = rec.get("Linguistic level", "unknown")
        prompt["mode"] = rec["Mode"]
        prompt["user_input"] = user_input
        try: prompt["attack_type"] = rec['Type of attack']
        except KeyError as e: print(e, task)
        prompt["is_black_box"] = rec.get("White/Black", "T")
        try: prompt["intent"] = rec["Intent"]
        except KeyError as e: print(e, task)
        return prompt

    def get_final_list_of_prompts(self, model_name: str) -> List[dict]:
        final_list_of_prompts = []
        for task, base_prompt in self.base_prompts[model_name].items():
            logging.debug(f"There are {len(self.attack_prompts_dfs[task].dropna(subset=['Prompt']))} attack prompts for {task}")
            logging.debug(f"For attacks that are not User, there are {len(self.user_inputs[task])} user inputs for {task}")
            for rec in self.attack_prompts_dfs[task].to_dict("records"):
                # check if rec['Mode'] is User, if so, set User input to none
                for user_input in self.user_inputs[task]['input'].tolist():
                    if rec["Mode"].lower() == "user":
                        user_input = ""
                    else:
                        user_input = user_input.strip()+"\n"
                    
                    prompt = self.create_attack_prompt(base_prompt, rec, user_input, task)
                    if prompt is None:
                        # No attack prompt was created
                        break
                    final_list_of_prompts.append(prompt)

                    if user_input == "":
                        logging.debug("attack is of the nature of 'User', so no user input is required")
                        break
            
                if rec['Mode'].lower() == "user/mitm":
                    # Add a User Prompt aside from the MITMs
                    prompt = self.create_attack_prompt(base_prompt, rec, "", task)
                    if prompt is not None:
                        final_list_of_prompts.append(prompt)

        return final_list_of_prompts
    
    def get_test_list_of_prompts(self, model_name: str) -> List[dict]:
        test_list_of_prompts = []
        
        # create a set of all tasks in self.base_prompts
        tasks = set()
        for task, base_prompt in self.base_prompts[model_name].items():
            tasks.add(task)
        max_user_input_indices = {}

        for task in tasks:
            # create a list for argmax of max length of user inputs
            user_inputs = self.user_inputs[task]['input'].tolist()
            user_inputs = [x.strip()+"\n" for x in user_inputs]
            # find argmax
            argmax = np.argmax([len(x) for x in user_inputs])
            max_user_input_indices[task] = argmax

        for task, base_prompt in self.base_prompts[model_name].items():
            logging.debug(f"There are {len(self.attack_prompts_dfs[task].dropna(subset=['Prompt']))} attack prompts for {task}")
            logging.debug(f"For attacks that are not User, there are {len(self.user_inputs[task])} user inputs for {task}")
            
            for rec in self.attack_prompts_dfs[task].to_dict("records"):
                # check if rec['Mode'] is User, if so, set User input to none
                # for user_input in self.user_inputs[task]['input'].tolist():
                np.argmax([len(x) for x in self.user_inputs[task]['input'].tolist()])
                user_input = self.user_inputs[task]['input'].tolist()[max_user_input_indices[task]]
                if rec["Mode"].lower() == "user":
                    user_input = ""
                else:
                    user_input = user_input.strip()+"\n"
                
                prompt = self.create_attack_prompt(base_prompt, rec, user_input, task)
                if prompt is None:
                    # No attack prompt was created
                    continue
                test_list_of_prompts.append(prompt)

                if user_input == "":
                    logging.debug("attack is of the nature of 'User', so no user input is required")

        # get gpt3 ada tokenizer
        encoding = tiktoken.get_encoding('r50k_base')
        # test if number of tokens exceeds 1900
        error_prompts = []
        for prompt in test_list_of_prompts:
                num_tokens = len(encoding.encode(prompt['final_prompt']))
                if num_tokens > 1900:
                     error_prompts.append(prompt)
        if len(error_prompts) > 0:
            with open("outputs/error_prompts.json", "w") as f:
                f.write(json.dumps(error_prompts, indent=4))
            raise Exception(f"Number of tokens exceeds 1900 for {len(error_prompts)} prompts")



        return test_list_of_prompts         
        
