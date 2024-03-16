import re
import os
import glob
import json
import nltk
import spacy
import pathlib
import textwrap
import numpy as np
from typing import *
from pprint import pprint
# from bertopic import BERTopic
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import defaultdict
from src.datautils import read_jsonl

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

TERM_MAPPING = {
    "dan": "DAN", "jim": "Jim", "sam": "Sam", "Maximum": "Maximum",
    "jail break": "jailbreak",   
}

def process_text_for_lda(sent: str):
    """dp processing of text for LDA modeling"""
    # remove emails.
    sent = re.sub('\S*@\S*\s?', '', sent)
    # remove URLs.
    sent = re.sub(r'http\S+', '', sent)
    # sent = re.sub(r'^https?:\/\/.*[\r\n]*', '', sent, flags=re.MULTILINE)
    # remove new line characters.
    sent = re.sub('\s+', ' ', sent)
    # remove distracting single quotes
    sent = re.sub("\'", "", sent)
    
    return sent

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

# Define functions for stopwords, bigrams, trigrams and lemmatization
# def remove_stopwords(texts, stop_words):
#     return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
def remove_stopwords(texts: List[List[str]], stop_words):
    return [[word for word in doc if word not in stop_words and len(word) > 1] for doc in texts]

def make_bigrams(texts, bigram_model):
    return [bigram_model[doc] for doc in texts]

def make_trigrams(texts, bigram_model, trigram_model):
    return [trigram_model[bigram_model[doc]] for doc in texts]

def lemmatization(texts, nlp, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

def analyze_token_counts():
    nlp = spacy.load("en_core_web_lg")
    stop_words = stopwords.words('english')
    stop_words.extend(['openai', 'chatgpt', 'reddit', 
                       'https', 'ive', 'com','new','use','m'])
    for path in glob.glob("./Scraping/RedditScraping/*.jsonl"):
        data = [process_text_for_lda(post["selftext"]) for post in read_jsonl(path)]
        data_words = list(sent_to_words(data))
        data_words = lemmatization(data_words, nlp)
        data_words = remove_stopwords(data_words, stop_words)
        term_counts = defaultdict(lambda:0)
        for sent in data_words:
            for word in sent:
                term_counts[word] += 1
        tot = sum(list(term_counts.values()))
        term_counts = {k: round(100*v/tot, 3) for k,v in sorted(
            list(term_counts.items())[:10], 
            key=lambda x: x[1], reverse=True, 
        )}
        subreddit_name = pathlib.Path(path).stem

        print()
        print(f"TOTAL REDDIT COMMENTS: {tot} for {subreddit_name}")
        print()
        
        save_dir = "./Scraping/RedditScraping/plots"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{subreddit_name}_term_counts.png")

        plt.clf()
        plt.figure(figsize=(12,8), dpi=200)
        x = [i for i in range(1, len(term_counts)+1)]
        y = list(term_counts.values())
        plt.title("terms vs counts")
        plt.xlabel("term")
        plt.ylabel("Fraction of posts with term")
        plt.xticks(x, ["\n".join(textwrap.wrap(term, width=20)) for term in term_counts], rotation=45, fontsize=20)
        bar = plt.bar(x, y, color="green", width=0.95)
        for rect in bar:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width()/2,
                height, f'{height:.3f}', ha='center',
                va='bottom',fontsize=18
            )
        plt.tight_layout()
        plt.savefig(save_path)

def analyze_post_topics():
    nlp = spacy.load("en_core_web_lg")
    stop_words = stopwords.words('english')
    stop_words.extend(['openai', 'chatgpt', 'reddit', 
                       'https', 'ive', 'com','new','use'])
    for path in glob.glob("./Scraping/RedditScraping/*.jsonl"):
        data = [process_text_for_lda(post["selftext"]) for post in read_jsonl(path)]
        data_words = list(sent_to_words(data))
    # Build the bigram and trigram models
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
    trigram = gensim.models.Phrases(bigram[data_words], threshold=100)  
    # Faster way to get a sentence clubbed as a trigram/bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)

def analyze_topics_dist():
    save_dir = "./Scraping/RedditScraping/plots"
    topic_model = BERTopic()
    nlp = spacy.load("en_core_web_lg")
    stop_words = stopwords.words('english')
    stop_words.extend(['openai', 'chatgpt', 'reddit', 
                       'https', 'ive', 'com','new','use'])
    for path in glob.glob("./Scraping/RedditScraping/*_by_flair.jsonl"):
        data = [process_text_for_lda(post["title"]) for post in read_jsonl(path)]
        data_words = list(sent_to_words(data))
        data_words = lemmatization(data_words, nlp)
        data_words = remove_stopwords(data_words, stop_words)
        titles = [" ".join([w for w in words if w.strip() != ""]) for words in data_words]
        subreddit_name = pathlib.Path(path).stem
        topics, probs = topic_model.fit_transform(titles)
        print(f"{subreddit_name} TITLES:")
        topic_info = topic_model.get_topic_info()
        print(topic_info)
        for i in range(len(topic_info)-1):
            print([t for t,_ in topic_model.get_topic(i)])

def analyze_search_term_dist():
    global TERM_MAPPING
    for path in glob.glob("./Scraping/RedditScraping/*.jsonl"):
        if path.endswith("_by_flair.jsonl"): # How did copilot figure this out?!
            continue
        posts = read_jsonl(path)
        search_term_dist = defaultdict(lambda:0)
        for post in posts:
            search_term = post["search_term"]
            search_term = TERM_MAPPING.get(
                search_term, 
                search_term,
            )
            subreddit_name = pathlib.Path(path).stem
            search_term_dist[search_term] += 1
        search_term_dist = dict(sorted(search_term_dist.items(), key=lambda x: x[0]))
        save_dir = "./Scraping/RedditScraping/plots"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{subreddit_name}.png")
        print()
        print("\x1b[33;1m"+subreddit_name+"\x1b[0m")
        print("\n".join([f"{k} | {v}" for k,v in search_term_dist.items()]))
        print()
        plt.clf()
        x = range(1, len(search_term_dist)+1)
        y = list(search_term_dist.values())
        plt.title("search terms vs #posts")
        plt.xlabel("search terms")
        plt.ylabel("#posts")
        plt.xticks(x, ["\n".join(textwrap.wrap(term, width=12)) for term in search_term_dist], rotation=45)
        bar = plt.bar(x, y, color="green", width=0.5)
        for rect in bar:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width()/2,
                height, f'{height:.0f}', ha='center',
                va='bottom',
            )
        plt.tight_layout()
        plt.savefig(save_path)

# main.
if __name__ == "__main__":
    #analyze_search_term_dist()
    analyze_token_counts()
    #analyze_topics_dist()