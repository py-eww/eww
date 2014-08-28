#! /usr/bin/env python

from setuptools import setup

import eww

setup(name='eww',
      version = eww.__version__,
      url = 'https://eww.io',
      license = 'MIT',
      author = 'Alex Philipp',
      author_email = 'alex@eww.io',
      description = 'A pretty nifty debugger.',
      long_description = open('README.rst').read(),
      packages = ['eww'],
      install_requires=['pygal == 1.5.0'],
      scripts = ['scripts/eww'],
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: System Administrators',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 2 :: Only',
                     'Programming Language :: Python :: Implementation :: CPython',
                     'Programming Language :: Python :: Implementation :: PyPy',
                     'Topic :: Software Development :: Debuggers',
                     'Topic :: Software Development :: Interpreters',
                     'Topic :: Software Development :: Quality Assurance',
                     'Topic :: System :: Monitoring',
                     'Topic :: System :: Systems Administration',
                     'Topic :: Utilities'])
