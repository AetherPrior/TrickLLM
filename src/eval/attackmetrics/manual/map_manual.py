from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from src.eval.attackmetrics.GPT4_test_analysis import DL_load_outputs
from src.eval.attackmetrics.get_prop_test_stats import compute_attack_success
from src.datautils import read_jsonl
import matplotlib.pyplot as plt
import json
import random
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import os
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('--manual-path', type=str, default='src/eval/attackmetrics/manual/manual.xlsx', help='Path to manual evaulations')


args = argparser.parse_args()
# load proptest outputs
models = ['OPT','gpt_turbo','code','FLAN', 'BLOOMHUB','t_davinci2','t_ada','t_babbage','t_curie']
outputs = ['OPT','gpt_turbo','Codex','FLAN', 'BLOOM','dv2','ada','babbage','curie']

model_dict = dict()
datapoints = dict()
for model in models:
    model_dict[model] = dict({
        'gpt4_outputs': DL_load_outputs(f"outputs/processed/{model}_processed.jsonl",f'src/eval/attackmetrics/DL_outputs/{model}-output.jsonl'),
        'proptest_outputs': read_jsonl(f'src/eval/attackmetrics/proptest_outputs/{model}_outputs.jsonl'),
        'input_to_proptest': read_jsonl(f'outputs/processed/{model}_processed.jsonl')
    })

    datapoints[model] = [{'input': model_dict[model]['input_to_proptest'][i]['final_prompt']+'\n'+model_dict[model]['input_to_proptest'][i]['output'], 'property_test': model_dict[model]['proptest_outputs'][i]['label'] } for i in range(len(model_dict[model]['input_to_proptest']))]

# find if the datapoints['OPT'] contains a "here's the prompt for code-generation"

xlsx = pd.ExcelFile(args.manual_path)
sheets = []
sheet_names = xlsx.sheet_names
# iterate over df sheets
for sheet in xlsx.sheet_names:
    # iterate over rows, and find datapoint that matches row input
    df = xlsx.parse(sheet)
    for row in df.iterrows():
        # if task != Translation continue
        if row[1]['task'] != 'Translation':
            continue
        model = row[1]['model']
        input = row[1]['input']
        datapoint = [dp for dp in datapoints[model] if input in dp['input']]
        
        if len(datapoint) == 0:
            # check if input contains German
            if 'Translate to German' in input:
                print(f'{input}\n\n----------------------------------\n\n')
                continue
            else:
                continue
        datapoint = datapoint[0]
        # update the property_test column of the row
        index = row[0]
        print(df.loc[index, 'proptest'], datapoint['property_test'])
        df.loc[index,'proptest'] = 'TRUE' if datapoint['property_test'] is True else 'FALSE'
    # append to sheets
    sheets.append(df)

# save sheets to excel
with pd.ExcelWriter('src/eval/attackmetrics/manual/manual_mod.xlsx') as writer:
    for i, sheet in enumerate(sheets):
        sheet.to_excel(writer, sheet_name=sheet_names[i], index=False)


            
        