`main.py` takes `YoutubeURL.csv` as input.<br /><br />
For every Youtube video, two files are generated namely `comments<no>.csv` and `info<no>.csv` in the `output` folder.<br />
`YoutubeURL.csv` contains the Url's of the Youtube videos.

Four type of search phrases have been used:<br />
    1. Attack Prompts<br />
    2. code injection in gpt<br />
    3. dan gpt<br />
    4. Jailbreak gpt<br />

The `YoutubeURL.csv` files of the aforementioned search phrases are put in the respective folders.
These folders have been created manually (output is stored in the `output` folder).

Every `comments<no>.csv` file contains the following fields: <br />
    1. &ensp;UserId<br />
    2. &ensp;replyCount<br />
    3. &ensp;likeCount<br />
    4. &ensp;publishedAt<br />
    5. &ensp;UserName<br />
    6. &ensp;text<br />
    7. &ensp;authorChannelId<br />
    8. &ensp;authorChannelUrl<br />
    9. &ensp;isReply<br />
    10. isReplyToUserId<br />
    11. isReplyToName
