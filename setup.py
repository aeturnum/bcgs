#!/usr/bin/env python

from distutils.core import setup

setup(name='bcgs',
      version='0.1',
      description='Flask framework that grabs comments from breitbart and puts them in an xls file',
      author='Drex',
      author_email='aeturnum@gmail.com',
      packages=['bcgs'],
      license="MIT",
      requires=["beautifulsoup4", "requests", "flask", "openpyxl"]
     )