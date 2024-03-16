import os
import json
from typing import *
from tqdm import tqdm

class BaseModelInferencer:
    def __init__(self) -> None:
        self.model_name = "base"
        self.batch_size = 1

    def _check_final_prompt_structure(self, final_prompt: dict):
        required_keys = [
            'task_name', 'agent', 'linguistic_level', 
            'final_prompt', 'attack_prompt', 'base_prompt', 
            'mode', 'attack_type', 'is_black_box', 'intent',
        ]
        for key in required_keys:
            assert key in final_prompt.keys(), f"missing required key: {key}"

    def run(self, final_list_of_prompts: List[dict], overwrite: bool=True):
        """read a list of final prompts and write them to a JSONL"""
        print(self.batch_size)
        # structural constraints of the list of final prompts.
        os.makedirs(self.op_folder, exist_ok=True)
        op_path = os.path.join(self.op_folder, f"{self.model_name}.jsonl")
        if overwrite: open(op_path, "w")
        batched_list_of_prompts = [final_list_of_prompts[i:i+self.batch_size] for i in range(0,len(final_list_of_prompts),self.batch_size)]
        
        batch_pad = False
        batch_num = 0
        empty_prompt = {
            'task_name': "", 'agent': "", 'linguistic_level':"", 
            'final_prompt':"", 'attack_prompt':"", 'base_prompt':"", 
            'mode':"", 'attack_type':"", 'is_black_box':"", 'intent':"",
        }
        for batched_input in tqdm(batched_list_of_prompts):
            if len(batched_input) < self.batch_size:
                batch_pad = True 
                batch_num = len(batched_input)
                # last batch needs to be padded
                for i in range(self.batch_size-len(batched_input)):
                    batched_input.append(empty_prompt)
            for input_inst in batched_input:
                self._check_final_prompt_structure(input_inst)
            
            batched_output = self([prompt['final_prompt'] for prompt in batched_input])

            for (i,input_inst),(j,output) in zip(enumerate(batched_input), enumerate(batched_output)):
                batched_input[i]["output"] = batched_output[j]
            
            with open(op_path, "a") as f:
                if batch_pad: 
                    # cut the batch down, after removing the pads
                    batched_input = batched_input[:batch_num]
                    batch_pad = False
                for input_inst in batched_input:
                    f.write(json.dumps(input_inst)+"\n")
