import json
import requests
from tqdm import tqdm
openai_endpoint = "https://AOAI-westeurope.openai.azure.com/openai/deployments/text-davinci-003/completions?api-version=2023-05-15"
def get_inference(text: str):
    '''
    This function is used to get the inference from the Azure OpenAI API
    '''
    with open("openai_api_key.txt",'r') as f:
        _ = f.readline().strip()
        openai_api_key = f.readline().strip()
    headers = {
        'Content-Type': 'application/json',
        'api-key': openai_api_key,
    }
    data = {
        'prompt': text,
        'max_tokens': 200,
        'temperature': 1,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
    }
    response = requests.post(openai_endpoint, headers=headers, data=json.dumps(data))
    return response.json()

# main function.
if __name__ == "__main__":
    # test and example usage.
    text = """Instruction: This is a code generation task. Generate code as per the user's command in PYTHON.
 
# Input 1
 
Write a code in Python to perform circular shift the digits of the integer x, shift the digits right by "shift" and return the
result as a string. If shift > number of digits, return digits reversed.
>>> circular_shift(12, 1)
"21"
 
# Output 1
 
def circular_shift(x, shift):
    x = str(x)
    if shift > len(x):
        return x[::-1]
    else:
        return x[-shift:] + x[:-shift]
 
# Input 2"""
    out_list = []
    for i in tqdm(range(100)):
        outputs = get_inference(text)
        out = outputs['choices'][0]['text']
        out_list.append({'input': json.dumps(out.split("# Output 2")[0].strip())})
    with open("datacollectcodegen.jsonl",'w') as f:
        f.writelines(json.dumps(out_list))