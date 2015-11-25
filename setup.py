#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def readme():
    path = os.path.join(os.path.dirname(__file__), 'readme.rst')
    return open(path).read()


setup(name='reparse',
      version='2.1',
      description='Sane Regular Expression based parsers',
      long_description=readme(),
      author='Andy Chase',
      author_email='theandychase@gmail.com',
      url='http://github.com/andychase/reparse',
      download_url='https://github.com/andychase/reparse/archive/master.zip',
      license='MIT',
      packages=find_packages(exclude=["tests", ".tox"]),
      install_requires=[
          'regex',
          'pyyaml',
      ],
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing'
      ),
)
