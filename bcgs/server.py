from flask import Flask, jsonify, send_from_directory
import requests
import re
from bs4 import BeautifulSoup
import json
import uuid
from openpyxl import Workbook

app = Flask(__name__)

_DISQUS_ID_RE = "var\s*disqus_identifier\s*=\s*'(\d+)'"
_THREAD_DATA_RE = '<script type="text/json" id="disqus-forumData">(.*)</script>$'
# this probably changes
_API_KEY = "E8Uh5l5fHZ6gD8U3KycjAIAk46f68Zw7C6eW8WSjZvCLXebZ7p0r1yrYDrLilk2F"

# "author": {
#         "about": "",
#         "avatar": {
#             "cache": "//a.disquscdn.com/1519942534/images/noavatar92.png",
#             "isCustom": false,
#             "large": {
#                 "cache": "//a.disquscdn.com/1519942534/images/noavatar92.png",
#                 "permalink": "https://disqus.com/api/users/avatars/felix1999.jpg"
#             },
#             "permalink": "https://disqus.com/api/users/avatars/felix1999.jpg",
#             "small": {
#                 "cache": "//a.disquscdn.com/1519942534/images/noavatar32.png",
#                 "permalink": "https://disqus.com/api/users/avatars/felix1999.jpg"
#             }
#         },
#         "disable3rdPartyTrackers": false,
#         "id": "5472588",
#         "isAnonymous": false,
#         "isPowerContributor": false,
#         "isPrimary": true,
#         "isPrivate": true,
#         "joinedAt": "2010-11-20T04:45:33",
#         "location": "",
#         "name": "felix1999",
#         "profileUrl": "https://disqus.com/by/felix1999/",
#         "signedUrl": "",
#         "url": "",
#         "username": "felix1999"
#     },
#     "canVote": false,
#     "createdAt": "2018-04-05T02:44:32",
#     "dislikes": 0,
#     "forum": "breitbartproduction",
#     "id": "3839799615",
#     "isApproved": true,
#     "isDeleted": false,
#     "isDeletedByAuthor": false,
#     "isEdited": false,
#     "isFlagged": false,
#     "isHighlighted": false,
#     "isSpam": false,
#     "likes": 0,
#     "media": [],
#     "message": "<p>She's just insane.  Another MUSLIM flips out.</p>",
#     "moderationLabels": [],
#     "numReports": 0,
#     "parent": 3839693015,
#     "points": 0,
#     "raw_message": "She's just insane.  Another MUSLIM flips out.",
#     "sb": false,
#     "thread": "6595667472"
# }

_user_labels = ['Global ID', 'Display Name', 'Username', 'Location', 'Join Date', 'Profile Webpage']
_comment_labels = ['Global ID', 'Author Global Id', 'Source Thread', 'Parent Global ID', 'Sub-thread', 'Date', 'Text', 'Likes']

def add_comment(comment, req_info, comment_ws, user_ws):
    """

    :param dict comment:
    :param dict req_info:
    :param openpyxl.worksheet.worksheet.Worksheet comment_ws:
    :param openpyxl.worksheet.worksheet.Worksheet user_ws:
    :return:
    """
    # print(comment)
    # print(req_info)
    try:
        user = comment['author']
        comment_ws.append([
            comment['id'], user.get('id', 'Anonymous'), req_info['thread'], comment['parent'],
            comment['thread'], comment['createdAt'], comment['raw_message'], comment['likes']
        ])


        # check for anonumous users
        if 'id' in user and user['id'] not in req_info['users']:
            # don't double-add users
            req_info['users'].add(user['id'])
            user_ws.append([user['id'], user['name'], user['username'], user['location'], user['joinedAt'], user['profileUrl']])
    except:
        print("something went wrong with a comment")
        print(comment)

def add_comments(current_comments, req_info, comment_ws, user_ws):
    """

    :param dict current_comments:
    :param dict req_info:
    :param openpyxl.worksheet.worksheet.Worksheet comment_ws:
    :param openpyxl.worksheet.worksheet.Worksheet user_ws:
    :return:
    """
    # print(current_comments.keys())
    comments = current_comments['response']

    if type(comments) is dict and 'posts' in comments:
        # first format is different
        comments = comments['posts']
    for comment in comments:
        add_comment(comment, req_info, comment_ws, user_ws)

def get_next_comments(previous_comments, req_info):
    result = None

    if previous_comments['cursor']['hasNext']:
        # get next comments
        # https://disqus.com/api/3.0/threads/listPostsThreaded?limit=100&thread=6595667472&forum=breitbartproduction&order=popular&cursor=1%3A0%3A0&api_key=E8Uh5l5fHZ6gD8U3KycjAIAk46f68Zw7C6eW8WSjZvCLXebZ7p0r1yrYDrLilk2F
        cursor = previous_comments['cursor']['next']
        thread = req_info['thread']
        next_comments = requests.get(
            'https://disqus.com/api/3.0/threads/listPostsThreaded',
            {'limit': 100, 'forum': 'breitbartproduction', 'api_key': _API_KEY, 'cursor': cursor, 'thread': thread}
        )
        result = next_comments.json()

    print("got next comment")
    return result

@app.route('/')
def hello_world():
    req_info = {
        'users': set(),
        'thread': None
    }
    data = requests.get('http://www.breitbart.com/california/2018/04/04/report-nasim-aghdams-brother-warned-police-she-might-do-something/')
    match = re.search(_DISQUS_ID_RE, data.text)
    if not match:
        return "error: couldn't find disqus id"

    disqus_id = match.group(1)

    # first_comments = requests.get(f'https://disqus.com/embed/comments/?base=default&f=breitbartproduction&t_i={disqus_id}')
    first_comments = requests.get(
        'https://disqus.com/embed/comments/',
        params={'base': 'default', 'f': 'breitbartproduction', 't_i': disqus_id}
    )

    bs = BeautifulSoup(first_comments.text, 'html.parser')
    comment_json = bs.find(id="disqus-threadData").next
    comment_json = json.loads(comment_json)


    req_info['thread'] = comment_json['response']['thread']['id']


    wb = Workbook()
    comments = wb.create_sheet("Comments")
    comments.append(_comment_labels)
    users = wb.create_sheet("Users")
    users.append(_user_labels)


    while True:
        add_comments(comment_json, req_info, comments, users)
        comment_json = get_next_comments(comment_json, req_info)
        if comment_json is None:
            break


    name = f'{str(uuid.uuid4())}.xlsx'
    wb.save(name)
    return send_from_directory(".", name, attachment_filename="breitbart.xlsx")


    # return jsonify(comment_json)

if __name__ == '__main__':
    app.run()