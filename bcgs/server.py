from aiohttp import web
import asyncio

import re
from bs4 import BeautifulSoup
import json
import traceback


from aiohttp_helpers import create_session
from request_helpers import RequestInfo
from disqus_objects import User
from worksheet import WorksheetManager
from constants import API_KEY, DISQUS_ID_RE

aioapp = web.Application()


#   "author": {
#         ... (see disqus_objects.py)
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

async def process_comment(comment, req_info: RequestInfo, comment_ws:WorksheetManager):
    try:
        user = User(comment['author'])

        row = [comment['id'], user.id, req_info.thread, comment['parent'], comment['thread']]
        if not user.private:
            row.extend([comment['createdAt'], comment['raw_message'], comment['likes']])

        comment_ws.append(row)

        # for private and anonymous users, do not record information
        if not user.private:
            await req_info.user_queue.put(user)

    except Exception as e:
        print("something went wrong with a comment")
        print(e)
        print(comment)

def unwrap_comments(comment_response):
    comments = comment_response['response']

    if type(comments) is dict and 'posts' in comments:
        # first format is different
        comments = comments['posts']

    return comments

async def record_comments(req_info: RequestInfo, comment_ws:WorksheetManager):
    while True:
        comment_response = await req_info.comment_queue.get()

        if comment_response is None:
            # signal we're done here too
            await req_info.user_queue.put(None)
            break

        comments = unwrap_comments(comment_response)

        for comment in comments:
            await process_comment(comment, req_info, comment_ws)

        await req_info.print_elapsed_time(f'Recorded {len(comments)} comments')

async def record_users(req_info: RequestInfo, user_ws:WorksheetManager):
    loop = asyncio.get_event_loop()
    while True:
        user = await req_info.user_queue.get()

        if user is None:
            # wait for all users to be recorded
            await req_info.wait_for_users_to_record()
            break

        loop.create_task(req_info.add_user(user, user_ws))


async def fetch_thread_comments(comments, req_info: RequestInfo):
    async with create_session() as session:
        while True:
            await req_info.comment_queue.put(comments)

            has_next = comments.get('cursor', {}).get('hasNext', False)
            if not has_next:
                # signal we're done
                await req_info.comment_queue.put(None)
                # leave
                break

            cursor = comments.get('cursor', {}).get('next')
            # https://disqus.com/api/3.0/threads/listPostsThreaded?limit=100&thread=6595667472&forum=breitbartproduction&order=popular&cursor=1%3A0%3A0&api_key=E8Uh5l5fHZ6gD8U3KycjAIAk46f68Zw7C6eW8WSjZvCLXebZ7p0r1yrYDrLilk2F

            comment_request =  await session.get(
                'https://disqus.com/api/3.0/threads/listPostsThreaded',
                params = {
                    'limit': 50, # god if only we could ask for more
                    'forum': 'breitbartproduction',
                    'api_key': API_KEY,
                    'cursor': cursor,
                    'thread': req_info.thread,
                    'order': 'popular'
                }
            )

            comments = await comment_request.json()

            await req_info.print_elapsed_time(f'Fetched Comments {cursor} & {req_info.thread}')


async def fetch_article_info(req_info: RequestInfo):
    async with create_session() as session:
        response = await session.get(req_info.url)
        data = await response.text()

        match = re.search(DISQUS_ID_RE, data)

        # if the match is wrong, return an empty id
        if match:
            req_info.disqus_id = match.group(1)

            title_parser = BeautifulSoup(data, 'html.parser')
            for meta_tag in title_parser.head.find_all('meta'):
                content = meta_tag.get('content', None)
                property = meta_tag.get('property', None)
                if property == 'og:title':
                    req_info.title = content

    await req_info.print_elapsed_time('Initial Request')
    return req_info


async def fetch_comments(request):
    try:
        # synchronous section
        data = await request.post()
        url_arg = data['URL']

        req_info = RequestInfo(url_arg)

        # 'http://www.breitbart.com/california/2018/04/04/log_report-nasim-aghdams-brother-warned-police-she-might-do-something/'
        req_info = await fetch_article_info(req_info)

        # first_comments = requests.get(f'https://disqus.com/embed/comments/?base=default&f=breitbartproduction&t_i={disqus_id}')
        comment_json = None
        async with create_session() as session:
            first_comments = await session.get(
                'https://disqus.com/embed/comments/',
                params={'base': 'default', 'f': 'breitbartproduction', 't_i': req_info.disqus_id}
            )

            bs = BeautifulSoup(await first_comments.text(), 'html.parser')
            comment_json = bs.find(id="disqus-threadData").next
            comment_json = json.loads(comment_json)

        if comment_json is None:
            raise Exception(f"Unable to load comments from {url_arg}")

        req_info.thread = comment_json['response']['thread']['id']
        await req_info.print_elapsed_time('First comment load')

        wb = await req_info.create_workbook()

        # end synchronous section

        await asyncio.gather(
            fetch_thread_comments(comment_json, req_info),
            record_comments(req_info, wb.comment_worksheet),
            record_users(req_info, wb.user_worksheet)
        )

        await req_info.print_elapsed_time("All Done")
        wb.save()

        return web.FileResponse(wb.path)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return web.json_response({
            'exception': str(e),
            'traceback': traceback.format_exc()
        })

async def index(request):
    return web.FileResponse("./static/index.html")

aioapp.add_routes([
    web.get('/', index),
    web.post('/comments', fetch_comments)
])
