#%%
import json
import sys
import os
print(os.getcwd())
os.chdir('../../../')
from src.datautils import read_jsonl
import pandas as pd

PROP_TEST_OUTPUT_PATHS = './src/eval/attackmetrics/proptest_outputs/'
INT_TEST_OUTPUT_PATH = './src/eval/attackmetrics/intent_test_outputs'


#%%
if __name__ == '__main__':
    model_intents = []
    for filename in os.listdir(INT_TEST_OUTPUT_PATH):
        intent_test_path = os.path.join(INT_TEST_OUTPUT_PATH, filename)
        model_name = filename.split('.')[0]
        prop_test_path = os.path.join(PROP_TEST_OUTPUT_PATHS, filename)

        intent_json = read_jsonl(intent_test_path)
        prop_json = read_jsonl(prop_test_path)

        new_intent = []
        for i in intent_json:
            for p in prop_json:
                if i['final_prompt'] == p['final_prompt']:
                    i['prop_label'] = p['label']
                    new_intent.append(i)
                    break

        df = pd.DataFrame(new_intent)
        df['model_name'] = ["_".join(filename.split('_')[:-1]) for i in range(len(df))]
        model_intents.append(df)
    df = pd.concat(model_intents)
    print(df.columns)

#%%
df = df.dropna()
(~df['label']).value_counts(), df['prop_label'].value_counts()

# %%
df2 = df
df2['prop_label'] = ~df['prop_label']
df2['label'].value_counts(), df2['prop_label'].value_counts()
#%%
print(df2[['prop_label','label']].value_counts())
# %%
print(df2.groupby('task_name')[['prop_label','label']].value_counts().to_dict())
print(df2.groupby('intent')[['prop_label','label']].value_counts().to_dict())
print(df2.groupby('attack_type')[['prop_label','label']].value_counts().to_dict())
print(df2.groupby('model_name')[['prop_label','label']].value_counts().to_dict())
# %%
dfm = pd.read_excel('./src/eval/attackmetrics/manual/manual_results.xlsx', sheet_name='results')
dfm['manual_label'] = dfm['manual_label'].astype('boolean')
dfm['proptest'] = dfm['proptest'].astype('boolean')
# %%
print(dfm[['proptest','manual_label']].value_counts())
# print(df.groupby('task')       [['proptest','manual_label']].value_counts())
# print(df.groupby('intent')     [['proptest','manual_label']].value_counts())
# print(df.groupby('attack_type')[['proptest','manual_label']].value_counts())
# print(df.groupby('model')      [['proptest','manual_label']].value_counts())
# %%
print(df2.groupby('model_name')[['prop_label','label']].value_counts())

#%%
dfm.columns
# %%
dfm.join(df2, 'final_prompt','inner')
# %%
