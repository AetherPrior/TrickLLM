import numpy as np
import pandas as pd
import json
import os
from src.datautils import read_jsonl
import random

file_suffix = ['code_outputs.jsonl','FLAN_outputs.jsonl','gpt_turbo_outputs.jsonl','OPT_outputs.jsonl']
file_prefix = './src/eval/attackmetrics/proptest_outputs'

for fs in file_suffix:
    task_to_attack = {
    'Translation': {},
    'Code Generation': {},
    'Summarization': {},
    'Text Classification': {}
    }

    # sample from dictionary
    sampled_task_to_attack = {
        'Translation': {},
        'Code Generation': {},
        'Summarization': {},
        'Text Classification': {}
    }
    file_path = os.path.join(file_prefix, fs)
    # find all unique attacks and keep them as keys
    recs = read_jsonl(file_path)
    for rec in recs:
        task_to_attack[rec['task_name']][rec['attack_prompt']] = []

    for rec in recs:
        task_to_attack[rec['task_name']][rec['attack_prompt']].append(rec)

    for k, v in task_to_attack.items():
        items = list(v.items())
        items.sort(key= lambda x: len(x[1]))
        rec1s = 0
        recIndex = -1
        for attack, recs in items:
            if (len(recs) == 1): 
                rec1s+=1
                recIndex+=1
                sampled_task_to_attack[k][attack] = recs
            else:
                break

        num_attacks = len(v.keys())-rec1s
        # Get quotient and remainder to sample 100 attacks as uniquely and uniformly as possible
        q = (100-rec1s)//num_attacks
        r = (100-rec1s)%num_attacks
        for attack, recs in items[rec1s:]:   
            if r != 0:
                r-=1
                attack_rec_chunk = random.sample(recs,q+1)
            else:
                attack_rec_chunk = random.sample(recs,q)
            sampled_task_to_attack[k][attack] = attack_rec_chunk

    # save to pandas 
    for task in sampled_task_to_attack.keys():
        recs = []
        for attack,rec_chunk in sampled_task_to_attack[task].items():
            recs.extend(rec_chunk)
        
        df = pd.DataFrame(recs)
        model = "_".join(fs.split('_')[:-1])
        df['model'] = [model for i in range(len(df))]
        df.to_csv(f'./src/eval/attackmetrics/manual/model_wise/{model}_{task}.tsv',sep='\t', index=False)


from collections import defaultdict
model_dict = defaultdict(list)

prefix = './src/eval/attackmetrics/manual/model_wise'
for file in os.listdir(prefix):
    model_dict[file.split('_')[0]].append(pd.read_csv(os.path.join(prefix,file),sep='\t'))

for k,v in model_dict.items():
    df = pd.concat(v)
    df.to_csv(os.path.join(prefix,f'{k}.tsv'),sep='\t', index=False)
    





    


    
    


