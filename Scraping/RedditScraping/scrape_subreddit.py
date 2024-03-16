import sys
import json
import praw
from typing import *
from tqdm import tqdm

secrets = json.load(open("Scraping/RedditScraping/secrets.json"))
USER_AGENT = "reddit_scraper_for_llm_jailbreaking"

def scrape_subreddit_by_search_terms(reddit_reader, name: str, search_terms: List[str], limit: int=10000):
    """scrape subreddit."""
    subreddit = reddit_reader.subreddit(name)
    # print(subreddit.display_name)
    # print(subreddit.title)
    # print(subreddit.description)
    with open(f"./Scraping/RedditScraping/{name}.jsonl", "w") as f:
        pbar = tqdm(search_terms)
        for term in pbar:
            for i, post in enumerate(subreddit.search(term, limit=limit)):
                pbar.set_description(f"{i+1}")
                rec = {}
                for key in ["title", "selftext", "id", 
                            "score", "num_comments", "url"]:
                    rec[key] = getattr(post, key)            
                rec["search_term"] = term
                f.write(json.dumps(rec)+"\n")

def scrape_subreddit_by_flair(reddit_reader, name: str, 
                              flair: str, limit: int=10000):
    """scrape subreddit."""
    subreddit = reddit_reader.subreddit(name)
    with open(f"./Scraping/RedditScraping/{name}_by_flair.jsonl", "w") as f:
        for i, post in tqdm(
            enumerate(subreddit.search(
                f'flair:"{flair}"', 
                limit=limit)
            )):
                rec = {}
                for key in ["title", "selftext", "id", 
                            "score", "num_comments", "url"]:
                    rec[key] = getattr(post, key)            
                rec["flair"] = flair
                f.write(json.dumps(rec)+"\n")

# main
if __name__ == "__main__":
    reddit_reader = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["secret"],
        user_agent=USER_AGENT,
    )
    # subs_and_search_terms = {
    #     "openai": ["jailbreak", "jail break", 
    #     "prompt injection", "dan", "jim"],
    #     "ChatGPT": ["jailbreak", "jail break", 
    #     "prompt injection", "dan", "jim",
    #     "prompt leakage"],
    # }
    # for sub, search_terms in subs_and_search_terms.items():
    #     scrape_subreddit_by_search_terms(reddit_reader, sub, search_terms)
    scrape_subreddit_by_flair(reddit_reader, "ChatGPT", "Jailbreak")