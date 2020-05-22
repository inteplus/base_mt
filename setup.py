#!/usr/bin/env python3

from setuptools import setup, find_packages, find_namespace_packages
from mt.base.version import version

setup(name='basemt',
      version=version,
      description="The most fundamental Python modules for Minh-Tri Pham",
      author=["Minh-Tri Pham"],
      packages=find_packages(where='src') + find_namespace_packages(include=['mt.*'], where='src'),
      package_dir={
          'basemt': 'src/basemt',
          'mt.base': 'src/mt/base',
      },
      install_requires=[
          'colorama',  # for colored text
          'Cython',  # for fast speed on tiny objects
          'dask[distributed]',  # for simple multiprocessing jobs
      ]
      )
