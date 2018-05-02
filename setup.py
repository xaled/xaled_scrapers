#!/usr/bin/env python3

from distutils.core import setup

import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if not path.endswith('__pycache__') and not filename.endswith(".pyc"):
                paths.append(os.path.relpath(os.path.join(path, filename), directory))
    return paths

extra_files = package_files('xaled_scrapers/')

#print extra_files

setup(
      name='xaled_scrapers',
      version='0.1.0', # major.minor.fix: MAJOR incompatible API changes, MINOR add backwards-compatible functionality, FIX bug fixes
      description='A collection of helper functions for scraping web sites.',
      long_description='A collection of helper functions for scraping web sites.',
      long_description_content_type='text/x-rst',
      keywords='scraper selenium proxy',
      author='Khalid Grandi',
      author_email='kh.grandi@gmail.com',
      url='https://github.com/xaled/xaled_scrapers/',
      install_requires=['selenium', 'requests', 'pyquery', 'pyvirtualdisplay', 'mitmproxy>=2,<3',' xaled_utils'],
      python_requires='>=3',
      packages=['xaled_scrapers'],
      package_data={'': extra_files},
     )
