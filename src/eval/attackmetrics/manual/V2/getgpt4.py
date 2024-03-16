from src.datautils import read_jsonl
import os
import pandas as pd
import json

PATH_TO_MANUAL_RESULTS = '/home/asura/Documents/git-clones/PAWG/src/eval/attackmetrics/manual/V2'
PATH_TO_PROPTEST_RESULTS = '/home/asura/Documents/git-clones/PAWG/src/eval/attackmetrics/proptest_outputs'
PATH_TO_GPT4_RESULTS = '/home/asura/Documents/git-clones/PAWG/src/eval/attackmetrics/DL_outputs'


def get_gpt4_results():
    model_mappping = {}
    for name in os.listdir(PATH_TO_MANUAL_RESULTS):
        count = 0
        if '.xlsx' not in name:
            continue
        # get model name
        model_name = name.split('.')[0]
        # open file
        file_path = os.path.join(PATH_TO_MANUAL_RESULTS,name)
        # read file
        df = pd.read_excel(file_path)
        # print(df.head())
        # add an "gpt4_label" column
        df['gpt4_label'] = [None for i in range(len(df))]
        # add a model column
        df['model'] = [model_name for i in range(len(df))]
        # get gpt4 model outputs
        gpt4_outputs = read_jsonl(os.path.join(PATH_TO_GPT4_RESULTS,f'{model_name}-output.jsonl'))
        # sort by "request": "_batch_request_metadata": {"key": 163}
        gpt4_outputs.sort(key=lambda x: x['request']['_batch_request_metadata']['key'])
        # ALSO Load the property testing results
        proptest_outputs = read_jsonl(os.path.join(PATH_TO_PROPTEST_RESULTS,f'{model_name}_outputs.jsonl'))
        # iterate over rows and get the gpt-4 outputs for each 'final_prompt'
        for row in df.iterrows():
            # get final_prompt
            final_prompt = row[1]['final_prompt']
            if '_x0080__x0099_' in final_prompt:
                final_prompt = final_prompt.replace('_x0080__x0099_','')
            # extract gpt-4 output from openai prompt response json file
            # split by newline
            # if it is "Yes" put True in the gpt4-label or else put False
            # update gpt4-label column
            gpt4_label_output = [output['response']['choices'][0]['text'] for ptest, output in zip(proptest_outputs, gpt4_outputs) if final_prompt in ptest['final_prompt']]
            if len(gpt4_label_output) == 0:
                count+=1
                with open('missing_gpt4.txt','a') as f:
                    f.write(f'{model_name}\t{final_prompt}\n')
                continue
            gpt4_label_output = gpt4_label_output[0].split('\n')[0]
            if 'yes' in gpt4_label_output.lower():
                df.loc[row[0],'gpt4_label'] = True
                # print("got here!")
            else:
                df.loc[row[0],'gpt4_label'] = False


        # save to file as model_name_mod.xlsx in a new dir called mod
        df.to_excel(os.path.join(PATH_TO_MANUAL_RESULTS,f'mod/{model_name}_mod.xlsx'),index=False)
        # save to file as model_name_mod.tsv in a new dir called tsvs
        # check if the dir exists otherwise create it!
        if not os.path.exists(os.path.join(PATH_TO_MANUAL_RESULTS,'tsvs')):
            os.makedirs(os.path.join(PATH_TO_MANUAL_RESULTS,'tsvs'))
        df.to_csv(os.path.join(PATH_TO_MANUAL_RESULTS,f'tsvs/{model_name}_mod.tsv'),sep='\t',index=False)

        print(f'No gpt4 output for {count} prompts')

# save a combined output for all models
# read all files in mod dir
# combine them all into one file
# save as all_models_mod.tsv
def combine_all_results():
    df = pd.DataFrame()
    for file in os.listdir(os.path.join(PATH_TO_MANUAL_RESULTS,'tsvs')):
        df = pd.concat((df,pd.read_csv(os.path.join(PATH_TO_MANUAL_RESULTS,'tsvs',file),sep='\t')))
    df.to_csv(os.path.join(PATH_TO_MANUAL_RESULTS,'tsvs/all_models_mod.tsv'),sep='\t',index=False)

if __name__ == '__main__':
    get_gpt4_results()
    combine_all_results()
