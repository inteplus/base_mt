#!/usr/bin/env python3

from setuptools import setup, find_packages, find_namespace_packages
from mt.base.version import VERSION

setup(name='basemt',
      version=VERSION,
      description="The most fundamental Python modules for Minh-Tri Pham",
      author=["Minh-Tri Pham"],
      packages=find_packages() + find_namespace_packages(include=['mt.*']),
      install_requires=[
          'colorama',  # for colored text
          'Cython',  # for fast speed on tiny objects
          'dask[distributed]',  # for simple multiprocessing jobs
      ]
      )
