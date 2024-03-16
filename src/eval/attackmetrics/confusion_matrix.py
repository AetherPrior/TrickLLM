from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
# print confusion matrix

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

# load proptest outputs
models = ['OPT','gpt_turbo','code','FLAN', 'BLOOMHUB','t_davinci2','t_ada','t_babbage','t_curie']
outputs = ['OPT','gpt_turbo','Codex','FLAN', 'BLOOM','dv2','ada','babbage','curie']

model_dict = dict()
for model in models:
    model_dict[model] = dict({
        'gpt4_outputs': DL_load_outputs(f"outputs/processed/{model}_processed.jsonl",f'src/eval/attackmetrics/DL_outputs/{model}-output.jsonl'),
        'proptest_outputs': read_jsonl(f'src/eval/attackmetrics/proptest_outputs/{model}_outputs.jsonl'),
        'input_to_proptest': read_jsonl(f'outputs/processed/{model}_processed.jsonl')
    })

# filter out any outputs and inputs which contain a 'swear at me' or 'please misclassify'
filtered_model_dict = defaultdict(lambda: defaultdict(list)) 
for model in models:
    for inp, prop, gpt4 in zip(model_dict[model]['input_to_proptest'], model_dict[model]['proptest_outputs'], model_dict[model]['gpt4_outputs']):
        # if 'swear at me' in inp['final_prompt'] or 'please misclassify' in inp['final_prompt']:
        #     continue
        filtered_model_dict[model]['input_to_proptest'].append(inp)
        filtered_model_dict[model]['proptest_outputs'].append(prop)
        filtered_model_dict[model]['gpt4_outputs'].append(gpt4)

model_dict = filtered_model_dict

# extract labels
num_points = 0
overall_proptest_labels = []
overall_GPT4_labels = []
for model in models:
    if not os.path.isdir(f'src/eval/attackmetrics/manual/{model}'):
        os.mkdir(f'src/eval/attackmetrics/manual/{model}')
    proptest_labels = [output['label'] for output in model_dict[model]['proptest_outputs']]
    GPT4_labels = [output['attack_success'] for output in model_dict[model]['gpt4_outputs']]

    overall_proptest_labels += proptest_labels
    overall_GPT4_labels += GPT4_labels

    proptest_task_labels = defaultdict(list)
    GPT4_task_labels = defaultdict(list)
    for output in model_dict[model]['proptest_outputs']:
        proptest_task_labels[output['task_name']].append(output['label'])
    for output in model_dict[model]['gpt4_outputs']:
        GPT4_task_labels[output['task_name']].append(output['attack_success'])

    # compute confusion matrix for each task
    for task_name in proptest_task_labels.keys():
        plt.clf()
        print(task_name)
        matrix = confusion_matrix(proptest_task_labels[task_name], GPT4_task_labels[task_name])
        print(matrix)
        cm_display = ConfusionMatrixDisplay(confusion_matrix = matrix, display_labels = [False, True])
        cm_display.plot()
        cm_display.ax_.set(xlabel=f'GPT-4 for {model} and {task_name}', ylabel=f'Property test for {model} and {task_name}')
        plt.savefig(f'src/eval/attackmetrics/cmplots/{model}_{task_name}.png')
        plt.close('all')
    # compute overall confusion matrix for each model
    plt.clf()
    matrix = confusion_matrix(proptest_labels, GPT4_labels)
    cm_display = ConfusionMatrixDisplay(confusion_matrix = matrix, display_labels = [False, True])
    cm_display.plot()
    cm_display.ax_.set(xlabel=f'GPT-4 for {model}', ylabel=f'Property test for {model}')
    plt.savefig(f'src/eval/attackmetrics/cmplots/{model}.png')
    print(matrix)
    plt.close('all')
