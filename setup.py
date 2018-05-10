#!/usr/bin/env python

from distutils.core import setup

setup(name='bcgs',
      version='0.1',
      description='Aiohttp server that grabs comments from breitbart and puts them in an xlsx file',
      author='Drex',
      author_email='aeturnum@gmail.com',
      packages=['bcgs'],
      license="MIT",
      install_requires=["beautifulsoup4", "requests", "openpyxl", "aiohttp"]
     )
