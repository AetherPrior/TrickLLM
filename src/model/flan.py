# inferencing code for FLAN-T5.
import os
import json
import torch
from typing import *
from tqdm import tqdm
import torch.nn as nn
from src.datautils import OP_FOLDER_DIR, FinalPromptBuilder
from transformers import T5Tokenizer, T5ForConditionalGeneration
from src.model.base import BaseModelInferencer
import argparse
import pdb
parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                        '--loglevel',
                        default='warning',
                        help='Provide logging level. Example --loglevel debug, default=warning' )
parser.add_argument("-test", action='store_true')

# %%
os.environ['TRANSFORMERS_CACHE'] = '/relevance-nfs/users/t-raoabhinav/transformers'
# inferencing code for FLAN-T5
class FlanInferencer(BaseModelInferencer):
    def __init__(self, path: str="google/flan-t5-xxl", 
                 device: str="cuda", op_folder=OP_FOLDER_DIR, batch_size: int=1):
        self.path = path
        self.model_name = "FLAN"
        self.op_folder = op_folder
        self.device = device if torch.cuda.is_available() else "cpu"
        self.batch_size=batch_size
        print(self.device)
        #print(torch.cuda.device_count())
        self.tokenizer = T5Tokenizer.from_pretrained(path,padding_side='left',max_length=2048,padding=True, model_max_length=2048, add_special_tokens=False)
        self.model = T5ForConditionalGeneration.from_pretrained(path, device_map="auto")
        #try: self.model.to(device) #mat kar yeh abhi
        #except RuntimeError as e: print(e)

    def __call__(self, batch_input_text: List[str]):
        input_ids = self.tokenizer(batch_input_text, return_tensors="pt",padding='longest').input_ids.to(self.device)
        # # remove the last token from all input_ids
        # print(input_ids)
    
        # input_ids = torch.cat([input_id[:-1] for input_id in input_ids])
        # if len(input_ids.shape) < 2:
        #     input_ids = torch.unsqueeze(input_ids,dim=0)
        # print(input_ids)
        # print(self.tokenizer.batch_decode(input_ids))
        outputs = self.model.generate(input_ids, max_new_tokens=100)
        # print(outputs)
        return self.tokenizer.batch_decode(outputs)

# main function.
if __name__ == "__main__":
    # test and example usage.
    args = parser.parse_args()
    inferencer = FlanInferencer("google/flan-t5-xxl",batch_size=2)
    builder = FinalPromptBuilder()
    if args.test:
        test_list_of_prompts = builder.get_test_list_of_prompts(
            inferencer.model_name
        )
        inferencer.run(test_list_of_prompts)
    else:
        final_list_of_prompts = builder.get_final_list_of_prompts(
            inferencer.model_name
        )
        inferencer.run(final_list_of_prompts)