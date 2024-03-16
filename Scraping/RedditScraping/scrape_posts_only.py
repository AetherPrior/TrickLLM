import os
import bs4
import json
import praw
import pathlib
from tqdm import tqdm
from praw.models.reddit.comment import Comment
# def filter_attrs(obj):
#     attr_dict = {}
#     for attr in dir(obj):
#         value = getattr(obj, attr)
#         if type(value) in [str, list, dict, set, float, int]:
#             attr_dict[attr] = type(value)

#     return attr_dict
USER_AGENT = "please don't throttle me. I need your data to pass a course :(" # "reddit CMV thread scraper by /u/hl4aiproject for a course project"

def author_to_dict(author) -> dict:
    if author is None: 
        name = ""
        fullname = "[DELETED]"
    else: 
        name = getattr(author, "name", "[BANNED]")
        fullname = getattr(author, "fullname", "[BANNED]")

    return {"name": name, "fullname": fullname}

def submission_to_dict(sub) -> dict:
    sub_json = {}
    author = author_to_dict(sub.author)
    for attr in dir(sub):
        value = getattr(sub, attr)
        if attr.startswith("_"): continue 
        if attr.endswith("flair_css_class"): continue
        if attr.endswith("flair_background_color"): continue
        if attr in ["author_flair_background_color", 
                    "author_flair_text_color",
                    "author_flair_css_class", 
                    ]: continue
        if attr in ["MISSING_COMMENT_MESSAGE", "STR_FIELD"]: continue
        if type(value) in [str, list, dict, set, float, int]:
            sub_json[attr] = value
    sub_json["selftext"] = bs4.BeautifulSoup(sub.selftext_html, features="lxml").text
    sub_json["author"] = author

    return sub_json

# main method:
if __name__ == "__main__":
    secret = json.load(open("secrets.json"))
    reddit = praw.Reddit(
        client_id=secret["client_id"],
        client_secret=secret["secret"],
        user_agent=USER_AGENT,
    )
    folder = "./CMV_submissions_text_only/"
    os.makedirs(folder, exist_ok=True)
    urls = json.load(open("urls.json", "r"))
    for i, url in tqdm(enumerate(urls),
                    total=len(urls)):
        name = pathlib.Path(url).name
        fname = f"{name}_{i}.json"
        submission = reddit.submission(url=url)
        data = submission_to_dict(submission)
        save_path = os.path.join(folder, fname)
        with open(save_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)