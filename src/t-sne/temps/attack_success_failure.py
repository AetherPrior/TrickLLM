import json
from collections import defaultdict
from src.eval.attackmetrics.GPT4_test_analysis import DL_load_outputs


# load dl outputs for FLAN
FLAN = DL_load_outputs("outputs/FLAN_processed.jsonl",'src/eval/attackmetrics/DL_outputs/FLAN-output.jsonl')

# load FLAN_processed.jsonl
with open('outputs/FLAN_processed.jsonl','r', encoding='utf-8') as f:
    FLAN_attack = [json.loads(line) for line in f.readlines()]


# Classification task, attacks and their success rates
# filter in only Text classification task
FLAN_attack = [output for output in FLAN_attack if output['task_name'] == 'Summarization']
FLAN = [output for output in FLAN if output['task_name'] == 'Summarization']

print(len(FLAN_attack), len(FLAN))
# tabulate all attacks and their success count
attack_success = defaultdict(int)
for output, output_with_attack_prompt in zip(FLAN, FLAN_attack):
    attack_success[output_with_attack_prompt['attack_prompt'][:]] += 1 if output['attack_success'] else 0

print(json.dumps(attack_success, indent=4))



