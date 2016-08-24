#!/usr/bin/python3

# dvcz/setup.py

import re
from distutils.core import setup
__version__ = re.search("__version__\s*=\s*'(.*)'",
                        open('dvcz/__init__.py').read()).group(1)

# see http://docs.python.org/distutils/setupscript.html

setup(name='dvcz',
      version=__version__,
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      py_modules=[],
      packages=['dvcz'],
      # following could be in scripts/ subdir
      scripts=['dvcCommit'],
      description='a simple distributed version control system',
      url='https://jddixon.github.io/dvcz',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
