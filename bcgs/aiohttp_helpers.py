import aiohttp

from constants import VERIFY_SSL


def create_session():
    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=VERIFY_SSL))