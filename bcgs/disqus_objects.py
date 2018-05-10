import requests

import aiohttp
from constants import API_KEY

class User(object):
    def __init__(self, author_info):
            #   "author": {
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
        self._basic_info = author_info
        self._detailed_info = None

    async def load(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            user_info = await session.get(
                'https://disqus.com/api/3.0/users/details.json',
                params={'user': self.id, 'api_key': API_KEY}
            )

            detail_json = await user_info.json()
            if detail_json['code'] != 0:
                print(f'Problem with getting user details from user {self.id}')
                print(detail_json)

            self._detailed_info = detail_json['response']

    def _get_detailed_info(self):
        # https://disqus.com/api/3.0/users/details.json?user=137780765&api_key=E8Uh5l5fHZ6gD8U3KycjAIAk46f68Zw7C6eW8WSjZvCLXebZ7p0r1yrYDrLilk2F
        # {
        #     "code": 0,
        #     "response": {
        #         "about": "",
        #         "avatar": {
        #             "cache": "https://c.disquscdn.com/uploads/users/13778/765/avatar92.jpg?1433896551",
        #             "isCustom": true,
        #             "large": {
        #                 "cache": "https://c.disquscdn.com/uploads/users/13778/765/avatar92.jpg?1433896551",
        #                 "permalink": "https://disqus.com/api/users/avatars/disqus_FqhLpDGmTT.jpg"
        #             },
        #             "permalink": "https://disqus.com/api/users/avatars/disqus_FqhLpDGmTT.jpg",
        #             "small": {
        #                 "cache": "https://c.disquscdn.com/uploads/users/13778/765/avatar32.jpg?1433896551",
        #                 "permalink": "https://disqus.com/api/users/avatars/disqus_FqhLpDGmTT.jpg"
        #             }
        #         },
        #         "disable3rdPartyTrackers": false,
        #         "id": "137780765",
        #         "isAnonymous": false,
        #         "isPowerContributor": false,
        #         "isPrimary": true,
        #         "isPrivate": false,
        #         "joinedAt": "2015-01-02T18:40:14",
        #         "location": "",
        #         "name": "Bob",
        #         "numFollowers": 2,
        #         "numFollowing": 0,
        #         "numForumsFollowing": 0,
        #         "numLikesReceived": 8967,
        #         "numPosts": 4147,
        #         "profileUrl": "https://disqus.com/by/disqus_FqhLpDGmTT/",
        #         "rep": 3.5297520000000002,
        #         "reputation": 3.5297520000000002,
        #         "reputationLabel": "High",
        #         "signedUrl": "",
        #         "url": "",
        #         "username": "disqus_FqhLpDGmTT"
        #     }
        # }
        print("WARNING: auto-loading user in async version of code!!!!")
        details = requests.get(
            'https://disqus.com/api/3.0/users/details.json',
            {'user': self.id, 'api_key': API_KEY}
        )

        detail_json = details.json()
        if detail_json['code'] != 0:
            print(f'Problem with getting user details from user {self.id}')
            print(detail_json)

        self._detailed_info = detail_json['response']

    @property
    def anonymous(self):
        return 'id' not in self._basic_info

    @property
    def private(self):
        return self.anonymous or self._basic_info.get('isPrivate')

    @property
    def id(self):
        if self.private:
            return 'Private'
        return self._basic_info.get('id', 'Anonymous')

    @property
    def name(self):
        return self._basic_info.get('name')

    @property
    def username(self):
        return self._basic_info.get('username')

    @property
    def location(self):
        return self._basic_info.get('location')

    @property
    def joined_at(self):
        return self._basic_info.get('joinedAt')

    @property
    def profile_url(self):
        return self._basic_info.get('profileUrl')

    @property
    def total_posts(self):
        if self._detailed_info is None:
            self._get_detailed_info()
        return self._detailed_info.get('numPosts')

    @property
    def total_likes(self):
        if self._detailed_info is None:
            self._get_detailed_info()
        return self._detailed_info.get('numLikesReceived')

    @property
    def user_info_row(self):
        return [
            self.id,
            self.name,
            self.username,
            self.total_posts,
            self.total_likes,
            self.location,
            self.joined_at,
            self.profile_url
        ]
