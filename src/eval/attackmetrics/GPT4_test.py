import json
from typing import *
from liquid import Template
from src.datautils import read_jsonl
# confidential file with paths. Not included in repo. Contains only one function called "submitPrompt"
from src.eval.attackmetrics.DL_prompt_submit import submitPrompt

def create_attack_prompt(base_prompt: str, attack_prompt: str, user_input: str, task: str):
    prompt = {}
    if not isinstance(attack_prompt, str): return None
    if '{text input here}' in base_prompt:
                    prompt["final_prompt"] = base_prompt.replace(
                    "{text input here}", 
                    user_input+attack_prompt,
                    )
    else:
        prompt["final_prompt"] = f"""{base_prompt}"""+" "+f"""{user_input+attack_prompt}"""
    prompt["attack_prompt"] = attack_prompt
    prompt["base_prompt"] = base_prompt
    prompt["task_name"] = task

    prompt["user_input"] = user_input

    return prompt
        
def DL_property_test_input_create(inst: dict, num: int) -> Dict[str, Any]:
    '''
    create an OpenAI prompt format input for AI scraping of the property test
    the base prompt should be shrouded in between 
    '''
    task_name = inst['task_name']
    final_prompt = inst["final_prompt"]
    user_input = inst["user_input"]
    attack_prompt = inst["attack_prompt"]

    output = inst['output']
    if isinstance(inst['output'], list):
        output = inst["output"][0]
    # create DL test input
    task_mapping = {
        "Code Generation": "codegenerate.md",
        "Dialogue Generation": "dialoguegenerate.md",
        "Text Classification": "classify.md",
        "Translation": "MT.md",
        "Summarization": "summarize.md",
    }
    with open(f'src/eval/attackmetrics/propertyprompts/{task_mapping[task_name]}','r',encoding='utf-8') as f:
        template = Template(f.read())
    # create the eval prompt
    try: 
        # find user_input+attack_prompt in final_prompt
        index = final_prompt.index(user_input+attack_prompt)
        if index == -1:
            print("ERROR: "+final_prompt)
            exit()
        # replace user_input+attack_prompt with << user_input+attack_prompt >>
        final_prompt = final_prompt[:index]+"Last user input: << "+user_input+attack_prompt+" >>"+final_prompt[index+len(user_input+attack_prompt):]
        # replace output with << output >>
        output = "Last model output: << "+output+" >>"
        eval_prompt = template.render(datapoint=final_prompt.strip()+'\n'+output)
    except:
        print(final_prompt)
        exit()
    # wrap into openai jsonl
    openai_jsonl = {
        "prompt": eval_prompt,
        "temperature": 0,
        "max_tokens": 150,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "_batch_request_metadata": {"key": num}
    }
    return openai_jsonl

def DL_property_tests_eval(data: List[Dict],model_name: str):
    '''
    evaluate the DL property tests
    '''
    # create the input for DL
    openai_list = []
    for i, inst in enumerate(data):
        openai_jsonl = DL_property_test_input_create(inst, i)
        openai_list.append(json.dumps(openai_jsonl))
    # write to jsonl
    with open(f'src/eval/attackmetrics/DL_prompts/{model_name}.jsonl','w') as f:
        for line in openai_list:
            f.write(line+'\n')
    # run the DL model
    submitPrompt(model_name=model_name)

if __name__ == '__main__':
    prompts_list = ['BLOOMHUB_processed','t_ada_processed','t_babbage_processed','t_curie_processed','t_davinci2_processed'] #['BLOOMHUB_processed'] # GPT3.5-002
    models_list = ['BLOOM','t_ada','t_babbage','t_curie','t_davinci2'] #['BLOOM'] # GPT3.5-002
    for p,m in zip(prompts_list,models_list):
        DL_property_tests_eval(read_jsonl(f"outputs/processed/{p}.jsonl"),f"{m}")