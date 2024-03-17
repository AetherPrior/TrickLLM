# TrickLLM
This repository contains the code for the paper "Tricking LLMs into Disobedience: Formalizing, Analyzing, and Detecting Jailbreaks" by Abhinav Rao, Sachin Vashishta*, Atharva Naik*, Somak Aditya, and Monojit Choudhury, accepted at LREC-CoLING 2024  

[![arXiv](https://img.shields.io/badge/arXiv-2305.14965-b31b1b.svg)](https://arxiv.org/abs/2305.14965)  

### Abstract
Recent explorations with commercial Large Language Models (LLMs) have shown that non-expert users can jailbreak
LLMs by simply manipulating their prompts; resulting in degenerate output behavior, privacy and security breaches,
offensive outputs, and violations of content regulator policies. Limited studies have been conducted to formalize
and analyze these attacks and their mitigations. We bridge this gap by proposing a formalism and a taxonomy of
known (and possible) jailbreaks. We survey existing jailbreak methods and their effectiveness on open-source and
commercial LLMs (such as GPT-based models, OPT, BLOOM, and FLAN-T5-XXL). We further discuss the challenges
of jailbreak detection in terms of their effectiveness against known attacks. For further analysis, we release a dataset of model outputs across 3700 jailbreak prompts over 4 tasks.

### Directory structure
```
├── alpa
├── attacks                                 # contains the attacks
│   ├── codegenerate.csv
│   ├── hateSpeech.csv
│   ├── MT.csv
│   └── summarize.csv
├── Base Prompts                            # contains the task prompts
│   └── List of Base Prompts.xlsx
├── environment.yml
├── inputs                                  # contains the user-inputs
│   ├── codegenerate.csv    
│   ├── hateSpeech.csv
│   ├── MT.csv
│   └── summarize.csv
├── LICENSE
├── Observations                            # Misc observations
├── outputs
│   └── postprocess_outputs.py
├── paper_resources
├── plots                                   # contains the plots for attack success metrics
├── ray_setup.sh
├── ray_shutdown.sh
├── README.md
├── requirements.txt
├── Scraping                                # contains the code for scraping Reddit and Youtube
│   ├── RedditScraping
│   │   ├── analyze_posts.py
│   │   ├── ChatGPT_by_flair.jsonl
│   │   ├── ChatGPT.jsonl
│   │   ├── openai.jsonl
│   │   ├── plots                           # contains the plots for the Reddit scraping
│   │   ├── scrape_posts_only.py
│   │   ├── scrape_submissions.py
│   │   └── scrape_subreddit.py
│   ├── requirements.txt
│   └── YoutubeScraping
│       ├── analyse_youtube.py
│       ├── config.py
│       ├── main.py
│       ├── output
│       ├── utils
│       │   └── helper.py
│       └── video_comments.py
└── src
    ├── code_generation_collection.py      # to collect user-inputs for code generation
    ├── datautils.py
    ├── eval
    │   ├── attackmetrics
    │   │   ├── confusion_matrix.py
    │   │   ├── DL_prompts
    │   │   ├── get_prop_test_stats.py    # to get the attack success rates for programmatic tests
    │   │   ├── GPT4_test_analysis.py     # to get the attack success rates for GPT-4 tests
    │   │   ├── GPT4_test.py              # conduct the GPT-4 test
    │   │   ├── __init__.py
    │   │   ├── intent_test_results       # additional code on intent tests (not included in paper)
    │   │   ├── manual                    # manual analysis scripts
    │   │   └──  propertyprompts
    │   │       ├── classify.md
    │   │       ├── codegenerate.md
    │   │       ├── MT.md
    │   │       └── summarize.md
    │   └──  __init__.py
    ├── __init__.py
    ├── main.py
    ├── model
    │   ├── base.py
    │   ├── bloom.py
    │   ├── flan.py
    │   ├── __init__.py
    │   ├── openai.py
    │   └── opt.py
    └── t-sne                            # contains the code for t-sne visualization    
        ├── class.png
        ├── flan_embeddings_generator.py
        ├── summ.png
        ├── temps
        │   └── attack_success_failure.py
        └── t-sne_visualization.ipynb

```
### Data  

- Manual evaluations present [here](https://github.com/AetherPrior/TrickLLM/blob/main/src/eval/attackmetrics/manual/V2/tsvs/all_models_mod.tsv)  
- Model outputs: Refer to [this folder](https://github.com/AetherPrior/TrickLLM/blob/main/outputs/processed/) for the drive link. Make sure that you place all files in the `outputs/processed` directory.
- GPT-4 test outputs: Refer to [this folder](https://github.com/AetherPrior/TrickLLM/blob/main/src/eval/attackmetrics/DL_outputs/) for the drive link. Make sure that you place all files in the `src/eval/attackmetrics/DL_outputs` directory.
### Installation 
#### Cloning
```
$ git clone --recurse-submodules git@github.com:Aetherprior/TrickLLM.git 
$ cd TrickLLM
$ python -m venv /path/to/venv
$ pip install -r requirements.txt 
```
#### Serving OPT-175B
Serving the OPT-175B model requires the installation of the `alpa` library. Use the `alpa` submodule to install the library and the examples for inference.  
```
$ cd alpa && pip install . && cd examples && pip install .
```
Unfortunately, you will need a clone of [**OPT weights**](https://github.com/facebookresearch/metaseq/tree/main/projects/OPT) . The conversion step to obtain them in a consolidated form is inefficient and takes 700+ gigs of RAM [\(find out more here\)](https://github.com/alpa-projects/alpa/blob/main/examples/llm_serving/scripts/step_2_consolidate_992_shards_to_singleton.py). You may download the outputs from the drive link instead.  
#### Setup Ray to inference OPT-175B
The `alpa` library requires `ray` to be set up on your GPU node(s) for inference. Please run the `./ray_setup.sh` script after adding your **path to the venv** and **IP addresses of your nodes** in the script


### Model Inference
Each model can be run using the following command:  
```
$ python -m src.model.<model_name>
``` 

### Evaluation
Scripts for property tests and GPT-4 tests are present in the `eval` directory. The `attackmetrics` directory contains the scripts for the property tests
- The `get_prop_test_stats.py` script is used to get the attack success rates for programmatic tests.
- `GPT4_test.py` script is used to conduct the GPT-4 tests.
- `GPT4_test_analysis.py` script is used to get the attack success rates for GPT-4 tests.

### Contributors
- [Abhinav Rao](https://github.com/Aetherprior)  - Attack prompts, OPT, FLAN, GPT model inferencing code, manual annotations and analysis, property-test and GPT-4 test & analysis
- [Sachin Vashishta](https://github.com/SachinVashisth)*  - BLOOM inferencing code, Youtube Scraping, T-SNE experiments, Base prompts collection using Promptsource, manual annotations.
- [Atharva Naik](https://github.com/atharva-naik/)*  - Base model + prompt structuring, Reddit Scraping, manual annotations.
- [Somak Aditya](https://github.com/adityaSomak) - Project Advisor
- [Monojit Choudhury](https://mbzuai.ac.ae/study/faculty/monojit-choudhury/) - Project Advisor

#### Citation  
If you find this work useful, do consider citing our paper:  

```
@misc{rao2024tricking,
      title={Tricking LLMs into Disobedience: Formalizing, Analyzing, and Detecting Jailbreaks}, 
      author={Abhinav Rao and Sachin Vashistha and Atharva Naik and Somak Aditya and Monojit Choudhury},
      year={2024},
      eprint={2305.14965},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
