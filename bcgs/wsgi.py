from server import aioapp
from aiohttp import web

application = aioapp

if __name__ == '__main__':
    web.run_app(aioapp)
