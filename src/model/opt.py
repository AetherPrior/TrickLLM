"""Use huggingface/transformers interface and Alpa backend for distributed inference."""

import argparse

import numpy as np
from transformers import AutoTokenizer, AutoModel

import alpa
from llm_serving.model.wrapper import get_model

import os
import json
import torch
from typing import *
from tqdm import tqdm
import torch.nn as nn
from src.datautils import OP_FOLDER_DIR, FinalPromptBuilder
from src.model.base import BaseModelInferencer
import traceback
import pdb
os.environ['TRANSFORMERS_CACHE'] = '/relevance-nfs/users/t-raoabhinav/transformers'
# inferencing code for OPT
class OPTInferencer(BaseModelInferencer):
    def __init__(self, path: str="~/opt_weights", op_folder=OP_FOLDER_DIR, batch_size: int=1):
        self.path = path
        self.model_name = "OPT"
        self.op_folder = op_folder
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-30b", padding_side='left')
        self.tokenizer.add_bos_token = False
        self.generate_params = {
        "do_sample": 'store_true',
        "num_beams": 1,
        "num_return_sequences": 1
        }
        self.batch_size = batch_size
        self.model = get_model(model_name="alpa/opt-175b",
                      path=path,
                      batch_size=self.batch_size,
                      encoder_chunk_sizes=[1, 256, 1024],
                      **self.generate_params)

    def __call__(self, input_text: List[str]):
        input_ids = self.tokenizer(input_text, return_tensors="pt", padding="longest").input_ids
        output_ids = self.model.generate(input_ids,
                            max_new_tokens=200)

        outputs = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)

        postprocessed_outputs = []
        for input_inst, output in zip(input_text, outputs):
            postprocessed_outputs.append(output[min(len(input_inst),len(output)):])
        return postprocessed_outputs


# main function.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='/relevance-nfs/users/t-raoabhinav/opt_175b')
    args = parser.parse_args()
    
    # test and example usage.
    inferencer = OPTInferencer(path=args.path,batch_size=8)
    builder = FinalPromptBuilder()
    final_list_of_prompts = builder.get_final_list_of_prompts(
        inferencer.model_name
    )
    inferencer.run(final_list_of_prompts, overwrite=False)
    
    


