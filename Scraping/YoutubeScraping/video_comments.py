from collections import defaultdict
import json
import csv
import pandas as pd
from utils.helper import openURL
import googleapiclient.discovery
from config import YOUTUBE_COMMENT_URL, SAVE_PATH




totalCommentsDict = {}
api_service_name = "youtube"
api_version = "v3"
# This key needs to be generated using Youtube Data API v3
DEVELOPER_KEY = "AIzaSyDYUgKVQYrbeVaO9gvMDOhbNvtzNGN_2hc"
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

class VideoComment:
    def __init__(self, maxResults, videoId, key, video_Number):
        self.v_N = video_Number
        self.comments = defaultdict(list)
        self.replies = defaultdict(list)
        self.params = {
                    'part': 'snippet,replies',
                    'maxResults': maxResults,
                    'videoId': videoId,
                    'textFormat': 'plainText',
                    'key': key
                }

    def comments_list(self, service, part, parent_id, npt):
        results = service.comments().list(
        parentId=parent_id,
        part=part,
        maxResults=100,
        pageToken=npt,
        textFormat= 'plainText'
        ).execute()

        return results

    #(id, replyCount, likeCount, publishedAt, authorName, text, authorChannelId, authorChannelUrl,
    # isReply, isReplyTo, isReplyToName, totalComments)
    
    def load_comments(self, mat, npt):
        try:
            for item in mat["items"]:
                comment = item["snippet"]["topLevelComment"]
                self.comments["id"].append(comment["id"])
                
                try:
                    self.comments["replyCount"].append(item["snippet"]["totalReplyCount"])
                except:
                    self.comments["replyCount"].append("NO_REPLY_COUNT")

                try:
                    self.comments["likeCount"].append(comment["snippet"]["likeCount"])
                except:
                    self.comments["likeCount"].append("NO_LIKE_COUNT")

                try:
                    self.comments["publishedAt"].append(comment["snippet"]["publishedAt"])
                except:
                    self.comments["publishedAt"].append("NO_PUBLISHED_AT")

                self.comments["authorName"].append(comment["snippet"]["authorDisplayName"])
                self.comments["comment"].append(comment["snippet"]["textDisplay"])
                try:
                    self.comments["authorChannelId"].append(comment["snippet"]["authorChannelId"]["value"])
                except:
                    self.comments["authorChannelId"].append("NO_CHANNEL_ID")
                self.comments["authorChannelUrl"].append(comment["snippet"]["authorChannelUrl"])
                self.comments["isReply"].append(0)
                self.comments["isReplyTo"].append("")
                self.comments["isReplyToName"].append("")
            
                totalCommentsDict[comment["snippet"]["authorDisplayName"]] = totalCommentsDict.get(comment["snippet"]["authorDisplayName"], 0) + 1
            
                if item["snippet"]["totalReplyCount"] > 0:
                    re  = self.comments_list(youtube, "snippet", comment["id"], npt)
                
                    for r in re["items"]:
                        self.replies["id"].append(r["id"])
                        self.replies["replyCount"].append("")
                        try:
                            self.replies["likeCount"].append(r["snippet"]["likeCount"])
                        except:
                            self.replies["likeCount"].append("NO_LIKECOUNT_REPLY")

                        try:
                            self.replies["publishedAt"].append(r["snippet"]["publishedAt"])
                        except:
                            self.replies["publishedAt"].append("NO_PUBLISHEDAT_REPLY")
                        
                        self.replies["authorName"].append(r['snippet']['authorDisplayName'])
                        self.replies["comment"].append(r["snippet"]["textDisplay"])
                        self.replies["authorChannelId"].append(r["snippet"]["authorChannelId"]["value"])
                        self.replies["authorChannelUrl"].append(r["snippet"]["authorChannelUrl"])
                        self.replies["isReply"].append(1)
                        self.replies["isReplyTo"].append(comment["id"])
                        self.replies["isReplyToName"].append(comment["snippet"]["authorDisplayName"])

                        totalCommentsDict[r['snippet']['authorDisplayName']] = totalCommentsDict.get(r['snippet']['authorDisplayName'], 0) + 1
        except Exception as e:
            print("error ", e)
            #print(self.comments["id"])


    def prepare_file(self):
        fields = ["UserId", "replyCount", "likeCount", "publishedAt", "UserName", "text", "authorChannelId", "authorChannelUrl", "isReply", "isReplyToUserId", "isReplyToName"]
        with open("output/comments{}.csv".format(self.v_N), "a") as commentfile:
            csvwriter1 = csv.writer(commentfile)
            csvwriter1.writerow(fields)

        fields2 = ["AuthorName", "TotalComments"]
        with open("output/Info{}.csv".format(self.v_N), "a") as commentfile2:
            csvwriter2 = csv.writer(commentfile2)
            csvwriter2.writerow(fields2)

    def upload_data(self):

        #print(len(self.comments["id"]))
        #print(len(self.replies["id"]))
        ffinallist = []
        for i in range(len(self.comments["id"])):
            ftemplist = []
            
            ftemplist.append(self.comments["id"][i])
            ftemplist.append(self.comments["replyCount"][i])
            ftemplist.append(self.comments["likeCount"][i])
            ftemplist.append(self.comments["publishedAt"][i])
            ftemplist.append(self.comments["authorName"][i])
            ftemplist.append(self.comments["comment"][i])
            ftemplist.append(self.comments["authorChannelId"][i])
            ftemplist.append(self.comments["authorChannelUrl"][i])
            ftemplist.append(self.comments["isReply"][i])
            ftemplist.append(self.comments["isReplyTo"][i])
            ftemplist.append(self.comments["isReplyToName"][i])
            ffinallist.append(ftemplist)
            #ftemplist.clear()

            for j in range(len(self.replies["id"])):
                freplist = []
                #print(str(self.replies["isReplyTo"][j])+"    "+ str(self.comments["id"][i]))
                if str(self.replies["isReplyTo"][j]) == str(self.comments["id"][i]):
                    #print("hello")
                    freplist.append(self.replies["id"][j])
                    freplist.append(self.replies["replyCount"][j])
                    freplist.append(self.replies["likeCount"][j])
                    freplist.append(self.replies["publishedAt"][j])
                    freplist.append(self.replies["authorName"][j])
                    freplist.append(self.replies["comment"][j])
                    freplist.append(self.replies["authorChannelId"][j])
                    freplist.append(self.replies["authorChannelUrl"][j])
                    freplist.append(self.replies["isReply"][j])
                    freplist.append(self.replies["isReplyTo"][j])
                    freplist.append(self.replies["isReplyToName"][j])
                    ffinallist.append(freplist)
                    #ftemplist.clear()

        with open("output/comments{}.csv".format(self.v_N), "a") as cf:
            cw = csv.writer(cf)
            cw.writerows(ffinallist)

        ffinallist.clear()

    def count_comments(self):
        ftCClist = []
        tempcounter = 0
        #print(totalCommentsDict)
        for k in totalCommentsDict:
            tCClist = []
            tCClist.append(k)
            tCClist.append(totalCommentsDict[k])
            ftCClist.append(tCClist)

        with open("output/Info{}.csv".format(self.v_N), "a") as cf2:
            cw2 = csv.writer(cf2)
            cw2.writerows(ftCClist)

        ftCClist.clear()
        totalCommentsDict.clear()


    def get_video_comments(self):
        url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
        nextPageToken = url_response.get("nextPageToken")
        self.load_comments(url_response, nextPageToken)

        while nextPageToken:
            self.params.update({'pageToken': nextPageToken})
            url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
            nextPageToken = url_response.get("nextPageToken")
            self.load_comments(url_response, nextPageToken)
        
        self.prepare_file()
        self.upload_data()
        self.count_comments()
