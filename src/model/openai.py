from tqdm import tqdm
from src.datautils import OP_FOLDER_DIR, FinalPromptBuilder
import os
import json
from typing import *
import requests
from src.model.base import BaseModelInferencer
import logging
import argparse
import openai
openai.api_type = "azure"
openai.api_base = "https://promptinjres.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = "*******"
parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                        '--loglevel',
                        default='warning',
                        help='Provide logging level. Example --loglevel debug, default=warning' )
parser.add_argument("-test", action='store_true')

class OpenAIGPTInferencer(BaseModelInferencer):
    def __init__(self, model_name: str="GPT3.5-003", path: str="text-davinci-003", 
                 op_folder=OP_FOLDER_DIR, batch_size: int=1):
        super().__init__()
        self.path = path
        self.model_name = model_name
        self.op_folder = op_folder
        self.batch_size = batch_size
        if path == 'text-davinci-003':
            API_KEY_FILE = 'openai_api_key_3.txt'
        elif path == 'text-davinci-002':
            API_KEY_FILE = 'openai_api_key_2.txt'
        # initialize openai api for model inference.
        with open(API_KEY_FILE,'r') as f:
            self.endpoint = f.readline().strip()
            self.openai_api_key = f.readline().strip()

    def get_inference(self, text: str):
        '''
        This function is used to get the inference from the Azure OpenAI API
        '''
        logging.debug(f"Getting inference from OpenAI API for text: {text}")
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.openai_api_key,
        }
        response = openai.Completion.create(
        engine="TestSomakgpt35",
        prompt=text,
        temperature=0,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
        try:
            logging.debug(f"Response from OpenAI API: {response['choices'][0]['text']}")
        except:
            logging.debug(f"Response from OpenAI API: {response}")
        return response

    def __call__(self, batched_input_text: str):
        total_outputs = []
        i = 0       
        for input_text in batched_input_text:
            while i < 3:
                outputs = self.get_inference(input_text)
                if 'error' in outputs.keys():
                    if 'maximum context' in outputs['error']['message']:
                        print("PROMPTS ARE WAY TOO BIG, EXITING")
                        exit()
                    if outputs['error']['code'] == 'content_filter':
                        i=0
                        total_outputs.append("CONTENT REDACTED BY OPENAI")
                        break
                    elif outputs['error']['code'] == 'timeout':
                        i+=1
                        continue
                    else:
                        print(outputs['error'])
                        print("UNKNOWN ERROR, EXITING")
                        exit()
                else:
                    i=0
                    total_outputs.append(outputs['choices'][0]['text'])
                    break
            if i == 3:
                print("ETIMEDOUT 3 times, exiting")
                exit()
        return total_outputs
# main function.
if __name__ == "__main__":
    # test and example usage.
    args = parser.parse_args()
    logging.basicConfig( level=args.loglevel.upper() )
    inferencer = OpenAIGPTInferencer(model_name='GPT3.5',path="text-davinci-002")
    builder = FinalPromptBuilder()
    if args.test:
        test_list_of_prompts = builder.get_test_list_of_prompts(
            inferencer.model_name
        )
        inferencer.run(test_list_of_prompts, overwrite=False)
    else:
        final_list_of_prompts = builder.get_final_list_of_prompts(
            inferencer.model_name
        )
        inferencer.run(final_list_of_prompts, overwrite=False)