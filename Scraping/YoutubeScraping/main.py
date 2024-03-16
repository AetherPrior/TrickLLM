import os
import re
import sys
import argparse
import pandas as pd
from urllib.parse import urlparse, urlencode, parse_qs
from video_comments import VideoComment

def main():
    
    df = pd.read_csv("YoutubeURL.csv")
    #print(len(df))
    count = 0
    for i in range(0, len(df)):
        yurl = df['YoutubeUrl'].iloc[i]
        ylink = re.search(r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)", yurl).group(0)
        #print(type(ylink))
        print(ylink)
        vc = VideoComment(100, ylink, "AIzaSyDYUgKVQYrbeVaO9gvMDOhbNvtzNGN_2hc", count)
        vc.get_video_comments()
        count += 1
    

if __name__ == '__main__':
    main()
