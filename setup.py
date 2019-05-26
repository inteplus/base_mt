#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='basemt',
      version='0.0.1',
      description="Most fundamental Python modules for Minh-Tri Pham",
      author=["Minh-Tri Pham"],
      packages=find_packages(),
      install_requires=[
        'colorama', # for colored text
        'Cython', # for fast speed on tiny objects
        'dask[distributed]', # for simple multiprocessing jobs
        'dask[dataframe]', # for reading chunks of CSV files in parallel
      ]
    )
