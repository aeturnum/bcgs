import asyncio
from datetime import datetime

from worksheet import WorksheetManager, WorkbookManager
from disqus_objects import User

from constants import DEBUG


class RequestInfo(object):
    def __init__(self, url):
        self.url = url
        self.title = "Title not found by tool - email this to aeturnum@gmail.com"
        self.start = datetime.utcnow()
        self.thread = None
        self.disqus_id = None
        self._timestamps = [self.start]

        # user variables
        self.users = set()
        self._user_tasks = 0
        self._user_management_lock = asyncio.Lock()
        self._user_record_event = asyncio.Event()

        self.comment_queue = asyncio.Queue()
        self.user_queue = asyncio.Queue()

        # debug variables
        self._print_lock = asyncio.Lock()

    async def create_workbook(self) -> WorkbookManager:
        wbm = WorkbookManager(self.title, self.url)

        await self.print_elapsed_time("Workbook Created")

        return wbm

    async def print_elapsed_time(self, label):
        if DEBUG:
            with await self._print_lock:
                self._timestamps.append(datetime.utcnow())
                start_delta = self._timestamps[-1] - self.start
                last_delta = self._timestamps[-1] - self._timestamps[-2]
                # print(f'[{start_delta.strftime("%H:%M:%S")}]{label}: +{last_delta.strftime("%H:%M:%S")}')
                print(f'[{start_delta}]{label}: +{last_delta}')

    async def add_user(self, user: User, user_ws: WorksheetManager):
        with await self._user_management_lock:
            if user.id in self.users:
                return

            # not done
            self._user_record_event.clear()
            self.users.add(user.id)
            self._user_tasks += 1

        await user.load()

        with await self._user_management_lock:
            # don't double-add users
            user_ws.append(user.user_info_row)
            await self.print_elapsed_time(f'Recorded User {user.id}')
            self._user_tasks -= 1
            if self._user_tasks == 0:
                self._user_record_event.set()

    async def wait_for_users_to_record(self):
        # block until all users are recorded
        await self._user_record_event.wait()