# compute overall confusion matrix for all models
plt.clf()
matrix = confusion_matrix(overall_proptest_labels, overall_GPT4_labels)
cm_display = ConfusionMatrixDisplay(confusion_matrix = matrix, display_labels = [False, True])
cm_display.plot()
cm_display.ax_.set(xlabel=f'GPT-4 for all models', ylabel=f'Property test for all models')
plt.savefig(f'src/eval/attackmetrics/cmplots/all.png')
print(matrix)
plt.close('all')
'''
    # randomly sample 50 points per model per task
    
    for task_name in proptest_task_labels.keys():
        print(task_name)
        
        task_indices = [i for i, output in enumerate(model_dict[model]['proptest_outputs']) if output['task_name'] == task_name]
        random.shuffle(task_indices)
        # create a set of all attacks for the task
        attack_set = set()
        for i in task_indices:
            attack_set.add(model_dict[model]['input_to_proptest'][i]['attack_prompt'])
        # stratify 50/x attacks
        sampled_indices = []
        for attack in attack_set:
            attack_indices = [i for i in task_indices if model_dict[model]['input_to_proptest'][i]['attack_prompt'] == attack]
            random.shuffle(attack_indices)
            sampled_indices += attack_indices[:max(1,50//len(attack_set))]
        
        # random sample the rest (if any)
        while len(sampled_indices) < 50:
            i = random.choice(task_indices)
            if i not in sampled_indices:
                sampled_indices.append(i)

        # datapoint =  model_dict[model]['input_to_proptest'][i]['final_prompt']+'\n'+model_dict[model]['input_to_proptest'][i]['output']
        sampled_datapoints = [model_dict[model]['input_to_proptest'][i]['final_prompt']+'\n'+model_dict[model]['input_to_proptest'][i]['output'] for i in sampled_indices]
        sampled_proptest_labels = [proptest_labels[i] for i in sampled_indices]
        sampled_GPT4_labels = [GPT4_labels[i] for i in sampled_indices]
        sampled_explanation = [model_dict[model]['gpt4_outputs'][i]['explanation'] for i in sampled_indices]
        model_name = [model for i in sampled_indices]
        sampled_intent = [model_dict[model]['input_to_proptest'][i]['intent'] for i in sampled_indices]
        sampled_at_type = [model_dict[model]['input_to_proptest'][i]['attack_type'] for i in sampled_indices]
        sampled_df = pd.DataFrame({'input': sampled_datapoints, 'proptest': sampled_proptest_labels, 'gpt4': sampled_GPT4_labels, 'gpt4_explanation': sampled_explanation, 'model': model_name, 'task': task_name, 'intent': sampled_intent, 'attack_type': sampled_at_type})
        df_list.append(sampled_df)

# concat list of dfs to df
df = pd.concat(df_list)
print(len(df))
df.to_csv('src/eval/attackmetrics/manual/manual.csv',encoding='utf-8-sig',index=False)
'''

'''
    gpt4propconfusion = [defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)]
    for i, output in tqdm(enumerate(model_dict[model]['gpt4_outputs'])):
        if output['explanation'][0] == '=':
            output['explanation'] = output['explanation'][1:]
        datapoint =  model_dict[model]['input_to_proptest'][i]['final_prompt']+'\n'+model_dict[model]['input_to_proptest'][i]['output']
        if output['attack_success']:
            if model_dict[model]['proptest_outputs'][i]['label']:
                gpt4propconfusion[0][output['task_name']].append({'input': datapoint, 'proptest': True, 'gpt4': True, 'gpt4_explanation': output['explanation']})
            else:
                gpt4propconfusion[1][output['task_name']].append({'input': datapoint, 'proptest': False, 'gpt4': True, 'gpt4_explanation': output['explanation']})
        else:
            if model_dict[model]['proptest_outputs'][i]['label']:
                gpt4propconfusion[2][output['task_name']].append({'input': datapoint, 'proptest': True, 'gpt4': False, 'gpt4_explanation': output['explanation']})
            else:
                gpt4propconfusion[3][output['task_name']].append({'input': datapoint, 'proptest': False, 'gpt4': False, 'gpt4_explanation': output['explanation']})

        # sample randomly 30 (or len) points from each task for each element in gpt4propconfusion 
        for i in range(4):
            for task_name in gpt4propconfusion[i].keys():
                gpt4propconfusion[i][task_name] = random.sample(gpt4propconfusion[i][task_name], min(len(gpt4propconfusion[i][task_name]), 30))
        
    # concatenate all the lists
    gpt4propconfusionconcat = defaultdict(list)

    for task_name in ['Translation','Summarization','Code Generation','Text Classification']:
        if model == 'BLOOMHUB' and task_name == 'Code Generation':
            for i in range(4):
                print(len(gpt4propconfusion[i][task_name]))
        gpt4propconfusionconcat[task_name] = [gpt4propconfusion[i][task_name] for i in range(4)]
        gpt4propconfusionconcat[task_name] = [item for sublist in gpt4propconfusionconcat[task_name] for item in sublist]
        
        print(len(gpt4propconfusionconcat[task_name]))
        num_points += len(gpt4propconfusionconcat[task_name])

    
    # save to csv
    for task_name in gpt4propconfusionconcat.keys():
        pd.DataFrame(gpt4propconfusionconcat[task_name]).to_csv(f'src/eval/attackmetrics/manual/{model}/{model}_{task_name}.csv',encoding='utf-8-sig')

print(num_points)
'''
