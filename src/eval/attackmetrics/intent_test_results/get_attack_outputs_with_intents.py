import json
from src.datautils import ATTACKS_FOLDER_DIR, read_jsonl
from src.datautils import FinalPromptBuilder
import pandas as pd
import os 
import logging
from tqdm import tqdm
import math

final_prompt_builder = FinalPromptBuilder()

os.makedirs("./outputs/intents",exist_ok=True)
ATTACKS_FOLDER_DIR = "./attacks"
# find records with attacks having intent tests
for filename in os.listdir("./outputs/processed"):
    recs = read_jsonl(os.path.join("./outputs/processed",filename))
    new_recs = []
    
    logging.debug(f"filename: {filename}")
    attacks_map = {
            "codegenerate.csv": pd.read_csv(os.path.join(ATTACKS_FOLDER_DIR, "codegenerate.csv"), encoding='utf-8-sig'),
            "hateSpeech.csv": pd.read_csv(os.path.join(ATTACKS_FOLDER_DIR, "hateSpeech.csv"),encoding='utf-8-sig'),
            "MT.csv": pd.read_csv(os.path.join(ATTACKS_FOLDER_DIR, "MT.csv"),encoding='utf-8-sig'),
            "summarize.csv": pd.read_csv(os.path.join(ATTACKS_FOLDER_DIR, "summarize.csv"),encoding='utf-8-sig') 
        }
    
    tasks_map = {
            "Code Generation": "codegenerate.csv",
            "Dialogue Generation": "dialoguegenerate.csv",
            "Text Classification": "hateSpeech.csv",
            "Translation": "MT.csv",
            "Summarization": "summarize.csv", 
    }
    # find if attack matches the prompt

    for rec in tqdm(recs):
        df = attacks_map[tasks_map[rec['task_name']]]
        df = df.fillna("")
        for promptIndex, prompt in df.iterrows():
            if (len(prompt['Prompt']) != 0) and (len(prompt['Intent Test'].strip()) != 0):
                if rec['attack_prompt'].strip().lower() in prompt['Prompt'].lower():
                    rec['intent_test'] = prompt['Intent Test']
                    new_recs.append(rec)

    logging.debug(f"# of records = {len(new_recs)}")
    # dump to file
    with open(os.path.join('./outputs/intents',filename),'w') as f:
        to_write = [json.dumps(new_rec).strip()+"\n" for new_rec in new_recs]
        f.writelines(to_write)




    




    