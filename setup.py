#!/usr/bin/env python

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from setuptools import setup
import sys

install_requires = [
    'setuptools',
    'docopt',
    'docker-py>=1.2.1',
    'clint',  # to output colored text to terminal
    'requests>=2.5.2',  # help with docker-py requirement
    'watchdog' # For lesscd
]

exec(open("datacats/version.py").read())

setup(
    name='datacats',
    version=__version__,
    description='CKAN Data Catalog Developer Tools built on Docker',
    license='AGPL3',
    author='Boxkite',
    author_email='contact@boxkite.ca',
    url='https://github.com/datacats/datacats',
    packages=[
        'datacats',
        'datacats.tests',
        'datacats.cli',
        ],
    install_requires=install_requires,
    include_package_data=True,
    test_suite='datacats.tests',
    zip_safe=False,
    entry_points="""
        [console_scripts]
        datacats=datacats.cli.main:main
        datacats-lesscd=datacats.cli.lesscd:main
        """,
    )
