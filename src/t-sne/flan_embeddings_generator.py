import json
import numpy as np
import pandas as pd
#import seaborn as sn
from tqdm import tqdm
#import matplotlib.pyplot as plt
#from sklearn.manifold import TSNE
# from matplotlib.patches import Rectangle
# from sklearn.preprocessing import StandardScaler
from transformers import T5Tokenizer, T5ForConditionalGeneration
# %%
import torch
import os
os.environ['TRANSFORMERS_CACHE'] = '/relevance-nfs/users/t-raoabhinav/transformers'

input_file = "classification_non_attack_samples.json"

output_file_prefix = 'embeddings_non_attack_class_part'

with open(f'{input_file}','r',encoding='utf-8') as f:
    data = json.loads(f.read())

tokenizer = T5Tokenizer.from_pretrained('google/flan-t5-xxl', padding_side='left',max_length=2048,padding=True, model_max_length=2048, add_special_tokens=False)
model_t5 = T5ForConditionalGeneration.from_pretrained("google/flan-t5-xxl", device_map="auto")

with open(f"./{output_file_prefix}.jsonl", "w") as f1:
    for i in tqdm(range(3000), desc = "Completing in..."):
        input_ids = tokenizer(data[i]['prompt'], return_tensors="pt").input_ids #.to("cpu")
        # we only need the embeddings of the prompts, and not of their outputs
        # their outputs are only of interest to us in step 3
        # if len(input_ids > 512):
        #     outputs_list = [model_t5.encoder(input_ids=input_ids[i:i+512],return_dict=True).last_hidden_state for i in range(0,len(input_ids),512)]
        #     h_state_list = [state for output_list in outputs_list for state in output_list]
        #     # h_state_list.extend([output.last_hidden_state for output in outputs_list])
        # else:
        outputs = model_t5.encoder(input_ids=input_ids, return_dict=True)
        h_state_list = outputs.last_hidden_state
        pooled_sentence= torch.mean(h_state_list,dim=1) #.to('cpu')
        # base_prompt_o.append(tokenizer.decode(outputs[0]))
        json.dump(pooled_sentence.tolist()[0],f1)
        f1.write('\n')

import pickle
with open(f"./{output_file_prefix}.jsonl",'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f.readlines()]
with open(f"./{output_file_prefix}.pkl",'wb') as f:
    pickle.dump(lines,f)