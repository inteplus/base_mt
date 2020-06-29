#!/usr/bin/env python3

from setuptools import setup, find_packages
from mt.base.version import version

setup(name='basemt',
      version=version,
      description="The most fundamental Python modules for Minh-Tri Pham. The package is now deprecated. Use package 'mtbase' instead.",
      author=["Minh-Tri Pham"],
      packages=find_packages(),
      install_requires=[
          'mtbase>=0.4.0',
      ],
      url='https://github.com/inteplus/basemt',
      project_urls={
          'Documentation': 'https://basemt.readthedocs.io/en/stable/',
          'Source Code': 'https://github.com/inteplus/basemt',
          }
      )
