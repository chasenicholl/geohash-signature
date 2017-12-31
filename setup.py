#!/usr/bin/env python3
"""Setup for for installing geohash_signature module and CLI"""

from setuptools import setup, find_packages


setup(name='geohash_signature',
      version='0.0.1',
      url='https://github.com/chasenicholl/geohash-signature',
      author='Chase Nicholl',
      author_email='chasenicholl@gmail.com',
      packages=find_packages(),
      install_requires=['python-geohash', 'geojson', 'shapely'],
      extras_require={
          ':python_version == "2.7"': ['futures']
      },
      scripts=['scripts/geohash-signature'],
      test_suite='tests')
