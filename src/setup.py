#!/usr/bin/env python
# encoding: utf-8

import setuptools
from setuptools import setup, find_packages


setup(name='django-futures',
      version='0.1.0.0',
      description="Django asynchronous views and Tornado integration made easy.",
      author="Jeff Buttars",
      author_email="jeffbuttars@gmail.com",
      packages=find_packages(),
      license='MIT',
      package_dir={'django_futures': 'django_futures'},
      install_requires=[
          'tornado',
          'Django',
      ],
      # data_files=[
      #     ('/etc/init.d', ['conf/init.d/afile']),
      # ],
      )
